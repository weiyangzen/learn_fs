<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/diag.h

Purpose: Defines s390 DIAGNOSE instruction numbers, statistics IDs, and inline DIAG helpers.

Important APIs/types/functions: `enum diag_stat_enum`, `diag_stat_inc()`, and helper wrappers for selected DIAG calls such as time, VM, and hypervisor interactions. Source-visible declarations include: #define _ASM_S390_DIAG_H; enum diag_stat_enum {; void diag_stat_inc(enum diag_stat_enum nr);; void diag_stat_inc_norecursion(enum diag_stat_enum nr);; struct hypfs_diag0c_entry;; void diag0c(struct hypfs_diag0c_entry *data);; static inline void diag10_range(unsigned long start_pfn, unsigned long num_pfn); unsigned long start_addr, end_addr;; extern int diag14(unsigned long rx, unsigned long ry1, unsigned long subcode);; struct diag210 {.

Control flow: Call sites increment per-DIAG statistics and issue `diag` instructions with fixed register conventions, often only under VM/LPAR feature checks.

State and persistence behavior: State is hypervisor/firmware state plus diagnostic statistics counters.

Dependencies and integration points: Direct includes are #include <linux/if_ether.h>, #include <linux/percpu.h>, #include <asm/asm-extable.h>, #include <asm/sclp.h>, #include <asm/cio.h>. Integrated with Integrates hypfs, appldata, watchdog, cpcmd, VM detection, and low-level virtualization services..

Risks: DIAG availability is environment-specific. Incorrect register setup or calling outside supported hypervisors can trap or return misleading data.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 377 lines, 7913 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/diag.h -->
