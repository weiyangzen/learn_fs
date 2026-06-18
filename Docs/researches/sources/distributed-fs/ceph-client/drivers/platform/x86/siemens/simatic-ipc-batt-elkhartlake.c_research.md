# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc-batt-elkhartlake.c

Purpose: This backend module supplies Elkhart Lake GPIO lookup data for SIMATIC IPC CMOS battery monitoring on BX-21A device mode systems and delegates monitoring to the shared core.

Important APIs, types, and functions: `simatic_ipc_batt_gpio_table_bx_21a` maps two status GPIOs and one meter GPIO from `INTC1020` pinctrl devices. Probe and remove are thin wrappers around `simatic_ipc_batt_probe()` and `simatic_ipc_batt_remove()`.

Control flow: The module platform driver binds to a platform device created by `simatic-ipc.c` with the `_batt_elkhartlake` suffix. Probe installs the lookup table through the core; remove removes it.

State and persistence: Local persistent state is the static lookup table. The core owns the cached battery state and GPIO descriptors.

Dependencies and integration points: It depends on Elkhart Lake pinctrl, gpiolib lookup tables, and the shared SIMATIC battery core. Softdeps request `simatic-ipc-batt` and `elkhartlake-pinctrl`.

Risks and edge cases: The table's GPIO initial output polarity interacts with shared core logic that initializes the meter line low for BX-21A. Wrong GPIO chip names or indexes will fail probe or report false battery status.

Test signals: Validate BX-21A platform-device creation, GPIO resolution, meter GPIO polarity, hwmon values for full/critical/empty, and cleanup on remove.
