# Research: subset-b-004637

This grouped report covers the Solarflare/SFC Siena Management Controller Driver Interface core, public header contract, and hardware-monitor sensor integration. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.c

## Purpose
This file implements the Siena driver's Management Controller Driver Interface transport and a large set of firmware command helpers. It serializes MCDI requests, builds v1/v2 command headers, waits by polling or completion events, handles asynchronous request queues, translates firmware errors to Linux errno values, detects management-controller reboot/assertion/BIST events, and exposes utility commands for board configuration, firmware version, logging, NVRAM, wake-on-LAN, queue flushing, reset, and optional MTD-backed flash access.

## Important APIs, Types, And Functions
- Lifecycle entry points: `efx_siena_mcdi_init()`, `efx_siena_mcdi_detach()`, and `efx_siena_mcdi_fini()` allocate `efx->mcdi`, initialize wait queues, locks, async list/timer, optional logging buffer, poll for prior MC reboot state, recover assertions, and attach/detach the host driver with firmware.
- Core request path: `efx_mcdi_send_request()`, `efx_mcdi_read_response_header()`, `efx_mcdi_poll_once()`, `efx_mcdi_poll()`, `efx_mcdi_acquire_sync()`, `efx_mcdi_release()`, and `_efx_mcdi_rpc_finish()` implement one-at-a-time request ownership and response copying.
- Public RPC APIs: `efx_siena_mcdi_rpc()`, `efx_siena_mcdi_rpc_quiet()`, `efx_siena_mcdi_rpc_start()`, `efx_siena_mcdi_rpc_finish()`, and quiet finish variants are the main synchronous interface used by port, PTP, SR-IOV, hwmon, MTD, and board code.
- Async APIs: `_efx_mcdi_rpc_async()`, `efx_siena_mcdi_rpc_async()`, `efx_siena_mcdi_rpc_async_quiet()`, `efx_mcdi_complete_async()`, `efx_mcdi_timeout_async()`, and `efx_siena_mcdi_flush_async()` queue event-mode requests and guarantee exactly one completion callback on event, timeout, or queue cancellation.
- Event integration: `efx_siena_mcdi_process_event()` dispatches CMDDONE, link, sensor, reboot, BIST, FLR, PTP, flush, DMA-error, and proxy-response events to the relevant driver subsystems.
- Recovery helpers: `efx_mcdi_ev_death()`, `efx_mcdi_ev_bist()`, `efx_mcdi_abandon()`, `efx_siena_mcdi_poll_reboot()`, `efx_siena_mcdi_handle_assertion()`, and `efx_siena_mcdi_reset()` bridge firmware failure signals into the driver's reset machinery.
- Firmware command helpers include `efx_siena_mcdi_print_fwver()`, `efx_siena_mcdi_get_board_cfg()`, `efx_siena_mcdi_log_ctrl()`, `efx_siena_mcdi_nvram_types()`, `efx_siena_mcdi_nvram_info()`, `efx_siena_mcdi_nvram_test_all()`, ID LED, WOL filter, RX queue flush, and optional `efx_siena_mcdi_mtd_*()` operations.

## Control Flow
Initialization allocates `struct efx_mcdi_data`, puts the interface in `MCDI_MODE_POLL`, checks for MC reboot state, marks `new_epoch`, reads and clears any stored assertion, sends `MC_CMD_DRV_ATTACH`, and records function flags such as primary function ownership. Normal synchronous RPC flow checks command/version/length support, rejects calls while another function owns MC BIST or while mode is fail-fast, atomically changes the interface state from `QUIESCENT` to `RUNNING_SYNC`, writes the request into device MCDI shared memory through `efx->type->mcdi_request()`, then either polls shared memory or waits for an event-driven transition to `COMPLETED`.

Event-mode completions arrive through `efx_siena_mcdi_process_event()` and `efx_mcdi_ev_cpl()`. The completion event sequence is matched against `mcdi->seqno`; v2 completions force a shared-memory response-header read, while v1 completions can carry errno and data length directly. A matching event completes either a queued async request or the current sync waiter. Polling mode calls the NIC type's `mcdi_poll_response()` repeatedly with a fast initial microsecond spin and slower jiffy pacing until `MCDI_RPC_TIMEOUT`.

The async flow allocates a `struct efx_mcdi_async_param` followed by an aligned request/response buffer, appends it to `async_list`, and starts it immediately only if it reaches the queue head and can acquire `RUNNING_ASYNC`. Completion reads the response into the buffer, calls the provided completer in atomic context, deletes the timer when appropriate, frees the queue node, and then `efx_mcdi_release()` starts the next queued async request before returning to `QUIESCENT`.

