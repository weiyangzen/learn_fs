# sources/distributed-fs/ceph-client/arch/m68k/coldfire/device.c

Purpose: common ColdFire SoC platform-device registration for UART, FEC Ethernet, QSPI, IMX I2C, eDMA, eSDHC, and FlexCAN blocks. It converts SoC header macros such as `MCFUART_BASE*`, `MCFFEC_BASE*`, `MCFI2C_BASE*`, `MCFEDMA_BASE`, and IRQ constants into Linux `platform_device` and `resource` records.

Important APIs and data: `mcf_uart_platform_data`, `mcf_uart`, optional `mcf_fec0/1`, `mcf_qspi`, `mcf_i2c0..5`, `mcf_edma`, `mcf_esdhc`, `mcf_flexcan0`, and `mcf_devices[]`. QSPI chip selects are driven by `mcf_cs_setup()`, `mcf_cs_teardown()`, `mcf_cs_select()`, and `mcf_cs_deselect()` through the GPIO API. `mcf_init_devices()` is the `arch_initcall()` that calls `mcf_uart_set_irq()` then `platform_add_devices()`.

Control flow and state: all hardware description is static init data selected by compile-time SoC macros. Runtime state is only platform-core registration plus GPIO ownership for QSPI CS pins; there is no persistent storage. eDMA adds a static `dma_slave_map` and 32-bit DMA mask.

Dependencies and integration: Linux platform bus, FEC, QSPI, I2C, DMA engine, SDHCI, CAN, GPIO, and ColdFire register headers. It integrates with SoC-specific `config_BSP()` pinmux files that must configure pins before the drivers bind.

Risks and test signals: wrong base/IRQ macros silently create unusable devices; QSPI setup has explicit unwind paths for GPIO request/direction failures; FEC naming differs for `CONFIG_M5441x` (`enet-fec`). Test by booting target configs and checking platform device enumeration, driver bind logs, IRQ delivery, QSPI CS transitions, and eDMA slave lookup names.
