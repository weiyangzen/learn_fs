# sources/distributed-fs/ceph-client/arch/x86/boot/startup/exports.h

Purpose: linker alias header exposing selected position-independent startup symbols under their runtime names.

Important APIs and state: `PROVIDE()` aliases include `early_set_pages_state`, `early_snp_set_memory_private`, `early_snp_set_memory_shared`, `get_hv_features`, `sev_es_terminate`, `snp_cpuid`, `snp_cpuid_get_table`, `svsm_issue_call`, and `svsm_process_result_codes` to their `__pi_` prefixed implementations.

Control flow: build/link-time only.

Dependencies and integration: matches the `objcopy --prefix-symbols=__pi_` rule in startup `Makefile`. Runtime SEV code can call these functions while the actual implementation came from PI startup objects.

Risks and test signals: aliases must stay synchronized with startup implementation symbol names and consumers. Link failures catch many mismatches; SEV/SNP boot tests catch semantic drift.
