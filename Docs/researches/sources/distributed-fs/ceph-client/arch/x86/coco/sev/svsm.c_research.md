# sources/distributed-fs/ceph-client/arch/x86/coco/sev/svsm.c

## Purpose
SVSM support for SEV-SNP guests running above VMPL0. It implements GHCB/MSR call routing to the Secure VM Service Module, SVSM-assisted PVALIDATE batching, SVSM attestation requests, and SVSM vTPM probing/command forwarding.

## Important APIs, Types, And Functions
Exports `snp_issue_svsm_attest_req()`, `snp_svsm_vtpm_send_command()`, and `snp_svsm_vtpm_probe()`. Internal entry points include `svsm_perform_call_protocol()`, `svsm_perform_ghcb_protocol()`, `svsm_pval_pages()`, `svsm_build_ca_from_psc_desc()`, and `svsm_build_ca_from_pfn_range()`. Persistent state consists of `boot_svsm_ca_page`, `boot_svsm_caa_pa`, and per-CPU `svsm_caa`/`svsm_caa_pa`.

## Control Flow And State
Call protocol disables interrupts, chooses the runtime GHCB, boot GHCB, or early MSR protocol, then retries `-EAGAIN` SVSM results. GHCB protocol populates protocol metadata, emits `SVM_VMGEXIT_SNP_RUN_VMPL`, issues `svsm_issue_call()`, verifies exception information, and converts SVSM result codes. PVALIDATE builds up to `SVSM_PVALIDATE_MAX_COUNT` entries in the CAA buffer, invokes core call ID 1, stores failed 2M entries that need 4K fallback, and terminates on unrecoverable failure. Attestation copies the input request to the CAA buffer and propagates returned buffer lengths from output registers. vTPM probe requires nonzero `snp_vmpl`, performs `SVSM_VTPM_QUERY`, and checks TPM command bit 8.

## Dependencies And Integration
Integrates with `internal.h`, GHCB exception verification from `vc-shared.c`, SVSM call ABI definitions, SNP PSC descriptors, vTPM driver registration in `core.c`, and exported attestation/vTPM consumers.

## Risks And Test Signals
Risks include early-boot address-mode confusion between boot and per-CPU CAAs, stale interrupt state, CAA buffer overwrite, 2M fallback array bounds, incorrect length propagation for attestation, and accepting SVSM availability without `snp_vmpl`. Signals include SVSM guest boot, page-state transitions at VMPL1+, attestation ioctl paths, tpm-svsm device creation, and negative tests for missing SVSM or unsupported vTPM command bit.
