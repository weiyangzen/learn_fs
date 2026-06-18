<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/svm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/svm.h

Purpose: Defines AMD SVM VM-exit reason codes, SEV-ES/SNP VMGEXIT software events, termination reason encoding, and a string mapping list for exit decoding.

Important APIs/types/functions: `SVM_EXIT_*`, `SVM_VMGEXIT_*`, `SVM_VMGEXIT_TERM_REASON()`, `SVM_EXIT_SW`, `SVM_EXIT_ERR`, and `SVM_EXIT_REASONS`.

Control flow: KVM and perf tooling report SVM exits using these constants. SEV-ES/SNP guests use VMGEXIT event codes to communicate MMIO, AP setup, page-state changes, guest requests, SAVIC operations, hypervisor features, and termination.

State and persistence behavior: No state. Exit codes are ABI/trace values that persist in migration logs, trace output, and user tooling expectations.

Dependencies and integration points: Integrates with KVM SVM, perf KVM decoding, SEV-ES GHCB protocol, SNP page-state changes, nested virtualization, and userspace VMM exit handling.

Risks and test signals: Risks include exit-code mismatch with hardware or firmware, missing decode entries, and wrong termination encoding. Test AMD KVM selftests, SEV-ES/SNP guest boot, VMGEXIT MMIO and PSC paths, nested SVM, perf exit decoding, and trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/svm.h -->
