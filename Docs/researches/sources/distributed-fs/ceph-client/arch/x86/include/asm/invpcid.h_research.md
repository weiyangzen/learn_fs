<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/invpcid.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/invpcid.h

## Purpose
Inline INVPCID instruction wrapper and descriptor type definitions for precise TLB invalidation. The header is 50 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INVPCID`; `#define INVPCID_TYPE_INDIV_ADDR 0`; `#define INVPCID_TYPE_SINGLE_CTXT 1`; `#define INVPCID_TYPE_ALL_INCL_GLOBAL 2`; `#define INVPCID_TYPE_ALL_NON_GLOBAL 3`

Notable declarations and inline helpers: `#define _ASM_X86_INVPCID`; `static inline void __invpcid(unsigned long pcid, unsigned long addr,`; `unsigned long type)`; `struct { u64 d[2]; } desc = { { pcid, addr } };`; `#define INVPCID_TYPE_INDIV_ADDR 0`; `#define INVPCID_TYPE_SINGLE_CTXT 1`; `#define INVPCID_TYPE_ALL_INCL_GLOBAL 2`; `#define INVPCID_TYPE_ALL_NON_GLOBAL 3`; `static inline void invpcid_flush_one(unsigned long pcid,`; `unsigned long addr)`; `static inline void invpcid_flush_single_context(unsigned long pcid)`; `static inline void invpcid_flush_all(void)`; `static inline void invpcid_flush_all_nonglobals(void)`

## Control Flow
Callers build an invpcid_desc with PCID/address and invoke invpcid(type, desc) for individual address, single context, all contexts, or global invalidation.

## State and Persistence
State affected is CPU TLB/PCID state; no software state persists in the header.

## Dependencies and Integration Points
Depends on CPU INVPCID feature checks, CR4 PCIDE, TLB flush code, and inline asm memory clobber semantics.

## Risks
Risks include executing without feature support, wrong descriptor packing/alignment, and insufficient barriers around page-table changes.

## Test Signals
Tests should cover PCID-enabled TLB flush paths, KVM/VMX interactions, hugepage invalidations, and fallback on CPUs without INVPCID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/invpcid.h -->
