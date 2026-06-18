# Research: subset-b-004627

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.c

## Purpose
`mcdi.c` is the core Management Controller Driver Interface implementation for the Solarflare/Xilinx `sfc` NIC driver. It serializes commands to the firmware management controller, supports synchronous and asynchronous RPCs, decodes completions from polling or MCDI events, handles management-controller reboot/assertion/BIST conditions, and exposes common firmware commands for attach/detach, board configuration, firmware version, workarounds, privilege masks, NVRAM, wake-on-LAN, LED control, and reset flows.

The file is the central dependency for most higher-level driver modules that need firmware services. It turns driver-side command buffers built with `MCDI_*` macros into calls through `efx->type->mcdi_request`, reads responses through `efx->type->mcdi_read_response`, and maps raw firmware errors to Linux errno values.

## Important APIs, Types, And Functions
The public RPC surface is `efx_mcdi_rpc()`, `efx_mcdi_rpc_quiet()`, `efx_mcdi_rpc_start()`, `efx_mcdi_rpc_finish()`, and `efx_mcdi_rpc_async()`. The quiet variant suppresses automatic error logging so callers can tolerate expected firmware errors. The split start/finish calls let code issue an RPC and complete it later, but the interface remains globally serialized per NIC by `struct efx_mcdi_iface`.

Lifecycle functions are `efx_mcdi_init()`, `efx_mcdi_detach()`, and `efx_mcdi_fini()`. Init allocates `efx->mcdi`, initializes wait queues/spinlocks/async list/timer, polls for any pre-existing reboot, reads and exits saved MC assertions, performs `MC_CMD_DRV_ATTACH`, and marks primary functions from `DRV_ATTACH_EXT` flags. Detach calls `DRV_ATTACH` with driver-operating false and requires the interface to be quiescent. Fini releases logging storage and the MCDI object.

Internal state-machine helpers include `efx_mcdi_acquire_sync()`, `efx_mcdi_acquire_async()`, `efx_mcdi_release()`, `efx_mcdi_complete_sync()`, `efx_mcdi_complete_async()`, `efx_mcdi_poll()`, `efx_mcdi_poll_once()`, `efx_mcdi_await_completion()`, and `efx_mcdi_abandon()`. These operate on `MCDI_STATE_QUIESCENT`, `RUNNING_SYNC`, `RUNNING_ASYNC`, `PROXY_WAIT`, and `COMPLETED`, and on modes `MCDI_MODE_POLL`, `EVENTS`, and `FAIL`.

Event handling enters through `efx_mcdi_process_event()`. It dispatches command completion, link change, sensor, PTP, time sync, TX/RX flush, DMA error, proxy response, MC reboot, bad assertion, and BIST events. `efx_mcdi_ev_death()` and `efx_mcdi_ev_bist()` complete or abort outstanding waits, set reboot epoch state, and schedule resets.

Firmware service helpers include `efx_mcdi_print_fwver()`, `efx_mcdi_get_board_cfg()`, `efx_mcdi_log_ctrl()`, `efx_mcdi_nvram_types()`, `efx_new_mcdi_nvram_test_all()`, `efx_mcdi_nvram_test_all()`, `efx_mcdi_nvram_info()`, `efx_mcdi_nvram_metadata()`, `efx_mcdi_nvram_update_start()`, `efx_mcdi_nvram_write()`, `efx_mcdi_nvram_erase()`, `efx_mcdi_nvram_update_finish()`, `efx_mcdi_nvram_update_finish_polled()`, `efx_mcdi_set_id_led()`, `efx_mcdi_reset()`, `efx_mcdi_set_workaround()`, `efx_mcdi_get_workarounds()`, `efx_mcdi_get_privilege_mask()`, and optional MTD callbacks under `CONFIG_SFC_MTD`.

## Control Flow
For a normal synchronous command, `efx_mcdi_rpc()` calls `_efx_mcdi_rpc_evb_retry()`, which calls `_efx_mcdi_rpc()`. `_efx_mcdi_rpc()` validates buffer aliasing, calls `efx_mcdi_rpc_start()` to check command/version/length support, blocks if the MC is in BIST or fail-fast mode, atomically transitions the interface from quiescent to `RUNNING_SYNC`, and calls `efx_mcdi_send_request()`. The sender increments the sequence number under `iface_lock`, builds either an MCDI v1 header or an MCDI v2 extension header, optionally logs the request, submits it through the NIC type operation, and clears `new_epoch`.

Completion then flows through `_efx_mcdi_rpc_finish()`. In poll mode it runs `efx_mcdi_poll()`, which first checks reboot status, then polls rapidly for one jiffy and backs off to jiffy sleeps until `MCDI_RPC_TIMEOUT`. In event mode it waits for `MCDI_STATE_COMPLETED`, then falls back to polling if the driver switched to poll mode while waiting. Response headers are read in `efx_mcdi_read_response_header()`, which validates sequence, detects reboot-style zero-length error responses, maps firmware error codes, and records header/data lengths. The finish path copies response data to the caller, copies error data for logging, handles `-EIO`/`-EINTR` as MC reboot signals, and releases the interface unless it enters proxy wait.

