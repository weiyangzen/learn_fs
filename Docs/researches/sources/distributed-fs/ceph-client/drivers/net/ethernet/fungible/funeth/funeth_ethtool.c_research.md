# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_ethtool.c

## Purpose
Implements the ethtool surface for funeth: link settings, pause/FEC, register dumps, interrupt coalescing, channel and ring sizing, RSS, timestamp capabilities, module EEPROM reads, and extensive per-queue/MAC statistics. It is the user-facing configuration and diagnostics layer over state maintained in `struct funeth_priv` and hardware admin port resources.

## Important APIs and Functions
`fun_set_ethtool_ops()` installs `fun_ethtool_ops`. Link helpers translate Fungible port capability bits to ethtool link modes and back (`fun_link_modes_to_ethtool()`, `fun_advert_modes()`, `fun_speed_to_link_mode()`). `fun_get_link_ksettings()` snapshots asynchronous link fields under `link_seq`; `fun_set_link_ksettings()`, `fun_set_pauseparam()`, `fun_restart_an()`, `fun_set_fecparam()`, and `fun_set_phys_id()` issue `fun_port_write_cmd()` updates. Queue controls include `fun_set_coalesce()`, `fun_set_channels()`, and `fun_set_ringparam()`, which call live queue replacement/resizing helpers in `funeth_main.c`. RSS is handled by `fun_get_rxfh()` and `fun_set_rxfh()` using `fun_config_rss()`.

## Control Flow
Most setters validate ethtool inputs against hardware capability bits before issuing admin commands. Channel changes call `fun_change_num_queues()` when the netdev is running, otherwise they update real queue counts directly. Ring depth changes require powers of two and minimum depth, then use `fun_replace_queues()` for live disruptive replacement before committing new depths to `fp`. RSS updates are applied immediately when the port is running and cached in `fp->rss_key`, `fp->indir_table`, and `fp->hash_algo` for later open.

## State and Persistence
Persistent driver state includes advertised link bits, RSS key/LUT, queue depths, coalescing values, message level, hardware timestamp config, and TLS counters. Statistics combine DMA-backed MAC counters (`fp->stats`) with synchronized per-queue `u64_stats_sync` counters and aggregate totals. The code assumes RTNL protection for ethtool callbacks that dereference live queue arrays.

## Dependencies and Integration Points
Depends on `fun_port.h` admin keys, `funeth_txrx.h` queue statistics, PCI BAR register layout compatible with NVMe register offsets, and ethtool kernel APIs. Integration with `funeth_main.c` is tight: queue resizing and RSS mutation rely on queue arrays and hardware RSS ids managed there.

## Risks and Test Signals
Key risks are partial live queue replacement failure, RSS indirection entries referencing removed queues, invalid FEC/pause capability combinations, stats string/count mismatches, and DMA stats area size consistency. Test with `ethtool -k/-c/-C/-l/-L/-g/-G/-x/-X/-S`, link mode and FEC changes on physical ports, virtual-port unsupported-operation paths, XDP enabled while collecting stats, and module EEPROM reads on physical ports only.
