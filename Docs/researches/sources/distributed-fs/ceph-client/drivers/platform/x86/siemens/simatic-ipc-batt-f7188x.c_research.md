# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-f7188x.c

Purpose: This backend module selects Nuvoton F7188x and companion pinctrl GPIO lookup tables for SIMATIC IPC CMOS battery monitoring on 227G, BX-39A, and BX-59A device modes.

Important APIs, types, and functions: Three lookup tables describe 227G, BX-39A, and BX-59A GPIO wiring. `batt_lookup_table` stores the selected table globally. `simatic_ipc_batt_f7188x_probe()` reads `struct simatic_ipc_platform` platform data, switches on `devmode`, and delegates to `simatic_ipc_batt_probe()`.

Control flow: Probe selects a table according to `SIMATIC_IPC_DEVICE_227G`, `SIMATIC_IPC_DEVICE_BX_39A`, or `SIMATIC_IPC_DEVICE_BX_59A`, rejects all other modes, and calls the shared core. Remove passes the selected global table back to the core.

State and persistence: `batt_lookup_table` is global and supports one active instance. The selected static lookup table is mutated by the shared core with `dev_id`. Battery state caching is in the core.

Dependencies and integration points: It depends on `GPIO_F7188X`, Alder Lake/Elkhart Lake pinctrl where applicable, the central SIMATIC platform data, and the shared battery core. Softdeps request `gpio_f7188x` and pinctrl providers.

Risks and edge cases: The global selected table is not per-device, so multiple instances would conflict. The three table variants combine F7188x and Intel pinctrl GPIOs; missing either provider causes probe failures. Device-mode mapping in `simatic-ipc.c` must remain synchronized.

Test signals: Test each supported `devmode`, reject unsupported modes, verify GPIO lookup names and indexes, confirm meter-line polarity for BX-59A, and unload/reload cleanup.