Proxy authorization is a secondary control path. If a response is an `MC_CMD_ERR_PROXY_PENDING`, `_efx_mcdi_rpc_finish()` extracts a proxy handle and sets `MCDI_STATE_PROXY_WAIT`. `_efx_mcdi_rpc()` waits on `proxy_rx_wq` for `MCDI_EVENT_CODE_PROXY_RESPONSE`, retries the original request on approval, or releases the interface and may schedule reset on fatal proxy interruption.

Asynchronous RPCs allocate `struct efx_mcdi_async_param` with an inline request/response buffer, queue it under `async_lock`, and start the front request only in event mode. `efx_mcdi_complete_async()` handles normal or timeout completion in atomic context, reads response data, invokes the registered callback exactly once, frees the request object, and starts the next queued async request from `efx_mcdi_release()`.

Reset and fault control flow is deliberately conservative. Timeouts call `efx_mcdi_abandon()`, switch mode to `MCDI_MODE_FAIL`, and schedule `RESET_TYPE_MCDI_TIMEOUT`; recovery uses PCI function reset and restores poll mode. MC reboot/assertion events wake synchronous waiters or schedule MC-failure reset if no command owned the failure. BIST events set `efx->mc_bist_for_other_fn`, abort proxy waits, complete sync commands with `-EIO`, and schedule `RESET_TYPE_MC_BIST`.

NVRAM control flow uses small MCDI chunks. Read/write paths cap chunks at `EFX_MCDI_NVRAM_LEN_MAX` for MTD integration, start update sessions lazily on first erase/write, and finish with either wait, background, poll, or abort flags depending on firmware capabilities. `efx_mcdi_nvram_update_finish_polled()` uses background finish followed by exponential poll intervals up to the retry limit, translating firmware verification result codes to Linux errno.

## State And Persistence Behavior
All request state is volatile in `struct efx_mcdi_iface`: sequence number, current state, mode, response status/lengths, async queue, timer, proxy state, and the `new_epoch` flag. The MC command stream is serialized per NIC, so callers do not persist per-command state outside the response buffer unless using async cookies. `credits` tolerates late completion events after cancellation by allowing a bounded number of sequence mismatches.

Persistent state exists only when commands affect firmware or NVRAM. `DRV_ATTACH` changes MC-side driver ownership state. NVRAM write/erase/update operations modify persistent firmware partitions, with verification results surfaced by `NVRAM_UPDATE_FINISH`. Wake-on-LAN filters and LED settings are firmware-managed device state, not host disk state. MTD partition `updating` flags are RAM state used to bracket update sessions.

`new_epoch` marks start-of-day or reboot recovery and changes the `NOT_EPOCH` header bit. After MC reboot or assertion, the driver sleeps long enough for the status word to settle, polls reboot status, and marks the next command as a new epoch.

## Dependencies And Integration Points
This file depends on `net_driver.h`, `nic.h`, `io.h`, `mcdi_pcol.h`, Linux timers/wait queues/spinlocks/PCI reset/MTD support, and many NIC type callbacks in `efx->type`: request, response read, completion poll, reboot poll, reboot notification, capability-specific firmware-version printing, and reset scheduling.

It integrates with link handling through `efx_mcdi_process_link_change()`, sensor handling through `efx_sensor_event()`, PTP/time sync through `efx_ptp_event()` and `efx_time_sync_event()`, queue teardown through `efx->active_queues` and `flush_wq`, and global reset through `efx_schedule_reset()`. It is also the dependency layer for `mcdi_filters.c`, `mcdi_functions.c`, `mcdi_mon.c`, MAC code, PHY code, ethtool operations, and MTD partition code.

## Risks And Edge Cases
The most sensitive behavior is concurrency around `state`, `seqno`, response metadata, and events. The code uses `cmpxchg`, spinlocks, wait queues, memory barriers, and completion credits to handle late events, duplicate completions, and mode switching; regressions here can deadlock all firmware communication or corrupt response ownership.

Timeout and reboot handling is intentionally asymmetric: `MC_CMD_REBOOT` returning `-EIO` may be success, while unexpected `-EIO`/`-EINTR` on other commands triggers MC failure reset. Changing that mapping risks reset storms or missed firmware crashes. Proxy authorization must release the interface on every denial/error path or future RPCs will block.

NVRAM paths are persistent and high-risk. Chunking, update-session state, verification-result translation, and fallback from unsupported background/abort modes must be tested with old and new firmware. `efx_mcdi_nvram_metadata()` also has buffer-size validation around firmware-provided descriptions.

Async completion callbacks run in atomic context and receive buffers owned by the temporary async allocation; users must not sleep or retain the pointer. `efx_mcdi_flush_async()` depends on event processing being stopped and mode being poll/fail to safely walk the async list without holding `async_lock`.

## Test Signals
Useful validation signals include kernel build coverage for `CONFIG_SFC_MCDI_LOGGING` and `CONFIG_SFC_MTD`, lockdep/KCSAN runs around event-mode RPCs and async flush, simulated MC command timeouts, late completions after timeout, MC reboot/assertion/BIST event injection, proxy-pending approval/denial paths, and NVRAM update verification result mapping. Runtime logs to watch include "MC response mismatch", "MCDI request was completed without an event", "MC reboot detected", "MCDI is timing out", and NVRAM verification failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.h

