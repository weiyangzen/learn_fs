# sources/distributed-fs/ceph-client/arch/arm64/kvm/hypercalls.c

## Purpose
This file implements ARM64 KVM handling for SMCCC/PSCI-facing hypercalls and firmware pseudo-registers. It exposes architecture workarounds, PV time, stolen time, TRNG, KVM vendor hypervisor features, PTP time, userspace filtering/forwarding, and firmware register get/set ioctls.

## Important APIs, Types, and Functions
- `kvm_smccc_call_handler()` is the main HVC/SMC dispatch path.
- `kvm_arm_init_hypercalls()` and `kvm_arm_teardown_hypercalls()` initialize and destroy SMCCC feature/filter state.
- Firmware-register APIs include `kvm_arm_get_fw_num_regs()`, `kvm_arm_copy_fw_reg_indices()`, `kvm_arm_get_fw_reg()`, and `kvm_arm_set_fw_reg()`.
- SMCCC filter APIs include `kvm_vm_smccc_has_attr()`, `kvm_vm_smccc_set_attr()`, `kvm_smccc_set_filter()`, `kvm_smccc_filter_get_action()`, and `kvm_smccc_get_action()`.
- `kvm_ptp_get_time()` implements KVM vendor PTP using synchronized system time snapshots.

## Control Flow
The call handler obtains the SMCCC function ID, consults the filter and feature bitmaps, denies unsupported calls, forwards configured calls to userspace by filling `KVM_EXIT_HYPERCALL`, or handles the call in-kernel. Architecture calls report SMCCC version and Spectre workaround status. PV time calls report features or stolen-time GPA. Vendor calls report KVM UID, feature bitmaps, and PTP time. TRNG calls delegate to `kvm_trng_call()`, and unknown/default calls fall through to PSCI.

Firmware register get/set paths expose PSCI version, workaround levels, and feature bitmaps. Setters validate register size, userspace values, kernel mitigation capability, whether PSCI 0.2 was requested for the vCPU, unsupported feature bits, and whether the VM has already run. SMCCC filters are stored in a maple tree and reserve architecture ranges so userspace cannot misrepresent mitigation status.

## State and Persistence
State lives under `kvm->arch.smccc_feat` feature bitmaps, `kvm->arch.smccc_filter`, and `kvm->arch.psci_version`. Values are VM-wide and mostly immutable after first run. Hypercall return values are placed in guest registers; userspace exits are represented in `struct kvm_run`.

## Dependencies and Integration Points
It depends on ARM SMCCC constants, PSCI helpers, TRNG helpers, KVM PV time/stolen-time code, Spectre mitigation state queries, maple tree APIs, userspace copy helpers, and KVM one-reg/device-attr ioctls. It is reached from the KVM exception handling path for HVC/SMC traps.

## Risks and Edge Cases
Risks include allowing userspace to spoof architecture mitigation calls, changing feature bitmaps after a VM has run, mishandling PSCI 0.1 vs 0.2 compatibility, returning inconsistent PTP cycles if the clocksource is not the arch counter, and filter overlap/overflow mistakes. The reserved architecture filter ranges and config lock reduce these risks.

## Test Signals
Use KVM selftests for firmware registers, SMCCC filter insertion, PSCI version configuration, TRNG exposure, PV time/stolen time, vendor UID/features, PTP calls, and userspace-forwarded hypercalls. Negative tests should cover unsupported feature bits, late mutation after first run, invalid filter ranges, and disallowed workaround levels.
