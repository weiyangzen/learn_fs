# sources/distributed-fs/ceph-client/include/linux/kvm_para.h

Purpose: provides the generic kernel include wrapper for KVM paravirtual feature and hint discovery.

Important APIs and types: `kvm_para_has_feature()` tests `kvm_arch_para_features()` and `kvm_para_has_hint()` tests `kvm_arch_para_hints()` against a feature bit from the UAPI paravirtualization header.

Control flow: kernel subsystems or arch code call these helpers before enabling KVM paravirtual behavior; the actual feature bitmap source is architecture-specific.

State and persistence: no state is stored here. The helpers are pure bit tests over arch-provided runtime feature masks.

Dependencies and integration points: depends on `<uapi/linux/kvm_para.h>` and arch implementations of `kvm_arch_para_features()` and `kvm_arch_para_hints()`. It is a small integration point between generic code and paravirt hypervisor feature discovery.

Risks and test signals: risk is mostly arch drift or missing feature definitions causing silent false positives/negatives. Test with paravirt feature selftests and compile coverage for architectures implementing or omitting KVM paravirt hooks.