## Purpose
`mcdi.h` defines the public contract and wire-buffer helpers for the SFC Management Controller Driver Interface. It declares MCDI request state and mode enums, the per-NIC MCDI state containers, optional hwmon and MTD partition structures, the exported RPC/reset/NVRAM/workaround/monitor APIs, and a large set of macros for safely building and decoding firmware protocol buffers described by `mcdi_pcol.h`.

The header is the shared foundation used by MCDI command callers across the driver. It lets implementation files express command fields with protocol names while enforcing field size and alignment assumptions at compile time.

## Important APIs, Types, And Macros
`enum efx_mcdi_state` models ownership of the single per-NIC MCDI channel: quiescent, running synchronous, running asynchronous, proxy wait, and completed. `enum efx_mcdi_mode` selects poll, event, or fail-fast behavior.

`struct efx_mcdi_iface` holds the protocol state: owning NIC, state, mode, wait queue, `iface_lock`, epoch flag, sequence number, late-completion credits, response status and lengths, async queue lock/list/timer, optional logging buffer, and proxy authorization state. `struct efx_mcdi_data` embeds the interface plus optional `struct efx_mcdi_mon` and function flags from `DRV_ATTACH`.

`struct efx_mcdi_mon` is declared for the monitor implementation and stores DMA sensor buffer, update lock/cache timestamp, hwmon device, generated attributes, and sysfs groups. `struct efx_mcdi_mtd_partition` wraps an MTD partition with firmware NVRAM type/subtype and update-session state.

The main APIs declared here are `efx_mcdi_init()`, `efx_mcdi_detach()`, `efx_mcdi_fini()`, `efx_mcdi_rpc()`, `efx_mcdi_rpc_quiet()`, split start/finish RPCs, `efx_mcdi_rpc_async()`, `efx_mcdi_display_error()`, mode switching, async flush, reboot polling, event processing, firmware/version/board/workaround/privilege calls, reset mapping/execution, NVRAM and optional MTD operations, and optional monitor probe/remove wrappers.

The `MCDI_DECLARE_BUF`, `MCDI_PTR`, `MCDI_SET_*`, `MCDI_*`, `MCDI_ARRAY_*`, `MCDI_FIELD`, `MCDI_EVENT_FIELD`, and `MCDI_CAPABILITY` macros are a compact DSL for MCDI buffers. They use `BUILD_BUG_ON`/`BUILD_BUG_ON_ZERO`, byte-offset constants, endian casts, and `EFX_POPULATE_DWORD_*` helpers to avoid open-coded protocol offsets.

## Control Flow Role
The header does not implement runtime control flow, but it defines the state transitions and buffer operations used by `mcdi.c` and callers. Command code typically declares zero-filled dword arrays with `MCDI_DECLARE_BUF()`, fills fields with `MCDI_SET_DWORD()` or `MCDI_POPULATE_DWORD_*()`, issues an RPC, checks output length, and extracts fields with `MCDI_DWORD()`, `MCDI_WORD()`, `MCDI_QWORD()`, or array helpers.

The capability macros route feature checks through `efx->type->check_caps()` with bit and offset constants from `MC_CMD_GET_CAPABILITIES_V8_OUT_*`, giving firmware-dependent code a uniform `efx_has_cap(efx, FEATURE)` predicate.

## State And Persistence Behavior
The structs declared here are in-memory driver state. `efx_mcdi_iface` is initialized on probe and destroyed on driver removal. It does not persist to disk. Its fields reflect transient command ownership, current MC epoch, and response metadata. The MTD partition wrapper includes an `updating` boolean that persists only for the life of the Linux object and is used to decide whether `NVRAM_UPDATE_FINISH` is required.

Persistent device effects are exposed through APIs declared here but performed in `mcdi.c`: NVRAM updates, WOL filters, LED state, firmware attach state, and resets.

## Dependencies And Integration Points
The header depends on protocol constants from `mcdi_pcol.h`, NIC and net-driver types, Linux wait queues, timers, spinlocks, attributes, DMA buffers, and optional config symbols `CONFIG_SFC_MCDI_MON`, `CONFIG_SFC_MCDI_LOGGING`, and `CONFIG_SFC_MTD`.

It integrates with almost every SFC driver subsystem: queue lifecycle code uses the RPC and buffer macros; filter/RSS code uses `efx_has_cap()` and RPCs; monitor code uses `struct efx_mcdi_mon`; MAC/PHY code consumes board config, capabilities, and link events; reset paths use the reset mapping/execution declarations; ethtool/MTD paths use NVRAM metadata and update APIs.

## Risks And Edge Cases
The macros assume protocol offsets and lengths are correct and that command buffers have been sized with the corresponding `MC_CMD_*_LEN` expression. Incorrect buffer length checks at call sites can still cause truncated data interpretation even though field alignment is checked. `MCDI_VAR_ARRAY_LEN()` computes from a response length and should only be used after verifying the fixed minimum output length.

Endian behavior is mixed by design: most MCDI fields use little-endian dword helpers, while some network fields are explicitly written big-endian with `MCDI_SET_WORD_BE()` or `MCDI_STRUCT_SET_DWORD_BE()`. Callers that bypass these helpers can silently invert wire values.

Because `efx_mcdi_iface` state is shared across interrupt, timer, and process contexts, any new state fields added to the struct need explicit locking or barrier rules matching the implementation. Optional inline monitor stubs mean callers must tolerate monitor operations compiling to no-ops.

