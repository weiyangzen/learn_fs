# subset-b-001078 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_mem_io.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_mem_io.c

## Purpose
Implements memory-mapped register access setup for IPMI system-interface drivers. It binds `struct si_sm_io` to `readb/readw/readl/readq` and matching write helpers, reserves the register windows, maps them with `ioremap()`, and installs cleanup for the generic IPMI SI core.

## Important APIs, Types, and Functions
- `ipmi_si_mem_setup(struct si_sm_io *io)` is the exported setup entry point used when an IPMI SI resource is memory space.
- `intf_mem_inb/outb`, `intf_mem_inw/outw`, `intf_mem_inl/outl`, and optionally `mem_inq/outq` implement byte extraction/insertion across register widths using `regspacing` and `regshift`.
- `mem_region_cleanup()` releases each individually requested register region; `mem_cleanup()` unmaps and releases all regions if setup reached `ioremap()`.
- Depends on `struct si_sm_io` fields from `ipmi_si.h`: `addr_data`, `addr`, `regsize`, `regspacing`, `regshift`, `io_size`, `inputb`, `outputb`, `io_cleanup`, and `dev`.

## Control Flow
`ipmi_si_mem_setup()` rejects a zero physical address, selects accessors based on `regsize`, requests each register-sized memory region separately, computes a minimal contiguous mapping size, maps with `ioremap()`, and records `mem_cleanup()` as `io_cleanup`. On partial region reservation or mapping failure it unwinds all regions already claimed.

## State and Persistence
The persistent state is stored in the caller-owned `si_sm_io`: assigned function pointers, `io->addr` mapping, and cleanup callback. Resource ownership persists until the SI core calls `io_cleanup`.

## Dependencies and Integration Points
This is used by PCI, ACPI, OF, and platform SI discovery paths when the resource is `IPMI_MEM_ADDR_SPACE`. It depends on Linux MMIO APIs and `SI_DEVICE_NAME` for resource ownership.

## Risks
Register sizing is strict; unsupported `regsize` fails. `intf_mem_outw()` uses `writeb()` with shifted data while the read side uses `readw()`, which is intentional-looking legacy behavior but worth regression testing on 16-bit windows. Mapping spans from first register through the last full register while individual reservations may be disjoint, so any future change to `io_size` or `regspacing` arithmetic can over-map more than intended.

## Test Signals
Useful tests are probe/unprobe on KCS/SMIC/BT memory resources with 1, 2, 4, and 8 byte registers, failure injection for `request_mem_region()` and `ioremap()`, and ACPI systems with disjoint reserved register regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_mem_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_parisc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_parisc.c

## Purpose
Adds PA-RISC-specific discovery for IPMI KCS system interfaces exposed as PA-RISC management controller devices. It converts a `parisc_device` into a standard `si_sm_io` and registers it with the generic IPMI SI core.

## Important APIs, Types, and Functions
- `ipmi_si_parisc_init()` registers `ipmi_parisc_driver`.
- `ipmi_si_parisc_shutdown()` unregisters it if registration happened.
- `ipmi_parisc_probe()` builds a memory-space KCS `si_sm_io` at `dev->hpa.start`.
- `ipmi_parisc_remove()` calls `ipmi_si_remove_by_dev()`.
- `ipmi_parisc_tbl` matches PA-RISC management controller hardware IDs.

## Control Flow
Driver init registers a PA-RISC bus driver. Probe zeroes an `si_sm_io`, fills KCS metadata, marks the source as device tree, configures 8-bit memory registers with no IRQ, and calls `ipmi_si_add_smi()`. Remove tears down by device.

## State and Persistence
Only `parisc_registered` is file-local persistent state. Per-interface state is owned by the SI core after `ipmi_si_add_smi()`.

## Dependencies and Integration Points
Depends on PA-RISC bus APIs, `asm/hardware.h`, `asm/parisc-device.h`, and generic IPMI SI registration. It integrates only when PA-RISC support builds this file.

## Risks
The address source is reported as `SI_DEVICETREE` even though the bus is PA-RISC-specific, which may affect diagnostics. The file hardcodes KCS, memory space, byte registers, and no interrupt; any PA-RISC platform that differs will need new detection logic.

## Test Signals
Boot/probe on matching PA-RISC management controller hardware, verify `ipmi_si_add_smi()` succeeds, and verify unregister removes only devices attached through this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_parisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_pci.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_pci.c

## Purpose
Discovers IPMI system interfaces exposed on PCI, chooses the correct KCS/SMIC/BT state machine, determines I/O versus memory access, probes KCS register spacing, and registers the interface with the generic IPMI SI core.

## Important APIs, Types, and Functions
- `ipmi_si_pci_init()` and `ipmi_si_pci_shutdown()` register/unregister the PCI driver under the `trypci` module parameter.
- `ipmi_pci_probe()` is the main PCI probe path.
- `ipmi_pci_probe_regspacing()` tests KCS spacing of 1, 4, and 16 bytes by temporarily setting up I/O, writing an invalid command, and reading status.
- `ipmi_pci_remove()` delegates to `ipmi_si_remove_by_dev()`.
- `ipmi_pci_devices` matches HP MMC and PCI serial IPMI classes; `ipmi_pci_blacklist` excludes a Realtek virtual device.

