<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-setup.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-setup.c

Purpose: board support for the Technologic Systems TS-78xx Orion5x SBC. It maps the FPGA register window, configures Orion5x core peripherals, and dynamically exposes FPGA-attached devices: M48T86 RTC, platform NAND, and timer-IOMEM RNG.

Important APIs and functions: `ts78xx_map_io()` extends `orion5x_map_io()` with an FPGA `map_desc`; `ts78xx_init()` configures MPP pins, EHCI, Ethernet, SATA, UARTs, XOR, then initializes FPGA devices and sysfs. NAND callbacks `ts78xx_ts_nand_cmd_ctrl()`, `*_dev_ready()`, `*_write_buf()`, and `*_read_buf()` translate Linux NAND operations to FPGA control/data registers and optimize aligned longword transfers. The sysfs attribute `ts78xx_fpga` uses `ts78xx_fpga_show()` and `ts78xx_fpga_store()` to report or toggle online/offline state.

Control flow: boot enters the `MACHINE_START(TS78XX)` hooks, maps Orion and FPGA IO, then `ts78xx_init()` calls `ts78xx_fpga_devices_zero_init()` and `ts78xx_fpga_load()`. Loading reads the FPGA ID, derives supported devices in `ts78xx_fpga_supports()`, and calls individual platform-device register helpers. Unloading verifies the FPGA ID did not change before deleting devices.

State and persistence: `static struct ts78xx_fpga_data ts78xx_fpga` persists FPGA ID, online state, device-present flags, and once-registered `init` bits. NAND partition layout is fixed in static MTD partitions; no runtime persistence beyond registered platform devices and sysfs state.

Dependencies and integration: depends on Orion5x machine helpers, Marvell Ethernet/SATA platform data, MTD NAND core, RTC, timeriomem RNG, sysfs `firmware_kobj`, and TS-78xx FPGA constants. It is ATAGS-era board code, not DT.

Risks and test signals: sysfs offline/online can race external `/dev/mem` FPGA reprogramming; mismatched FPGA ID marks state negative and requires power cycle. Device registration failures clear presence flags and return `-EBUSY` from FPGA load. Test with TS78xx boot logs, `/sys/firmware/ts78xx_fpga`, MTD partition discovery, RTC registration, RNG registration, and NAND read/write alignment paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-setup.c -->
