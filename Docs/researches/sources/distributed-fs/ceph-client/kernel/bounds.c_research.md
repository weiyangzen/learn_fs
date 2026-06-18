# sources/distributed-fs/ceph-client/kernel/bounds.c

Purpose: build-time generator that emits constants for `include/generated/bounds.h` through kbuild's `DEFINE()` mechanism.

Important APIs/types/functions: `main` calls `DEFINE` for `NR_PAGEFLAGS`, `MAX_NR_ZONES`, optional `NR_CPUS_BITS`, `SPINLOCK_SIZE`, and optional multigenerational LRU widths `LRU_GEN_WIDTH` and `__LRU_REFS_WIDTH`.

Control flow: the host-built program includes kernel headers with `__GENERATING_BOUNDS_H` and `COMPILE_OFFSETS`, emits constants as assembler-like output consumed by kbuild post-processing, then exits.

State and persistence: no runtime kernel state. Its generated constants persist in build artifacts and influence preprocessor-visible kernel configuration.

Dependencies and integration: depends on page flags, memory zone, spinlock type, `linux/kbuild.h`, `linux/log2.h`, SMP and LRU generation Kconfig symbols. It is part of early generated-header build plumbing.

Risks: incorrect constants can break low-level layout assumptions across the kernel. Conditional constants must stay aligned with headers that consume generated bounds. Host compilation must avoid depending on unavailable runtime kernel state.

Test signals: full kernel builds, generated header diffs, SMP/non-SMP builds, and `CONFIG_LRU_GEN` on/off builds catch most issues.
