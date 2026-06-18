# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/mce.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/mce.h

Purpose: x86 Machine Check Exception helper declarations/constants for KVM selftests.

Important APIs/types/functions: includes MCE-related MSR/register constants, helper declarations for injecting or checking machine-check state, and integration points for guest exception handlers.

Control flow and state: tests configure MCE capability/state through KVM vCPU ioctls or MSRs, inject machine-check conditions, run the vCPU, and validate guest exception or KVM exit behavior. Persistent state is vCPU MCE bank/register state.

Dependencies and integration: depends on `x86/processor.h` MSR and exception helpers and common KVM utility ioctls.

Risks: MCE behavior is CPU-model and KVM-capability dependent. Tests must gate on MCE support and avoid assuming host-specific bank counts or status bits.

Test signals: x86 MCE selftests validate injection, state get/set, guest handler dispatch, and expected KVM error handling.
