<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/facility.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/facility.h

Purpose: Implements s390 facility-bit manipulation and STFLE probing.

Important APIs/types/functions: `stfle_fac_list`, `__set_facility()`, `__clear_facility()`, `__test_facility()`, constant optimized tests, `test_facility()`, `__stfle()`, `stfle()`, and `stfle_size()`. Source-visible declarations include: #define __ASM_FACILITY_H; #define MAX_FACILITY_BIT (sizeof(stfle_fac_list) * 8); extern u64 stfle_fac_list[16];; static inline void __set_facility(unsigned long nr, void *facilities); unsigned char *ptr = (unsigned char *) facilities;; static inline void __clear_facility(unsigned long nr, void *facilities); unsigned char *ptr = (unsigned char *) facilities;; static __always_inline bool __test_facility(unsigned long nr, void *facilities); unsigned char *ptr;; static __always_inline bool __test_facility_constant(unsigned long nr).

Control flow: Boot code stores facility lists with STFLE, helpers test MSB-numbered facility bits, and optimized constant tests read the global list directly when in range.

State and persistence behavior: Persistent state is global probed facility list and caller-provided STFLE buffers.

Dependencies and integration points: Direct includes are #include <asm/facility-defs.h>, #include <linux/minmax.h>, #include <linux/string.h>, #include <linux/types.h>, #include <linux/preempt.h>, #include <asm/alternative.h>, #include <asm/lowcore.h>. Integrated with Integrates CPU feature detection, alternatives, CPACF, vector/FPU, MM, and virtualization feature gating..

Risks: Facility bit numbering is MSB-oriented and easy to invert; false feature tests lead to illegal instructions or disabled optimizations.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 142 lines, 3491 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/facility.h -->
