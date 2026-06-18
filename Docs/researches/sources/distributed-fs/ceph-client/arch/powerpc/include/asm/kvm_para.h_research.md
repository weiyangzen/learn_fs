# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_para.h

Purpose: implements PowerPC KVM paravirtual feature discovery and availability checks.

Important APIs/types/functions: `kvm_para_available()` checks `CONFIG_KVM_GUEST` and `is_kvm_guest()`. `kvm_arch_para_features()` issues `epapr_hypercall0_1(KVM_HCALL_TOKEN(KVM_HC_FEATURES), &r)` and returns the feature bitmap or zero. `kvm_arch_para_hints()` and `kvm_check_and_clear_guest_paused()` currently return zero/false.

Control flow: callers first test availability, then query KVM features through the ePAPR hypercall. Hypercall failure collapses to no features.

State and persistence: this header stores no state; availability comes from the static key in `kvm_guest.h`, and features are fetched on demand.

Dependencies and integration points: includes `asm/kvm_guest.h` and UAPI KVM para definitions. It integrates guest kernel paravirt setup with hypervisor feature tokens.

Risks: feature queries must not run outside KVM guest mode. The no-hints and no-paused-state behavior is guest ABI behavior for this architecture.

Test signals: boot PowerPC KVM guests with `CONFIG_KVM_GUEST`, validate feature bitmap hypercalls, ensure non-KVM boots see zero features, and check callers handle zero hints.
