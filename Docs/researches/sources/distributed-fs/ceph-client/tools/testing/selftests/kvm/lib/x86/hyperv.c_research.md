<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/hyperv.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/hyperv.c

## Purpose
`hyperv.c` provides x86 Hyper-V enlightenment helpers for KVM selftests. It queries supported Hyper-V CPUID leaves, installs merged CPUID into vCPUs, allocates shared Hyper-V test pages, and enables the guest VP assist page.

## Important APIs, Types, and Functions
Key functions are `kvm_get_supported_hv_cpuid()`, `vcpu_set_hv_cpuid()`, `vcpu_get_supported_hv_cpuid()`, `kvm_hv_cpu_has()`, `vcpu_alloc_hyperv_test_pages()`, and `enable_vp_assist()`. The page allocator fills `struct hyperv_test_pages` with guest, host, and GPA addresses for VP assist, partition assist, and enlightened VMCS pages.

## Control Flow
Supported Hyper-V CPUID is cached after `KVM_GET_SUPPORTED_HV_CPUID`. `vcpu_set_hv_cpuid()` merges normal KVM CPUID with Hyper-V leaves while dropping conflicting KVM 0x400000xx leaves, then calls `vcpu_init_cpuid()`. VP assist enabling writes `HV_X64_MSR_VP_ASSIST_PAGE` and updates `current_vp_assist`.

## State and Persistence
Static CPUID caches persist process-wide. Allocated pages live in guest memory for the VM lifetime. `current_vp_assist` is guest-visible state used by VMX/Hyper-V paths.

## Dependencies and Integration Points
The file depends on `processor.h`, `hyperv.h`, KVM ioctls, CPUID helpers, and Hyper-V MSR definitions. It integrates with enlightened VMCS tests, nested VMX paths, and feature probes guarded by `KVM_CAP_SYS_HYPERV_CPUID`.

## Risks and Test Signals
Risks include stale CPUID caching, duplicate or conflicting hypervisor leaves, unsupported KVM caps, and mismatched guest physical addresses for assist pages. Test signals include successful `KVM_GET_SUPPORTED_HV_CPUID`, vCPU CPUID installation, feature checks via `kvm_hv_cpu_has()`, and Hyper-V tests observing valid assist page state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/hyperv.c -->