## Test Signals
Compile coverage should include configurations with and without MCDI monitor, logging, and MTD. Sparse/endian checking is valuable for `__force` casts. Build failures from `BUILD_BUG_ON` are expected safety signals when protocol constants change. Runtime tests should exercise representative command buffers with minimum and extended response lengths so array and capability macros are validated against real firmware responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.c

## Purpose
`mcdi_filters.c` implements firmware-backed RX filter and RSS context management for EF10/EF100-style SFC NICs using MCDI commands. Firmware owns the real filter tables and returns opaque 64-bit handles, while Linux needs stable smaller filter IDs and replacement/lookup semantics. This file therefore maintains a software hash table shadow, translates generic `struct efx_filter_spec` matches into MCDI match masks, synchronizes automatic MAC/VLAN/default filters from netdevice state, restores filter/RSS allocations after MC reboot, and manages shared/exclusive RSS contexts.

## Important APIs, Types, And Functions
The public filter-table lifecycle is `efx_mcdi_filter_table_probe()`, `efx_mcdi_filter_table_down()`, `efx_mcdi_filter_table_remove()`, `efx_mcdi_filter_table_restore()`, and `efx_mcdi_filter_table_reset_mc_allocations()`. Probe asks firmware for supported normal and encapsulated RX matches, disables VLAN hw filtering if required match types are absent, allocates the 8192-row software table, initializes VLAN state, and attaches it to `efx->filter_state`.

User-visible filter operations are `efx_mcdi_filter_insert()`, `efx_mcdi_filter_remove_safe()`, `efx_mcdi_filter_get_safe()`, `efx_mcdi_filter_clear_rx()`, `efx_mcdi_filter_count_rx_used()`, `efx_mcdi_filter_get_rx_id_limit()`, and `efx_mcdi_filter_get_rx_ids()`. IDs encode firmware match-priority index plus local software row. Internally `efx_mcdi_filter_insert_locked()` performs priority, duplicate, multicast-recipient, and RSS-context handling before calling `efx_mcdi_filter_push()` to issue `MC_CMD_FILTER_OP`.

Automatic receive-mode functions are `efx_mcdi_filter_sync_rx_mode()`, `efx_mcdi_filter_add_vlan()`, `efx_mcdi_filter_del_vlan()`, `efx_mcdi_filter_cleanup_vlans()`, and `efx_mcdi_filter_find_vlan()`. Per-VLAN state stores unicast, multicast, broadcast, and default mismatch filter IDs.

RSS APIs are `efx_mcdi_rx_push_rss_context_config()`, `efx_mcdi_pf_rx_push_rss_config()`, `efx_mcdi_vf_rx_push_rss_config()`, `efx_mcdi_push_default_indir_table()`, `efx_mcdi_rx_pull_rss_context_config()`, `efx_mcdi_rx_pull_rss_config()`, `efx_mcdi_rx_free_indir_table()`, and `efx_mcdi_rx_restore_rss_contexts()`. Internal helpers allocate/free/populate firmware RSS contexts and optionally enable UDP 4-tuple hashing.

When `CONFIG_RFS_ACCEL` is enabled, `efx_mcdi_filter_rfs_expire_one()` coordinates accelerated RFS rule expiry with the filter table and RPS hash table.

## Control Flow
Filter insertion starts with `efx_mcdi_filter_insert()`, which takes `efx->filter_sem` for read and calls the locked insertion path. The locked path takes the table write lock, rejects non-RX filters, maps the spec match flags to a firmware match-priority index, locks RSS state if the filter uses RSS, and probes the software table with `efx_filter_spec_hash()` up to `EFX_EF10_FILTER_SEARCH_LIMIT`. Existing equivalent filters are replaced, preserved, or rejected depending on priority and `replace_equal`. Multicast-recipient filters may coexist by subscription, but lower-priority recipients can be unsubscribed after a successful higher-priority insertion.

`efx_mcdi_filter_push_prep_set_match_fields()` converts match flags and values into `FILTER_OP` fields. Encapsulation is handled first by inserting outer ethertype/IP protocol and setting VXLAN/GENEVE/NVGRE metadata, then choosing inner-frame unknown unicast/multicast match bits. `efx_mcdi_filter_push_prep()` selects insert/subscribe/replace, vport, RX destination, queue, RX mode, and RSS context. `efx_mcdi_filter_push()` sends the command quietly, logs non-hint failures, stores the returned firmware handle, and maps `-ENOSPC` to `-EBUSY`.

Removal validates either encoded ID or raw row index, checks priority masks, and either removes a user filter, downgrades an over-auto filter back to automatic, or unsubscribes/removes in firmware according to exclusivity. `efx_mcdi_filter_remove_old()` implements mark-and-sweep for automatic filters whose VLAN/MAC/default subscriptions were not renewed.

Receive-mode sync is a multi-step refresh. `efx_mcdi_filter_sync_rx_mode()` marks old auto filters, snapshots unicast/multicast address lists under `netif_addr_lock_bh()`, reacts to VLAN-filtering changes by removing old filters early, then synchronizes each VLAN. Per-VLAN sync inserts unicast address filters or unicast default fallback, installs encapsulated unicast defaults, then handles multicast/broadcast/default filters with different rollback behavior depending on multicast chaining support, promiscuous/allmulti state, and multicast-list overflow. Finally, old filters are removed and `mc_promisc_last` is updated.

