
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.c

## Purpose
Provides the host-side shadow TLB implementation for e500 KVM. It translates guest TLB entries to real host TLB entries, installs them with MAS registers and `tlbwe`, tracks guest-to-host TLB1 mappings, invalidates shadow entries, handles the magic page on e500v2, and supplies MMU notifier callbacks.

## Important APIs, Types, And Functions
Externally used functions are `inval_gtlbe_on_host()`, `kvmppc_core_flush_tlb()`, `kvmppc_mmu_map()`, `kvmppc_load_last_inst()`, `kvm_unmap_gfn_range()`, `kvm_age_gfn()`, `kvm_test_age_gfn()`, `e500_mmu_host_init()`, and `e500_mmu_host_uninit()`. Core internals include `__write_host_tlbe()`, `get_host_mas0()`, `write_stlbe()`, `kvmppc_e500_shadow_map()`, `kvmppc_e500_tlb0_map()`, and `kvmppc_e500_tlb1_map()`.

## Control Flow
`kvmppc_mmu_map()` dispatches by guest TLB selection. TLB0 entries map one page through host TLB0, reusing existing private metadata if present. TLB1 entries call `kvmppc_e500_shadow_map()`, which resolves GFN to HVA/PFN under the KVM MMU invalidation sequence, inspects Linux PTE WIMG bits, chooses a shadow page size bounded by host page size and memslot alignment, records private PFN/permission metadata, flushes icache, and emits a shadow TLBE. Large safe mappings are placed into reserved host TLB1 slots with reverse maps; 4 KiB fallbacks use host TLB0.

## State And Persistence
Global host geometry is cached in `host_tlb_params`. Per-vCPU persistent state includes `gtlb_priv`, `g2h_tlb1_map`, `h2g_tlb1_rmap`, and `host_tlb1_nv`. Shadow entries live in hardware TLBs and are reconstructed as needed. `kvmppc_core_flush_tlb()` invalidates all host shadow TLB state and clears metadata. PFN/page references are released through `kvm_release_faultin_page()` after shadow setup.

## Dependencies And Integration Points
Depends on low-level PowerPC MAS/TLB instructions, KVM memslot and MMU notifier infrastructure, Linux PTE walking via `find_linux_pte()`, page fault-in helpers, e500 TLB helper macros, and BookE tracepoints. It is called by `e500_mmu.c` for pre-maps and invalidations and by instruction emulation paths that need to fetch the trapped instruction in BookE HV mode.

## Risks
Hardware TLB manipulation requires interrupts/preemption control and careful MAS5/MAS8 cleanup. The GFN notifier path is coarse: unmap requests return true to force global shadow invalidation, while age/test-age do nothing, trading performance for simplicity. Large-page shadow selection has subtle alignment and memslot-boundary requirements. `kvmppc_load_last_inst()` refuses non-RAM or execute-disallowed mappings, so failures may cause retry loops if guests continually fault on evicted or unsafe instruction pages.

## Test Signals
No local unit tests exist. Regression signals include successful e500 guest boot, MMU notifier stress with memory hot-unplug/memslot updates, tracepoints `kvm_booke206_stlb_write` and `kvm_booke206_ref_release`, and negative tests around execute permission, storage attributes, and non-RAM instruction fetches.
