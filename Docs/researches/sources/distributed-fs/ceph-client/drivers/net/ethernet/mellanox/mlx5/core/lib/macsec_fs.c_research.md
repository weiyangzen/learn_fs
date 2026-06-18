# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/macsec_fs.c

## Purpose
`macsec_fs.c` builds the mlx5 MACsec flow-steering implementation for Ethernet and RoCE traffic. It creates TX/RX crypto and validation tables, installs per-SA encrypt/decrypt rules, manages packet reformat and metadata actions, tracks MACsec security-association IDs, exposes counter reads, and publishes notifier events so RoCE MACsec rules can be synchronized with SA lifetime.

## Important APIs, types, and functions
The public entry points are `mlx5_macsec_fs_init()`, `mlx5_macsec_fs_cleanup()`, `mlx5_macsec_fs_add_rule()`, `mlx5_macsec_fs_del_rule()`, `mlx5_macsec_fs_get_stats_fill()`, `mlx5_macsec_fs_get_stats()`, `mlx5_macsec_fs_get_fs_id_from_hashtable()`, and exported RoCE helpers `mlx5_macsec_add_roce_rule()`, `mlx5_macsec_del_roce_rule()`, `mlx5_macsec_add_roce_sa_rules()`, and `mlx5_macsec_del_roce_sa_rules()`. Core state is split across `struct mlx5_macsec_fs`, `struct mlx5_macsec_tx`, `struct mlx5_macsec_rx`, `struct mlx5_macsec_tables`, `struct mlx5_macsec_device`, and `struct mlx5_fs_id`. `union mlx5_macsec_rule` stores the caller-owned TX or RX rule handle. The file uses `rhashtable` for SCI and RX fs-id lookups, `xarray` for per-netdev SA IDs, and `ida` for TX fs-id allocation.

## Control flow
Initialization allocates the top-level object, initializes SCI and fs-id rhashtables, creates TX/RX counter containers, initializes the TX ID allocator, and initializes the MACsec notifier head on `mdev`. Flow tables are created lazily on first rule add through `macsec_fs_tx_ft_get()` or `macsec_fs_rx_ft_get()` and destroyed when the corresponding table refcount returns to zero.

TX rule creation allocates the TX tables if needed, builds an ADD_MACSEC packet reformat buffer from `struct macsec_context`, allocates a packet reformat object, allocates a 1-16 interface fs-id, matches WQE metadata register A, sets MACsec crypto object parameters, and forwards encrypted traffic to a check table. The check table allows packets with a clean ASO status and counts drops on the default miss rule. RX rule creation programs metadata register B with a MACsec marker plus fs-id, adds decrypt rules for SCI-present traffic and, for end-station SCIs, source-MAC-based no-SCI traffic, then forwards to the RX check table where the SecTAG is removed and clean packets continue to the next priority or to RoCE dispatch.

RoCE integration creates extra RDMA TX/RX MACsec flow tables when capabilities permit. TX RoCE rules match source IP and write MACsec TX metadata before jumping to the regular MACsec crypto table. RX RoCE rules match destination IP and metadata copied from register B to register C, allowing only packets whose SA metadata matches the expected fs-id.

## State and persistence behavior
All state is in kernel memory and hardware flow-steering objects. There is no disk persistence. Hardware state includes flow tables, groups, rules, counters, modify-header objects, packet reformat objects, and MACsec crypto actions. Software state tracks per-device TX/RX fs-id entries; TX maps SCI to fs-id for datapath lookups, while RX maps fs-id to SCI/SA ownership. Refcounts prevent duplicate RX fs-id objects and release flow tables only after the last SA rule is deleted.

## Dependencies and integration points
The file depends on Linux MACsec types, mlx5 flow steering, packet reformat, modify-header, counters, rhashtable, xarray, IDA, RoCE GID notification lists, and capability helpers such as `mlx5_is_macsec_roce_supported()`. It is consumed by the mlx5 MACsec accelerator path and by RoCE code that adds or removes IP-based MACsec rules as GIDs appear and disappear.

## Risks and edge cases
The highest-risk areas are unwind paths after partial flow-table creation, fs-id refcount symmetry, and RoCE rule cleanup after a partial add failure. TX fs-id allocation supports only 16 interfaces, so exhaustion is a functional limit. RX no-SCI matching depends on the SCI default port convention and source MAC extraction. Counter and table cleanup assumes callers delete all SA rules before final cleanup; otherwise the code logs nonzero table refcounts and leaves objects rather than tearing down live hardware state.

## Test signals
Useful tests include MACsec TX/RX offload add/delete for SCI-present and no-SCI SAs, VLAN MACsec TX reformat offset, interface-count exhaustion, repeated add/delete on the same RX fs-id, stats counter reads for pass/drop paths, RoCE GID add/delete synchronization, hardware capability-disabled RoCE paths, module unload with no leaked table refcounts, and fault injection around flow-table, flow-rule, modify-header, packet-reformat, counter, xarray, and rhashtable allocation failures.
