# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c

Purpose: board support for Sharp SL-C3000 Spitz, SL-C3100 Borzoi, and SL-C1000 Akita PXA27x PDAs. It declares fixed GPIO/pin mux, platform devices, software nodes, memory devices, and machine descriptors.

Important APIs/types/functions: key init routines include `spitz_init()`, `spitz_fixup()`, `spitz_spi_init()`, `spitz_scoop_init()`, `spitz_pcmcia_init()`, `spitz_mkp_init()`, `spitz_keys_init()`, `spitz_leds_init()`, `spitz_mmc_init()`, `spitz_uhc_init()`, `spitz_lcd_init()`, `spitz_nand_init()`, `spitz_nor_init()`, `spitz_i2c_init()`, and `spitz_audio_init()`. Machine descriptors are `MACHINE_START(SPITZ)`, `BORZOI`, and `AKITA`.

Control flow: boot fixup saves Sharp parameters and adds a 64 MiB memblock. Machine init registers software GPIO nodes, reset/poweroff handlers, applies PXA MFP config, registers UART defaults, then conditionally instantiates SPI, SCOOP GPIO expanders, matrix keypad, gpio-keys, gpio-leds, MMC, PCMCIA, USB host, LCD, NOR, NAND, I2C, audio, and regulator constraints.

State and persistence: defines platform resources, partition tables, OOB layout callbacks, regulator constraints, software node properties, and poweroff/restart hooks. It mutates PXA PM/PCFR/MSC0 registers and card-power GPIO/SCOOP state.

Dependencies and integration points: integrates PXA27x core, SCOOP, PCMCIA, matrix-keypad, gpio-keys, LEDs, PXA SPI, ADS7846, corgi LCD, MAX1111, MMC, OHCI, PXA framebuffer, SharpSL NAND, physmap NOR, I2C devices, regulators, audio, and `sharpsl_pm`.

Risks: legacy non-DT board file has many compile-time optional paths; missing driver configs silently become no-op init stubs. Akita-specific differences for second SCOOP, MAX7310, NAND OOB, and audio/LCD GPIOs are easy to regress. Power sequencing for shared CF/SD rails is timing-sensitive.

Test signals: boot on all three machine IDs, device enumeration, keypad matrix, suspend key, LED triggers, SPI touchscreen/LCD/ADC, MMC detect/write-protect, PCMCIA slot count, NAND OOB behavior, NOR partitions, USB host power, and restart/poweroff.
