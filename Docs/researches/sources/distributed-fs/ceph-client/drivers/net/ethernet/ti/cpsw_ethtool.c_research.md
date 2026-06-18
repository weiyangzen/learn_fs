# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_ethtool.c

## Purpose
`cpsw_ethtool.c` implements the shared ethtool helper functions used by the legacy and switchdev CPSW drivers. It exposes hardware statistics, CPDMA channel statistics, interrupt coalescing, pause/WOL/link settings through PHYs, ALE register dumps, queue/channel configuration, ring sizing, and timestamping capabilities.

## Important APIs, Types, And Functions
Statistics are described by `struct cpsw_hw_stats`, `struct cpsw_stats`, `cpsw_gstrings_stats[]`, and `cpsw_gstrings_ch_stats[]`. Public helpers include `cpsw_get_msglevel()`, `cpsw_set_msglevel()`, `cpsw_get_coalesce()`, `cpsw_set_coalesce()`, `cpsw_get_sset_count()`, `cpsw_get_strings()`, `cpsw_get_ethtool_stats()`, `cpsw_get_pauseparam()`, `cpsw_get_wol()`, `cpsw_set_wol()`, `cpsw_get_regs_len()`, `cpsw_get_regs()`, `cpsw_ethtool_op_begin()`, `cpsw_ethtool_op_complete()`, channel/ring getters and setters, PHY ksettings/EEE/nway helpers, and `cpsw_get_ts_info()`.

## Control Flow
Stats collection reads fixed CPSW hardware statistic offsets and then CPDMA RX/TX channel stats for each configured channel. Coalescing computes wrapper interrupt pacing prescale and interrupt counts from requested RX usecs, clamps to hardware limits, writes RX/TX `*_imax`, updates `int_control`, and stores `coal_intvl`. Channel changes suspend data passing by disabling interrupts, stopping TX queues, and stopping CPDMA; create/destroy CPDMA channels; update real queue counts on running netdevs; rebalance NAPI budgets; recreate XDP RX queues/page pools if RX count changes; and resume DMA/interrupts. Ring changes similarly suspend data, adjust RX descriptor count, recreate pools, and resume. Ettool begin/complete pair runtime-PM get/put around operations needing register access.

## State And Persistence
The file mutates `cpsw->coal_intvl`, wrapper interrupt registers, CPDMA channel objects, `rx_ch_num`, `tx_ch_num`, TX queue maxrate defaults, NAPI budgets, page pools, XDP RXQ registrations, and CPDMA RX descriptor count. It reads but does not reset hardware stats. Channel/ring changes affect all CPSW slave netdevs because CPDMA is shared.

## Dependencies And Integration Points
It depends on `cpsw_priv.h`, `cpsw_ale.h`, `davinci_cpdma`, phylib ethtool helpers, runtime PM, CPTS, and netdev queue APIs. Legacy and switchdev drivers plug these helpers into their ethtool ops tables.

## Risks
Channel and ring updates are disruptive and close all CPSW netdevs on failure through `cpsw_fail()`. Multi-queue changes must stay synchronized with page pools and XDP RX queues; otherwise RX callbacks can reference freed or missing pools. Coalescing uses only RX usecs but programs both RX and TX pacing. `cpsw_get_regs()` dumps ALE entries only, not all CPSW registers, so users may misinterpret the register dump scope. PHY-dependent helpers must handle absent PHYs, especially during down or partially probed states.

## Test Signals
Use `ethtool -S`, `--show-coalesce`, `--coalesce`, `-l`, `-L`, `-g`, `-G`, `-d`, `--show-eee`, `--set-eee`, WOL, link ksettings, and timestamp info on both legacy and switchdev netdevs. Exercise channel/ring changes while interfaces are up, while XDP is attached, and with both dual-EMAC ports running; verify data resumes or devices close cleanly on injected CPDMA allocation failures.