## Control Flow
Probe rejects blacklisted devices, selects `si_info` from PCI class, enables the device, selects `ipmi_si_port_setup()` for I/O BARs or `ipmi_si_mem_setup()` for memory BARs, derives BAR start, probes spacing, attaches the PCI IRQ if present, logs resource metadata, and calls `ipmi_si_add_smi()`.

## State and Persistence
`pci_registered` records whether the PCI driver was registered. `si_trypci` persists as module configuration. Runtime interface state is owned by the SI core.

## Dependencies and Integration Points
Integrates with PCI core, IPMI SI state machines, port/memory setup helpers, and standard IRQ setup. It is one of several SI discovery lanes alongside platform, ACPI, OF, DMI, hardcoded, and PA-RISC paths.

## Risks
Register spacing probing performs live writes to the KCS command register, so it must only happen after correct resource setup and cleanup. The default branch for unknown IPMI class returns `-ENOMEM`, which is semantically odd. Systems without `CONFIG_HAS_IOPORT` reject I/O BAR devices with `-ENXIO`.

## Test Signals
Probe KCS, SMIC, and BT class devices; validate spacing detection on 1, 4, and 16 byte KCS mappings; confirm blacklist behavior; exercise removal while IRQ setup is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_platform.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_platform.c

## Purpose
Provides platform-bus discovery for IPMI SI interfaces from firmware or synthetic platform devices: Open Firmware/device tree, ACPI, DMI-created devices, hardcoded devices, hotmod devices, and generic platform resources.

## Important APIs, Types, and Functions
- `ipmi_platform_driver` is the platform driver exported for SI platform devices.
- `ipmi_si_platform_init()` and `ipmi_si_platform_shutdown()` manage registration.
- `ipmi_probe()` attempts OF first, then ACPI, then generic platform properties.
- `of_ipmi_probe()`, `acpi_ipmi_probe()`, and `platform_ipmi_probe()` each construct `si_sm_io`.
- `ipmi_get_info_from_resources()` derives address space, base, and spacing from platform resources.
- `acpi_gpe_irq_setup()` and `acpi_gpe_irq_cleanup()` adapt ACPI GPE interrupts to the SI IRQ handler.
- `ipmi_remove_platform_device_by_name()` removes matching platform devices by name.

## Control Flow
The probe dispatcher prefers device tree if `of_node` exists and succeeds. ACPI probe reads `_IFT`, ignores SSIF, parses resources, optional `_GPE` or platform IRQ, DMI slave address, requests `acpi_ipmi`, and registers. Generic platform probe reads `addr-source`, `ipmi-type`, `reg-size`, `reg-shift`, resources, `slave-addr`, optional IRQ, and registers.

## State and Persistence
Module parameters gate discovery lanes: `tryplatform`, `tryacpi`, `tryopenfirmware`, and `trydmi`. `platform_registered` tracks registration. Per-interface state is transferred to the SI core.

## Dependencies and Integration Points
Depends on platform device APIs, device properties, OF address and IRQ parsing, ACPI methods `_IFT` and `_GPE`, DMI slave address decoding, and generic SI state machines. It creates the common bridge from firmware descriptions to `ipmi_si_add_smi()`.

## Risks
Probe order can mask later discovery lanes when an earlier lane returns success. Firmware property validation is strict for OF `reg-size`, `reg-spacing`, and `reg-shift`. ACPI GPE cleanup must coordinate with `ipmi_irq_start_cleanup()` before removing the handler. Generic platform probe calls `ipmi_si_add_smi(&io)` but returns `0`, so registration failure is not propagated from that branch.

## Test Signals
Exercise OF, ACPI, DMI, hardcode, and hotmod sources; verify GPE and standard IRQ setup/cleanup; test invalid firmware properties; validate duplicate or disabled discovery via module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_port_io.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_port_io.c

## Purpose
Implements I/O-port register access setup for IPMI SI devices. It assigns `inb/inw/inl` and `outb/outw/outl` accessors, reserves each port window, and records cleanup.

## Important APIs, Types, and Functions
- `ipmi_si_port_setup(struct si_sm_io *io)` is the setup entry point for `IPMI_IO_ADDR_SPACE`.
- `port_inb/outb`, `port_inw/outw`, and `port_inl/outl` apply `regspacing` and `regshift`.
- `port_cleanup()` releases all requested I/O regions.

## Control Flow
Setup rejects address zero, selects accessors for register sizes 1, 2, or 4, requests each register region separately to tolerate firmware that reserved disjoint ports, and installs `port_cleanup()`. Partial reservation failure unwinds already claimed regions.

## State and Persistence
Accessors and cleanup callback are stored in the supplied `si_sm_io`. Region reservations persist until cleanup.

## Dependencies and Integration Points
Used by PCI and platform SI discovery paths for I/O resources and depends on legacy port I/O support. The surrounding code avoids this path when `CONFIG_HAS_IOPORT` is unavailable.

## Risks
Unsupported `regsize` fails. Region arithmetic depends on `io_size`, `regspacing`, and `regsize` being set correctly by the chosen SI state machine. Port access is not memory-barrier-rich beyond the semantics of the port I/O helpers.

