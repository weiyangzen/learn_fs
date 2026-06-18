<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fault.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fault.h

Purpose: Defines translation-exception identification decoding helpers.

Important APIs/types/functions: `union teid` and TEID-related fault type bits. Source-visible declarations include: #define _ASM_S390_FAULT_H; union teid {; unsigned long val;; struct {; unsigned long addr : 52; /* Translation-exception Address */; unsigned long fsi : 2; /* Access Exception Fetch/Store Indication */; unsigned long : 2;; unsigned long b56 : 1;; unsigned long : 3;; unsigned long b60 : 1;.

Control flow: Fault handlers decode the hardware TEID word to determine address, protection, store/fetch, and translation details.

State and persistence behavior: State is transient fault metadata captured by low-level exception code.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates page fault handling, KVM, user access recovery, and MM diagnostics..

Risks: Bitfield layout is hardware ABI; wrong decoding misclassifies page faults or protection exceptions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 28 lines, 730 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fault.h -->
