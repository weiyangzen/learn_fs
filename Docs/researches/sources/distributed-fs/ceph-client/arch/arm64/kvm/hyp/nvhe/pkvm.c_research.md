<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/pkvm.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/pkvm.c

## Purpose
`pkvm.c` manages protected-KVM VM and vCPU metadata inside the hypervisor. It allocates and publishes VM handles, pins host-visible KVM/vCPU/SVE state, initializes protected feature and trap state, maps host-donated metadata into hyp, tears down dying VMs, and handles protected guest hypercalls for memory sharing.

## Important APIs, Types, and Functions
Global exported state includes `__icache_flags`, `kvm_arm_vmid_bits`, and `kvm_host_sve_max_vl`. `loaded_hyp_vcpu` tracks the current vCPU per physical CPU. VM-table APIs include `pkvm_hyp_vm_table_init()`, `__pkvm_reserve_vm()`, `__pkvm_unreserve_vm()`, `get_vm_by_handle()`, `get_pkvm_hyp_vm()`, and `get_np_pkvm_hyp_vm()`. `pkvm_load_hyp_vcpu()` / `pkvm_put_hyp_vcpu()` enforce single-load and VM refcounts. `__pkvm_init_vm()` and `__pkvm_init_vcpu()` consume host-donated pages for hyp VM/vCPU structures and stage-2 PGD. `__pkvm_start_teardown_vm()`, `__pkvm_finalize_teardown_vm()`, and `__pkvm_reclaim_dying_guest_page()` reclaim resources. `kvm_handle_pvm_hvc64()` handles protected guest KVM vendor hypercalls.

## Control Flow, State, and Persistence
The VM table is hyp-owned persistent state protected by `vm_table_lock`; handles start at `HANDLE_OFFSET`, and entries move from empty to `RESERVED_ENTRY` to initialized VM pointer to removed. VM and vCPU metadata pages are transferred from host to hyp via `__pkvm_host_donate_hyp()`, zeroed on map, and returned via memcaches on teardown. Protected VMs receive restricted features and trap settings; non-protected VMs copy host-selected features. vCPU registration uses release-store publication, and load uses acquire-load plus a per-vCPU loaded pointer to prevent concurrent execution.

## Dependencies and Integration Points
It depends on `mem_protect.c` for ownership, `mm.c` for donated-memory mapping, `sys_regs.c` for protected ID-register views, generic KVM ARM HCR/MDCR/SVE helpers, host hypercall wrappers in `hyp-main.c`, and guest exit handling in `switch.c`.

## Risks and Test Signals
Risks include VM-handle lifetime races, leaked pinned host pages on initialization failure, feature exposure mistakes for protected VMs, SVE state size mismatch, teardown while a vCPU is loaded, and guest memshare paths that deliberately convert missing mappings into host-visible data aborts. Test signals include reserve/unreserve/init/fail paths, concurrent vCPU load rejection, protected/non-protected feature masks, SVE enabled/disabled setup, full teardown memcache accounting, guest MEM_SHARE/MEM_UNSHARE HVCs, and dying-VM page reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/pkvm.c -->
