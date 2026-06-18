# sources/distributed-fs/ceph-client/arch/s390/include/asm/machine.h

Purpose: This header defines runtime machine-feature bits and efficient predicates for platform capabilities such as relocated lowcore, PCI MIO, SCC, guest TLB support, transactional execution, ESOP, DIAG9C, VM, KVM, and LPAR.

Important APIs/types/functions: `MFEATURE_*` constants, global `machine_features`, bit set/clear/test helpers, alternative-backed `__test_machine_feature_constant()`, generated `machine_has_*()` predicates, and aliases `machine_is_vm/kvm/lpar` are the main APIs.

Control flow: Early machine detection sets feature bits, alternatives can patch constant feature tests, and later code uses predicates to select platform-specific paths.

State and persistence: Persistent state is the global machine feature bitmap and any alternative-patched instruction sites derived from it.

Dependencies and integration points: It depends on Linux bitops and s390 alternative patching, integrating boot environment detection with lowcore, PCI, virtualization, and CPU feature consumers.

Risks and test signals: Feature misdetection sends code down unsupported privileged paths. Tests should cover boot under LPAR, z/VM, KVM, bare-metal-like environments, and alternatives using each feature bit.
