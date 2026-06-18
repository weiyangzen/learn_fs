# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_ethtool.c

## Purpose

`en_ethtool.c` is the mlx5e Ethernet driver's primary implementation of Linux `ethtool_ops`. It translates user-facing ethtool operations into mlx5 channel parameter updates, RSS/RXFH programming, port register queries, link-mode programming, stats collection, module EEPROM access, FEC control, Wake-on-LAN programming, private feature flags, and physical link diagnostics. The file is not a standalone subsystem; it is the netdev control surface for `struct mlx5e_priv`, `struct mlx5_core_dev`, `priv->channels.params`, `priv->rx_res`, and mlx5 port-management helpers.

## Important APIs, Types, And Functions

The file publishes `const struct ethtool_ops mlx5e_ethtool_ops`, whose callbacks are installed by the mlx5e netdev layer. Public helper entry points such as `mlx5e_ethtool_get_drvinfo`, `mlx5e_ethtool_get_sset_count`, `mlx5e_ethtool_get_strings`, `mlx5e_ethtool_get_ethtool_stats`, `mlx5e_ethtool_get_ringparam`, `mlx5e_ethtool_set_ringparam`, `mlx5e_ethtool_get_channels`, `mlx5e_ethtool_set_channels`, `mlx5e_ethtool_get_coalesce`, `mlx5e_ethtool_set_coalesce`, `mlx5e_ethtool_get_ts_info`, `mlx5e_ethtool_get_rxfh_key_size`, `mlx5e_ethtool_get_rxfh_indir_size`, and `mlx5e_ethtool_flash_device` are thin enough to be reused by profile-specific wrappers. Static netdev callbacks usually fetch `priv = netdev_priv(dev)` and delegate to those helpers.

Link-mode translation uses `struct ptys2ethtool_config`, `ptys2legacy_ethtool_table`, `ptys2ext_ethtool_table`, and `mlx5e_build_ptys2ethtool_map()`. This table maps mlx5 PTYS protocol bits to ethtool link mode bitmaps for both legacy and extended modes, including modern 100G/200G/400G/800G/1600G encodings. `mlx5e_ethtool_get_link_ksettings()` queries PTYS, pause, connector, FEC, and partner advertisement state; `mlx5e_ethtool_set_link_ksettings()` converts ethtool advertising or forced speed/lane settings back into PTYS admin bits and toggles the port link after programming.

RSS and classifier integration is split between RXFH callbacks and RXNFC callbacks. `mlx5e_get_rxfh()`, `mlx5e_set_rxfh()`, `mlx5e_create_rxfh_context()`, `mlx5e_modify_rxfh_context()`, and `mlx5e_remove_rxfh_context()` operate on `priv->rx_res`; `mlx5e_get_rxnfc()` and `mlx5e_set_rxnfc()` delegate rule handling to `en_fs_ethtool.c` through `mlx5e_ethtool_get_rxnfc()` and `mlx5e_ethtool_set_rxnfc()`. `mlx5e_get_rxfh_fields()` and `mlx5e_set_rxfh_fields()` similarly bridge to hash-field helpers implemented outside this file.

Private flags are described by `struct pflag_desc mlx5e_priv_flags[]`. The handlers include CQE-based moderation toggles, RX CQE compression, striding RQ, RX checksum-complete suppression, XDP/SKB MPWQE TX, and TX port timestamping. `mlx5e_set_priv_flags()` serializes changes under `priv->state_lock`, invokes each changed flag handler through `mlx5e_handle_pflag()`, updates `priv->channels.params.pflags`, and refreshes netdev features.

Other notable control functions include coalescing helpers that use DIM state and CQ moderation registers, PFC storm prevention tunables, pause parameters, WOL conversion between Linux and mlx5 bit definitions, FEC conversion between PPLM and ethtool values, module EEPROM readers, firmware flashing, LED physical ID, and extended link-state mapping from PDDR troubleshooting status opcodes to `struct ethtool_link_ext_state_info`.

## Control Flow

Most get operations read cached driver state or query firmware registers, then return ethtool-shaped values. Stats callbacks lock `priv->state_lock` only around `mlx5e_stats_update()` and then fill the supplied array. Ring, channel, coalesce, private-flag, RSS, and tunable setters validate user input, acquire `priv->state_lock`, clone `priv->channels.params`, mutate the clone, and call `mlx5e_safe_switch_params()` when the change requires reopening or reconfiguring channels.

