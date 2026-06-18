# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_guest.h

Purpose: exposes a low-overhead runtime predicate for whether the kernel is running as a KVM guest.

Important APIs/types/functions: when pSeries or KVM guest support is built, it declares `DECLARE_STATIC_KEY_FALSE(kvm_guest)`, `is_kvm_guest()`, and `check_kvm_guest()`. Otherwise, `is_kvm_guest()` returns false and `check_kvm_guest()` returns zero.

Control flow: early initialization calls `check_kvm_guest()` to detect KVM and enable the static key. Runtime users call `is_kvm_guest()`, which becomes a static-branch test in enabled configurations and a constant false in disabled ones.

State and persistence: the `kvm_guest` static key persists for the boot lifetime once detection completes. Disabled builds have no stored state.

Dependencies and integration points: depends on Linux jump labels and is included by `kvm_para.h` and paravirtual feature code.

Risks: calling before detection completes can report false. Static-key state must reflect the actual hypervisor to avoid issuing KVM-specific hypercalls on non-KVM systems.

Test signals: boot pSeries under KVM and non-KVM hypervisors, verify static key transitions, and check that `kvm_para_available()` only returns true under KVM guest conditions.