Restoration after MC reboot is driven by `must_restore_filters` and `must_restore_rss_contexts`. RSS contexts are recreated under ethtool RSS lock by iterating `net_dev->ethtool->rss_ctx`, resetting firmware IDs to invalid, and pushing each context. Filters are restored by replaying saved specs to firmware and deleting entries that are no longer supported or whose RSS context cannot be found.

## State And Persistence Behavior
The software filter table is RAM state under `efx->filter_state`. Each row stores a pointer to a saved `struct efx_filter_spec` plus low-bit private flags, and the 64-bit firmware handle needed for removal. Firmware filter allocations persist only until removed or until MC reboot; after reboot the saved specs are the source of truth for restoration.

VLAN list entries persist while VLANs are configured and include per-VLAN auto filter row IDs. Netdevice address-list shadows are refreshed on receive-mode sync. RSS context IDs are firmware allocations stored in `struct efx_rss_context_priv`; they become invalid after MC reboot and must be reallocated. No state is written to disk.

## Dependencies And Integration Points
This file depends on `mcdi_filters.h`, `mcdi.h`, `nic.h`, `rx_common.h`, `filter.h`, netdevice unicast/multicast lists, ethtool RSS context infrastructure, xarray iteration, RFS/RPS helpers when enabled, and MCDI protocol commands `GET_PARSER_DISP_INFO`, `FILTER_OP`, `RSS_CONTEXT_*`.

It integrates with the driver filter API, receive-mode updates from netdev flags, VLAN feature negotiation, RSS configuration from ethtool, MC reboot recovery, vport IDs, queue IDs, and accelerated receive flow steering.

## Risks And Edge Cases
The software table is authoritative for Linux but write-only relative to firmware. Any mismatch between saved specs, row IDs, and firmware handles can leak subscriptions, remove another consumer's multicast subscription, or report stale filter IDs to userspace. The low-bit flag packing in `entry[].spec` assumes allocated pointers are sufficiently aligned.

Concurrency is guarded by `efx->filter_sem`, `table->lock`, `rss_lock`, netdev address locks, and RPS hash locks. Lock ordering matters, especially in RFS expiry and filter insertion with RSS. Reboot restoration must handle capabilities changing between firmware boots; unsupported saved filters are validly dropped.

Fallback behavior is subtle. Unicast/multicast address insertion failures can move the device to default/promiscuous filters. Multicast chaining differences exist for older firmware. Encapsulation default filters are skipped when capability `VXLAN_NVGRE` is absent. RSS allocation falls back from exclusive to shared only in non-user PF paths after `-ENOBUFS`.

## Test Signals
Test with firmware variants that support and do not support VLAN match flags, encapsulated matches, multicast chaining, additional RSS modes, and RX RSS limited mode. Exercise `ip link set promisc/allmulti`, large multicast lists to trigger overflow, VLAN add/remove with hw VLAN filtering toggles, ethtool RSS context create/delete/set/get, MC reboot recovery with active filters, and RFS expiry. Watch for logs about unsupported firmware match flags, failed filter restores, broadcast/default insert failures, RSS context fallback, and stale/null auto filter markings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.h

## Purpose
`mcdi_filters.h` declares the MCDI-backed filter/RSS interface and the software state structures used by `mcdi_filters.c`. It bridges the generic SFC filter API to firmware-owned filter tables by defining default filter slots, per-VLAN automatic filter state, software table metadata, and exported operations for filter insertion/removal/query, VLAN synchronization, RSS context programming, and RFS expiry.

## Important APIs And Types
`enum efx_mcdi_filter_default_filters` enumerates automatic default filters stored per VLAN: broadcast, unicast default, multicast default, and IPv4/IPv6 default filters for VXLAN, NVGRE, and GENEVE unicast/multicast traffic.

`struct efx_mcdi_filter_vlan` stores one configured VLAN ID plus arrays of automatic unicast and multicast address filter row IDs and default filter IDs. `struct efx_mcdi_dev_addr` is a compact Ethernet-address holder for netdevice address-list shadows.

`struct efx_mcdi_filter_table` is the main software shadow. It contains firmware-supported match masks in priority order, `rx_match_count`, whether the default RSS context is exclusive, an rwsem-protected 8192-entry table mapping saved specs to firmware handles, unicast/multicast address-list snapshots protected by `mac_lock`, promiscuous/overflow state, reboot restoration flags, multicast chaining capability, VLAN-filtering state, and the VLAN list.

The exported operations include table lifecycle (`probe`, `down`, `remove`, `restore`, `reset_mc_allocations`), match support checks, RX mode synchronization, safe filter insert/remove/get/count/clear/list operations, VLAN add/find/delete/cleanup, RSS context push/pull/free/restore helpers, default indirection programming, a no-op `efx_mcdi_update_rx_scatter()`, and optional RFS expiry.

## Control Flow Role
The header is consumed by NIC type operation tables and netdev/ethtool paths. Probe must be called under the filter semaphore write lock before filter operations. Most operational APIs acquire `efx->filter_sem` internally or require it by documented convention, then `mcdi_filters.c` manages the more granular table lock and firmware commands.

