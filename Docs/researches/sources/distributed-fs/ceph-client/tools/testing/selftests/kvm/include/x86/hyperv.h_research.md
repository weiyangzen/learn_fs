# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/hyperv.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/hyperv.h

Purpose: x86 Hyper-V enlightenment definitions for KVM selftests. It records Hyper-V CPUID leaves, synthetic MSRs, feature bits, hypercall numbers/status codes, VP assist page layout, and helper APIs for Hyper-V CPUID and test-page setup.

Important APIs/types/functions: `HYPERV_CPUID_*`, `HV_X64_MSR_*`, `HV_*` feature descriptors, `HVCALL_*`, `HV_STATUS_*`, `HV_HYPERCALL_*`, `__hyperv_hypercall`, `hyperv_hypercall`, `hyperv_write_xmm_input`, `HYPERV_LINUX_OS_ID`, `struct hv_nested_enlightenments_control`, `struct hv_vp_assist_page`, `current_vp_assist`, `enable_vp_assist`, `struct hyperv_test_pages`, `vcpu_alloc_hyperv_test_pages`, `kvm_get_supported_hv_cpuid`, `vcpu_get_supported_hv_cpuid`, `vcpu_set_hv_cpuid`, and `kvm_hv_cpu_has`.

Control flow and state: tests configure Hyper-V CPUID/MSRs on a vCPU, optionally allocate VP/partition assist pages and eVMCS storage, issue hypercalls through `vmcall`, and assert status/vector outcomes. State persists in vCPU CPUID, synthetic MSRs, assist-page memory, and nested enlightenment fields.

Dependencies and integration: depends on `x86/processor.h` for CPUID feature descriptors, safe assembly, SSE writes, and guest assertions. It integrates with eVMCS, nested Hyper-V, SynIC, synthetic timer, and hypercall tests.

Risks: Hyper-V ABI fields are dense and version-sensitive. Hypercall helpers clobber registers and rely on exception-fixup machinery. Feature bits must be checked before using optional MSRs/hypercalls.

Test signals: Hyper-V CPUID/MSR tests, hypercall tests, VP assist/eVMCS tests, and synthetic timer/SynIC tests validate this header.
