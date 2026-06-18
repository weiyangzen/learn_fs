<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/setup.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/setup.c

## Purpose
`setup.c` performs protected nVHE initialization after the host donates a contiguous memory pool. It partitions the pool, rebuilds hyp mappings, backs the vmemmap, creates host stage-2 and fixmaps, reconciles ownership metadata, initializes FF-A and the VM table, and tail-calls back to the host with the result.

## Important APIs, Types, and Functions
`divide_memory_pool()` carves selftest, vmemmap, VM table, hyp stage-1 page tables, host stage-2 page tables, and FF-A proxy pages. `recreate_hyp_mappings()` builds a fresh hyp page table and maps idmap text, vectors, vmemmap, hyp text/data/rodata/bss, donated pool, per-CPU areas, stacks, and host SVE state. `update_nvhe_init_params()` publishes the new PGD to every CPU. `fix_host_ownership()` walks hyp mappings and sets matching host/hyp page states. `fix_hyp_pgtable_refcnt()` fixes allocator refcounts for table pages. `__pkvm_init_finalise()` installs full allocators and subsystems after switching page tables. `__pkvm_init()` validates inputs and invokes the idmapped PGD switch.

## Control Flow, State, and Persistence
Initialization first uses the early allocator on the donated pool, then switches to a proper hyp pool once the vmemmap is backed. `__pkvm_init()` builds all mappings, updates init params, and calls `__pkvm_init_switch_pgd()` by physical address; control resumes in `__pkvm_init_finalise()` on the new stack/page tables. Finalization writes the return value into the saved host context and exits with `__host_enter()`.

## Dependencies and Integration Points
It integrates early allocation, `mm.c` mapping helpers, `page_alloc.c`, host stage-2 setup in `mem_protect.c`, FF-A initialization, VM table setup in `pkvm.c`, per-CPU init params, host SVE data, and optional ownership selftests.

## Risks and Test Signals
Risks include mispartitioning the donated pool, missing mappings for per-CPU/stack/SVE data, wrong ownership conversion for executable hyp text, page-table refcount leaks, and failures after PGD switch that must still return cleanly. Test signals are pKVM initialization under different CPU counts and SVE support, forced allocation failures per partition, ownership selftest success, host stage-2 finalization, and boot-time mapping permission audits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/setup.c -->
