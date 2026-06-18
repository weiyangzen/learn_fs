# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_cpuid.c

Purpose: Validates `KVM_GET_SUPPORTED_HV_CPUID` behavior and the Hyper-V CPUID leaves exposed to a vCPU, including eVMCS-related feature expectations and buffer sizing errors.

Important APIs/types/functions: `guest_code()` is a minimal guest body; `test_hv_cpuid()` fetches and inspects Hyper-V CPUID entries; `test_hv_cpuid_e2big()` verifies the `E2BIG` path for undersized structures. It uses `vcpu_set_hv_cpuid()`, `kvm_get_supported_hv_cpuid()`, VMX/eVMCS feature checks, and KVM CPUID ioctls.

Control flow: The host creates a VM/vCPU, queries supported Hyper-V CPUID, optionally enables eVMCS-related support, and validates advertised leaves and feature bits. It also intentionally supplies a too-small CPUID buffer to ensure KVM reports the required size.

State and persistence behavior: CPUID state is vCPU-local and configuration-only. No external state is persisted.

Dependencies and integration points: Depends on `KVM_CAP_HYPERV_CPUID`, Hyper-V CPUID leaf definitions, and VMX/eVMCS capability reporting. It is an ABI check for VMMs that query Hyper-V features.

Risks and maintenance notes: Hyper-V feature expansion requires updating expected leaves and eVMCS bit logic. The `E2BIG` path is sensitive to structure sizing and kernel ioctl conventions.

Test signals: Passing means Hyper-V CPUID enumeration is complete, correctly sized, and consistent with eVMCS availability. Failures point to CPUID ABI or feature advertisement regressions.
