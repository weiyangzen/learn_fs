# sources/distributed-fs/ceph-client/arch/m68k/coldfire/stmark2.c

Purpose: board support for the Sysam AMCORE/STMark2 board's DSPI controller and SPI NOR flash partitioning.

Important APIs and data: `stmark2_partitions[]`, `stmark2_spi_flash_data`, `stmark2_board_info[]`, `dspi_spi0_info`, `dspi_spi0_resource[]`, `dspi_spi0_device`, `stmark2_devices[]`, and `init_stmark2()` as a `device_initcall()`.

Control flow and state: init programs DSPI pin assignment registers, board GPIO/pad registers, CAN pads, adds the DSPI platform device, and registers SPI board info for an `m25p80`/`is25lp128` flash on bus 0 chip select 1. State includes pinmux registers and platform/SPI core registration; persistent data is flash partition contents.

Dependencies and integration: FSL DSPI platform driver, SPI NOR driver, MTD partitioning, eDMA DMA resources, and board pinmux.

Risks and test signals: the comment says proper pinmux is mandatory; wrong pad setup breaks SPI. Flash partition names/sizes assume a 16 MiB device and U-Boot/kernel layout. Test DSPI probe, DMA channels, SPI NOR JEDEC read, `/proc/mtd` partition layout, and CAN pad side effects.
