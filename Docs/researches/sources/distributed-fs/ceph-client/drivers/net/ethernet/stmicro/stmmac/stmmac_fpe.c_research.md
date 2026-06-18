# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.c

Purpose: Implements Frame Preemption / MAC Merge (802.3 Qbu/802.3br) support for GMAC5 and XGMAC3-style hardware.

Important APIs and flow: Public helpers report support, initialize ethtool MMSV, handle FPE interrupts, get/set additional fragment size, and map preemption classes for GMAC5 and XGMAC3. `stmmac_mmsv_ops` integrates with ethtool's MAC Merge state machine by configuring TX FPE, enabling PMAC interrupts, and sending verify/response mPackets.

Control flow and state: FPE state persists in MAC and MTL FPE registers plus `priv->fpe_cfg.fpe_csr` cache and `ethtool_mmsv`. IRQ status reads the clear-on-read MAC FPE status register only in `stmmac_fpe_irq_status()`, translates verify/response events, and passes them to ethtool MMSV. Preemption class mapping writes queue bitmaps into MTL registers and, for XGMAC, reprograms TC-to-queue fields.

Dependencies and integration: Depends on `stmmac_priv`, selected `stmmac_fpe_reg` offsets from `hwif.c`, ethtool MMSV helpers, MAC interrupt locking, queue/TC mappings, and GMAC/XGMAC register definitions. Ethtool calls this file for `get_mm`, `set_mm`, and MM stats.

Risks and test signals: Clear-on-read interrupt status and TC-to-queue mapping are delicate. Test FPE supported/unsupported combinations, PMAC interrupt enable/disable races, verify/response state transitions, additional fragment size, GMAC5 one-to-many TC validation under SP and weighted schedulers, XGMAC no-TC default restoration, and MM statistics from MMC counters.
