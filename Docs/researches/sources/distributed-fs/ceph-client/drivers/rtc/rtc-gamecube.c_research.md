# sources/distributed-fs/ceph-client/drivers/rtc/rtc-gamecube.c

Purpose: supports the RTC/SRAM portion of Nintendo GameCube, Wii, and Wii U MX23L4005 hardware over the EXI bus. The hardware counter is combined with a platform bias value stored in SRAM to produce Unix time.

Important APIs/types/functions: `struct priv` stores regmap, EXI MMIO base, and `rtc_bias`. `exi_read()`/`exi_write()` implement 24-bit register access over EXI immediate transfers. `gamecube_rtc_read_time()` adds counter plus bias; `gamecube_rtc_set_time()` writes timestamp minus bias. `gamecube_rtc_ioctl()` implements `RTC_VL_READ`. `gamecube_rtc_read_offset_from_sram()` unlocks SRAM access on Wii/Wii U style systems and reads `RTC_SRAM_BIAS`.

Control flow: probe maps EXI registers, creates a custom regmap bus, reads the RTC bias from SRAM, allocates the RTC, sets the U32 range, and registers it. EXI operations select device 1, send register address, spin until transfer completion, read/write data, then clear channel parameters. Voltage-low ioctl reads control flags and reports invalid/low-backup state.

State and persistence: RTC counter and SRAM bias persist in console hardware. The driver caches `rtc_bias` because it may not be persistently writable on all supported consoles.

Dependencies and integration: depends on platform/OF matching for `nintendo,latte-exi`, `hollywood-exi`, and `flipper-exi`, OF address lookup for SRAM protection registers, regmap, MMIO big-endian access, and RTC core.

Risks and test signals: the driver assumes no other EXI bus users and directly manipulates SRAM protection. `devm_rtc_register_device()` return is ignored. Test bias read on GameCube/Wii/Wii U paths, voltage-low ioctl, regmap access table enforcement, EXI timeout assumptions, and set/read with nonzero bias.
