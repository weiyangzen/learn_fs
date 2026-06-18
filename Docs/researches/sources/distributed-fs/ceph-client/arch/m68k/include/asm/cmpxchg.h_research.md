<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cmpxchg.h

## Purpose
This header implements m68k exchange and compare-exchange primitives. It supports CAS-capable CPUs with `casb/casw/casl` and fallback uniprocessor paths protected by local interrupt disabling.

## Important APIs, Types, And Functions
- `__arch_xchg()` exchanges 1-, 2-, or 4-byte values, using `swap()` under IRQ disable when `CONFIG_RMW_INSNS` is absent or CAS loops when present.
- `arch_xchg()` is the typed public macro.
- `arch_cmpxchg64_local()` maps to generic local 64-bit compare-exchange.
- `__cmpxchg()` implements 1-, 2-, and 4-byte CAS for RMW-capable builds.
- `arch_cmpxchg()`, `arch_cmpxchg_local()`, and `arch_cmpxchg64()` expose typed APIs.
- Invalid size hooks are `__invalid_xchg_size()` and `__invalid_cmpxchg_size()`.

## Control Flow
CAS exchange loops read the old value, attempt `cas*`, and retry until successful. Fallback exchange disables local interrupts, swaps by size, and restores interrupts. Non-CAS compare-exchange delegates to generic support.

## State And Persistence Behavior
Only the target memory and temporary interrupt state are mutated. The fallback assumes uniprocessor m68k, so local IRQ exclusion is sufficient for kernel atomicity.

## Dependencies And Integration Points
It depends on irqflags, minmax, generic cmpxchg-local helpers, and generic cmpxchg fallback code. It underpins atomics, locks, reference counts, and lockless kernel algorithms.

## Risks And Edge Cases
Unsupported sizes route to invalid helper symbols. CAS instruction availability must match `CONFIG_RMW_INSNS`. Memory ordering depends on the assembly memory clobbers and surrounding generic barriers.

## Test Signals
Atomic/cmpxchg selftests, xchg size tests, lock/refcount stress, CAS contention loops, and builds with and without `CONFIG_RMW_INSNS` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cmpxchg.h -->
