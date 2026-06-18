# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sev.h

Purpose: declares the compressed-stage SEV/SNP helpers and provides no-op stubs when AMD memory encryption is disabled.

Important APIs and state: declares `snp_accept_memory()`, `sev_get_status()`, and `early_is_sevsnp_guest()`. Under `CONFIG_AMD_MEM_ENCRYPT`, inline helpers `sev_es_rd_ghcb_msr()` and `sev_es_wr_ghcb_msr()` wrap raw reads/writes to `MSR_AMD64_SEV_ES_GHCB`.

Control flow: no standalone control flow; it gates real SEV functionality behind the config symbol and returns inert values otherwise.

Dependencies and integration: included by compressed boot code that must compile regardless of SEV config. It depends on `<asm/shared/msr.h>` for raw MSR helpers and on SEV MSR definitions.

Risks and test signals: the stub behavior must preserve non-SEV boot behavior without accidental references to unavailable symbols. Test by building with and without `CONFIG_AMD_MEM_ENCRYPT`, and by confirming GHCB MSR wrappers are used only in early code paths where raw MSR access is valid.
