# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_ethtool.c

`otx2_ethtool.c` implements ethtool operations for PF and VF netdevs: stats, channel/ring/coalesce tuning, RSS hash configuration and contexts, ntuple rule control, pause/FEC/link settings, timestamp capability reporting, and message level.

PF ops are in `otx2_ethtool_ops` and installed by `otx2_set_ethtool_ops`; VF ops are in `otx2vf_ethtool_ops` and installed by `otx2vf_set_ethtool_ops`. Major callbacks include `otx2_get_ethtool_stats`, `otx2_set_channels`, `otx2_set_ringparam`, `otx2_set_coalesce`, RXNFC get/set, RSS get/set/context operations, `otx2_get_ts_info`, FEC get/set/stats, and link ksettings get/set.

Stats collect device counters, driver atomics, queue stats, CGX/RPM stats, reset count, and FEC data. Channel and ring setters stop/reopen the device when running, update in-memory queue/ring state, and rely on open to rebuild hardware. Coalesce clamps usec/frame values and reprograms CINTs. RSS callbacks validate TOP hash use and program keys, tables, and contexts. RXNFC bridges ethtool class-rule commands into `otx2_flows.c`.

Runtime state lives in `pfvf->hw` RSS/queue/ring/coalesce/stat fields, `pfvf->flags`, `flow_cfg`, `linfo`, and `msg_enable`. Dependencies are Linux ethtool, CGX firmware mailbox APIs, PTP helpers, MCAM flow helpers, RSS helpers, and netdev stop/open.

Risks include device restart failures, RSS ESP/AH key-size constraints, operations requiring the netdev to be running, firmware-dependent FEC/link errors, and reduced VF capability surfaces. Test stats under traffic, channel/ring/coalesce changes, RSS key/table/context operations, ntuple add/list/delete, pause/FEC/link modes, timestamp reporting, and VF-specific ethtool behavior.