## Test Signals
Probe I/O-port KCS/SMIC/BT interfaces with register sizes 1, 2, and 4; force `request_region()` failure mid-loop; confirm unload releases all port windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_port_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_sm.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_sm.h

## Purpose
Defines the low-level state-machine contract between the generic IPMI SI policy layer and concrete KCS, SMIC, and BT state machines.

## Important APIs, Types, and Functions
- `struct si_sm_data` is opaque state owned by each state-machine implementation.
- `enum si_sm_result` communicates scheduling outcomes such as immediate call, delayed call, transaction complete, idle, hosed, or attention.
- `struct si_sm_handlers` defines callbacks: `init_data`, `start_transaction`, `get_result`, `event`, `detect`, `cleanup`, and `size`.
- Extern handler tables: `kcs_smi_handlers`, `smic_smi_handlers`, and `bt_smi_handlers`.

## Control Flow
The SI core allocates handler-sized opaque state, calls `init_data()` to bind `si_sm_io` and learn I/O size, uses `start_transaction()` to submit messages, repeatedly calls `event()` under polling or interrupt-driven scheduling, and calls `get_result()` after `SI_SM_TRANSACTION_COMPLETE`.

## State and Persistence
State is intentionally hidden behind `struct si_sm_data`. The contract centralizes result codes and callback meanings so the upper layer can treat KCS, SMIC, and BT uniformly.

## Dependencies and Integration Points
Includes `ipmi_si.h` for `struct si_sm_io` and SI metadata. It is included by low-level state machine C files and by the SI core.

## Risks
The API relies on callback conventions rather than type-enforced ownership rules. A state machine returning the wrong scheduling result can cause busy loops, missed attention, or transaction stalls.

## Test Signals
State-machine unit tests should validate callback return contracts, size/init consistency, error return values for invalid transaction length/state, and `SI_SM_ATTN` behavior when hardware flags asynchronous data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_sm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_smic_sm.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_smic_sm.c

## Purpose
Implements the SMIC low-level IPMI system-interface state machine. It serializes request bytes through SMIC control/data/flag registers, reads response bytes, handles timeout/error recovery, and exposes a `si_sm_handlers` table.

## Important APIs, Types, and Functions
- `struct si_sm_data` stores SMIC state, `si_sm_io`, write/read buffers, positions, retry count, truncation state, and timeout.
- `init_smic_data()`, `start_smic_transaction()`, `smic_get_result()`, `smic_event()`, `smic_detect()`, `smic_cleanup()`, and `smic_size()` implement the `si_sm_handlers` contract.
- Register helpers read/write SMIC data, status, control, and flags offsets.
- `start_error_recovery()` retries the original write up to `SMIC_MAX_ERROR_RETRIES` before marking `SMIC_HOSED`.

## Control Flow
Transactions begin in `SMIC_START_OP`, issue `GET_STATUS`, proceed through `WR_START`, repeated `WR_NEXT`, `WR_END`, wait for `RX_DATA_READY`, then issue `RD_START`, repeated `RD_NEXT`, and `RD_END`. `smic_event()` advances one or more steps depending on flags/status, returns delay guidance, and returns `SI_SM_TRANSACTION_COMPLETE` when the read end confirms ready with no error.

## State and Persistence
All per-transaction state lives in `si_sm_data`. `smic_timeout` is decremented by elapsed microseconds while non-idle, `error_retries` persists across restart attempts, and `truncated` causes `smic_get_result()` to report `IPMI_ERR_MSG_TRUNCATED`.

## Dependencies and Integration Points
Depends on `ipmi_si_sm.h`, IPMI completion codes, and `si_sm_io` accessor callbacks installed by memory or port setup. The handler table is selected by PCI/platform/ACPI discovery for SMIC interfaces.

## Risks
The state machine is sensitive to exact hardware status codes and `SMIC_FLAG_BSY`. Timeout accounting has a FIXME for calls with `time > SMIC_RETRY_TIMEOUT`, which can delay error recovery. Buffer limits are fixed at 80 bytes; overlong reads are drained but reported truncated.

## Test Signals
Tests should simulate normal write/read, busy flag delays, bad status at every phase, RX/TX readiness delays, timeout retry then hosed behavior, oversized responses, and `SMIC_SMS_DATA_AVAIL` returning `SI_SM_ATTN` while idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_smic_sm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ssif.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ssif.c

## Purpose
Implements the host-side IPMI SSIF driver for SMBus/I2C-attached BMCs. It discovers SSIF devices through module parameters, ACPI, DMI/platform devices, and I2C detection; registers an IPMI SMI; and runs a nonblocking SMBus transaction engine with retries, alert handling, event/message fetching, watchdog pretimeout reporting, multipart messages, PEC, and sysfs statistics.

## Important APIs, Types, and Functions
- `struct ssif_addr_info` stores discovered addresses, adapter names, debug settings, slave address, source metadata, and active client linkage.
- `struct ssif_info` is the live interface state: IPMI SMI pointer, spinlock-protected queues/state, timers, kernel thread I2C work fields, multipart buffers, capability flags, and atomic stats.
- `sender()`, `ssif_start_processing()`, `get_smi_info()`, `request_events()`, and `ssif_set_need_watch()` implement `ipmi_smi_handlers`.
- `ipmi_ssif_thread()` executes blocking SMBus operations serialized through `ssif_i2c_send()`.
- `msg_written_handler()` and `msg_done_handler()` drive send, receive, retry, multipart, and higher-level state transitions.
- `ssif_probe()`, `ssif_detect()`, `new_ssif_client()`, `init_ipmi_ssif()`, and `cleanup_ipmi_ssif()` cover discovery and lifecycle.