The constants `EFX_EF10_FILTER_DEV_UC_MAX`, `EFX_EF10_FILTER_DEV_MC_MAX`, and `EFX_MCDI_FILTER_TBL_ROWS` define the size boundaries for address-list syncing and the software hash table. These values control when the implementation falls back to promiscuous/all-multicast behavior and how Linux-visible IDs are encoded.

## State And Persistence Behavior
All structures in this header represent RAM shadow state. Firmware filter handles and RSS context IDs are device-side allocations, but the host-side table and VLAN arrays are the data retained across driver operations and used to restore firmware state after MC reboot. The booleans `must_restore_rss_contexts` and `must_restore_filters` are explicit reboot-recovery cursors. No on-disk persistence exists.

## Dependencies And Integration Points
The header depends on `net_driver.h`, `filter.h`, and `mcdi_pcol.h`. It integrates with netdevice feature flags, multicast/unicast address lists, VLAN offload, ethtool RSS contexts, RFS acceleration, and the MCDI core declared in `mcdi.h`.

Downstream code should treat this as the firmware-backed implementation of the generic filter/RSS hooks. It is not a standalone filter API; it assumes `efx->filter_state`, `efx->filter_sem`, `efx->rss_context`, `efx->net_dev`, and NIC capability helpers are available and initialized.

## Risks And Edge Cases
The table row count and ID encoding are part of the ABI between these routines and users of filter IDs. Changing `EFX_MCDI_FILTER_TBL_ROWS` or ID arithmetic requires auditing `get_rx_id_limit`, insertion return values, RFS expiry, and removal-by-ID. The unicast and multicast address array limits are fallback thresholds; too-small values increase promiscuous fallback, while too-large values increase sync cost and firmware pressure.

The header documents some locking assumptions in comments but cannot enforce them. Callers of VLAN find/delete and table removal must hold the proper semaphore or the implementation can leak memory or return inconsistent state. The no-op scatter update is intentional for this MCDI path and should not be mistaken for missing RX scatter support.

## Test Signals
Compile users with `CONFIG_RFS_ACCEL` enabled and disabled, and with firmware feature combinations that change VLAN and encapsulation support. API-level tests should verify that `get_rx_id_limit()` matches the number of probed match priorities, VLAN filter arrays initialize to invalid IDs, and table restoration flags are set by MC allocation reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.c

## Purpose
`mcdi_functions.c` contains MCDI command adapters for allocating virtual interfaces, initializing and finalizing event/TX/RX DMA queues, flushing DMA queues, translating VI window mode to register stride, and querying the PF index. It is the hardware resource lifecycle layer used by NIC bring-up and teardown code once the core MCDI RPC layer is available.

## Important APIs And Functions
`efx_mcdi_alloc_vis()` and `efx_mcdi_free_vis()` manage firmware VI allocation through `MC_CMD_ALLOC_VIS` and `MC_CMD_FREE_VIS`. Free treats `-EALREADY` as success because firmware may already have no VIs assigned.

Event queue functions are `efx_mcdi_ev_probe()`, `efx_mcdi_ev_init()`, `efx_mcdi_ev_fini()`, and `efx_mcdi_ev_remove()`. Probe/remove allocate/free host DMA memory. Init fills the event queue with empty events, builds `INIT_EVQ` with queue size, instance, IRQ vector index, timer/counting config, v1 or v2 flags, and per-page DMA addresses. Fini sends `FINI_EVQ` and tolerates `-EALREADY`.

TX queue functions are `efx_mcdi_tx_init()`, `efx_mcdi_tx_fini()`, and `efx_mcdi_tx_remove()`. Init builds `INIT_TXQ` with target event queue, label, instance, owner, vport, descriptor-page DMA addresses, checksum flags, timestamp flag, and TSOv2 selection. If firmware returns `-ENOSPC` for TSOv2 context allocation, it disables TSOv2 and retries.

RX queue functions are `efx_mcdi_rx_probe()`, `efx_mcdi_rx_init()`, `efx_mcdi_rx_fini()`, and `efx_mcdi_rx_remove()`. RX init sets prefix and timestamp flags, queue/label/target event queue, vport, optional EF100 page-buffer size, and descriptor-page DMA addresses before issuing `INIT_RXQ`.

`efx_fini_dmaq()` finalizes all RX and TX queues and waits for flush events by monitoring `efx->active_queues`. `efx_mcdi_window_mode_to_stride()` maps firmware capability window modes to byte strides. `efx_get_pf_index()` calls `GET_FUNCTION_INFO` and returns the PF number.

## Control Flow
The usual bring-up flow allocates VI resources, probes DMA buffers for event/RX/TX queues, initializes event queues, then initializes TX and RX queues with firmware. Every queue init constructs an MCDI input buffer sized for the maximum queue DMA address array and uses the actual number of DMA pages to choose the input length where the protocol supports variable lengths.

Teardown is split between firmware finalization and host memory release. `*_fini()` functions issue firmware `FINI_*` commands and handle idempotent `-EALREADY`; `*_remove()` functions free host DMA buffers. `efx_fini_dmaq()` skips firmware writes during EEH recovery, handles MC reboot by zeroing `active_queues` when VIs must be reallocated, otherwise finalizes every queue and waits up to `EFX_MAX_FLUSH_TIME` for active queue drain events delivered through the MCDI event path.

