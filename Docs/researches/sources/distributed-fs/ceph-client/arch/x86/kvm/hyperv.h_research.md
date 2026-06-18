<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.h

### Purpose
`hyperv.h` is the internal interface for KVM's x86 Hyper-V emulation. It exposes TLFS-related constants, accessor helpers for VM/vCPU Hyper-V state, declarations for Hyper-V MSR, SynIC, stimer, CPUID, eventfd, TSC page, and nested TLB-flush services, plus no-op stubs when `CONFIG_KVM_HYPERV` is disabled.

### Important APIs, Types, And Functions
The header defines the Hyper-V CPUID signature, synthetic debugger CPUID leaves/MSRs, and debugger capability bits. Inline accessors include `to_kvm_hv()`, `to_hv_vcpu()`, `to_hv_synic()`, `hv_synic_to_vcpu()`, `to_hv_syndbg()`, `kvm_hv_get_vpindex()`, `to_hv_stimer()`, and `hv_stimer_to_vcpu()`. It declares `kvm_hv_set_msr_common()`, `kvm_hv_get_msr_common()`, `kvm_hv_hypercall()`, `kvm_hv_synic_set_irq()`, `kvm_hv_synic_send_eoi()`, `kvm_hv_process_stimers()`, `kvm_hv_setup_tsc_page()`, `kvm_hv_set_cpuid()`, `kvm_get_hv_cpuid()`, and `kvm_hv_vcpu_flush_tlb()`.

### Control Flow
Most helpers are simple accessors or feature gates. `kvm_hv_hypercall_enabled()` requires both vCPU Hyper-V enablement and a nonzero guest OS ID. `kvm_hv_synic_has_vector()` and `kvm_hv_synic_auto_eoi_set()` query bitmaps maintained by `hyperv.c`. `kvm_hv_invtsc_suppressed()` hides invariant TSC when the Hyper-V invariant-TSC control is exposed but not enabled. TLB helpers select the L1 or L2 flush FIFO based on guest mode, purge pending flushes on request consumption, detect Hyper-V TLB flush hypercalls from guest registers, and request FIFO re-checking on nested transitions.

### State, Persistence, And Dependencies
The header does not own storage, but its helpers directly expose fields in `kvm->arch.hyperv` and `vcpu->arch.hyperv`. It depends on `linux/kvm_host.h`, KVM x86 state from `x86.h`, Hyper-V TLFS constants from included kernel headers, kfifo-backed TLB flush FIFOs, and the vCPU request mechanism.

### Integration Points
Consumers include x86 MSR/hypercall handling, APIC EOI paths, CPUID setup, nested VMX/SVM paths, TSC page updates, IRQ routing, and timer processing. The stubs allow callers outside `CONFIG_KVM_HYPERV` blocks to compile while making Hyper-V features appear absent.

### Risks
The inline helpers assume `vcpu->arch.hyperv` is allocated before dereferencing except where explicitly guarded. Misusing `to_hv_synic()` or `to_hv_stimer()` before `kvm_hv_vcpu_init()` would fault. The invariant-TSC suppression logic must stay aligned with CPUID exposure, and TLB FIFO selection must match L1/L2 transitions or stale flush requests can be lost.

### Test Signals
Build both with and without `CONFIG_KVM_HYPERV`. Exercise Hyper-V disabled guests, CPUID enforcement, invariant TSC control, SynIC vector/AutoEOI queries, nested TLB flush request purging, and callers that use the no-op stubs under non-Hyper-V configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.h -->
