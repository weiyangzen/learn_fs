<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apic_access_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apic_access_test.c

## Purpose
This nested VMX test validates APIC-access address handling. It verifies that L2 can launch with a memory-backed APIC-access page and that using a valid but unbacked L1 physical address produces a KVM internal emulation error rather than unsafe behavior.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code()`, `prepare_virtualize_apic_accesses()`, `prepare_vmcs()`, `vmlaunch()`, and `vmresume()`. It writes VMCS fields `CPU_BASED_VM_EXEC_CONTROL`, `SECONDARY_VM_EXEC_CONTROL`, and `APIC_ACCESS_ADDR`.

## Control Flow, State, and Persistence
L1 prepares VMX, enables secondary controls and APIC-access virtualization, sets `APIC_ACCESS_ADDR` to the allocated page, syncs to host, launches L2, and observes VMCALL. It then changes `APIC_ACCESS_ADDR` to a high unbacked GPA, syncs again, and resumes L2. The host treats the second sync as a predictor and expects the following `KVM_RUN` to exit with `KVM_EXIT_INTERNAL_ERROR` and `KVM_INTERNAL_ERROR_EMULATION`. State is nested VMCS APIC-access address and VM memory backing.

## Dependencies and Integration Points
The file requires VMX support and integrates with nested VMX APIC-access virtualization, selftests VMX page allocation, and KVM internal-error reporting.

## Risks and Test Signals
Risks include KVM dereferencing unbacked APIC-access memory, returning the wrong exit reason, or failing valid launch. Signals are a successful first L2 VMCALL and an internal emulation error for the unbacked APIC-access address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apic_access_test.c -->
