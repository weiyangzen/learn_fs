# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-ethtool.c

## Purpose
This file implements ethtool operations for the TI K3 AM65 CPSW NUSS ethernet driver. It exposes driver identity, message level, channel counts, ring parameters, pause/WOL/link/EEE through phylink, register dumps, statistics, timestamping capabilities, private flags, interrupt coalescing, and MAC Merge/IET frame preemption controls.

## Important APIs, Types, and Functions
The exported object is `am65_cpsw_ethtool_ops_slave`. Important internal types are `struct am65_cpsw_regdump_hdr`, `struct am65_cpsw_regdump_item`, `struct am65_cpsw_stats_regs`, and `struct am65_cpsw_ethtool_stat`. Key functions include runtime PM wrappers `am65_cpsw_ethtool_op_begin/complete`, stats string/count/data helpers, `am65_cpsw_get_regs_len`, `am65_cpsw_get_regs`, phylink forwarding helpers, `am65_cpsw_get_ethtool_ts_info`, private flag get/set, MAC Merge helpers `am65_cpsw_get_mm`, `am65_cpsw_set_mm`, `am65_cpsw_get_mm_stats`, and queue coalescing get/set routines.

## Control Flow and State
Ettool calls begin by runtime-resuming the device and complete by putting PM runtime. Driver/link settings are read from `am65_cpsw_common`, `am65_cpsw_ndev_priv`, slave data, host port, and active port structures. Register dump length is computed from static ranges plus dynamic ALE table size; dump output serializes module ID, length, register offset/value pairs, and ALE table contents. Stats use static offset tables into host and slave stat MMIO. Channel changes are rejected while `common->usage_count` indicates active interfaces. Coalescing stores microsecond values as nanosecond pacing timeouts per TX channel/RX flow. Private flag changes are rejected while active and when round-robin RX packet-type mode conflicts with QoS EST.

## State and Persistence Behavior
The file mutates `priv->msg_enable`, `common->tx_ch_num`, `common->rx_ch_num_flows` via `am65_cpsw_nuss_update_tx_rx_chns`, `common->pf_p0_rx_ptype_rrobin`, per-channel pacing timeouts, and MAC Merge state in port IET registers and `port->qos.iet`. `am65_cpsw_set_mm` also saves/restores original FIFO `MAX_BLKS`, toggles PMAC/TX preemption bits, updates verification mode/time, and commits preemptible traffic classes. Statistics and register dumps are read-only snapshots of hardware state.

## Dependencies and Integration Points
The file depends on `am65-cpsw-nuss.h`, `am65-cpsw-qos.h`, `cpsw_ale.h`, `am65-cpts.h`, phylink, runtime PM, platform device, and timestamping headers. It integrates with phylink for pause, WOL, link settings, EEE, and nway reset; with CPTS for PHC/timestamp reporting; with ALE for table dumps; and with QoS/IET helpers for frame preemption. `IS_ENABLED` guards keep timestamping/QoS behavior optional at compile time.

## Risks and Test Signals
Risks include register dump length/index accounting, runtime PM imbalance, channel changes racing active traffic, private flag/QoS conflicts, coalescing unit conversion and minimum validation, MM/IET register sequencing, and optional config combinations. In `am65_cpsw_get_regs`, the ALE-table branch advances `pos` by a byte length even though `reg` is a `u32 *`, which deserves scrutiny. Tests should cover `ethtool -i`, `-S`, `-d`, `-l/-L`, `-c/-C` including per-queue, phylink settings, timestamping with/without CPTS, private flag toggles while down/up, MM get/set/stats with QoS on/off, and runtime PM failure injection.