Error and recovery control flow is deliberately conservative. Timeout in `_efx_mcdi_rpc_finish()` logs, optionally detects a completed response that missed its event, calls `efx_mcdi_abandon()` to enter `MCDI_MODE_FAIL`, increments `seqno` and `credits` so a late event is ignored, and schedules an MCDI-timeout reset. MC reboot/assertion/BIST events abort proxy waits, complete sync waiters with `-EIO` or `-EINTR`, poll for the status word, set `new_epoch`, and schedule the appropriate reset. Proxy authorization errors place the state into `MCDI_STATE_PROXY_WAIT`, wait on `proxy_rx_wq`, and retry the original command if the proxy response authorizes it.

The bottom half of the file layers command-specific helpers on top of the transport. Board and firmware helpers validate minimum response lengths before reading fields. NVRAM helpers enumerate, query, and test flash partitions. Optional MTD functions split reads and writes into 128-byte MCDI chunks, start update sessions lazily on erase/write, finish and verify updates in sync, and rename partitions with firmware subtype data.

## State And Persistence
Primary runtime state lives in `struct efx_mcdi_iface`: request state, mode, wait queues, `iface_lock`, sequence number, late-event credits, response metadata, async lock/list/timer, optional page-sized trace buffer, epoch flag, and proxy authorization wait state. `struct efx_mcdi_data` also stores `fn_flags` returned by `MC_CMD_DRV_ATTACH`.

The file does not persist state to disk. It does persist state in firmware and hardware through MCDI commands: driver attachment, selected firmware ID, MC reboot/function reset requests, WOL filters, NVRAM contents, NVRAM update sessions, log destinations, LED state, and RX queue flushes. In-memory `new_epoch` controls the MCDI header's epoch bit after startup or reboot recovery. Optional `struct efx_mcdi_mtd_partition::updating` tracks whether an MTD erase/write session has begun and must be finished.

## Dependencies And Integration Points
The implementation depends on the Siena NIC type operation vector for hardware-specific MCDI transport hooks: `mcdi_request`, `mcdi_read_response`, `mcdi_poll_response`, `mcdi_poll_reboot`, optional `mcdi_reboot_detected`, SR-IOV FLR, and firmware-version extension printing. It uses MCDI protocol constants and layouts from `mcdi_pcol.h`, bitfield helpers from the SFC support headers, Linux timers/wait queues/spinlocks/jiffies, PCI reset, and netdev logging.

Higher layers call this file heavily. Port and MAC code use `efx_siena_mcdi_rpc()` for PHY, link, loopback, MAC stats, and media commands. `ptp.c` uses synchronous start/finish paths for timestamp-sensitive commands. `siena_sriov.c` uses it for SR-IOV and memory copy commands. `mcdi_mon.c` uses it to enumerate and read sensors. `siena.c` calls init/probe/remove helpers and wires optional MTD callbacks. `efx_channels.c` switches between poll and event modes when event queues start/stop, and `farch.c` forwards MCDI events into `efx_siena_mcdi_process_event()`.

## Risks And Edge Cases
- The state machine is lock-light and relies on `cmpxchg()`, barriers, wait queues, and lock ordering across process, NAPI, timer, and reset contexts. Reordering state, mode, or response metadata updates can create missed wakeups or stale response reads.
- Late completion events are handled with `seqno` increments and `credits`; changes around timeout or async cancellation must preserve this duplicate/late-event suppression.
- `efx_siena_mcdi_mode_poll()` is intentionally lockless and may be called with arbitrary locks held; adding locking can deadlock error paths.
- Async completions run in atomic context and must not sleep. `efx_siena_mcdi_flush_async()` avoids holding `async_lock` while invoking callbacks to prevent lock-order inversions.
- MCDI v1 and v2 header formats differ. Command length and command-space checks in `efx_mcdi_check_supported()` protect older firmware and must track protocol limits.
- Proxy authorization temporarily keeps the interface out of `QUIESCENT`; failures must always release it or subsequent MCDI callers will block.
- MTD update state is per partition and assumes callers eventually call sync. Failed erase/write paths may leave `updating` true so a later sync can finish the firmware update session.
- Several helpers trust firmware response layouts after minimum length checks; any new variable-length command must validate outlen before every field read.

