# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ethtool.c

## Purpose

`nfp_net_ethtool.c` implements ethtool operations for NFP data vNICs and NFP ports/representors. It reports driver and firmware identity, link settings, ring/channel configuration, self-tests, software/hardware/MAC/application stats, RSS and flow-steering controls, CFG BAR register dumps, firmware diagnostic dumps, module EEPROM reads, interrupt coalescing, FEC, pause, LED identification, and persistent port MAC access.

## Important APIs, Types, and Functions

The main exported objects are `nfp_net_ethtool_ops`, `nfp_port_ethtool_ops`, and `nfp_net_set_ethtool_ops()`. Key helpers include `nfp_net_get_drvinfo()`, `nfp_net_nway_reset()`, `nfp_net_get_link_ksettings()`, `nfp_net_set_link_ksettings()`, ring/channel setters, self-test functions (`nfp_test_link()`, `nfp_test_nsp()`, `nfp_test_fw()`, `nfp_test_reg()`), stats string/value helpers for software, legacy hardware, TLV hardware, MAC, and app stats, RSS helpers, flow-steering add/delete/get functions, dump helpers, module EEPROM helpers, coalesce setters, FEC/pause setters, `nfp_net_get_eeprom()`, and `nfp_net_set_eeprom()`.

## Control Flow

Read operations translate current driver state and firmware tables into ethtool data structures. Link settings prefer NSP ETH-table data and fall back to the CFG BAR link-rate field for plain vNICs. Set operations validate support and bounds, write through NSP or CFG BAR/mailbox helpers, and then trigger refresh or reconfiguration. Ring size/channel changes clone the datapath, alter counts, and call `nfp_net_ring_reconfig()`. RSS changes update local key/table/config and signal `NFP_NET_CFG_UPDATE_RSS`. Flow-steering converts ethtool flow specs to `struct nfp_fs_entry`, checks duplicates and masks, updates firmware through `nfp_net_fs_add_hw()`/`nfp_net_fs_del_hw()`, and keeps `nn->fs.list` sorted by location.

## State and Persistence Behavior

State read or changed here includes `nn->rss_key`, `nn->rss_itbl`, `nn->rss_cfg`, `nn->fs.list`, `nn->fs.count`, `nn->dp` ring sizes/counts, coalesce fields, `pf->dump_flag`, `pf->dump_len`, persistent hwinfo MAC strings, NSP port configuration, FEC/pause settings, LED mode, and stats counters. Many changes are persistent in firmware/NSP configuration rather than only Linux memory.

## Dependencies and Integration Points

The file bridges Linux ethtool to NFP core services: NSP open/config/read-module/hwinfo APIs, CPP/resource reads, app stats hooks, port helpers, shared control BAR offsets, flow-steering hardware helpers, debugdump routines, and NFP ETH-table media/FEC/speed metadata. Representors reuse `nfp_port_ethtool_ops` with switch-perspective stats.

## Risks and Edge Cases

Large scope makes consistency between string counts and data counts important. Link-mode arrays must match `NFP_MEDIA_LINK_MODES_NUMBER` and media bitmaps. Changing link settings is refused while netdev is running to avoid port-disable states. Flow steering supports only selected masks and only RSS context 0. The `nfp_net_fs_add()` insertion path uses sorted list traversal and replacement semantics that must remain valid for empty/end insertion. Coalesce conversion depends on TLV ME frequency; zero or stale frequency would break usec-to-tick validation.

## Test Signals

Run `ethtool -i`, `-S`, `-k`, `-l/-L`, `-g/-G`, `-c/-C`, `-x/-X`, `-n/-N`, `-d`, `--get-dump/--set-dump`, module EEPROM reads, FEC/pause/LED operations, and link-mode changes on physical ports and representors. Include TLV stats firmware, legacy stats firmware, unsupported NSP feature versions, flow-steering duplicate/mask errors, and ring/channel reconfiguration under traffic.