## State And Persistence Behavior
The file primarily mutates firmware resource state and host DMA buffer state. VI, EVQ, TXQ, and RXQ allocations are firmware-side runtime allocations and disappear on MC reset or device reset. Host DMA buffers live in `channel->eventq`, `tx_queue->txd`, and `rx_queue->rxd` until removed. TX queue initialization may persistently change `tx_queue->tso_version` for the life of the queue if TSOv2 firmware resources are unavailable.

`efx->vi_stride` is derived once from firmware-reported VI window mode. `efx->active_queues` is reset or waited on during DMAQ teardown and is coupled to MCDI TX/RX flush events.

## Dependencies And Integration Points
This file depends on `net_driver.h`, `efx.h`, `nic.h`, `mcdi_functions.h`, `mcdi.h`, and `mcdi_pcol.h`. It uses `efx_nic_alloc_buffer()`/`efx_nic_free_buffer()`, queue/channel iteration macros, RX queue index helpers, netdev logging, MCDI buffer macros, and `efx_mcdi_rpc()`/`efx_mcdi_rpc_quiet()`.

It integrates with probe/remove paths, interrupt/event queue setup, datapath queue creation, reset recovery, EEH recovery, TSO/checksum offload selection, timestamping, and the MCDI event flush handler that decrements `active_queues`.

## Risks And Edge Cases
Queue initialization is sensitive to descriptor ring sizing, DMA page count, and protocol input lengths. Supplying the wrong number of DMA addresses can make firmware DMA to invalid memory. TX offload flags are subtle: TSOv2 changes IP checksum-offload semantics, and fallback disables hardware segmentation support to avoid firmware context exhaustion.

Teardown depends on flush events arriving and on `active_queues` matching the number of queues firmware will drain. MC reboot and EEH recovery intentionally skip normal firmware writes; changing that can hang recovery. RX init logs a warning rather than returning an error, so callers must already be structured to detect or tolerate failed RX queue initialization.

## Test Signals
Validation should include queue bring-up/teardown under normal probe, reset, MC reboot, and EEH recovery. Exercise TSOv2 available/unavailable paths, timestamping queues, EF100 RX buffer size handling, multiple event queue sizes, and forced missing flush events to confirm `-ETIMEDOUT`. Build and runtime logs should be checked for `INIT_*`/`FINI_*` errors, TSOv2 fallback warnings, unrecognized VI window modes, and failed queue flush counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.h

## Purpose
`mcdi_functions.h` declares the MCDI-backed hardware resource lifecycle functions used by the SFC driver for VI allocation, event queue setup, TX/RX queue setup, DMA queue finalization, VI window stride derivation, and PF index lookup.

## Important APIs
The VI allocation APIs are `efx_mcdi_alloc_vis()` and `efx_mcdi_free_vis()`. Event queue APIs are `efx_mcdi_ev_probe()`, `efx_mcdi_ev_init()`, `efx_mcdi_ev_remove()`, and `efx_mcdi_ev_fini()`. TX queue APIs are `efx_mcdi_tx_init()`, `efx_mcdi_tx_remove()`, and `efx_mcdi_tx_fini()`. RX queue APIs are `efx_mcdi_rx_probe()`, `efx_mcdi_rx_init()`, `efx_mcdi_rx_remove()`, and `efx_mcdi_rx_fini()`. Miscellaneous helpers are `efx_fini_dmaq()`, `efx_mcdi_window_mode_to_stride()`, and `efx_get_pf_index()`.

## Control Flow Role
This header lets NIC type code and probe/reset paths bind their resource operations to the MCDI implementation in `mcdi_functions.c`. The split naming convention is important: `probe/remove` manage host-side DMA memory, while `init/fini` manage firmware-side queue state. Callers are expected to order those phases correctly during device bring-up and teardown.

## State And Persistence Behavior
The header declares operations that affect runtime firmware allocations and host DMA buffers. Nothing in the header itself persists state. The implementation updates `efx->vi_stride`, queue descriptors, TSO mode, active queue counters, and firmware allocation state.

## Dependencies And Integration Points
The declarations require driver types such as `struct efx_nic`, `struct efx_channel`, `struct efx_tx_queue`, and `struct efx_rx_queue` to be visible to includers through surrounding driver headers. They integrate with the MCDI core, queue/channel management, reset recovery, and PCI function capability discovery.

## Risks And Edge Cases
The prototypes expose both void-returning and int-returning operations. RX init is void even though its implementation can log failure, so callers cannot rely on a return code there. `efx_fini_dmaq()` returns errors and should be checked by teardown/reset callers. Any new call site must respect the probe/init/fini/remove distinction to avoid freeing DMA memory before firmware no longer references it.

## Test Signals
Compile coverage should verify all NIC type operation tables using these prototypes remain consistent. Runtime validation should cover allocation/free idempotence, queue init/fini ordering, reset-time DMAQ finalization, and PF index query behavior on PF and VF configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_mon.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_mon.c

## Purpose
`mcdi_mon.c` implements SFC hardware monitoring over MCDI sensor commands. It translates management-controller sensor IDs and states into kernel logs for sensor events and, when `CONFIG_SFC_MCDI_MON` is enabled, registers a Linux hwmon device with generated sysfs attributes backed by `MC_CMD_READ_SENSORS` DMA reads.

