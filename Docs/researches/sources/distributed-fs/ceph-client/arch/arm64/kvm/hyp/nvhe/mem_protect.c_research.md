<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mem_protect.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mem_protect.c

## Purpose
`mem_protect.c` is the pKVM memory-ownership and stage-2 protection state machine. It builds host and guest stage-2 page tables, tracks page ownership in hyp vmemmap metadata, transitions pages between host, hyp, guest, and FF-A/shared states, resolves host stage-2 faults, poisons reclaimed guest pages, and provides debug selftests for ownership invariants.

## Important APIs, Types, and Functions
`host_mmu` and `host_s2_pool` hold the protected host stage-2 page table and allocator. `kvm_host_prepare_stage2()` initializes the host idmap page table. `kvm_guest_prepare_stage2()` initializes each hyp VM’s guest stage-2 and mm ops. `__pkvm_prot_finalize()` enables host stage-2 translation per CPU. `handle_host_mem_abort()` lazily maps allowed host memory/MMIO or injects host aborts. Ownership APIs include `__pkvm_host_share_hyp()`, `__pkvm_host_unshare_hyp()`, `__pkvm_host_donate_hyp()`, `__pkvm_hyp_donate_host()`, `__pkvm_host_share_ffa()`, `__pkvm_host_unshare_ffa()`, `__pkvm_host_donate_guest()`, `__pkvm_host_share_guest()`, `__pkvm_host_unshare_guest()`, `__pkvm_guest_share_host()`, `__pkvm_guest_unshare_host()`, `__pkvm_host_force_reclaim_page_guest()`, and `__pkvm_host_reclaim_page_guest()`. Guest maintenance helpers implement dirty/young/write-protect and permission relaxation for non-protected VMs.

## Control Flow, State, and Persistence
The file persists page ownership in `struct hyp_page` host/hyp state fields, guest state in guest stage-2 PTEs, donated guest owner metadata in invalid host stage-2 PTE annotations, and transient current guest VM in per-CPU `__current_vm`. Component locks are always acquired in host/hyp/guest order through `host_lock_component()`, `hyp_lock_component()`, and `guest_lock_component()`. Host stage-2 mappings are rebuilt lazily on host faults and may recycle MMIO mappings on allocation pressure. Guest donation annotates the host PTE with guest handle/GFN metadata, then maps the guest IPA as owned. Reclaim unmaps or poisons guest mappings and returns ownership to the host.

## Dependencies and Integration Points
It depends on KVM page-table primitives, memblock memory ranges from `mm.c`, hyp buddy allocation from `page_alloc.c`, pKVM VM handles from `pkvm.c`, hyp fixmap/fixblock helpers from `mm.c`, host trap handling in `hyp-main.c`, FF-A proxy calls in `ffa.c`, and architecture workarounds for speculative AT and SME DVM sync.

## Risks and Test Signals
Risks are high because this file enforces confidentiality: lock-order bugs, invalid range validation, host PTE annotation corruption, block mapping side effects, incomplete TLB/cache maintenance, refcount errors on pinned shared pages, and guest reclaim races can all break pKVM guarantees. Built-in `pkvm_ownership_selftest()` covers many transitions under `CONFIG_NVHE_EL2_DEBUG`; additional signals include protected VM boot/teardown, forced reclaim of poisoned pages, FF-A share/reclaim cycles, host abort injection, MMIO lazy mapping under low page-table memory, and permission operations rejected for protected VMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mem_protect.c -->