## Test Signals
Build with and without `CONFIG_SFC_SIENA_MCDI_LOGGING` and `CONFIG_SFC_SIENA_MTD`. Runtime signals include successful probe attach, firmware-version display, board config read, transition from polling to event completion as event queues start, normal CMDDONE completion under link/PHY/PTP traffic, async queue completion and timeout callbacks, event-queue shutdown flushing pending async requests with `-ENETDOWN`, MC reboot/assertion/BIST events scheduling resets, MCDI timeout switching to fail-fast and FLR recovery, proxy authorization retry behavior, NVRAM type/info/test success, WOL filter set/get/remove/reset, RX flush drain completion, and MTD read/erase/write/sync verification. Negative tests should cover short firmware responses, unsupported commands, oversized SDUs, sequence mismatches, missed events with polling fallback, and unload after queued async work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.h

## Purpose
This header defines the Siena driver's internal MCDI contract: request state and mode enums, protocol context structures, monitor and MTD extension structures, public MCDI transport APIs, event hooks, command helper prototypes, and the macros used to declare, populate, and decode MCDI request/response buffers safely.

## Important APIs, Types, And Functions
- `enum efx_mcdi_state` models the single-request state machine: `QUIESCENT`, synchronous running, asynchronous running, proxy wait, and completed-but-not-consumed.
- `enum efx_mcdi_mode` selects polling, event-driven completions, or fail-fast behavior after severe timeout.
- `struct efx_mcdi_iface` stores NIC association, state, mode, wait queues, locks, sequence/error/response metadata, async queue/timer, optional logging fields, and proxy response wait state.
- `struct efx_mcdi_data` embeds the MCDI interface, optional `struct efx_mcdi_mon`, and function flags returned from firmware attach.
- `struct efx_mcdi_mon` and `struct efx_mcdi_mtd_partition` define shared state for hwmon sensor export and optional MTD flash partitions.
- Accessors `efx_mcdi()` and optional `efx_mcdi_mon()` enforce the expected `efx->mcdi` allocation and return embedded substructures.
- RPC prototypes expose synchronous, quiet, split start/finish, and asynchronous MCDI command paths plus mode switching, async flushing, event processing, reboot polling, reset mapping, and command-specific helpers.
- Buffer macros such as `MCDI_DECLARE_BUF()`, `MCDI_PTR()`, `MCDI_SET_DWORD()`, `MCDI_DWORD()`, `MCDI_SET_QWORD()`, `MCDI_ARRAY_FIELD()`, and `MCDI_EVENT_FIELD()` centralize field offset, alignment, endian, and bitfield access for generated MCDI protocol definitions.

## Control Flow
Most source files include this header, declare stack MCDI buffers with `MCDI_DECLARE_BUF()`, fill fields with the `MCDI_SET_*` and `MCDI_POPULATE_*` macros, call an `efx_siena_mcdi_rpc*()` function, then decode outbuf fields with `MCDI_*` accessors after checking response length. Event paths decode MCDI event qwords with `MCDI_EVENT_FIELD()` and pass events to the handlers declared here.

The state/mode definitions are consumed by `mcdi.c` to serialize callers and by surrounding driver code to switch completion modes when event queues are enabled or disabled. Conditional prototypes and inline stubs make hwmon monitoring disappear when `CONFIG_SFC_SIENA_MCDI_MON` is disabled while preserving call sites.

## State And Persistence
The header declares runtime-only in-memory state. It does not write hardware or persistent storage by itself. Persistent effects happen through functions declared here, especially NVRAM/MTD operations, WOL filters, firmware driver attach/detach, and reset commands implemented in `mcdi.c`. Compile-time state is shaped by `CONFIG_SFC_SIENA_MCDI_LOGGING`, `CONFIG_SFC_SIENA_MCDI_MON`, and `CONFIG_SFC_SIENA_MTD`.

The buffer macros enforce a critical persistence boundary between C structures and firmware ABI: MCDI buffers are dword arrays with explicit little-endian field access rather than native packed C structs. This avoids accidental host layout dependence while matching shared-memory and event formats.

## Dependencies And Integration Points
The header assumes `struct efx_nic`, `struct efx_channel`, `efx_dword_t`, `efx_qword_t`, reset types, LED modes, MTD wrapper types, and generated `MC_CMD_*` constants are available through neighboring Siena headers. It is included by MCDI core code, port/MAC/PHY code, PTP, SR-IOV, hwmon, MTD, board probe, ethtool firmware display, and event processing paths.

