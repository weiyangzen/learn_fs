# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_fpe.h

Purpose: Declares stmmac FPE/MAC Merge support APIs and exported register layout instances.

Important APIs and data: Declares support detection, initialization, IRQ handling, additional-fragment-size accessors, GMAC5/XGMAC3 preemption class mapping callbacks, and `dwmac5_fpe_reg`/`dwxgmac3_fpe_reg`.

Control flow and state: The header has no state, but its APIs operate on `priv->fpe_cfg`, ethtool MMSV state, MAC FPE status/control, MTL FPE control, and MAC interrupt enable registers.

Dependencies and integration: Includes Linux types and netdevice definitions and forward-declares `stmmac_priv`. `dwxgmac2_core.c`, `hwif.c`, `stmmac_ethtool.c`, and `stmmac_fpe.c` rely on this contract.

Risks and test signals: Optional FPE support depends on both hardware capability and a valid preemption mapping callback. Build and runtime tests should cover GMAC5, XGMAC3, and unsupported cores, plus ethtool MAC Merge operations when the callbacks are absent.
