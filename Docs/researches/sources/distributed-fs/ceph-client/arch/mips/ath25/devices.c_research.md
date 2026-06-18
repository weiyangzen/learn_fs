## sources/distributed-fs/ceph-client/arch/mips/ath25/devices.c

Purpose: owns ATH25 global board/SoC state, shared WMAC platform devices, system type strings, early serial setup, and late device/arch initcall dispatch.

Important APIs and functions: globals `ath25_board` and `ath25_soc` are exported through declarations in `devices.h`. `get_system_type()` maps `ath25_soc` to a printable string. `ath25_serial_setup()` installs an 8250 console port when `CONFIG_SERIAL_8250_CONSOLE` is enabled. `ath25_add_wmac()` fills resources and registers `ar231x-wmac` platform devices. Initcalls `ath25_register_devices()` and `ath25_arch_init()` call family-specific device and arch setup.

Control flow: family-specific code sets `ath25_soc` and board config first. Device init calls AR5312 or AR2315 device registration based on `is_ar5312()`. Arch init later sets up serial and optional PCI through the family hooks. WMAC registration updates resource start/end pairs for memory and IRQ before platform registration.

State and persistence: `ath25_board` contains pointers to copied board/radio data and the device ID. `ath25_soc` controls system type reporting. Static platform devices are reused for WMAC0 and WMAC1. No durable state is written.

Dependencies and integration: depends on Linux platform device core, serial 8250, ATH25 platform structures, AR5312/AR2315 hooks, and CPU type helpers.

Risks: `ath25_add_wmac()` assumes `nr` is 0 or 1. `get_system_type()` reports unknown if `ath25_soc` is not set before use. Serial setup is compiled out without 8250 console support, so early/console behavior differs by config.

Test signals: registered `ar231x-wmac` devices should have correct MMIO/IRQ resources and platform data. `get_system_type()` should match detected SoC. Serial console should work when configured.