It also defines capability helpers, `MCDI_CAPABILITY()`, `MCDI_CAPABILITY_OFST()`, and `efx_has_cap()`, that map generated capability bit names to the NIC type's `check_caps()` implementation. Those helpers tie firmware capability discovery to feature gating elsewhere in the driver.

## Risks And Edge Cases
- The MCDI field macros depend on generated protocol offset and length constants being accurate. Wrong constants or misuse of a field macro on the wrong buffer type will compile but decode incorrect firmware data.
- `_MCDI_CHECK_ALIGN()` catches required alignment at build time for scalar access. New protocol fields with unusual alignment need appropriate array/pointer helpers rather than raw casts.
- `MCDI_VAR_ARRAY_LEN()` subtracts a field offset from the supplied response length; callers must first ensure the response reaches the array offset to avoid size underflow.
- The accessor macros cast byte pointers into `efx_dword_t *` or little-endian scalar pointers. The surrounding comments document that 64-bit MCDI fields are only 32-bit aligned, so users must keep using the split dword qword helpers.
- State enum semantics are part of the concurrency contract. Adding new states or mode transitions requires auditing wait predicates, `cmpxchg()` transitions, and async release logic.
- Conditional inline stubs for hwmon mean call sites cannot infer whether monitoring was actually registered from a successful return unless configuration is known.

## Test Signals
Compile coverage is the primary signal for field-name macros, response-layout constants, and conditional configuration combinations. Runtime signals include successful use of declared RPC APIs by port, PTP, SR-IOV, hwmon, WOL, NVRAM, and reset paths. Tests should exercise buffer macros on 8-, 16-, 32-, and 64-bit fields, variable arrays, event fields, capability checks, build variants with MCDI logging/hwmon/MTD enabled and disabled, and static analysis for invalid pointer aliasing or missing response-length checks before macro reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_mon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_mon.c

## Purpose
This file implements Siena MCDI sensor handling and optional Linux hwmon device registration. It maps firmware sensor IDs to human-readable labels, hwmon classes, units, and port affinity; logs asynchronous sensor-warning events; queries firmware sensor pages; allocates a DMA buffer for sensor readings; and creates read-only sysfs hwmon attributes for values, thresholds, alarms, and labels.

## Important APIs, Types, And Functions
- `enum efx_hwmon_type` classifies firmware sensors as temperature, cooling/fan, voltage, current, power, or unknown.
- `efx_mcdi_sensor_type[]` maps `MC_CMD_SENSOR_*` IDs to label, hwmon type, and optional port number. The table includes board, PHY, fan, regulator, AOE, current, power, internal ADC, ambient, airflow, and hotpoint sensors known to this driver.
- `sensor_status_names[]` maps firmware sensor state IDs to text used in warning logs.
- `efx_siena_mcdi_sensor_event()` decodes MCDI sensor events and emits a netdev hardware error message with sensor ID, label, state text, value, and unit.
- Under `CONFIG_SFC_SIENA_MCDI_MON`, `struct efx_mcdi_mon_attribute` stores one sysfs `device_attribute` plus sensor index/type, hwmon class, cached threshold value, and generated attribute name.
- `efx_mcdi_mon_update()` sends `MC_CMD_READ_SENSORS` with a DMA address and length so firmware writes current sensor entries into the DMA buffer.
- `efx_mcdi_mon_get_entry()` caches readings for one second under `update_lock` and returns a requested sensor entry.
- Attribute readers `efx_mcdi_mon_show_value()`, `efx_mcdi_mon_show_limit()`, `efx_mcdi_mon_show_alarm()`, and `efx_mcdi_mon_show_label()` implement hwmon sysfs reads.
- `efx_siena_mcdi_mon_probe()` discovers sensors via paged `MC_CMD_SENSOR_INFO`, allocates DMA and attribute arrays, creates conventional hwmon names, and registers `hwmon_device_register_with_groups()`. `efx_siena_mcdi_mon_remove()` unregisters and frees those resources.

## Control Flow
Sensor events can be processed regardless of hwmon registration. `efx_siena_mcdi_process_event()` dispatches sensor event qwords to the driver's sensor handler, which extracts monitor, state, and value fields, looks up metadata if known, substitutes fallback text for unknown sensor names, and logs a hardware warning/error.

