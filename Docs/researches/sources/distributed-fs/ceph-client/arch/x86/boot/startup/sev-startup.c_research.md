# sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-startup.c

Purpose: startup-side SEV/SNP helpers for early page-state changes and SNP initialization after or without the compressed boot stage.

Important APIs and state: exports `early_set_pages_state()`, `early_snp_set_memory_private()`, `early_snp_set_memory_shared()`, and `snp_init()`. It includes `sev-shared.c` and uses `boot_svsm_ca_page`, `boot_svsm_caa_pa`, `sev_status`, and `sev_secrets_pa`.

Control flow: memory-private/shared functions build `psc_desc` values and call `early_set_pages_state()` page by page only when SNP is enabled. `snp_init()` finds the CC blob via `boot_params.cc_blob_address` or setup_data, caches the secrets page PA, copies the CPUID table, runs SVSM setup/remap for non-VMPL0 guests, caches the blob address back into boot params, and returns whether SNP setup was performed.

Dependencies and integration: called by `sme_enable()` and early mapping code while identity mapped. Depends on shared SEV functions, boot params, CC blob/secrets page, and SVSM MSR protocol.

Risks and test signals: blob/MSR mismatch terminates later in `sme_enable()`. Non-VMPL0 remap must occur while old and new CA addresses are still usable. Test direct firmware/PVH boot with setup_data CC blob, compressed boot handoff via `cc_blob_address`, SNP secrets-page presence, and shared/private page transitions.
