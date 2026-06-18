# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt.c

Purpose: This shared Siemens SIMATIC IPC CMOS battery monitor exposes battery condition through hwmon. It supports GPIO-based status lines for most models and an I/O-port status register for IPC227E.

Important APIs, types, and functions: The exported `simatic_ipc_batt_probe()` and `simatic_ipc_batt_remove()` are used by backend GPIO modules. Static `priv` stores devmode, cached current state, up to three GPIO descriptors, and cache timestamp. `simatic_ipc_batt_read_gpio()` samples empty/low/meter GPIOs. `simatic_ipc_batt_read_io()` reads I/O port `0x404d`. `simatic_ipc_batt_ops` implements `in_input` and `in_lcrit`.

Control flow: Probe reads platform data `devmode`, optionally assigns and adds a supplied lookup table, gets required empty/low GPIOs and optional meter GPIO, or skips GPIO for IPC227E. It registers a hwmon device and immediately samples once to warn about aging batteries. Reads are cached for 24 hours to avoid frequent battery measurement.

State and persistence: Battery level is reported as millivolt-like constants: full 3000, critical 2750, empty 0. `priv.current_state` and `last_updated_jiffies` cache the result globally. Hardware state is sampled from GPIOs or a single I/O port. The optional meter GPIO is pulsed during reads.

Dependencies and integration points: It integrates with platform data from `simatic-ipc.c`, gpiolib lookup tables/consumers, hwmon, jiffies, I/O port resource arbitration, and backend modules through exported symbols.

Risks and edge cases: `priv` is a global singleton, so multiple devices would overwrite each other. `simatic_ipc_batt_remove()` unconditionally calls `gpiod_remove_lookup_table(table)` even with NULL in the IO wrapper, which deserves API-behavior review. Cached state can remain stale for up to 24 hours. GPIO reads sleep and meter GPIO timing is fixed at 150 ms. Error path removes lookup tables even when some GPIO descriptors are devm-managed.

Test signals: Test GPIO and IPC227E I/O modes, cache refresh after 24 hours, immediate warning on low/empty battery, hwmon `in0_input`/`in0_lcrit`, missing GPIO failures and cleanup, request-muxed-region failures, and backend module probe/remove.
