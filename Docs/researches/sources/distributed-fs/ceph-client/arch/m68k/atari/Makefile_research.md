# sources/distributed-fs/ceph-client/arch/m68k/atari/Makefile

Purpose: Atari platform object selection.

It always builds `config.o`, `time.o`, `debug.o`, `ataints.o`, `stdma.o`, `atasound.o`, and `stram.o`. It adds `atakeyb.o` for `CONFIG_ATARI_KBD_CORE` and `nvram.o` when `CONFIG_NVRAM` is modular-enabled through the substitution expression.

Control flow is Kbuild-only, selecting machine setup, clock/RTC, debug console, interrupt controller, shared DMA arbitration, sound, ST-RAM allocation, keyboard, and NVRAM support.

State/persistence: no runtime state in the Makefile; object inclusion shapes available hooks and exported symbols.

Dependencies include top-level `Kbuild` and Atari-related Kconfig symbols. Integration ensures `config_atari()` can reference functions such as `atari_sched_init()`, `atari_init_IRQ()`, and `atari_mksound()`.

Risks and test signals: the `CONFIG_NVRAM:m=y` expression is subtle and should be validated for built-in vs modular builds. Test Atari configs with and without keyboard core and NVRAM support.
