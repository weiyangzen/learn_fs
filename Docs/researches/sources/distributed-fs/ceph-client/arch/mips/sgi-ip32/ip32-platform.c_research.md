# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-platform.c

Purpose: registers SGI O2 platform devices for serial, Ethernet, audio, buttons, and RTC.

Important APIs and control flow: static 8250 platform data describes two MACE ISA serial ports. Device initcalls register `serial8250`, allocate/add `meth`, allocate/add `sgio2audio`, register `sgibtns`, and register a `rtc-ds1685` device with IRQ/MMIO resources, padded register step, BCD mode, and `ip32_prepare_poweroff()` callback.

State, persistence, and integration: state is platform-device registration and RTC platform data. Dependencies include MACE base/IRQ constants, platform drivers, and reset code's exported `ip32_prepare_poweroff()`. Risks include no device resources for `meth` and audio, simple-device helper returning `IS_ERR()` as int, and RTC poweroff module dependency. Test signals are ttyS registration, MACE Ethernet, O2 audio, buttons, RTC, and poweroff callback operation.