## Control Flow
Initialization records hardcoded addresses, optionally registers the DMI platform driver, builds an I2C address list, and registers `ssif_i2c_driver`. Probe validates a BMC with Get Device ID, obtains SSIF capabilities, tests multipart behavior, clears watchdog flags, enables event buffer and alerts when possible, starts a `kssif` thread, adds stats attributes, and registers with IPMI core. Runtime `sender()` queues one message, `start_send()` copies it into the SSIF buffer, `start_resend()` writes single or multipart requests, `msg_written_handler()` waits for alert or timer, and `msg_done_handler()` fetches and validates responses before delivering to IPMI core or advancing internal flag/event/message work.

## State and Persistence
Driver state is split between the global `ssif_infos` list under `ssif_infos_mutex`, per-interface `ssif_info` protected by a spinlock, retry/watch timers, and a single-threaded I2C worker. Module parameters persist configured addresses, adapter filters, debug masks, slave addresses, alert policy, and ACPI/DMI scan toggles. Sysfs stats persist as atomics for the interface lifetime.

## Dependencies and Integration Points
Depends on I2C/SMBus block transactions and alerts, IPMI SMI core, DMI decoding helpers, ACPI matching `IPI0001`, platform devices named `dmi-ipmi-ssif`, and optional `acpi_ipmi` loading. It exposes device attributes such as `sent_messages`, `receive_errors`, `flag_fetches`, `events`, and `watchdog_pretimeouts`.

## Risks
Concurrency is complex: timer callbacks, SMBus alert callback, IPMI sender, watch requests, shutdown, and the I2C thread all coordinate through flags and `ssif_info->lock`. `sender()` uses `BUG_ON(ssif_info->waiting_msg)`, so upstream serialization is assumed. Multipart probing handles ambiguous SSIF specification behavior; regressions can break systems that use command 8, zero-length end transactions, or 63-byte fallback. Shutdown waits for `ssif_state == SSIF_IDLE` with `schedule_timeout(1)`, so stuck state-machine bugs can delay removal.

## Test Signals
Test Get Device ID detection, ACPI/DMI/hardcoded discovery, duplicate ACPI-over-SMBIOS replacement, capability fallback, PEC enablement, event-buffer enable failures, alert and polling response paths, multipart read/write variants, retry exhaustion, sysfs stats increments, and unload while timers or worker transactions are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_ssif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_watchdog.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_watchdog.c

## Purpose
Implements `/dev/watchdog` using the IPMI watchdog timer. It watches for IPMI SMI interfaces, creates an IPMI user, exposes watchdog file operations and ioctls, maintains timeout/pretimeout policy, supports panic/reboot handling, and optionally uses x86 NMI pretimeout handling.

## Important APIs, Types, and Functions
- `ipmi_wdog_init()` registers parameter policy, reboot notifier, and an IPMI SMI watcher.
- `ipmi_register_watchdog()` creates the IPMI user, learns IPMI version, registers the misc watchdog device, optionally tests NMI pretimeout, and starts or stops the timer.
- `ipmi_set_timeout()`, `_ipmi_set_timeout()`, and `__ipmi_set_timeout()` send IPMI Set Watchdog Timer.
- `ipmi_heartbeat()`, `_ipmi_heartbeat()`, and `__ipmi_heartbeat()` send Reset Watchdog Timer and restore settings if the BMC reports timer-not-initialized.
- File operations implement open, write heartbeat and magic close, read/poll/fasync pretimeout notification, ioctls, and release.
- `ipmi_wdog_panic_handler()` and `wdog_reboot_handler()` adjust or disable the timer on panic, halt, poweroff, and reboot.

## Control Flow
The module registers an SMI watcher; when a suitable IPMI interface appears, it creates an IPMI user and registers `/dev/watchdog`. Opening the device marks it busy and defers actual start until first heartbeat. Writes reset the timer and optionally set magic close on `V`. Ioctls set timeout/pretimeout, enable/disable card, and keep alive. Close disables the card only after magic close unless `nowayout` or unexpected close behavior keeps it alive.

## State and Persistence
Global state includes timeout parameters, selected IPMI interface, `watchdog_user`, watchdog action/preaction/preop strings and encoded values, IPMI version, misc open bit, read waitqueue state, async queue, pretimeout flags, and shared static IPMI message buffers guarded by `ipmi_watchdog_mutex`, `ipmi_read_mutex`, atomics, and completion.

## Dependencies and Integration Points
Depends on IPMI user and SMI watcher APIs, Linux watchdog ABI, miscdevice `/dev/watchdog`, reboot notifiers, panic IPMI request path, and x86 NMI APIs when available. Module parameters expose `wdog_ifnum`, `timeout`, `pretimeout`, `panic_wdt_timeout`, `action`, `preaction`, `preop`, `start_now`, and `nowayout`.

