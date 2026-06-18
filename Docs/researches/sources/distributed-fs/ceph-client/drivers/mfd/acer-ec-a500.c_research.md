<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/acer-ec-a500.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/acer-ec-a500.c

Purpose: implements the Acer Iconia Tab A500 embedded-controller MFD driver over I2C. It exposes the KB930 controller through a custom regmap bus, creates battery and LED child devices, and optionally registers system power-off and restart hooks when the device tree marks the EC as the system power controller.

Important APIs and functions: `a500_ec_probe` initializes the regmap and MFD cells; `a500_ec_remove` unregisters power hooks. The regmap bus is backed by `a500_ec_read` and `a500_ec_write`, which issue SMBus word transactions with retry sleeps. Power hooks are `a500_ec_poweroff` and `a500_ec_restart_notify`; child cells are `"acer-a500-iconia-battery"` and `"acer-a500-iconia-leds"`.

Control flow: probe builds a devm regmap with 8-bit registers and 16-bit little-endian values, then calls `devm_mfd_add_devices`. If `of_device_is_system_power_controller()` is true, it stores the I2C client in the file-global `a500_ec_client_pm_off`, registers a restart notifier, and installs `pm_power_off` only if no handler is already present. Reads and writes retry up to five times with a 500 ms delay; current reads add an extra 10 ms delay for `REG_CURRENT_NOW`. Power-off and restart commands write fixed opcodes then block for one second.

State and persistence: persistent device state is in the external EC registers and firmware. Kernel state is a devm-managed regmap plus the global power-management I2C client pointer and restart notifier. There is no software cache beyond regmap defaults, and remove only clears `pm_power_off` if this driver owns it.

Dependencies and integration points: depends on Linux I2C SMBus, regmap custom bus support, MFD core, device-tree power-controller discovery, reboot notifier infrastructure, and the child battery/LED drivers named by the MFD cells. It integrates with system shutdown by writing EC reboot/shutdown registers directly instead of using child drivers.

Risks: the global `a500_ec_client_pm_off` assumes only one active system-power-controller instance. The power-off/restart paths ignore SMBus write failures and then delay, so failure diagnostics may be weak during shutdown. The custom regmap callbacks do unaligned pointer casts from `void *` buffers, which is common in old regmap bus code but sensitive to architecture assumptions. Retry delays are long enough to stall callers for seconds on an unresponsive bus.

Test signals: useful validation includes kernel build coverage with the OF compatible `acer,a500-iconia-ec`, probe with battery and LED child creation, SMBus failure injection for retry/error logs, system power-off and warm/cold reboot behavior on A500 hardware, and current-read timing behavior for the battery child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/acer-ec-a500.c -->
