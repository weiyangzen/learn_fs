<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sev.h

Purpose: declares AMD SEV-ES/SNP guest and host support interfaces, firmware message formats, secrets-page structures, SVSM protocol structures, RMP/PVALIDATE helpers, GHCB operations, memory private/shared transitions, secure TSC support, and KVM RMP-management hooks.

Important APIs/types/functions: `es_result`, `es_fault_info`, `es_em_ctxt`, `cc_blob_sev_info`, SNP CPUID table structures, `rmp_state`, SNP guest message/header/request/response structures, `snp_secrets_page`, `snp_msg_desc`, SVSM call/attestation/PVALIDATE structures, `pte_enc_desc`, `rmpadjust()`, `pvalidate()`, `setup_ghcb()`, SNP memory state APIs, `snp_send_guest_request()`, secure TSC init, `sev_es_ghcb_hv_call()`, `snp_cpuid()`, `sev_es_terminate()`, and KVM RMP helpers such as `rmp_make_private()` and `rmp_make_shared()`.

Control flow: early boot discovers SEV/SNP state, maps secrets/CPUID/GHCB resources, negotiates GHCB protocol, handles #VC exceptions by emulating or forwarding operations through GHCB/VMGEXIT, validates/accepts memory, and later services guest firmware requests using encrypted private buffers and shared GHCB/message pages. KVM host code uses RMP helpers to assign or release pages for SNP guests.

State and persistence: runtime state includes GHCB pages, boot GHCB pointer, negotiated GHCB version, SNP VMPL, secrets-page keys and message sequence numbers, secure TSC data, RMP entries, private/shared page-table encryption state, and SVSM calling areas. The data is memory-resident but security-sensitive and tied to firmware/hypervisor state.

Dependencies and integration points: depends on `sev-common.h`, SVM/GHCB layouts, confidential-computing detection, set-memory APIs, page tables, EFI/boot params, AES-GCM, KVM AMD SEV, exception entry, kexec, and firmware ABI. Risks are high: sequence-number/key misuse can break SNP request security; private/shared transitions can corrupt memory; `pvalidate`/`rmpadjust` failure handling affects page ownership; GHCB protocol errors can terminate guests. Test signals include SEV, SEV-ES, and SNP guest boot, #VC emulation, SNP guest requests/attestation, secure TSC, SVSM calls, kexec, KVM SNP page assignment, and non-AMD_MEM_ENCRYPT stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sev.h -->
