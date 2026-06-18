# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_94xx.c

Purpose: provides the Marvell 88SE94xx/Vanir hardware implementation behind `mvs_dispatch`. Compared with 64xx, it adds 6 Gb/s phy tuning, SGPIO LED support, larger register-set handling, non-specific NCQ error recovery, dual-core interrupt routing, and 94xx SPI access.

Important APIs/types/functions: exported `mvs_94xx_dispatch` binds `mvs_94xx_init()`, ioremap/iounmap, ISR controls, phy controls, register-set allocation, PRD building, identify-frame extraction, link-rate setting, SPI helpers, DMA workaround, interrupt tuning, `mvs_94xx_non_spec_ncq_error()`, and `mvs_94xx_gpio_write()`. Important internal helpers include `set_phy_tuning()`, `set_phy_ffe_tuning()`, `set_phy_rate()`, `mvs_94xx_config_reg_from_hba()`, and `mvs_94xx_sgpio_init()`.

Control flow: init maps per-core register windows, applies revision-specific phy and memory workarounds, programs all-phy VSR settings, resets command/STP state, configures SAS addresses and HBA-info-derived tuning per phy, enables and hard-resets phys, detects port type, unmasks per-phy interrupts, sets endian behavior, starts TX/RX queues, enables central and SRS interrupts, tunes timers for STP/expander performance, and initializes SGPIO. ISR status checks SAS_A/SAS_B bits; the ISR only services the matching core and calls common `mvs_int_full()` under lock. GPIO writes translate libsas SGPIO writes to DCTRL LED bitfields.

State and persistence: runtime state includes `mvi->sata_reg_set`, phy tuning defaults in `hba_info_param`, MMIO windows adjusted per host ID, SGPIO registers, and DMA work buffers. No driver persistence is written, though SPI helpers can support persistent HBA information when called by common code.

Dependencies and integration points: depends on `mv_sas.h`, `mv_94xx.h`, `mv_chips.h`, libsas GPIO APIs, common mvsas interrupt/task/device code, and PCI revision IDs. Selected by `mv_init.c` for 9180, 9480, 9445, 9485, Areca 1320, OCZ RevoDrive/zDrive, and related IDs.

Risks and test signals: revision-specific tuning is fragile and uses many magic constants. `mv_ffc64()`/register-set allocation must handle 64 SATA register sets correctly. `mvs_94xx_fix_dma()` uses `virt_to_phys()` on PRD memory for chained entries on A0/B0, which is architecture/DMA-sensitive. Tests should cover dual-core interrupt routing, SGPIO writes, non-specific NCQ error recovery, phy tuning across revisions, max scatter-gather PRDs, register-set exhaustion, and probe/remove on both single- and dual-host adapters.