## Risks
The driver uses static IPMI message buffers and completion accounting, so cleanup waits until lower layers release both send and receive messages. Panic and NMI paths intentionally avoid normal locking or use constrained operations. `preaction_op()` and `preop_op()` return 0 even if the set helper returns an error, which makes invalid strings worth checking against expected module-param behavior. Magic-close and nowayout interactions are safety-critical.

## Test Signals
Exercise watchdog open exclusivity, first heartbeat start, WDIOC timeout/pretimeout/keepalive/setoptions, magic close versus unexpected close, BMC reset response recovery, SMI hotplug/gone, reboot/halt/panic notifier behavior, and x86 NMI pretimeout registration/testing when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.c

## Purpose
Implements the shared BMC-side KCS device/client registry and access helpers. It lets hardware-specific KCS providers register channels and lets consumer drivers, such as the IPMI char device and serio adapter, attach to those channels.

## Important APIs, Types, and Functions
- Data helpers: `kcs_bmc_read_data()`, `kcs_bmc_write_data()`, `kcs_bmc_read_status()`, `kcs_bmc_write_status()`, and `kcs_bmc_update_status()`.
- Event and ownership helpers: `kcs_bmc_handle_event()`, `kcs_bmc_enable_device()`, `kcs_bmc_disable_device()`, and `kcs_bmc_update_event_mask()`.
- Registry APIs: `kcs_bmc_add_device()`, `kcs_bmc_remove_device()`, `kcs_bmc_register_driver()`, and `kcs_bmc_unregister_driver()`.
- Global lists `kcs_bmc_devices` and `kcs_bmc_drivers` are protected by `kcs_bmc_lock`.

## Control Flow
Hardware providers call `kcs_bmc_add_device()`, which initializes the channel lock, records the device, and calls every registered consumer driver's `add_device()`. Consumer drivers can register later and are attached to all existing devices. Active client ownership is exclusive via `kcs_bmc_enable_device()`, which enables IBF events. Hardware IRQs call `kcs_bmc_handle_event()`, which dispatches to the active client's event callback.

## State and Persistence
Persistent state is the global device/driver lists and each `kcs_bmc_device`'s active `client`. Interrupt mask state is delegated to the hardware provider through `ops->irq_mask_update()`.

## Dependencies and Integration Points
Sits between hardware drivers (`kcs_bmc_aspeed.c`, `kcs_bmc_npcm7xx.c`) and consumers (`kcs_bmc_cdev_ipmi.c`, `kcs_bmc_serio.c`). Exports symbols for loadable modules.

## Risks
There is no rollback in `kcs_bmc_add_device()` if one consumer driver's `add_device()` fails after earlier consumers succeeded. `kcs_bmc_remove_device()` calls all registered consumers and logs failures but cannot force recovery. Active-client locking uses spinlocks and hardware callbacks can run in IRQ context.

## Test Signals
Register devices before and after consumers, verify exclusive client open, event mask changes on enable/disable, IRQ dispatch with and without active client, and consumer add/remove failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.h

## Purpose
Defines the shared BMC-side KCS device model, register layout, event bits, and status bits used by hardware providers and client drivers.

## Important APIs, Types, and Functions
- `KCS_BMC_EVENT_TYPE_OBE` and `KCS_BMC_EVENT_TYPE_IBF` identify output-buffer-empty and input-buffer-full event classes.
- `KCS_BMC_STR_OBF`, `KCS_BMC_STR_IBF`, and `KCS_BMC_STR_CMD_DAT` define KCS status bits.
- `struct kcs_ioreg` maps input data, output data, and status registers.
- `struct kcs_bmc_device` holds list linkage, Linux device, channel number, register offsets, hardware ops, spinlock, and active client pointer.

## Control Flow
This header has no executable flow, but the structures define how hardware-specific drivers expose registers to generic client logic.

## State and Persistence
`struct kcs_bmc_device` is the durable per-channel state object owned by hardware providers and registered through `kcs_bmc_add_device()`.

## Dependencies and Integration Points
Included by `kcs_bmc.c`, `kcs_bmc_client.h`, `kcs_bmc_device.h`, and hardware/client modules.

## Risks
The header establishes a single active-client model. Any future multi-client behavior would need changes to `client` ownership and event-mask semantics.

## Test Signals
Compile coverage across all KCS BMC providers/consumers and event/status bit tests in client state machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_aspeed.c

## Purpose
Implements the Aspeed AST2400/AST2500/AST2600 hardware provider for BMC-side KCS channels. It maps LPC register offsets through a syscon regmap, configures LPC I/O addresses and host/BMC interrupts, emulates output-buffer-empty events where hardware lacks an IRQ, and registers channels with the generic KCS BMC core.

## Important APIs, Types, and Functions
- `struct aspeed_kcs_bmc` wraps `struct kcs_bmc_device`, `regmap`, upstream SerIRQ configuration, and OBE polling timer state.
- Register helpers `aspeed_kcs_inb()`, `aspeed_kcs_outb()`, and `aspeed_kcs_updateb()` implement `kcs_bmc_device_ops`.
- `aspeed_kcs_set_address()` programs LPC address registers for channels 1-4.
- `aspeed_kcs_config_upstream_irq()` configures host-directed SerIRQ from `aspeed,lpc-interrupts`.
- `aspeed_kcs_irq_mask_update()` enables/disables IBF interrupts and emulates OBE with polling and a timer.
- `aspeed_kcs_probe()` parses DT, configures hardware, enables the channel, and calls `kcs_bmc_add_device()`.

