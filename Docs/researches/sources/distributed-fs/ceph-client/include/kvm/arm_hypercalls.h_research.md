<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_hypercalls.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_hypercalls.h

## Purpose
`arm_hypercalls.h` declares ARM KVM handling for SMCCC firmware/hypervisor calls and exposes helpers for decoding call registers and managing firmware register attributes.

## Important APIs, types, and functions
`kvm_smccc_call_handler()` is the main call dispatch entry. Inline helpers `smccc_get_function()`, `smccc_get_arg1()`, `smccc_get_arg2()`, `smccc_get_arg3()`, and `smccc_set_retval()` read/write guest registers x0-x3 through KVM emulation helpers. Lifecycle and userspace APIs include `kvm_arm_init_hypercalls()`, `kvm_arm_teardown_hypercalls()`, firmware one-reg enumeration/copy/get/set functions, and VM SMCCC device attribute set/has helpers.

## Control flow
When a guest traps an SMCCC call, the handler reads x0 for the function ID and x1-x3 for arguments, dispatches internally, and writes return values back to x0-x3. VM initialization configures available hypercall features and teardown releases any VM-owned state.

## State and persistence behavior
State is VM-scoped hypercall capability/configuration maintained in `struct kvm`; this header only declares access. Firmware register state is exposed through the KVM one-reg/userspace attribute interfaces for migration and configuration.

## Dependencies and integration points
The file depends on `asm/kvm_emulate.h`, `struct kvm_vcpu`, userspace pointers, `struct kvm_one_reg`, and KVM device attributes. It integrates with PSCI, SMCCC feature discovery, guest firmware ABI emulation, and migration tooling.

## Risks and test signals
Risks include clobbering the wrong guest registers, misreporting SMCCC feature availability, incomplete one-reg migration state, and ABI mismatches between userspace and KVM. Test signals include SMCCC/PSCI guest tests, KVM one-reg enumeration round trips, migration compatibility tests, and negative attribute validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_hypercalls.h -->
