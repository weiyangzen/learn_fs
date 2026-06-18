<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.c

### Purpose
`kvm_onhyperv.c` implements optimizations for KVM running as an L1 hypervisor on a Hyper-V L0 host. Its main function is to use Hyper-V guest-mapping flush hypercalls for KVM remote TLB flushes and to track common root TDP values for faster flushes.

### Important APIs, Types, And Functions
Exported internal APIs are `hv_flush_remote_tlbs_range()`, `hv_flush_remote_tlbs()`, and `hv_track_root_tdp()`. Internal helpers include `kvm_fill_hv_flush_list_func()`, `hv_remote_flush_root_tdp()`, and `__hv_flush_remote_tlbs_range()`. `struct kvm_hv_tlb_range` carries start GFN and page count for range flushes.

### Control Flow
Range and full flush wrappers call `__hv_flush_remote_tlbs_range()` with or without a range descriptor. The common helper locks `hv_root_tdp_lock`. If no single valid root is cached, it iterates vCPUs, flushes each unique valid `vcpu->arch.hv_root_tdp`, and detects whether all vCPUs converged on one root for future fast flushes. If a common root is cached, it flushes that root directly. Range flushes build Hyper-V flush lists through `hyperv_fill_flush_guest_mapping_list()`, while full flushes use `hyperv_flush_guest_mapping()`. `hv_track_root_tdp()` updates per-vCPU and common-root tracking when KVM's active remote flush op is the Hyper-V implementation.

### State, Persistence, And Dependencies
State lives in `kvm->arch.hv_root_tdp`, `kvm->arch.hv_root_tdp_lock`, and each `vcpu->arch.hv_root_tdp`. Dependencies include host Hyper-V APIs from `asm/mshyperv.h`, KVM vCPU iteration, root HPA validity checks, and `kvm_x86_ops.flush_remote_tlbs` dispatch.

### Integration Points
This file plugs into KVM's remote TLB flush hooks when KVM detects it is running on Hyper-V. MMU/root changes call `hv_track_root_tdp()` so future flushes can target the right L0 guest mapping root.

### Risks
Incorrect common-root caching can miss a root and leave stale L0 mappings. The code deliberately stops early on some error/multiple-root cases, so return handling must preserve conservative flushing behavior. Range list construction must match Hyper-V's expected guest mapping format.

### Test Signals
Test KVM-on-Hyper-V with single and multiple vCPUs, root convergence and divergence, full and range remote TLB flushes, invalid root transitions, failures from Hyper-V flush hypercalls, and switching away from the Hyper-V flush op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.c -->
