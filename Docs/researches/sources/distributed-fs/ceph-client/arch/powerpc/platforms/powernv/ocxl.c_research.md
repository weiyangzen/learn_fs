
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ocxl.c

Purpose: supplies PowerNV OpenCAPI/OCXL platform services for actag allocation, PASID sizing, transaction-layer configuration, XSL register mapping, SPA setup, LPAR mapping, and ATSD TLB invalidation.

Important APIs/functions: exported functions include `pnv_ocxl_get_actag()`, `pnv_ocxl_get_pasid_count()`, `pnv_ocxl_get_tl_cap()`, `pnv_ocxl_set_tl_conf()`, `pnv_ocxl_get_xsl_irq()`, `pnv_ocxl_map_xsl_regs()`, `pnv_ocxl_unmap_xsl_regs()`, `pnv_ocxl_spa_setup()`, `pnv_ocxl_spa_release()`, `pnv_ocxl_spa_remove_pe_from_cache()`, `pnv_ocxl_map_lpar()`, `pnv_ocxl_unmap_lpar()`, and `pnv_ocxl_tlb_invalidate()`. `pnv_ocxl_fixup_actag()` is a PCI fixup that gathers desired actag counts during enumeration.

Control flow: a PCI header fixup identifies NPU OCAPI PHBs, reads IBM DVSEC AFU metadata, accumulates desired actags per function in shared `npu_link` entries, and later `assign_actags()` prorates the 64 Power9 actags across functions. Driver-facing calls return actag/PASID values, hard-coded TL capabilities, configure TL via OPAL, map DT-described XSL MMIO registers, set up SPA through OPAL, map LPAR ATSD registers, and issue ATSD invalidations by programming MMIO and polling status.

State and persistence: `links_list` stores per-link actag accounting protected by `links_list_lock`; SPA setup stores PHB OPAL ID and BDFN in caller-owned platform data. No persistent storage.

Dependencies and integration points: depends on PCI DVSEC config space, `struct pnv_phb`, OPAL NPU calls, OpenCAPI config definitions, device-tree properties such as `ibm,opal-xsl-irq`, `ibm,opal-xsl-mmio`, and PHB `ibm,mmio-atsd`, plus exported OCXL base-driver interfaces.

Risks: actag fairness depends on fixups having seen all functions before drivers query. Only one AFU-carrying function is effectively supported for PASID count. ATSD invalidation uses polling with timeout and direct MMIO bitfield programming. Hard-coded Power9 TL capabilities are not generic to future NPUs.

Test signals: multi-function OpenCAPI adapter enumeration, actag allocation under overcommit, PASID query, TL setup OPAL call success, XSL IRQ/MMIO DT parsing, SPA setup/release, LPAR mapping, and ATSD invalidation timeout behavior.