## Control Flow
Probe validates the parent LPC compatible, identifies channel by matching DT register offsets, reads LPC I/O addresses, optionally configures upstream SerIRQ, obtains the parent syscon regmap, programs address registers, requests the downstream IRQ, disables event masks, enables the channel, and registers with the KCS core. IRQs dispatch directly to `kcs_bmc_handle_event()`. Removal unregisters, disables the channel and events, marks OBE timer removal, and deletes the timer.

## State and Persistence
Hardware state persists in LPC control/address/interrupt registers. Driver state persists in `aspeed_kcs_bmc`, especially upstream IRQ mode/id and OBE timer removal flag protected by a spinlock.

## Dependencies and Integration Points
Depends on OF bindings `aspeed,ast2400-kcs-bmc-v2`, `aspeed,ast2500-kcs-bmc-v2`, and `aspeed,ast2600-kcs-bmc`, parent LPC syscon compatibility, platform IRQ, and generic KCS BMC core.

## Risks
Address programming differs significantly by channel, and channel 3 only supports inferred status address. SerIRQ support has chip-revision quirks for channel 1. OBE emulation is race-sensitive: the client must do a race-free check after enabling events, while the driver uses a short atomic poll then a slower timer. Removal must prevent timer rearming.

## Test Signals
Device-tree validation for all channels, one- and two-address configurations, invalid addresses, upstream IRQ modes and IDs, IBF IRQ delivery, OBE timer behavior, and remove while OBE timer is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_cdev_ipmi.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_cdev_ipmi.c

## Purpose
Provides a BMC-side IPMI character device client for KCS channels. It translates host KCS protocol events into request buffers readable by userspace and accepts userspace response buffers to send back to the host.

## Important APIs, Types, and Functions
- `struct kcs_bmc_ipmi` stores client linkage, protocol phase, error code, waitqueue, input/output buffers, mutex, spinlock, and miscdevice.
- KCS protocol phases include idle, write start/data/end/done, wait read, read, abort error stages, and error.
- `kcs_bmc_ipmi_event()` dispatches IBF events to command or data handlers.
- `kcs_bmc_ipmi_handle_cmd()` handles KCS control codes: write start, write end, and get-status/abort.
- `kcs_bmc_ipmi_handle_data()` receives request bytes, sends response bytes, and completes abort handshakes.
- File operations expose open, poll, read, write, ioctl, and release.

## Control Flow
Opening the misc device exclusively enables the KCS BMC device for this client. Host write-start/data/write-end events fill `data_in`; write-end marks a complete request and wakes readers. Userspace `read()` copies the request and moves to wait-read phase. Userspace `write()` copies a response, primes the first output byte, and moves to read phase. Host read-byte commands drain output until the final zero and return to idle. Abort or protocol errors force error states and status responses.

## State and Persistence
Per-channel protocol state is in `phase`, `error`, `data_in_avail`, indexes, and buffers. `queue` synchronizes userspace. `mutex` protects userspace buffer copies while `lock` protects IRQ-visible protocol state. Instances are tracked in `kcs_bmc_ipmi_instances`.

## Dependencies and Integration Points
Registers as a `kcs_bmc_driver` with the generic KCS core. Exposes misc devices named `ipmi-kcs<channel>`. Uses `linux/ipmi_bmc.h` ioctls for SMS attention and force abort.

## Risks
The protocol is IRQ-driven and phase-sensitive; userspace latency leaves the channel in `WAIT_READ`. Buffer size is fixed at 1000 bytes and length overflow forces abort. Release always force-aborts the channel, which is correct for cleanup but visible to host software.

## Test Signals
Exercise full KCS request/response, invalid command aborts, host abort handshake, userspace read too-small buffer, write before read returning `-EINVAL`, ioctl SMS_ATN set/clear, force abort, and concurrent open returning busy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_cdev_ipmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_client.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_client.h

## Purpose
Declares the client-facing KCS BMC API used by consumers that attach to a hardware KCS channel.

## Important APIs, Types, and Functions
- `struct kcs_bmc_driver_ops` supplies `add_device()` and `remove_device()` callbacks for consumer drivers.
- `struct kcs_bmc_driver` is registered globally.
- `struct kcs_bmc_client_ops` supplies the IRQ/event callback for an active client.
- `struct kcs_bmc_client` binds ops to a `kcs_bmc_device`.
- Declares register/unregister, enable/disable, event-mask update, and data/status access helpers.

## Control Flow
Consumer modules register a `kcs_bmc_driver`, receive every available `kcs_bmc_device`, create per-channel client state, and call `kcs_bmc_enable_device()` when opened or activated.

## State and Persistence
Consumer state embeds `kcs_bmc_client`, and active ownership is stored in the shared `kcs_bmc_device`.

## Dependencies and Integration Points
Included by KCS BMC consumers such as `kcs_bmc_cdev_ipmi.c` and `kcs_bmc_serio.c`.

## Risks
The API permits only one active client per channel. Consumers must balance enable/disable and avoid using device pointers after remove callbacks.

