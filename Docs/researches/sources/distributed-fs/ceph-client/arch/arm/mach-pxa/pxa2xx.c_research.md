<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx.c

Purpose: small PXA2xx-specific helpers for reset status and SDRAM row detection.

Important APIs/functions: `pxa2xx_clear_reset_status(mask)` writes RCSR with the shared reset-status mask. `pxa2xx_smemc_get_sdram_rows()` reads `MDCNFG`, inspects enabled SDRAM banks and DRAC fields, caches, and returns row count as `1 << (11 + max(drac0, drac2))`.

Control flow: reset code calls clear helper through `generic.c`; SMEMC users query SDRAM row geometry lazily.

State and persistence: `sdram_rows` static cache persists after first calculation. RCSR writes clear hardware reset causes.

Dependencies and integration: depends on PXA2xx register and SMEMC definitions and CPU-independent reset status constants.

Risks and test signals: SDRAM row cache assumes memory configuration does not change after first read. Test reset-status reporting/clearing and SMEMC row calculation on PXA25x/PXA27x memory configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx.c -->
