# sources/distributed-fs/ceph-client/arch/x86/coco/sev/core.c

## Purpose
Central runtime and early-boot implementation for AMD SEV-ES/SEV-SNP guests. It owns GHCB setup, SNP page-state transitions, AP startup through VMGEXIT or SVSM, kexec cleanup, Secure AVIC accessors, SNP guest-message setup, platform-device registration, VMPL/sysfs reporting, and Secure TSC initialization.

## Important APIs, Types, And Functions
Global state includes `sev_hv_features`, `sev_secrets_pa`, `snp_vmpl`, `ghcb_version`, `boot_ghcb`, per-CPU `runtime_data`, per-CPU `sev_vmsa`, and Secure TSC scale/offset/frequency caches. Public or cross-file APIs include `snp_set_memory_shared()`, `snp_set_memory_private()`, `snp_accept_memory()`, `snp_kexec_begin()`, `snp_kexec_finish()`, `snp_set_wakeup_secondary_cpu()`, `sev_es_setup_ap_jump_table()`, `sev_es_efi_map_ghcbs_cas()`, Secure AVIC helpers, `setup_ghcb()`, `sev_es_init_vc_handling()`, `snp_dmi_setup()`, `sev_show_status()`, `snp_msg_alloc()`, `snp_msg_init()`, `snp_msg_free()`, `snp_send_guest_request()`, `snp_secure_tsc_prepare()`, and `snp_secure_tsc_init()`.

## Control Flow And State
SNP page conversion builds `snp_psc_desc` entries, rescinds validation before shared conversion, asks the hypervisor to update RMP state via `SVM_VMGEXIT_PSC`, then validates after private conversion. If no GHCB exists, it falls back to the early MSR protocol and SVSM CAA addresses. VMSA/AP startup allocates an aligned VMSA page, initializes architectural reset fields, marks the page as VMSA via SVSM or `RMPADJUST`, then issues AP create/destroy VMGEXITs. Kexec paths first stop conversions, destroy/untag AP VMSAs, convert all shared direct-map and decrypted BSS memory back to private, then switch GHCB pages back to private last. SNP guest requests serialize on `snp_cmd_mutex`, encrypt payloads with AES-GCM using VMPCK keys and sequence numbers from the secrets page, issue GHCB guest-request VMGEXITs, retry BUSY responses, and disable the VMPCK on ambiguous firmware/host errors to avoid IV reuse.

## Dependencies And Integration
Depends on GHCB protocol helpers, `vc-shared.c` hypervisor calls, `internal.h`, SVSM helpers, RMP/PVALIDATE instructions, x86 page-table encryption APIs, memblock, CPU/APIC startup hooks, EFI page tables, platform devices (`sev-guest`, `tpm-svsm`), crypto AES-GCM, and UAPI SNP guest request structures.

## Risks And Test Signals
High-risk areas are GHCB availability during early boot, IRQ-disabled per-CPU GHCB usage, PSC descriptor retry semantics, 2M-to-4K PVALIDATE fallback, cache-coherency mitigation ordering, VMSA page tagging leaks, Secure TSC termination behavior, kexec shared-memory accounting, and VMPCK sequence-number handling. Signals include SEV-ES/SNP boot, AP hotplug and kexec/kdump tests, SNP guest driver attestation/TSC requests, Secure AVIC paths, EFI runtime with GHCB mappings, sysfs VMPL exposure, and crypto selftests for guest-message AES-GCM.
