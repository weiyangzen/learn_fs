# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.h

Purpose: defines the 88SE94xx hardware contract: register maps, revision IDs, interrupt causes, 6 Gb/s phy configuration bitfields, PRD format, SGPIO registers, SPI registers, and helper macros for SATA register-set enable registers.

Important APIs/types/functions: `MAX_LINK_RATE` is 6.0 Gb/s. `enum VANIR_REVISION_ID` distinguishes A0/B0/C0/C1/C2 tuning paths. `enum hw_registers`, `host_registers`, `pci_cfg_registers`, `sas_sata_vsp_regs`, `chip_register_bits`, and `pci_interrupt_cause` drive MMIO and interrupt handling. `union reg_phy_cfg` packs phy capability fields. `struct mvs_prd_imt` and packed `struct mvs_prd` describe 94xx PRDs. SGPIO enums define LED control. `mv_ffc64()`, `r_reg_set_enable()`, and `w_reg_set_enable()` support register-set allocation.

Control flow: no standalone flow. The constants and inline helper are consumed by `mv_94xx.c` and `mv_chips.h`.

State and persistence: describes hardware register state; no direct driver state. SGPIO and SPI fields target controller-side registers that may affect persistent or enclosure-visible behavior when used by implementation code.

Dependencies and integration points: includes `linux/types.h`, expects common mvsas definitions from `mv_defs.h`/`mv_sas.h`, and exports `mvs_94xx_dispatch` for `mv_init.c`.

Risks and test signals: bitfield layout in `union reg_phy_cfg` and `struct mvs_prd_imt` is endian-sensitive. SGPIO register offsets use host offsets and must match dual-core hardware. Test signals are build coverage on big/little endian, link-rate negotiation to 6 Gb/s, SGPIO LED control, SPI register reads, and max PRD DMA on 94xx adapters.
