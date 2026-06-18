# sources/distributed-fs/ceph-client/arch/x86/coco/sev/internal.h

## Purpose
Private SEV/SNP CoCo header shared by core, noinstr, VC handling, and SVSM code. It defines the per-CPU GHCB runtime state, cross-file globals, internal prototypes, GHCB MSR accessors, SVSM CAA selectors, and fatal PVALIDATE handling.

## Important APIs, Types, And Functions
`struct sev_es_runtime_data` contains the active GHCB page, backup GHCB for nested #VC/NMI cases, activity flags, and cached DR7. `struct ghcb_state` records whether a backup GHCB was used. The header declares per-CPU `runtime_data`, `sev_vmsa`, `svsm_caa`, and `svsm_caa_pa`, plus `sev_hv_features`, `sev_secrets_pa`, `boot_svsm_ca_page`, and `boot_svsm_caa_pa`. Inline helpers include `sev_es_rd_ghcb_msr()`, `sev_es_wr_ghcb_msr()`, `svsm_get_caa()`, `svsm_get_caa_pa()`, and `__pval_terminate()`.

## Control Flow And State
The header itself is declarative, but it encodes the core state model: GHCBs can be boot-time or per-CPU runtime resources; nested GHCB use must save/restore through `ghcb_state`; SVSM CAA selection switches from boot CAA to per-CPU CAA when `sev_cfg.use_cas` is enabled; and unrecoverable PVALIDATE failures terminate the guest.

## Dependencies And Integration
It depends on x86 SEV/GHCB definitions, native MSR access, per-CPU storage, and SNP/SVSM structures exposed through architecture headers. It is included by all SEV files in this subset, so changing field layout or inline semantics affects VC exception entry, page-state conversion, SVSM calls, Secure AVIC, and SNP guest messaging.

## Risks And Test Signals
Risks include struct layout assumptions for page alignment, missing IRQ-disabled constraints around `__sev_get_ghcb()`, DR7 cache semantics, and boot-vs-runtime CAA address selection. Compile coverage with `CONFIG_AMD_MEM_ENCRYPT`, SEV-ES boot with NMI/#VC nesting, SVSM boot, and PVALIDATE failure injection are useful signals.
