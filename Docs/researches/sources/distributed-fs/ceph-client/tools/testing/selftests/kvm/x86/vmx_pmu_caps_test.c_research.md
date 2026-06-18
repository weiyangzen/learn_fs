<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_pmu_caps_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_pmu_caps_test.c

## Purpose
This test validates virtualization of `MSR_IA32_PERF_CAPABILITIES` for VMX/vPMU guests. It checks guest write rejection, host-controlled immutability after run, fungible versus immutable feature bits, LBR behavior, and PDCM/PMU CPUID dependencies.

## Important APIs, Types, and Functions
Key data is `union perf_capabilities host_cap`, `immutable_caps`, and `format_caps`. Important tests are `guest_wrmsr_perf_capabilities`, `basic_perf_capabilities`, `fungible_perf_capabilities`, `immutable_perf_capabilities`, `lbr_perf_capabilities`, and `perf_capabilities_unsupported`. It uses `kvm_get_feature_msr()`, `vcpu_set_msr()`, `_vcpu_set_msr()`, `vcpu_clear_cpuid_feature()`, `vcpu_clear_cpuid_entry()`, `MSR_LBR_TOS`, and guest `wrmsr_safe()`.

## Control Flow, State, and Persistence
`main()` requires enabled PMU, PDCM, and nonzero PMU version, then captures host PERF_CAPABILITIES. Guest code attempts to write the current value, zero, and every single-bit variation and expects #GP. Host tests set supported values before first run, verify values remain unchanged after guest execution, reject changes after KVM_RUN, allow fungible features within host support, reject immutable/reserved LBR and PEBS formats, and verify disabling PMU/PDCM clears or rejects dependent state. State is vCPU PERF_CAPABILITIES MSR, CPUID PMU/PDCM model, and LBR MSRs.

## Dependencies and Integration Points
It integrates with vPMU exposure, VMX performance capability MSR virtualization, CPUID feature filtering, LBR MSR availability, and the KVM one-vCPU harness.

## Risks and Test Signals
Risks include allowing guest writes, accepting impossible LBR/PEBS formats, failing to clear capabilities without PDCM, or allowing LBR writes after vPMU removal. Signals are guest #GPs, exact host MSR readback, and expected `_vcpu_set_msr()` failures for invalid capability values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_pmu_caps_test.c -->
