
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu.c

## Purpose
Implements software guest TLB management for Freescale BookE/e500 KVM, including guest TLB search, MAS register emulation, userspace-visible TLB configuration, translation, and lifecycle allocation. It owns the guest-facing TLB arrays and calls host-shadow helpers in `e500_mmu_host.c` whenever guest TLB entries need to be mapped or invalidated on the real hardware.

## Important APIs, Types, And Functions
Key entry points include `kvmppc_e500_emul_tlbivax()`, `kvmppc_e500_emul_tlbilx()`, `kvmppc_e500_emul_tlbre()`, `kvmppc_e500_emul_tlbsx()`, `kvmppc_e500_emul_tlbwe()`, `kvmppc_core_vcpu_translate()`, `kvmppc_mmu_itlb_index()`, `kvmppc_mmu_dtlb_index()`, `kvmppc_mmu_xlate()`, `kvm_vcpu_ioctl_config_tlb()`, `kvm_vcpu_ioctl_dirty_tlb()`, `kvmppc_e500_tlb_init()`, and `kvmppc_e500_tlb_uninit()`. The file manipulates `struct kvmppc_vcpu_e500`, `struct kvm_book3e_206_tlb_entry`, `struct kvm_book3e_206_tlb_params`, and per-entry `struct tlbe_priv` storage allocated alongside the guest TLB arrays.

## Control Flow
Guest TLB lookup starts in `kvmppc_e500_tlb_index()`, which searches TLB0 by set/way and TLB1 by full entry range after checking the cached TLB1 effective-address min/max. Miss handling fills MAS0/MAS1/MAS2/MAS6 via `kvmppc_e500_deliver_tlb_miss()`. Emulated invalidate instructions clear matching guest entries and either flush all host shadow entries or call `inval_gtlbe_on_host()` for targeted teardown. `tlbwe` writes MAS values into the guest TLB array, invalidates any old host mapping, updates TLB1 range caches, and pre-maps host-safe entries through `kvmppc_mmu_map()`.

## State And Persistence
State lives in the vCPU: guest TLB arrays (`gtlb_arch`), TLB geometry (`gtlb_params`, `gtlb_offset`), next-victim state (`gtlb_nv`), TLB1 min/max search cache, private host shadow metadata, and optional userspace-pinned shared TLB pages. `kvm_vcpu_ioctl_config_tlb()` can replace the default kernel-owned arrays with userspace-backed pages via `get_user_pages_fast()` and `vmap()`. `free_gtlb()` flushes host mappings, releases private arrays, marks shared pages dirty, and drops page references.

## Dependencies And Integration Points
Depends on BookE MAS helpers/macros from e500 headers, host-shadow hooks from `e500_mmu_host.h`, KVM SRCU, usercopy, GUP/vmap, and tracepoints from `trace_booke.h`. Integrated with generic register ioctls via `kvmppc_get_one_reg_e500_tlb()`/`kvmppc_set_one_reg_e500_tlb()` and with e500mc setup through `kvmppc_e500_tlb_init()`.

## Risks
The correctness boundary is tight around guest-provided TLB geometry, pinned userspace pages, and TLB1 range caching. Bad geometry is rejected, but shared TLB mappings still rely on userspace arrays remaining valid until reconfiguration or teardown. Host shadow invalidation is deliberately conservative in some cases, which is safe but can be expensive. `tlbwe` pre-mapping is protected by SRCU but still depends on `tlbe_is_host_safe()` and host-shadow code honoring MMU notifier races.

## Test Signals
No direct tests in this subset target e500 TLB behavior. Useful signals are KVM selftests or QEMU BookE/e500 guests exercising `KVM_CAP_SW_TLB`, TLB invalidation instructions, migration/register save-restore of MAS/TLB state, and tracepoints `kvm_booke206_gtlb_write` plus host shadow write/release events.
