<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/tsb.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/tsb.S

## Purpose
Provides SPARC64 TSB and TLB miss assembly paths, plus helper routines for TSB insertion, invalidation, context switching, copying, and initialization. It is the fast path between hardware or hypervisor TLB misses and Linux page tables.

## Important APIs, Types, And Functions
Entry labels include `tsb_miss_dtlb`, `tsb_miss_itlb`, `tsb_miss_page_table_walk`, `tsb_reload`, `tsb_do_fault`, `sparc64_realfault_common`, `winfix_trampoline`, `__tsb_insert`, `tsb_flush`, `__tsb_context_switch`, `copy_tsb`, `tsb_init`, and `NGtsb_init`. It relies heavily on macros such as `TRAP_LOAD_TRAP_BLOCK`, `USER_PGTABLE_WALK_TL1`, `TSB_LOAD_QUAD`, `TSB_LOCK_TAG`, `TSB_WRITE`, and `TSB_STORE`.

## Control Flow
DTLB/ITLB miss stubs read the faulting virtual address, attempt a huge-page TSB lookup when enabled, then walk the current page table from the per-CPU trap block. Valid PTEs are written into the TSB and loaded into DTLB/ITLB, with Sun4v patched paths branching to hypervisor TLB load code. Invalid, non-executable, or missing mappings branch through `tsb_do_fault` into `do_sparc64_fault`; nested trap cases use `winfix_trampoline`. Context switches update per-CPU PGD/TSB state and either hypervisor scratchpad/fast-trap descriptors or Sun4u MMU TSB registers and locked TLB mappings.

## State And Persistence
State lives in TSB entries, per-CPU `trap_per_cpu` fields for page-table physical addresses and huge TSB config, Sun4v scratchpad registers, MMU context registers, and optional locked TLB mappings for TSB virtual aliases. `tsb_init` and `NGtsb_init` persist invalid-bit initialization across a TSB allocation.

## Dependencies And Integration Points
This code is included from SPARC64 TLB miss vectors in `ttable_64.S` and depends on page-table format bits, hypervisor fast traps, Sun4v patch sections, huge-page setup, `do_sparc64_fault`, and linker-collected patch sections from `vmlinux.lds.S`.

## Risks And Edge Cases
TSB tag locking must avoid racing with concurrent invalidation. Huge-page TSB allocation may be required from trap context and therefore bounces through a full trap frame. Sun4u versus Sun4v patching changes real instructions in place, so section boundaries and register conventions must remain exact. A bad PTE executable check on ITLB misses would execute non-executable pages.

## Test Signals
Signals include successful SPARC64 boot, context switching across processes, demand faults, ITLB execute-permission faults, hugepage and transparent hugepage faults, TSB resize/copy operations, and stress tests that invalidate TSB entries under concurrent TLB misses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/tsb.S -->
