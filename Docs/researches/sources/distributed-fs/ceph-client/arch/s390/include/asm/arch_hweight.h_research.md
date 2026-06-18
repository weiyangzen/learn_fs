<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch_hweight.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/arch_hweight.h

Purpose: Provides s390 accelerated Hamming-weight/popcount helpers.

Important APIs/types/functions: `arch_hweight8/16/32/64()` plus constant folding and runtime instruction paths. Source-visible declarations include: #define _ASM_S390_ARCH_HWEIGHT_H; static __always_inline unsigned long popcnt_z196(unsigned long w); unsigned long cnt;; static __always_inline unsigned long popcnt_z15(unsigned long w); unsigned long cnt;; static __always_inline unsigned long __arch_hweight64(__u64 w); static __always_inline unsigned int __arch_hweight32(unsigned int w); static __always_inline unsigned int __arch_hweight16(unsigned int w); static __always_inline unsigned int __arch_hweight8(unsigned int w).

Control flow: For compile-time constants the compiler can fold the result; otherwise inline assembly uses s390 population-count support when available by build target.

State and persistence behavior: No persistent state; helpers compute bit counts from input values.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <asm/march.h>. Integrated with Integrates with generic bitops, bitmap code, networking masks, sched masks, and CPU facility/build-level assumptions..

Risks: Instruction availability must match the selected march/facility support, and helper signatures must preserve generic hweight semantics.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 77 lines, 1695 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/arch_hweight.h -->
