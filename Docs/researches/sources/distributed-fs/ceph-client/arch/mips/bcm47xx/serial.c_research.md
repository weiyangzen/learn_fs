# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/serial.c

Purpose: registers early 8250 UART platform data for BCM47xx SoCs using either SSB or BCMA bus discovery.

Important APIs and functions: `uart8250_init_ssb()` and `uart8250_init_bcma()` fill a `plat_serial8250_port` array from the chipcommon UART descriptors and register the `serial8250` platform device. `uart8250_init()` dispatches based on `bcm47xx_bus_type` and is wired as a device initcall.

Control flow: after the SoC bus is available, the initcall chooses SSB or BCMA, converts bus-specific UART metadata into standard 8250 fields, terminates the array with an empty entry, and registers the platform device.

State and persistence: creates a platform device and immutable UART resource/clock descriptions for the serial core. There is no persistent state.

Dependencies and integration points: depends on global `bcm47xx_bus`, Linux 8250 platform driver, SSB/BCMA chipcommon UART inventory, and the BCM47xx bus setup path.

Risks and test signals: incorrect clock, memory base, or IRQ values break console/login serial. Test by booting with serial console, checking registered ttyS devices, and confirming both SSB and BCMA boards enumerate the expected UART count.
