# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_types.h

Purpose: selects module subcomponent names for split PowerPC Book3S KVM module builds.

Important APIs/types/functions: `KVM_SUB_MODULES` is defined as `kvm-pr,kvm-hv`, `kvm-pr`, or `kvm-hv` depending on whether `CONFIG_KVM_BOOK3S_64_PR` and/or `CONFIG_KVM_BOOK3S_64_HV` are modular. Otherwise it is undefined.

Control flow: no runtime flow; build and module metadata consume the macro.

State and persistence: no runtime state.

Dependencies and integration points: depends on Kconfig `IS_MODULE()` and is included by generic KVM type/module plumbing.

Risks: incorrect module naming breaks dependency/autoload handling for split PR/HV modules.

Test signals: build all combinations of built-in and modular Book3S PR/HV KVM, inspect generated module dependencies, and verify module autoload loads the expected submodules.
