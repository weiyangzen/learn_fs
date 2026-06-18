<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dat-bits.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dat-bits.h

Purpose: Defines s390 Dynamic Address Translation bitfield layouts for virtual addresses, ASCEs, region/segment tables, and PTEs.

Important APIs/types/functions: `union vaddress`, `union asce`, region table entry unions, segment table entry unions, `union page_table_entry`, and DAT bit enumerations. Source-visible declarations include: #define _S390_DAT_BITS_H; union vaddress {; unsigned long addr;; struct {; unsigned long rfx : 11;; unsigned long rsx : 11;; unsigned long rtx : 11;; unsigned long sx : 11;; unsigned long px : 8;; unsigned long bx : 12;.

Control flow: MM code composes table entries and ASCEs using these packed bitfields and hardware page-table walkers interpret the resulting words.

State and persistence behavior: Persistent state is page-table memory, mm context ASCEs, and hardware translation state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates low-level MM, KVM, page table allocation, fault handling, and control-register loading..

Risks: Every bit position is hardware ABI; C bitfield endianness/packing assumptions must remain valid for s390.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 198 lines, 5691 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dat-bits.h -->
