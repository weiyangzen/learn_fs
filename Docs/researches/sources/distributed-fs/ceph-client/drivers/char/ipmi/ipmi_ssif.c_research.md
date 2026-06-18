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
