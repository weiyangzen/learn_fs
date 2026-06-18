# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2.h

Purpose: Defines the DesignWare XGMAC2 register map, bit fields, descriptor fields, and exported operation tables used by the stmmac XGMAC/XLGMAC implementation. It is the hardware contract consumed mainly by `dwxgmac2_core.c`, `dwxgmac2_dma.c`, `dwxgmac2_descs.c`, `mmc_core.c`, `stmmac_fpe.c`, and `hwif.c`.

Important APIs and data: The header exports register offsets for MAC configuration, queue routing, RSS, timestamp/PPS, MTL scheduling, DMA channels, safety interrupts, L3/L4 filters, and XGMAC descriptor layouts. It declares `dwxgmac210_ops`, `dwxlgmac2_ops`, `dwxgmac210_dma_ops`, and `dwxgmac210_desc_ops`.

Control flow and state: No executable code lives here, but the macros define how runtime code persists hardware state through MMIO: link speed bits in `XGMAC_TX_CONFIG`, RX/TX enable bits, MTL queue maps, DMA ring addresses/tails/lengths, RSS key/table access windows, safety status latches, and descriptor ownership bits.

Dependencies and integration: Depends on `common.h` for shared DMA/MTL constants and kernel bit helpers. It integrates XGMAC2-specific code with generic `stmmac_ops`, `stmmac_dma_ops`, and `stmmac_desc_ops` callback dispatch in `hwif.h`.

Risks and test signals: Register masks are data-path critical. Regressions show up as broken link speed programming, DMA channel setup, RSS table writes, FPE/EST/PTP behavior, or descriptor ownership handoff. Test XGMAC and XLGMAC variants, all advertised speeds, RX/TX queue counts above four, RSS enable/disable, timestamp/PPS, and safety interrupt decoding.