Channel changes have explicit guards before switching: zero channels are rejected; XOR RSS cannot exceed the XOR8 channel limit; configured RXFH blocks changes that would resize the RSS table; HTB offload and MQPRIO channel mode block changes because queue numbering is externally visible. If aRFS is active, the setter disables aRFS before switching channels and attempts to re-enable it afterward.

Coalescing follows two paths. Global coalescing updates `new_params`, resets DIM/CQ moderation when period mode or adaptive state changes, applies moderation to existing channels, changes DIM state, then switches params without a full channel reset when possible. Per-queue coalescing directly modifies one channel's RX CQ and each TX CQ after toggling per-queue DIM state.

Link setting is register-driven: the setter chooses legacy versus extended PTYS mode from hardware support, requested advertisement, and autoneg state; converts ethtool bits to PTYS protocol bits or forced-speed info; intersects with hardware capability; checks special constraints such as 56G requiring autoneg; programs `mlx5_port_set_eth_ptys()`; then calls `mlx5_toggle_port_link()`.

RXFH context creation initializes an RSS object for the requested context, applies indir/key/hash function and symmetric transform settings, then reads the resulting values back into the ethtool context. Set/modify/remove operations are serialized by `state_lock` and update only `priv->rx_res`; RXNFC rules are delegated to the flow-steering ethtool module.

## State And Persistence

Persistent state here means driver memory and NIC firmware/hardware state, not filesystem persistence. The central software state is `priv->channels.params`, including queue sizes, channel count, moderation parameters, DIM enablement, private flags, packet merge settings, MPWQE flags, and timestamp-related fields. Hardware state is programmed through mlx5 port and CQ helpers: PTYS, pause, WOL, FEC, PFC stall watermark, module EEPROM reads, firmware flash, LED beacon, and CQ moderation. RSS state lives in `priv->rx_res` and can include multiple ethtool RXFH contexts.

`priv->state_lock` is the primary serialization mechanism for mutable channel/RSS state. Some port-management operations are not protected by this lock if they operate directly on firmware registers and do not mutate shared channel data. Netdev feature state is refreshed with `netdev_update_features()` after changes that affect advertised software features.

## Dependencies And Integration Points

This file depends on Linux ethtool/netdev APIs, `linux/dim.h`, mlx5 core port helpers, firmware flash helpers, stats helpers, RSS resource helpers, PTP support, channel parameter validation/switching, and `en_fs_ethtool.h` for RXNFC/RXFH field delegation. It is tightly coupled to `en_fs.c` and `en_fs_ethtool.c` through `priv->fs`, RX classifier callbacks, and timestamp/PTP flow-steering management. It also integrates with HTB, MQPRIO, XDP, HW-GRO/packet merge, WOL, FEC, and module EEPROM infrastructure.

## Risks And Edge Cases

The PTYS-to-ethtool map must be initialized before link-mode queries; stale or missing mapping entries can silently hide supported speeds. Link-mode conversion is subtle because extended and legacy PTYS admin fields are mutually exclusive, and forced mode uses a different conversion path than autoneg advertisement. Channel resizing is intentionally blocked in several externally visible configurations, but new queue-using features must add similar guards to avoid breaking qdisc or RSS assumptions.

Private flags have cross-feature constraints: RX CQE compression conflicts with HW-GRO/SHAMPO and can interact with hardware timestamping/PTP RX flow steering; TX port timestamping conflicts with HTB and MQPRIO channel mode; striding RQ cannot be disabled while HW-GRO/LRO packet merge is active. Some handlers update hardware state before `mlx5e_safe_switch_params()` returns, so rollback behavior depends on lower-layer switch semantics. FEC setting accepts only one ethtool FEC bit; unsupported combinations return `-EOPNOTSUPP`. EEPROM readers loop until the requested length is satisfied or hardware returns zero, so status/error handling is a useful failure signal.

## Test Signals

Useful runtime tests are ethtool get/set coverage for `-g/-G`, `-l/-L`, `-c/-C`, per-queue coalesce, `-k/-K` feature interactions, `--show-priv-flags/--set-priv-flags`, `-x/-X` and RXFH contexts, `-n/-N` RXNFC rules, `--show-fec/--set-fec`, pause, WOL, module EEPROM, and forced/autoneg link settings on hardware with both legacy and extended PTYS support. Negative tests should assert extack or errno paths for unsupported capabilities, invalid queue counts, RXFH table resize attempts, HTB/MQPRIO blockers, FEC multi-bit requests, and CQE compression plus HW-GRO/PTP conflicts. No local executable tests were run for this research item.
