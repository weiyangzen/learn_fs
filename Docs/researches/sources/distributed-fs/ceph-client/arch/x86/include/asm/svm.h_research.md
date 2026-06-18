<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/svm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/svm.h

Purpose: defines AMD SVM virtualization hardware structures, intercept constants, VMCB/GHCB layouts, AVIC fields, SEV feature bits, event injection encodings, and GHCB accessors used primarily by KVM and SEV guest code.

Important APIs/types: intercept enumerations, `vmcb_control_area`, TLB-control and interrupt-control bits, AVIC logical/physical table masks, SEV feature bits, `vmcb_seg`, `vmcb_save_area`, `sev_es_save_area`, `ghcb_save_area`, `ghcb`, `vmcb`, size/offset build checks, selector/event injection masks, and generated `ghcb_*` valid/get/set accessors.

Control flow: KVM programs VMCB control/save areas before VMRUN, handles exits by reading `exit_code/info`, injects events with encoded fields, manages AVIC acceleration, and uses GHCB pages for SEV-ES/SNP guest-host communication. Guest #VC paths use accessors to mark GHCB fields valid before VMGEXIT.

State and persistence: VMCB/GHCB pages are live virtualization state shared with CPU hardware or hypervisor; AVIC tables and SEV VMSA pages persist for the lifetime of vCPUs. Dependencies include AMD APM layout, KVM uapi, Hyper-V enlightenments, SEV/SNP ABI, and bitops.

Risks: packed layout and offsets are hardware ABI; any drift breaks virtualization. Event injection and intercept bits are security-critical. GHCB valid bitmap misuse can leak or ignore state. Test signals include KVM SVM unit tests, nested virtualization, AVIC/x2AVIC, SEV-ES/SNP guests, VMCB size build checks, and VM exit/injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/svm.h -->
