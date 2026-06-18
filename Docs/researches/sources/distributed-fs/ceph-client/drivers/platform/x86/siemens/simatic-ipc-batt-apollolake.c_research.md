# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-apollolake.c

Purpose: This backend module supplies Apollo Lake GPIO lookup data for SIMATIC IPC CMOS battery monitoring, specifically the 127E device mode, and delegates logic to the shared battery core.

Important APIs, types, and functions: `simatic_ipc_batt_gpio_table_127e` maps three GPIOs from `apollolake-pinctrl.0` and `.1` to indexed battery signals. `simatic_ipc_batt_apollolake_probe()` calls `simatic_ipc_batt_probe()`, and remove calls `simatic_ipc_batt_remove()`.

Control flow: The platform driver binds by module/platform name, registers through `module_platform_driver()`, and relies on `simatic-ipc.c` to create a platform device named with the `_batt_apollolake` suffix for matching devmode.

State and persistence: The only local state is the static lookup table. Runtime GPIO state and hwmon registration are owned by the shared battery core.

Dependencies and integration points: It depends on `simatic-ipc-batt.h`, gpiolib machine lookup tables, the Apollo Lake pinctrl provider, and the central SIMATIC platform driver. Softdeps request `simatic-ipc-batt` and `apollolake-pinctrl`.

Risks and edge cases: GPIO chip names and line numbers must match the kernel's Apollo Lake pinctrl device naming. The shared core mutates `table->dev_id` during probe, so the static table is effectively single-instance.

Test signals: Probe on 127E hardware, verify all three GPIOs resolve, hwmon battery voltage states change correctly, and lookup table is removed on module unload or probe failure.
