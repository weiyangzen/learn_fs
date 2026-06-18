# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm_common.c

## Purpose
Provides the common OMAP2+ PRM core: global PRM base/features, chained PRCM interrupt controller setup, suspend-aware PRCM IRQ masking, generic wrappers around SoC-specific `prm_ll_data`, device-tree PRM base discovery, clock provider setup, and late PRM initialization.

## APIs, Flow, And State
Public APIs include `omap_prcm_event_to_irq()`, `omap_prcm_irq_prepare()`, `omap_prcm_irq_complete()`, `omap_prcm_register_chain_handler()`, hardreset wrappers, context-loss wrappers, `omap_prm_reset_system()`, `omap_prm_clear_mod_irqs()`, VP helpers, `prm_register()`, `prm_unregister()`, `omap2_prcm_base_init()`, and `omap_prcm_init()`. State includes `prm_base`, `prm_features`, `prm_reboot_mode`, `prm_ll_data`, `prcm_irq_setup`, and allocated generic IRQ chip/mask arrays. IRQ flow masks at PRM level when suspended, repeatedly reads pending events, dispatches priority events first, acknowledges/EOIs/unmasks the parent IRQ, then performs an OCP barrier. Base init scans DT compatibles, ioremaps PRM/SCRM/PLLSS blocks, sets `prm_base`, calls SoC init hooks, then initializes CM bases and clock providers.

## Dependencies And Integration
Depends on Linux IRQ, OF address, clock provider, TI clock, PRM/CM/SCRM headers, control/PCS legacy setup, and SoC-specific PRM init data. It is the integration point between platform device tree nodes, clock infrastructure, powerdomain/hwmod reset wrappers, and PRCM wake IRQ handling.

## Risks And Test Signals
`OMAP_PRCM_MAX_NR_PENDING_REG` caps chained IRQ handling at two status registers. Registration rejects duplicate setup, and error cleanup must handle partially initialized IRQ chips. `omap_prm_reset_system()` spins forever after reset request. Test signals are DT PRM node discovery, IRQ descriptor allocation, `omap_prcm_event_to_irq("io")`, suspend/resume mask save/restore, PRM wrapper warnings, and subsystem late init success.