## Test Signals
Compile and module-load coverage with multiple consumers, exclusive enable tests, and remove while inactive/active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_device.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_device.h

## Purpose
Declares the hardware-provider-facing KCS BMC API and operations table.

## Important APIs, Types, and Functions
- `struct kcs_bmc_device_ops` supplies provider callbacks for IRQ mask updates, byte input, byte output, and masked byte updates.
- `kcs_bmc_handle_event()` is called by hardware IRQ handlers.
- `kcs_bmc_add_device()` and `kcs_bmc_remove_device()` publish or unpublish channels.

## Control Flow
Hardware drivers fill `struct kcs_bmc_device` and ops, call `kcs_bmc_add_device()` after hardware setup, dispatch IRQs to `kcs_bmc_handle_event()`, and call `kcs_bmc_remove_device()` before disabling hardware.

## State and Persistence
The header defines no state itself but establishes the provider-owned `kcs_bmc_device` lifecycle.

## Dependencies and Integration Points
Included by `kcs_bmc_aspeed.c`, `kcs_bmc_npcm7xx.c`, and the shared core.

## Risks
Provider callbacks can be invoked under spinlocks and IRQ context; implementations must not sleep in those paths unless the calling path permits it.

## Test Signals
Provider tests should cover add/remove sequencing, IRQ dispatch, register callback correctness, and mask update behavior for IBF/OBE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_npcm7xx.c

## Purpose
Implements the Nuvoton NPCM7xx hardware provider for BMC-side KCS channels. It maps per-channel registers through a parent syscon regmap, configures interrupts, enables channels, and registers with the generic KCS BMC core.

## Important APIs, Types, and Functions
- `struct npcm7xx_kcs_reg` describes status, data out, data in, control, and interrupt-enable register offsets.
- `struct npcm7xx_kcs_bmc` wraps `kcs_bmc_device`, regmap, and chosen register table entry.
- `npcm7xx_kcs_inb/outb/updateb()` implement provider register ops.
- `npcm7xx_kcs_enable_channel()` controls core IRQ enable bits.
- `npcm7xx_kcs_irq_mask_update()` controls IBF/OBE interrupt enables.
- `npcm7xx_kcs_probe()` parses `kcs_chan`, obtains regmap/IRQ, enables the channel, and registers it.

## Control Flow
Probe validates `kcs_chan` in range 1-3, allocates state, gets the parent syscon regmap, fills the generic device with channel-specific register offsets and ops, requests the platform IRQ, disables event masks, enables the channel, registers with KCS core, and logs offsets. IRQs call `kcs_bmc_handle_event()`. Remove unregisters then disables the channel and masks events.

## State and Persistence
Driver state is one `npcm7xx_kcs_bmc` per channel. Hardware interrupt enable and control bits persist while the channel is enabled.

## Dependencies and Integration Points
Matches OF compatible `nuvoton,npcm750-kcs-bmc`, depends on parent syscon regmap and generic KCS BMC core.

## Risks
Invalid or missing `kcs_chan` prevents probe. Unlike Aspeed, NPCM has hardware OBE interrupt bits, so event mask correctness depends directly on control register behavior. Removal order must avoid events after generic clients are removed.

## Test Signals
Probe channels 1-3, invalid channel values, IRQ request failure, IBF/OBE mask toggles, KCS client request/response through the generic cdev client, and remove/unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_npcm7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_serio.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_serio.c

## Purpose
Adapts BMC-side KCS channels to Linux serio ports, allowing host-written KCS data bytes to be delivered through the serio subsystem.

## Important APIs, Types, and Functions
- `struct kcs_bmc_serio` stores client linkage, serio port pointer, lock, and instance list entry.
- `kcs_bmc_serio_event()` reads status and data on IBF and calls `serio_interrupt()`.
- `kcs_bmc_serio_open()` and `kcs_bmc_serio_close()` enable/disable the KCS device for this client.
- `kcs_bmc_serio_add_device()` allocates a serio port of type `SERIO_8042`, registers it, and tracks the instance.
- `kcs_bmc_serio_remove_device()` unregisters the serio port and disables the client.

## Control Flow
The module registers a KCS BMC consumer driver. For each channel it creates a serio port whose open/close controls active KCS ownership. When a KCS event arrives and IBF is set, the byte is passed to the serio core.

## State and Persistence
Instances are tracked in `kcs_bmc_serio_instances` under a spinlock. The serio core owns the port lifetime after registration; the private state is device-managed except for the serio port allocation.

## Dependencies and Integration Points
Depends on the generic KCS BMC client API and Linux serio subsystem. It competes with the IPMI cdev client for exclusive channel ownership when opened.

## Risks
It treats KCS input as raw serio bytes and does not implement full IPMI KCS protocol phases. Because `SERIO_8042` is used, downstream interpretation depends on serio consumers. Removal must account for `serio_unregister_port()` freeing the port.

## Test Signals
Register/remove with active and inactive KCS channels, open exclusivity against other clients, IBF event byte delivery, and close disabling events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_serio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ssif_bmc.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ssif_bmc.c

## Purpose
Implements the BMC-side SSIF I2C slave driver. It exposes a misc character device for userspace IPMI service code, receives host SSIF write transactions into request messages, accepts userspace response messages, and serves them back through single- or multipart SMBus reads with optional PEC.

