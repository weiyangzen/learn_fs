<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/setup.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/setup.c

Purpose: This large board setup file initializes the Renesas AP-325RXA/AP-320A-compatible platform with Ethernet, NOR/NAND flash, LCDC/backlight, camera/CEU memory, MMC/SD, regulators, GPIO mappings, suspend SDRAM hooks, and other SH7723 peripherals.

Important APIs/types/functions: It defines `ceu_dma_membase`, dummy supplies, SMSC911x device, NOR and NAND partition/platform data, LCD/backlight helpers `ap320_wvga_set_brightness`, `ap320_wvga_power_on`, `ap320_wvga_power_off`, LCDC modes/info/resources/device, plus many platform resources/devices for camera, MMC/SD, GPIO/regulator/I2C/video integration, and board init/setup callbacks later in the file.

Control flow: Early setup reserves DMA memory for CEU, configures GPIO/pinmux and board FPGA registers, registers fixed regulators and platform devices, supplies LCD power/backlight callbacks to the framebuffer driver, and installs suspend SDRAM enter/leave code. Device registration is static platform-data driven rather than device-tree driven.

State and persistence: Persistent state includes reserved CEU DMA memory, flash partition layouts, platform-device/resource tables, GPIO lookup/regulator mappings, LCD/backlight register state, and SDRAM suspend code ranges.

Dependencies and integration points: It depends on SH7723 CPU headers, DMA memblock APIs, GPIO and gpiod lookup, fixed regulators, SMSC911x, physmap and SH flash controller MTD, TMIO/MMC, Renesas CEU/camera sensor data, SH Mobile LCDC, I2C, and SuperH suspend/machvec support.

Risks and test signals: Static platform data spans many devices, so resource overlap and incorrect GPIO polarity are common risks. Reserved CEU memory must be aligned and excluded from normal allocation. LCD/backlight callbacks directly touch FPGA/GPIO registers. Tests include AP325RXA boot, Ethernet, NOR/NAND partitions, LCD/backlight, camera capture, MMC/SD, suspend/resume SDRAM self-refresh, and regulator/GPIO lookup validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/setup.c -->
