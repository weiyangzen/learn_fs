# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_est.h

Purpose: Defines EST register offsets, bit fields, indirect GCL register indexes, and exports the `dwmac510_est_ops` callback table.

Important APIs and data: Provides GMAC and XGMAC EST base offsets, control/status/interrupt bits, PTOV masks and multipliers, error registers, frame-size capture masks, indirect GCL control/data registers, and indexes for BTR, CTR, TER, and LLR.

Control flow and state: No executable state exists here. These macros govern how `stmmac_est.c` writes schedule state into hardware and decodes interrupt state into statistics.

Dependencies and integration: Consumed by `hwif.c` for EST base offsets and by `stmmac_est.c` for all EST programming. It relies on kernel bit macros being available through including files.

Risks and test signals: Mask differences between GMAC5 and XGMAC are central to correct scheduling diagnostics. Test EST programming on both core types, status clear behavior, `EST_SZ_CAP_HBFQ_MASK()` for queue counts, and interrupt enable bit alignment.
