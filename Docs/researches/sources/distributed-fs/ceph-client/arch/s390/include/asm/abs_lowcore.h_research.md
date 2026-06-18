<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/abs_lowcore.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/abs_lowcore.h

Purpose: Declares absolute lowcore mapping helpers for accessing per-CPU lowcore memory at fixed absolute addresses.

Important APIs/types/functions: `ABS_LOWCORE_MAP_SIZE`, `__abs_lowcore`, `abs_lowcore_map()`, `abs_lowcore_unmap()`, `get_abs_lowcore()`, and `put_abs_lowcore()`. Source-visible declarations include: #define _ASM_S390_ABS_LOWCORE_H; #define ABS_LOWCORE_MAP_SIZE (NR_CPUS * sizeof(struct lowcore)); extern unsigned long __abs_lowcore;; int abs_lowcore_map(int cpu, struct lowcore *lc, bool alloc);; void abs_lowcore_unmap(int cpu);; static inline struct lowcore *get_abs_lowcore(void); int cpu;; static inline void put_abs_lowcore(struct lowcore *lc).

Control flow: `get_abs_lowcore()` maps the current CPU lowcore into the absolute-lowcore window, disables preemption to pin the CPU, and returns a typed pointer; `put_abs_lowcore()` unmaps and reenables preemption.

State and persistence behavior: State is the architecture-managed absolute lowcore mapping and the preemption-disabled critical section around a caller's access.

Dependencies and integration points: Direct includes are #include <linux/smp.h>, #include <asm/lowcore.h>. Integrated with Depends on `struct lowcore`, CPU IDs, `preempt_disable/enable`, and low-level memory mapping implementation..

Risks: Callers must pair get/put and keep access short; CPU migration or stale mappings would expose the wrong lowcore.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 28 lines, 595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/abs_lowcore.h -->