When hwmon support is enabled, probe first walks `MC_CMD_SENSOR_INFO` pages by repeatedly setting `SENSOR_INFO_EXT_IN_PAGE`, reading the response mask, counting present sensors, and following the `MC_CMD_SENSOR_PAGE0_NEXT` bit. If no sensors are present, it returns success without registering a device. Otherwise it allocates a DMA buffer sized for one `MC_CMD_SENSOR_VALUE_ENTRY_TYPEDEF` per present sensor, initializes the update mutex, performs an initial sensor read, allocates maximum possible attribute objects and attribute pointers, then walks the same paged sensor masks to build sysfs attributes.

For each present sensor, probe skips known sensors that belong to a different physical port. It selects hwmon prefix/index conventions (`temp` and `fan` are 1-based, `in` is 0-based, `curr` and `power` are 1-based), reads min/max threshold pairs from the sensor info entry, and creates `<prefix><n>_input`, `_min`, `_max`, optional `_crit`, `_alarm`, and optional `_label` attributes. Finally it registers a hwmon device with a single attribute group. On any failure after allocation, the shared fail path calls `efx_siena_mcdi_mon_remove()`.

Sysfs reads take the device's parent driver data to recover `struct efx_nic`, lock `update_lock`, refresh from firmware only if the cached buffer is at least one second old, copy the requested entry from DMA memory, and unlock. Value and limit reads convert temperature from degrees C to millidegrees and power from watts to microwatts to match Linux hwmon conventions. `NO_READING` maps to `-EBUSY`; alarms report non-OK firmware states as `1`.

## State And Persistence
Runtime state is stored in `struct efx_mcdi_mon`: DMA buffer, update mutex, last update jiffies, registered hwmon device, dynamic attribute array, attribute group, group list, and attribute count. Each attribute stores immutable sensor metadata and threshold values captured during probe. The DMA buffer holds the most recent firmware-written sensor values and is refreshed on demand with a one-second cache window.

There is no disk persistence. Firmware remains the authoritative source of sensor topology, thresholds, states, and readings. Sysfs attributes are created at probe and persist until `efx_siena_mcdi_mon_remove()` unregisters the hwmon device and frees arrays/DMA memory.

## Dependencies And Integration Points
The file depends on Linux hwmon, sysfs device attributes, slab allocation, bit operations, jiffies caching, and the Siena DMA buffer helpers `efx_siena_alloc_buffer()`/`efx_siena_free_buffer()`. It consumes MCDI protocol definitions from `mcdi_pcol.h` and request-buffer helpers from `mcdi.h`. It is called from Siena probe/remove paths in `siena.c` when `CONFIG_SFC_SIENA_MCDI_MON` is enabled and from the MCDI event dispatcher for sensor events. It depends on `efx_port_num()` to hide per-port sensors that do not belong to the current NIC function.

## Risks And Edge Cases
- `efx_siena_mcdi_sensor_event()` warns if the state index is outside `sensor_status_names`, but then indexes the table. If firmware emits a new out-of-range state, this can produce a bad pointer read rather than a graceful fallback.
- Unknown sensor types default to `EFX_HWMON_UNKNOWN` and are exposed with `in`-style naming if present. That may be semantically poor but keeps readings visible.
- The probe path counts all sensors in the firmware masks before later skipping wrong-port sensors; allocation is intentionally sized for the upper bound, so attribute storage can be larger than used.
- Attribute names are limited to 12 bytes. Current hwmon names fit, but adding longer prefixes or large indices could truncate names through `strscpy()` or `snprintf()`.
- `efx_mcdi_mon_get_entry()` copies the requested DMA entry even if `efx_mcdi_mon_update()` failed; it still returns the error, so current readers do not use the copied value, but future callers must preserve that ordering.
- Sensor info page handling depends on the page-next bit and variable response length checks. New firmware page formats or masks wider than 32 bits would require updates.
- Remove must unregister hwmon before freeing attributes and DMA memory because sysfs callbacks dereference both.

## Test Signals
Build with `CONFIG_SFC_SIENA_MCDI_MON` enabled and disabled. Runtime tests should verify sensor-info enumeration across one and multiple pages, no-device behavior when firmware reports zero sensors, correct filtering of PHY0/PHY1 port-specific sensors, sysfs attribute names and permissions, one-second cache behavior, value conversions for temperature and power, `-EBUSY` on `NO_READING`, alarm output for warning/fatal/broken states, label output for known sensors, clean fail-path cleanup after allocation or registration failures, clean remove/unload with active sysfs readers, and correct log output for sensor events including unknown sensor IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_mon.c -->
