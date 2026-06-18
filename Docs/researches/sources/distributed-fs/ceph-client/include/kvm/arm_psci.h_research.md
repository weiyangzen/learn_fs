<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_psci.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_psci.h

## Purpose
`arm_psci.h` declares ARM KVM's PSCI version constants and PSCI call entry point.

## Important APIs, types, and functions
The header maps KVM PSCI version constants from `PSCI_VERSION()` for versions 0.1 through 1.3 and defines `KVM_ARM_PSCI_LATEST`. `kvm_psci_version()` selects the guest-visible version for a VCPU. `kvm_psci_call()` handles trapped PSCI calls.

## Control flow
`kvm_psci_version()` returns PSCI 0.1 unless the VCPU has `KVM_ARM_VCPU_PSCI_0_2`; for v0.2-capable VCPUs, it returns a userspace-configured VM PSCI version if present, otherwise the latest supported version. The call handler is implemented elsewhere and uses this version decision when emulating firmware functions.

## State and persistence behavior
PSCI version state is VM-scoped through `vcpu->kvm->arch.psci_version`, with VCPU feature flags controlling the legacy v0.1 path. The version is migration/user-configuration relevant.

## Dependencies and integration points
The header depends on KVM host structures and UAPI PSCI definitions. It integrates with SMCCC/hypercall dispatch, guest CPU on/off/reset behavior, and userspace VM configuration.

## Risks and test signals
Risks include exposing a newer PSCI version than userspace intended, mishandling legacy v0.1 guests, and migration incompatibility if configured version is lost. Test signals include PSCI feature/version guest tests, CPU hotplug/reset tests, and migration of `arch.psci_version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_psci.h -->
