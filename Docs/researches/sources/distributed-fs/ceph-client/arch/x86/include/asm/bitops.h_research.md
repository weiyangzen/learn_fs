
# sources/distributed-fs/ceph-client/arch/x86/include/asm/bitops.h

Purpose: x86 atomic and non-atomic bit operations, bit scanning, and hweight integration for generic bitops users.

Important APIs and control flow: set/clear/change operations choose constant byte masks or variable `bts/btr/btc` forms, locked when atomic. Test-and-* variants return carry via `GEN_BINARY_RMWcc`. `arch_test_bit()` uses compile-time constant tests or `bt`; acquire version uses a memory-clobbered byte test for constants. `__ffs`, `ffz`, `__fls`, `ffs`, `fls`, and `fls64` use compiler builtins for constants and x86 scan/tzcnt/bsr instructions for variables.

State, dependencies, and risks: state is caller-owned bitmaps, often shared with locks or atomics. Dependencies include lock prefix alternatives, barriers, rmwcc, generic instrumented bitops, endian helpers, and hweight. Risks include confusing atomic and non-atomic variants, relying on undefined zero-input scan behavior, and byte-mask assumptions for constant bit numbers. Test signals are generic bitops tests, filesystem bitmap operations, scheduler masks, KVM comments around local atomic behavior, and KCSAN reports.