## Important APIs, Types, And Functions
`enum efx_hwmon_type` categorizes sensors as temperature, cooling/fan, voltage, current, power, or unknown. `efx_mcdi_sensor_type[]` maps firmware sensor IDs to human labels, hwmon type, and optional port affinity. `sensor_status_names[]` maps firmware sensor states to text.

`efx_mcdi_sensor_event()` is always compiled and logs asynchronous sensor events delivered through the MCDI event path. It extracts monitor ID, state, and value, looks up a label/type/unit when known, and emits a netdev hardware error log.

Under `CONFIG_SFC_MCDI_MON`, `struct efx_mcdi_mon_attribute` wraps a sysfs device attribute with sensor index, firmware type, hwmon type, limit value, and generated name. `efx_mcdi_mon_probe()` discovers available sensors using paged `MC_CMD_SENSOR_INFO`, allocates the DMA read buffer and attribute arrays, creates value/limit/alarm/label attributes, and registers a hwmon device. `efx_mcdi_mon_remove()` unregisters the device and frees allocations.

Data-read helpers are `efx_mcdi_mon_update()`, `efx_mcdi_mon_get_entry()`, `efx_mcdi_mon_show_value()`, `efx_mcdi_mon_show_limit()`, `efx_mcdi_mon_show_alarm()`, `efx_mcdi_mon_show_label()`, and `efx_mcdi_mon_add_attr()`.

## Control Flow
Sensor event control flow is direct: `efx_mcdi_process_event()` dispatches sensor events to `efx_sensor_event()`/`efx_mcdi_sensor_event()`, which formats a log message. Unknown sensor types are tolerated with a generic label; unknown states trigger paranoid warnings but are still indexed into the status array.

Monitor probe first counts sensors by reading each `SENSOR_INFO` page until the page-0 next bit is absent. It excludes the next-page bit from the count. If no sensors exist, probe succeeds without creating a hwmon device. Otherwise it allocates a DMA buffer sized for all sensor value entries, initializes the update mutex, performs an initial sensor read, allocates worst-case sysfs attribute capacity, then rereads sensor info pages while walking set bits.

For each present sensor, probe filters out sensors tied to a different port, chooses hwmon prefix/index conventions (`temp` and `fan` one-based, `in` zero-based, `curr`/`power` one-based), reads firmware min/max threshold pairs, creates input and threshold attributes when values are meaningful, always creates an alarm attribute, and creates a label attribute for known labelled sensors. It then registers with `hwmon_device_register_with_groups()`.

Sysfs reads call `efx_mcdi_mon_get_entry()`, which holds `update_lock`, reuses cached DMA data if the last update was less than one second ago, otherwise issues `READ_SENSORS` with the DMA buffer address and length. Value readers reject `NO_READING` with `-EBUSY`, convert temperatures to millidegrees Celsius and power to microwatts, and return decimal text. Alarm readers return whether state is not OK.

## State And Persistence Behavior
Monitor state is volatile in `struct efx_mcdi_mon`: DMA buffer, generated attributes, hwmon device pointer, and one-second cache timestamp. Sensor values are read from firmware into host DMA memory on demand; no values are persisted to disk. Thresholds are captured from firmware sensor info at probe time and stored in attribute objects. If firmware sensor topology changes after probe, the sysfs layout is not dynamically rebuilt by this file.

## Dependencies And Integration Points
The file depends on Linux `hwmon`, `slab`, `bitops`, device attributes, `net_driver.h`, `mcdi.h`, `mcdi_pcol.h`, and `nic.h`. It integrates with the MCDI event dispatcher for sensor event logging and with the optional monitor pointers embedded in `struct efx_mcdi_data`.

The monitor uses `efx_nic_alloc_buffer()`/`efx_nic_free_buffer()` for DMA storage and `efx_mcdi_rpc()` for `SENSOR_INFO` and `READ_SENSORS`. It is exposed to userspace through standard hwmon sysfs naming conventions rather than SFC-specific files.

## Risks And Edge Cases
The sensor map is necessarily firmware-version dependent. Unknown future sensors are skipped for labels/types or exposed as voltage-style `in` attributes when type is unknown, while event logs use a generic name. Unknown sensor states can produce out-of-range array access if firmware reports values beyond `sensor_status_names`; the code has only paranoid warnings, so robust firmware assumptions matter.

Probe has several allocation and short-response failure paths and relies on `efx_mcdi_mon_remove()` to clean partially initialized state. Attribute capacity is allocated as six per sensor, which must remain sufficient for the generated value/min/max/crit/alarm/label set. The one-second cache reduces firmware traffic but means sysfs reads can be stale by up to one second.

Port filtering must match board sensor semantics; otherwise a port may hide relevant sensors or expose another port's PHY sensors. Value unit conversion must follow hwmon ABI expectations; temperature and power are scaled, voltage/current/fan values are passed through.

## Test Signals
Test with `CONFIG_SFC_MCDI_MON` enabled and disabled, boards with zero sensors, multiple sensor-info pages, port-specific PHY sensors, unknown sensor IDs, and `NO_READING` states. Validate sysfs names and units against hwmon ABI (`temp*_input`, `fan*_input`, `in*_input`, `curr*_input`, `power*_input`, alarms, labels), short firmware responses, failed DMA allocation, and sensor event log formatting for warning/fatal/broken states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mcdi_mon.c -->
