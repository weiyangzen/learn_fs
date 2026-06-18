# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_ethtool.c

## Purpose
`vmxnet3_ethtool.c` implements vmxnet3's ethtool and stats surface. It reports driver/device/queue statistics, register dumps, WOL, link settings, ring sizes, RSS indirection and hash-field controls, coalescing modes, channel counts, and netdev feature reconciliation for checksum, LRO, VLAN, and tunnel offloads.

## Important APIs, Types, And Functions
`struct vmxnet3_stat_desc` maps labels to stat offsets. Exported/support functions include `vmxnet3_get_stats64()`, `vmxnet3_fix_features()`, `vmxnet3_features_check()`, `vmxnet3_set_features()`, and `vmxnet3_set_ethtool_ops()`. The static ethtool table wires stats, register dump, WOL, ringparam, RSS, coalesce, link settings, and channel callbacks.

## Control Flow
Stats issue `VMXNET3_CMD_GET_STATS` under `cmd_lock` and then read coherent queue stats plus driver counters. Feature reconciliation prevents LRO without RX checksum or with XDP, validates encapsulated offloads by tunnel port/revision, updates UPT feature bits, toggles DCR capabilities for rev7+, and sends `VMXNET3_CMD_UPDATE_FEATURE`. Ring changes validate size/alignment/revision requirements; while running they quiesce/reset, destroy and recreate queues, reactivate, or force close on unrecoverable failure. RSS and coalescing setters validate ethtool requests, update cached adapter state, and send device commands when running.

## State And Persistence
The file updates `adapter->wol`, `rss_fields`, `default_rss_fields`, `dev_caps`, `coal_conf`, `default_coal_mode`, queue ring sizes, data-ring descriptor size, and netdev feature bitmaps. Running-device changes are persisted through shared memory and BAR commands; down-device changes are cached for activation.

## Dependencies And Integration Points
Depends on ethtool, vmxnet3 shared ABI commands, netdev features, VXLAN/Geneve constants, optional RSS under `CONFIG_PCI_MSI`, XDP state checks, and lifecycle helpers in `vmxnet3_drv.c`.

## Risks
Stats offset tables must match ABI struct layout. Register dump format is versioned and needs userspace coordination. Ring resize tears down live queues and can close the interface on OOM. Offload negotiation spans netdev flags, UPT bits, DCR/PTCR capabilities, and revision checks; partial acceptance requires readback.

## Test Signals
Exercise `ethtool -S/-d/-k/-K/-g/-G/-c/-C/-l/-x/-X`, RSS hash-field controls, RXCSUM/LRO/XDP combinations, VXLAN/Geneve offloads, ring changes while up/down, WOL modes, and unsupported option error paths.
