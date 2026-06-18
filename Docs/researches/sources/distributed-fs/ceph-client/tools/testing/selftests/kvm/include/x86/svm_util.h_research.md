# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm_util.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm_util.h

Purpose: helper API for constructing and running nested AMD SVM guests in KVM selftests.

Important APIs/types/functions: `struct svm_test_data`, `vmmcall`, `stgi`, `clgi`, `vcpu_alloc_svm`, `generic_svm_setup`, `run_guest`, `kvm_cpu_has_npt`, `vm_enable_npt`, and `open_sev_dev_path_or_exit`.

Control flow and state: host allocates SVM test pages and VMCB data, guest setup fills VMCB control/save fields, `run_guest` executes VMRUN against the VMCB GPA, and tests inspect resulting VMCB exit state. `stgi/clgi` and `vmmcall` provide guest instruction helpers for intercept tests.

Dependencies and integration: includes `<asm/svm.h>`, `svm.h`, and `processor.h`. It integrates with nested SVM and SEV tests, and uses common VM memory allocation/mapping.

Risks: VMCB physical/virtual address pairing must be correct. NPT support and SEV device availability are host-dependent. Inline instruction helpers require SVM-enabled guest context.

Test signals: nested SVM selftests validate allocation, setup, VMRUN execution, NPT enablement, and expected intercepts from `vmmcall`, `stgi`, or `clgi`.
