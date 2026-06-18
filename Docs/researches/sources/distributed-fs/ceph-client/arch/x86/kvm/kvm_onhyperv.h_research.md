<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.h

### Purpose
`kvm_onhyperv.h` declares KVM-on-Hyper-V optimization hooks and provides config-dependent stubs. It also supplies allocation of the Hyper-V partition assist page required by L0 Hyper-V for direct TLB flush support of nested guests.

### Important APIs, Types, And Functions
When `CONFIG_HYPERV` is enabled, it declares `hv_flush_remote_tlbs_range()`, `hv_flush_remote_tlbs()`, and `hv_track_root_tdp()`, and defines `hv_get_partition_assist_page()`. The assist-page helper lazily allocates one zeroed page in `vcpu->kvm->arch.hv_pa_pg` and returns its physical address, or `INVALID_PAGE` on allocation failure. Without Hyper-V support, `hv_flush_remote_tlbs()` returns `-EOPNOTSUPP` and `hv_track_root_tdp()` is a no-op.

### Control Flow
The only inline control flow is lazy allocation of the shared partition assist page. The helper intentionally allocates one page for the VM, not per vCPU, because KVM does not currently use the page contents but must provide it to satisfy Hyper-V TLFS requirements.

### State, Persistence, And Dependencies
Persistent state is `kvm->arch.hv_pa_pg`, which remains allocated for the VM lifetime. Dependencies include `CONFIG_HYPERV`, KVM vCPU/KVM structures, page allocation, physical address conversion, and `INVALID_PAGE`.

### Integration Points
Nested virtualization setup uses the assist-page helper when exposing Hyper-V direct TLB flush support. KVM MMU code and x86 ops use the flush declarations when replacing standard remote TLB flushes with Hyper-V hypercalls.

### Risks
Allocation failure disables the assist page by returning `INVALID_PAGE`, so callers must handle that path. Sharing one page is intentional but relies on the current contract that KVM does not store per-vCPU data there. Missing stubs for range flush in the non-Hyper-V branch would need care if callers are added outside config guards.

### Test Signals
Build with and without `CONFIG_HYPERV`, test assist-page lazy allocation and reuse across vCPUs, verify failure handling under allocation fault injection, and exercise nested Hyper-V direct TLB flush setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.h -->
