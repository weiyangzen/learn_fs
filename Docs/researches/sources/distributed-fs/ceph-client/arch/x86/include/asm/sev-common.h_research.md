<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev-common.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sev-common.h

Purpose: defines shared AMD SEV/SEV-ES/SNP constants, GHCB MSR protocol values, VMGEXIT exit codes, SNP page-state-change operations, termination reasons, and hypervisor feature bits used by both guest and host code.

Important APIs/macros: GHCB MSR info/error encodings, `GHCB_MSR_*` requests/responses, `SVM_VMGEXIT_*` exit codes, page state change op values, SNP feature and termination constants, and helper masks/shifts for protocol fields.

Control flow: SEV-ES/SNP guest code encodes requests into GHCB MSR or GHCB shared pages, issues VMGEXIT, and decodes hypervisor responses with these constants. Host/KVM paths validate and synthesize matching values. State lives in GHCB pages/MSRs and SNP firmware-managed metadata.

Dependencies include AMD GHCB/SNP firmware ABI, SVM definitions, confidential computing core, and KVM/guest exception handling. Risks are ABI mismatches with firmware/hypervisor, wrong bit shifts, and ambiguous error handling during early boot. Test signals include SEV-ES boot, SNP guest requests, GHCB MSR fallback, page-state changes, KVM SEV tests, and termination/error-path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev-common.h -->
