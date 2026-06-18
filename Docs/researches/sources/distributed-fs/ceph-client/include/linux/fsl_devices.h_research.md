# sources/distributed-fs/ceph-client/include/linux/fsl_devices.h

Purpose: defines shared Freescale platform-data conventions and structures for USB, SPI, PCMCIA, and deep-sleep handling on older Freescale SoCs.

Important APIs and types: USB enums describe controller versions, operating modes, and PHY modes. `struct fsl_usb2_platform_data` carries controller/PHY mode, port enables, workarounds, board init/exit hooks, MMIO registers, clock, power budget, endian/setup flags, suspend state, erratum flags, PHY clock validation, and saved EHCI/USB register state. `struct fsl_spi_platform_data` stores initial SPMODE, bus number, CPM/QE mode flags, chipselect count/control hook, and sysclk. `struct mpc8xx_pcmcia_ops` supplies hardware control and voltage callbacks. `fsl_deep_sleep()` reports whether suspend removes core power on supported PPC83xx suspend builds, otherwise returns 0.

Control flow: board/platform code fills platform data before registering devices; drivers consume flags and callbacks during probe, runtime operation, suspend/resume, and errata handling. USB suspend stores registers into the save area and restores them later.

State and persistence: platform data is runtime configuration and suspend/resume state, not persistent storage. It reflects board wiring and SoC errata that must remain stable for a device instance.

Dependencies and integration points: integrates with Freescale USB host/device/OTG drivers, SPI drivers, PCMCIA platform code, clocks, platform devices, and PPC suspend support.

Risks and test signals: risks include wrong endian flags, stale erratum flags, callback lifetime issues, incorrect register restore, and mismatch between board wiring and platform data. Tests should cover USB modes/PHY variants, suspend/resume including deep sleep, SPI chipselect callbacks, CPM/QE mode selection, PHY clock timeout handling, and erratum-specific paths.
