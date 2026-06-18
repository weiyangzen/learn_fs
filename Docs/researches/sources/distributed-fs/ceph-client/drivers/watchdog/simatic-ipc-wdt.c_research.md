# sources/distributed-fs/ceph-client/drivers/watchdog/simatic-ipc-wdt.c

## Purpose
`simatic-ipc-wdt.c` supports watchdogs on Siemens SIMATIC IPC 227E and 427E systems. It controls fixed I/O ports for watchdog enable/trigger/timeout selection and, depending on platform mode, clears a secondary SAFE_EN_N reset gate through either a legacy I/O register or P2SB-discovered GPIO MMIO.

## Important APIs, types, and functions
Important constants are `WD_ENABLE_IOADR`, `WD_TRIGGER_IOADR`, timeout table `wd_timeout_table`, and SAFE_EN_N values. Watchdog operations are `wd_start()`, `wd_stop()`, `wd_ping()`, and `wd_set_timeout()`. Platform setup is split into `wd_secondary_enable()`, `wd_setup()`, and `simatic_ipc_wdt_probe()`. The global `wdd_data` is the registered `watchdog_device`.

## Control flow
Probe reads `struct simatic_ipc_platform` from platform data and accepts only 227E or 427E modes. It reserves the enable and trigger I/O ports; for 227E it temporarily reserves the GP status port, while for 427E it uses `p2sb_bar()` to locate GPIO community register space and maps PAD configuration. `wd_setup()` detects previous watchdog-triggered boot, resets the alarm bit, sets macro mode and default timeout index, and enables the secondary reset path. It then sets nowayout, asks the core to stop on reboot, and registers the watchdog.

## State and persistence behavior
The driver stores minimal state globally in `wdd_data` and `wd_reset_base_addr`. Hardware state persists in the I/O enable register, trigger side effects, timeout selection bits, and SAFE_EN_N gate. Bootstatus is captured from `WD_TRIGGERED` before the setup write clears alarm state.

## Dependencies and integration points
It integrates with the SIMATIC IPC base platform driver via `simatic_ipc_platform`, with x86 P2SB helpers for hidden bridge BAR discovery, fixed legacy I/O resource management, MMIO mapping, and the watchdog core.

## Risks and test signals
Risks are platform-data mismatch, fixed I/O port conflicts, incorrect timeout rounding via `find_closest()`, and failure to enable SAFE_EN_N, which would turn the watchdog into alarm-only behavior. Tests should cover both device modes, resource conflict failures, bootstatus when `WD_TRIGGERED` is set, timeout requests mapping to the supported table, trigger reads as pings, and reboot stop behavior.
