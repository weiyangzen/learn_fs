# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/svm.h

Purpose: AMD SVM architecture definitions for nested virtualization selftests. It defines intercept indexes, Hyper-V VMCB enlightenments, VMCB control/save layouts, bit masks for virtual interrupt control, event injection, IOIO intercept decoding, selector attributes, and intercept constants.

Important APIs/types/functions: intercept enum values, `struct hv_vmcb_enlightenments`, `HV_VMCB_NESTED_ENLIGHTENMENTS`, `HV_SVM_EXITCODE_ENL`, packed `struct vmcb_control_area`, `struct vmcb_seg`, `struct vmcb_save_area`, `struct vmcb`, TLB/interrupt masks, `SVM_IOIO_*`, `SVM_VM_CR_*`, `SVM_MISC*`, `SVM_SELECTOR_*`, CR/DR intercept constants, `SVM_EVTINJ_*`, and `SVM_EXITINTINFO_*`.

Control flow and state: nested SVM tests allocate and initialize a VMCB, set intercept and control bits, enter guest mode with `vmrun` via `svm_util.h`, then inspect exit code, exit info, event injection, and save-area state. State persists in the VMCB and guest physical pages shared with KVM.

Dependencies and integration: consumed by `svm_util.h`, SEV helpers, and nested SVM tests. It relies on exact AMD architecture layout and KVM's nested SVM interpretation.

Risks: packed VMCB layout correctness is critical. Bit definitions must match hardware, and nested tests can silently validate the wrong behavior if intercept bits or event-info masks are wrong.

Test signals: nested SVM tests validate VMRUN/VMEXIT behavior, intercept decoding, event injection, virtual interrupt masking, and Hyper-V enlightenment support.
