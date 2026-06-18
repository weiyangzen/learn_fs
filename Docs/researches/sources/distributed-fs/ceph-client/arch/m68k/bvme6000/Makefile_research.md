# sources/distributed-fs/ceph-client/arch/m68k/bvme6000/Makefile

Purpose: BVME6000 platform object selection.

It builds `config.o` and `rtc.o`, providing board setup, timer/clocksource, reset, hardware clock, and a misc RTC device driver.

Control flow is Kbuild-only and relies on top-level `Kbuild` selecting `bvme6000/` for `CONFIG_BVME6000`.

State/persistence: no runtime state in the Makefile.

Risks and test signals: omitting `rtc.o` removes `/dev/rtc` support while `config.o` still has `mach_hwclk`; omitting `config.o` breaks board boot. Validate BVME6000 builds and boot initcalls.
