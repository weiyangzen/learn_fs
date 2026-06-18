# sources/distributed-fs/ceph-client/arch/arm64/kvm/psci.c

Purpose: emulates the ARM Power State Coordination Interface for KVM guests. It handles vCPU suspend/off/on, affinity queries, PSCI feature discovery, system shutdown/reset/suspend exits to userspace, PSCI version dispatch from 0.1 through 1.3, and SMCCC register return conventions.

Important APIs and functions: `kvm_psci_call()` is the exported dispatcher. Key helpers include `kvm_psci_vcpu_suspend()`, `kvm_psci_vcpu_on()`, `kvm_psci_vcpu_affinity_info()`, `kvm_prepare_system_event()`, `kvm_psci_system_off()`, `kvm_psci_system_off2()`, `kvm_psci_system_reset()`, `kvm_psci_system_reset2()`, `kvm_psci_system_suspend()`, `kvm_psci_narrow_to_32bit()`, `kvm_psci_check_allowed_function()`, `kvm_psci_0_1_call()`, `kvm_psci_0_2_call()`, and `kvm_psci_1_x_call()`.

Control flow: `kvm_psci_call()` first rejects 64-bit PSCI function IDs from 32-bit vCPUs, then dispatches based on the VM-configured PSCI version. PSCI 0.1 supports only legacy CPU off/on. PSCI 0.2 adds version, suspend, affinity info, migrate info type, system off, and system reset. PSCI 1.x layers feature discovery, optional system suspend, reset2, and off2 based on the minor version and VM flags. Most calls write return values through `smccc_set_retval()` and return 1 to resume the guest. System off/reset/off2 and suspend prepare `KVM_EXIT_SYSTEM_EVENT` and return 0 so userspace handles the event.

CPU_ON resolves the target MPIDR, verifies the vCPU exists and is stopped, stores reset PC, endianness, and x0/r0 in `reset_state`, sets `reset = true`, issues `KVM_REQ_VCPU_RESET`, uses a write barrier before marking the vCPU runnable, and wakes it. SYSTEM_* events stop all vCPUs, request sleep, populate `run->system_event`, and preload an internal-failure return value for cases where userspace incorrectly resumes the caller.

State and persistence: persistent state touched here includes `vcpu->arch.mp_state`, `mp_state_lock`, `reset_state`, VM PSCI version/config flags, and `kvm_run.system_event`. Suspend is modeled as WFI and does not persist power-down state. CPU_OFF updates the vCPU power state through shared KVM helpers.

Dependencies and integration: depends on SMCCC argument helpers, KVM MP state, vCPU wakeup and reset requests, `kvm_mpidr_to_vcpu()`, ARM PSCI constants, hypercall dispatch, userspace KVM exits, and system suspend enable flags. Reset state written by PSCI is consumed by `reset.c` in `kvm_reset_vcpu()`.

Risks: PSCI is guest ABI. Return-code differences between PSCI 0.1 and newer versions matter, especially CPU_ON already-on handling. System event exits intentionally stop all vCPUs before userspace action; allowing vCPUs to continue can violate PSCI immediacy expectations. 32-bit narrowing must be applied to the right calls before reading affinity/entry parameters. Reset2/off2 feature reporting must track the advertised minor version and validate type arguments.

Test signals: KVM PSCI tests should cover all configured versions, CPU_ON success/already-on/invalid-affinity, 32-bit callers invoking 64-bit functions, AFFINITY_INFO levels, SYSTEM_OFF/RESET/SUSPEND exits, RESET2 warm/vendor ranges, OFF2 hibernate validation, and userspace resuming after a system event.
