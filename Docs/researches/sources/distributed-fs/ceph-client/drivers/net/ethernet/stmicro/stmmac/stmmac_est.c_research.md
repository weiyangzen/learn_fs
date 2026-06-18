# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.c

Purpose: Implements Enhanced Scheduled Traffic (802.3 Qbv) hardware programming and interrupt decoding for GMAC5/XGMAC EST blocks.

Important APIs and flow: Exported `dwmac510_est_ops` provides `configure` and `irq_status`. `est_configure()` validates PTP rate, writes base time, cycle time, gate-list length, time extension, and each gate control list entry through the indirect GCL access registers, configures PTOV differently for XGMAC and GMAC5, enables/disables EST, and controls EST interrupts.

Control flow and state: EST configuration persists in hardware registers under `priv->estaddr`; desired software schedule state is supplied in `struct stmmac_est`. `est_write()` polls the `EST_SRWO` bit after each indirect write. Interrupt status handling reads error bits, clears latches, updates `stmmac_extra_stats`, tracks per-TXQ head-of-line blocking reasons, and emits rate-limited diagnostics.

Dependencies and integration: Depends on `stmmac.h`, `stmmac_est.h`, PTP rate supplied by common TC/TAPRIO setup, and callback dispatch through `hwif.h`. `hwif.c` assigns this ops table to GMAC4+/XGMAC entries with EST offsets.

Risks and test signals: Indirect write timeout, bad PTP rate, and gate-list sizing can break schedules. Test enable and disable, GMAC5 versus XGMAC PTOV fields, full GCL programming, base-time rollover, all EST interrupts, per-queue HLB accounting, and taprio reconfiguration under `est_lock`.
