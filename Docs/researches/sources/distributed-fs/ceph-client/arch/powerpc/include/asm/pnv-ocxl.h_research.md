# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pnv-ocxl.h

Purpose: This header declares PowerNV platform services for OpenCAPI/OCXL devices, including translation layer capabilities, XSL register mapping, SPA setup, LPAR mapping, and TLB invalidation control.

Important APIs/types/functions: Constants define TL template/rate-buffer sizes and ATS/ATSD register offsets and bitfields such as `PNV_OCXL_ATSD_LNCH_RIC`, `PID`, `AP`, `L`, and AVA masks. Public APIs include `pnv_ocxl_get_actag`, `pnv_ocxl_get_pasid_count`, `pnv_ocxl_get_tl_cap`, `pnv_ocxl_set_tl_conf`, `pnv_ocxl_get_xsl_irq`, `pnv_ocxl_map_xsl_regs`, `pnv_ocxl_unmap_xsl_regs`, `pnv_ocxl_spa_setup`, `pnv_ocxl_spa_release`, `pnv_ocxl_spa_remove_pe_from_cache`, `pnv_ocxl_map_lpar`, `pnv_ocxl_unmap_lpar`, and `pnv_ocxl_tlb_invalidate`.

Control flow: An OCXL PCI driver queries ACTAG/PASID/TL capabilities, configures TL rates with a physical rate buffer, maps interrupt and XSL fault/status registers, initializes SPA memory for process elements, maps an LPAR address register view, and issues ATSD invalidates by writing launch/address fields. Release paths unmap registers and LPAR views and tear down SPA platform data.

State and persistence: Runtime state is owned by callers and returned platform data: mapped MMIO pointers, SPA memory, platform-private data, PE cache state, and LPAR ARVA mappings. The header encodes register layout but does not allocate storage.

Dependencies and integration points: It depends on `linux/bitfield.h`, `linux/pci.h`, and PowerPC `PPC_BIT`/`PPC_BITMASK` semantics. It integrates PCI OCXL drivers with PowerNV OPAL/platform code, radix translation invalidation, XSL interrupt handling, and process address space management.

Risks and test signals: Register bitfield mistakes can invalidate the wrong PID, page size, scope, or address. Rate-buffer physical addresses and sizes must match firmware expectations. Mapping lifetimes must avoid stale MMIO pointers after device removal. Tests should include OCXL capability probing, TL setup round trips, SPA create/remove, PE cache removal, TLB invalidation for 4K/64K/2M/1G pages, and device hot-unplug cleanup.
