# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_vmcall_test.c

## Purpose
`xen_vmcall_test.c` is a KVM selftest for userspace hypercall interception. It verifies that a guest `vmcall` and a guest call through the configured Xen hypercall page produce `KVM_EXIT_XEN` exits with the expected register payload, and that a Hyper-V hypercall page can still be used for a normal Hyper-V hypercall result after Xen interception is enabled.

## Important APIs, Types, And Functions
The test uses the KVM selftest helpers `vm_create_with_one_vcpu()`, `vcpu_set_hv_cpuid()`, `vm_ioctl()`, `vm_userspace_mem_region_add()`, `virt_map()`, `vcpu_run()`, `get_ucall()`, and `kvm_vm_free()`. Kernel-facing APIs include `KVM_CAP_XEN_HVM`, `KVM_XEN_HVM_CONFIG`, `struct kvm_xen_hvm_config`, `KVM_XEN_HVM_CONFIG_INTERCEPT_HCALL`, and the `KVM_EXIT_XEN`/`KVM_EXIT_XEN_HCALL` run-state payload. The guest writes `XEN_HYPERCALL_MSR`, `HV_GUEST_OS_ID_MSR`, and `HV_HYPERCALL_MSR`, and invokes hypercalls with inline assembly.

## Control Flow
`main()` requires Xen HVM hypercall interception support, creates one guest vCPU, exposes Hyper-V CPUID leaves, configures the Xen hypercall MSR, and maps two pages at `HCALL_REGION_GPA`: one for Xen and one for Hyper-V. `guest_code()` first executes `vmcall` directly and expects userspace to return `RETVALUE` in `rax`. It then writes the Xen hypercall page MSR and the Hyper-V guest/hypercall MSRs, calls a Xen hypercall slot based on `INPUTVALUE`, and finally calls the Hyper-V page with a deliberately misaligned input GPA expecting `HV_STATUS_INVALID_ALIGNMENT`. The host loop handles each `KVM_EXIT_XEN`, validates CPL, long mode, input number, and six arguments, writes `run->xen.u.hcall.result`, and otherwise handles guest ucall completion or assertion failures.

## State, Persistence, And Dependencies
All state is transient VM state: guest registers, MSRs, the mapped hypercall pages, and the current `kvm_run` exit payload. No persistent files are written. The test depends on x86 KVM selftest infrastructure, host kernel Xen HVM interception support, Hyper-V CPUID setup helpers, and a system that allows `/dev/kvm` test execution.

## Integration Points
This file integrates the Xen and Hyper-V emulation surfaces in one VM. It exercises the host userspace exit ABI for Xen hypercalls while relying on KVM's Hyper-V hypercall implementation for the invalid-alignment return. It is built and run by the KVM selftests framework under `tools/testing/selftests/kvm/x86`.

## Risks
The test is architecture- and feature-specific and skips unless `KVM_CAP_XEN_HVM` includes `KVM_XEN_HVM_CONFIG_INTERCEPT_HCALL`. Inline assembly register constraints are central to the test; compiler or ABI mistakes could make a failure look like a KVM bug. The test assumes the two-page GPA mapping is free and identity-mapped for guest calls. It validates only the configured simple hypercall payload and one Hyper-V error path, not broader hypercall page behavior.

## Test Signals
Strong success signals are two validated `KVM_EXIT_XEN` exits, guest assertions that both Xen paths return `RETVALUE`, the Hyper-V invalid-alignment status, and clean `UCALL_DONE`. Failure signals are a missing capability, wrong exit reason, mismatched hypercall fields, guest assertion aborts, or inability to configure/map the VM.