## Important APIs, Types, and Functions
- `struct ssif_part_buffer` stores one SMBus transaction part, including address, command, length, payload, PEC, and index.
- `enum ssif_state` models SSIF slave transaction phases from ready through receiving, sending, and aborting.
- `struct ssif_bmc_ctx` stores I2C client, miscdev, locks, waitqueue, timer, request/response buffers, multipart counters, and flags.
- File operations `ssif_bmc_read()`, `ssif_bmc_write()`, `ssif_bmc_open()`, `ssif_bmc_poll()`, and `ssif_bmc_release()` form the userspace ABI.
- I2C slave callback `ssif_bmc_cb()` dispatches to event handlers for read requested/processed, write requested/received, and stop.
- KUnit tests under `CONFIG_SSIF_IPMI_BMC_KUNIT_TEST` exercise state-machine edge cases.

## Control Flow
Host write events move through start, command, receive, and stop. A valid singlepart or multipart end calls `handle_request()`, marks a request available, wakes userspace, sets busy, and arms a response timeout. Userspace reads the request and writes a response before timeout; the response is then served to host read transactions by `set_singlepart_response_buffer()` or `set_multipart_response_buffer()`. Stop after final response part calls `complete_response()`. Invalid PEC, unexpected event order, timeout, or protocol interruption moves to aborting until a new valid start.

## State and Persistence
Per-device state is in `ssif_bmc_ctx` protected by a spinlock. Userspace waiters use `wait_queue`. A response timer recovers from userspace not providing a response. `running` enforces single opener. Request/response buffers persist until consumed or invalidated.

## Dependencies and Integration Points
Depends on I2C slave support, miscdevice, `linux/ipmi_ssif_bmc.h`, OF compatible `ssif-bmc`, and optional KUnit. It presents device name `ipmi-ssif-host`.

## Risks
The state machine handles many interrupted-transaction cases and must return `-EBUSY` to the I2C core while waiting for userspace. PEC validation and multipart length accounting are security-sensitive because the host controls transaction bytes. Userspace response timeout changes state asynchronously and can race with write attempts.

## Test Signals
Built-in KUnit cases cover singlepart request, restart without stop, restart after invalid command, singlepart response completion with PEC, stop during start, read/write interruptions, and timeout retry. Additional integration tests should cover multipart request/response and real I2C slave controller behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ssif_bmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/lp.c -->
# sources/distributed-fs/ceph-client/drivers/char/lp.c

## Purpose
Implements the generic parallel printer character driver. It binds `/dev/lpN` devices to parport devices, supports write and optional IEEE-1284 readback, exposes legacy printer ioctls and timeout controls, optionally registers an lp console, and handles module/boot-time port selection.

## Important APIs, Types, and Functions
- Global `lp_table[LP_NO]` stores per-printer `struct lp_struct`; `port_num[]` tracks bindings.
- `lp_write()` claims the parport, negotiates ECP or compatibility mode, writes user data in `LP_BUFFER_SIZE` chunks, handles status errors, and yields on preemption.
- `lp_read()` under `CONFIG_PARPORT_1284` negotiates nibble mode and reads peripheral data.
- `lp_open()` validates device existence/busy state, handles abort-open status checks, allocates a buffer, and detects best mode.
- `lp_do_ioctl()`, `lp_ioctl()`, and `lp_compat_ioctl()` implement legacy ioctls and 32/64-bit timeout conversion.
- `lp_attach()`/`lp_detach()` bind/unbind parport devices; `lp_init()` registers char major, class, and parport driver.

## Control Flow
Module parameters or `lp=` boot arguments configure port binding. Initialization clears tables, registers major `LP_MAJOR`, class `printer`, and the parport driver. Parport attach selects a free or requested `lpN`, registers a parport device with preemption callback, optionally resets the printer, creates `/dev/lpN`, and maybe registers console. File I/O claims the parport lazily, negotiates mode, performs transfer, releases on preemption or close, and reports printer status.

## State and Persistence
Persistent driver state includes `lp_table`, flags such as `LP_EXIST`, `LP_BUSY`, `LP_ABORT`, `LP_ABORTOPEN`, `LP_CAREFUL`, current/best IEEE-1284 modes, waitqueues, timeout values, per-open buffer, and parport claimed/preempt bits. `lp_mutex` protects global open/ioctl state; each device has `port_mutex` for transfer and status operations.

## Dependencies and Integration Points
Depends on the parport subsystem, character device major `LP_MAJOR`, device class creation, legacy `linux/lp.h` ioctls, optional compat ioctl support, optional IEEE-1284 readback, and optional console support.

## Risks
This is legacy hardware code with unusual semantics: `O_NONBLOCK` is commandeered for `LP_ABORTOPEN`, status bits can stall writes unless abort flags are set, console output can block depending on `CONSOLE_LP_STRICT`, and detach notes that richer cleanup is deferred. Timeout conversion must guard overflow and compat ABI differences.

## Test Signals
Test port selection modes (`auto`, `none`, explicit), open busy/existence/error paths, ECP fallback to compatibility, write partial/error/nonblock/signal paths, IEEE-1284 readback when enabled, all ioctls including timeout old/new and compat forms, parport preemption release, detach cleanup, and optional console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/lp.c -->
