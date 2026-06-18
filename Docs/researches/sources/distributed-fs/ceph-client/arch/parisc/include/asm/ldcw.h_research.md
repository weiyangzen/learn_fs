# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ldcw.h

Purpose: defines the PA-RISC `ldcw` lock primitive and alignment helpers used by spinlocks and low-level atomic serialization.

Important APIs/types/functions: exports `__ldcw`, `LDCW_ALIGN`, lock-value helpers, and architecture-specific inline assembly for load-and-clear-word.

Control flow: locking code repeatedly executes `ldcw` on an aligned word until it obtains the lock value, with barriers around acquisition and release.

State and persistence: lock words in memory persist as synchronization state. Dependencies and integration: used by `spinlock.h`, atomic hash locks, and any PA-RISC low-level lock users.

Risks and test signals: PA-RISC requires strict alignment for `ldcw`; misalignment can break all locking. Test with lock alignment assertions, SMP stress, and lockdep.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
