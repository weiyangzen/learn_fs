# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/Makefile

Purpose: selects architecture-specific PowerPC KASAN initialization objects while disabling instrumentation on the KASAN implementation itself.

Important APIs and control flow: `KASAN_SANITIZE := n` and `KCOV_INSTRUMENT := n` prevent recursive sanitizer/coverage instrumentation. Object selection adds common 32-bit init, 8xx specialization, Book3S32 BAT specialization, and Book3S64 or Book3E64 initializers according to configuration.

State and dependencies: no runtime state. It depends on Kconfig symbols `CONFIG_PPC32`, `CONFIG_PPC_8xx`, `CONFIG_PPC_BOOK3S_32`, `CONFIG_PPC_BOOK3S_64`, and `CONFIG_PPC_BOOK3E_64`. Risks are recursive KASAN faults if instrumentation flags are removed, missing platform initializer objects, and duplicate symbol definitions if mutually exclusive configs are wrong. Test signals are successful KASAN builds for every PowerPC MMU family and early boot before KASAN is fully initialized.
