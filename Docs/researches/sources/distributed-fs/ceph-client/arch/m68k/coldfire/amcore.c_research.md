# sources/distributed-fs/ceph-client/arch/m68k/coldfire/amcore.c

Purpose: Sysam AMCORE board platform-device registration.

Important objects include optional DM9000 Ethernet resources/platform data, NOR flash partitions and physmap platform data, an `rtc-ds1307` platform device, I2C board info for a DS1338 at address `0x68`, and `amcore_devices[]`. `dm9000_pre_init()` marks IRQ 25 as autovectored with `mcf_autovector()`.

Control flow in `init_amcore()` optionally pre-initializes DM9000 interrupt routing, registers I2C RTC board info on bus 0, and calls `platform_add_devices()` for selected devices. It runs as an `arch_initcall`.

State is registered platform devices, flash partition metadata, and autovector configuration. There is no runtime driver logic here after registration.

Dependencies include ColdFire SIM/autovector APIs, platform bus, DM9000, MTD physmap/partition support, I2C board info, and downstream drivers. Integration is selected by `CONFIG_AMCORE` in the ColdFire Makefile.

Risks and test signals: DM9000 resources assume a 32-bit data bus via address/data spacing; flash partition sizes must match board flash; the `rtc_device` is generic while I2C info supplies the actual chip. Test platform device creation, DM9000 IRQ delivery, MTD partition layout, and DS1338 RTC probe.
