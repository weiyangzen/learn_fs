# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/common.h

## Purpose
`vmx/common.h` contains small pieces shared by Intel VMX and TDX-backed execution paths: VM-exit reason decoding, the common `vcpu_vt` state embedded in both VMX and TDX vCPU structs, TDX type predicates, EPT-violation translation, and posted-interrupt delivery helpers.

## Important APIs, Types, And Functions
`union vmx_exit_reason` exposes the raw 32-bit VM-exit reason and named bits including `basic`, bus-lock detection, enclave mode, SMI indicators, and failed VM-entry. `struct vcpu_vt` stores the posted-interrupt descriptor, PI wakeup list node, last exit reason, qualification, interrupt info, guest-state-loaded flag, emulation-required flag, and host kernel GS base on x86-64. With `CONFIG_KVM_INTEL_TDX`, `is_td()` and `is_td_vcpu()` classify TD VMs; otherwise they compile to false.

`vt_is_tdx_private_gpa()` interprets a GPA as private for TDX using KVM's direct/shared address mask. `__vmx_handle_ept_violation()` converts EPT violation qualification bits into KVM page-fault error flags, including read/write/fetch, present/protection, guest page versus final translation, and private access, then calls `kvm_mmu_page_fault()`. `kvm_vcpu_trigger_posted_interrupt()` chooses between sending a posted-interrupt notification IPI to an in-guest vCPU or waking a non-running/blocking vCPU. `__vmx_deliver_posted_interrupt()` sets the PIR bit, sets PID.ON if needed, and triggers notification.

## Control Flow
EPT violation handling is a straight qualification-to-error-code translation followed by MMU fault dispatch. Posted interrupt delivery is more stateful: first set the target vector in PIR; if it was already pending, return. Then set PID.ON; if another notification is already in flight, return. Otherwise, if the vCPU is in guest mode and not the current running vCPU, send the posted-interrupt IPI; if it is not in guest mode, wake it so normal vCPU entry can sync PIR into vIRR.

## State And Persistence
`vcpu_vt` persists per-vCPU posted-interrupt state and the latest VM-exit metadata. Posted interrupts modify the `pi_desc` bitmap and ON bit, which are consumed by APIC/vCPU entry paths. `guest_state_loaded` tracks whether hardware currently contains guest or host state. EPT handling does not persist local state but may update MMU state through `kvm_mmu_page_fault()`.

## Dependencies And Integration Points
The file depends on KVM host definitions, posted interrupt primitives, and VMX MMU constants. It integrates with VMX/TDX vCPU structs via common offset requirements, APIC posted-interrupt code, vCPU wake/block logic, EPT MMU fault handling, and NMI handling through the external `vmx_handle_nmi()` declaration.

## Risks And Edge Cases
Posted-interrupt ordering is concurrency-sensitive. The barrier implied by `pi_test_and_set_on()` must pair with mode transitions in `vcpu_enter_guest()` so a missed IPI still leaves a visible pending interrupt. Sending an IPI to the currently running vCPU is intentionally avoided because the fastpath will sync PIR before reentry. For TDX, classifying private GPAs incorrectly would produce wrong MMU error codes and could confuse shared/private memory handling. EPT qualification bit mapping must remain aligned with KVM page-fault semantics.

## Test Signals
Coverage should include EPT violation tests for read, write, execute, permission, translated-GVA, and private/shared GPA cases; APICv posted-interrupt delivery to running, non-running, blocking, and current vCPU cases; SMP and !SMP builds; TDX private memory fault tests; and stress tests for interrupt races around vCPU mode transitions.
