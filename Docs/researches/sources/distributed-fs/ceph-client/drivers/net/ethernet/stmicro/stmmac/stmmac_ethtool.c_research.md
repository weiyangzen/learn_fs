# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_ethtool.c

Purpose: Implements ethtool operations for stmmac: driver info, link settings, register dumps, ring sizes, coalescing, queue counts, RSS, Wake-on-LAN, EEE, timestamp capabilities, selftests, statistics, and MAC Merge/FPE controls.

Important APIs and flow: `stmmac_set_ethtool_ops()` installs `stmmac_ethtool_ops`. Stats paths build string/count/data arrays from safety counters, MMC counters, software extra stats, aggregate queue stats, and per-queue stats. Ring/channel setters validate bounds and power-of-two sizes before calling reinit helpers. RSS get/set copies `priv->rss` and invokes hardware RSS configuration. Coalescing translates RX RIWT between microseconds and watchdog units and updates per-queue TX timers/frame thresholds.

Control flow and state: User requests mutate `priv->msg_enable`, ring sizes through reinit, coalescing arrays, RX watchdog registers, RSS key/table, queue counts, FPE additional fragment size, and ethtool MMSV state. Register dumps call selected MAC/DMA dump callbacks, then reshape older DMA register regions into ethtool's expected layout.

Dependencies and integration: Depends on phylink ethtool helpers, PTP clock registration, FPE helpers, MMC read callbacks, DMA/MAC debug callbacks, selftest hooks, per-CPU stats sync, and the selected hardware vtables.

Risks and test signals: Stats string/count/data ordering must stay identical. Test `ethtool -S`, `-d`, `-g/-G`, `-c/-C` including per-queue, `-l/-L`, RSS key/indir updates, timestamp info with and without PHC, WOL/EEE forwarding through phylink, MAC Merge get/set/stats, and invalid ring/coalesce inputs.
