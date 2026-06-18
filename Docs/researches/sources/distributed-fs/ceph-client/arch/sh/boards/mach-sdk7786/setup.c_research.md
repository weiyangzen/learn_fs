<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/setup.c

## Purpose
SDK7786 board setup. It registers heartbeat, SMSC911x, FPGA SMBus devices, I2C board data, PCIe clocks, restart/power-off hooks, and machine-vector callbacks for mode pins, clock init, and IRQ init.

## Important APIs, Types, and Functions
- functions: sdk7786_i2c_setup, sdk7786_devices_setup, sdk7786_mode_pins, sdk7786_pcie_clk_enable, sdk7786_pcie_clk_disable, sdk7786_clk_init, sdk7786_restart, sdk7786_power_off, sdk7786_setup.
- integration hooks: platform_add_devices, device_initcall, sh_machine_vector, i2c_register_board_info, pm_power_off, clk_register, clkdev_add.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- installs board power/suspend callbacks used later by PM paths.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/platform_device.h, linux/io.h, linux/regulator/fixed.h, linux/regulator/machine.h, linux/smsc911x.h, linux/i2c.h, linux/irq.h, linux/clk.h, linux/clkdev.h.
- resource/data arrays: dummy_supplies, smsc911x_resources.
- Source-tree integration: mach-sdk7786; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- static bus addresses and board straps must match hardware for probe success.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-sdk7786/setup.c -->
