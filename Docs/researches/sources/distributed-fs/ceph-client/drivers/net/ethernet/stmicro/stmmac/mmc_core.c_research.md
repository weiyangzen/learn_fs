# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/mmc_core.c

Purpose: Implements MMC statistics callbacks for GMAC-style and XGMAC-style counter blocks. It masks counter interrupts, controls counter behavior, and accumulates hardware counters into `struct stmmac_counters`.

Important APIs and flow: Exported `dwmac_mmc_ops` and `dwxgmac_mmc_ops` implement `ctrl`, `intr_all_mask`, and `read`. `dwmac_mmc_read()` reads 32-bit GMAC counters directly. `dwxgmac_mmc_read()` uses `dwxgmac_read_mmc_reg()` for 64-bit register pairs, saturating software fields to `~0U` if the hardware value exceeds 32 bits.

Control flow and state: Hardware counters are read from `priv->mmcaddr`; software state is monotonically accumulated in `priv->mmc` because the hardware is normally configured to reset counters after reads. XGMAC masking differs from GMAC: RX/TX interrupt masks are written as zero while FPE and IPC masks use all ones.

Dependencies and integration: Depends on `hwif.h` and `mmc.h`. Ethtool calls `stmmac_mmc_read()` when RMON is supported and exposes the fields; MAC Merge stats also read FPE-specific counters.

Risks and test signals: Counter offset mistakes cause misleading user diagnostics. The XGMAC RX CRC register is read twice into the same field, which is worth regression awareness because reset-on-read hardware could double-clear or miscount depending on semantics. Test GMAC and XGMAC counter readback, reset-on-read accumulation, FPE counters, IPC counters, LPI counters, and interrupt mask behavior.
