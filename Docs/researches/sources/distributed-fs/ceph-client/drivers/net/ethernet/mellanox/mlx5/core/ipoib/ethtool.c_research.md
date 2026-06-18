# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ipoib/ethtool.c

## Purpose
`ipoib/ethtool.c` adapts mlx5 Ethernet ethtool operations to IPoIB netdevices. Most handlers delegate to shared `mlx5e` helpers, while link settings and RX flow validation account for InfiniBand/IPoIB semantics.

## Important APIs, Types, And Functions
- `mlx5i_get_drvinfo`, strings, stats, ringparam, channels, coalesce, timestamp, flash, RSS hash fields, RX NFC, and RX ring count wrap `mlx5e_ethtool_*` helpers using `mlx5i_epriv`.
- `mlx5i_set_channels` rejects channel-count changes while parent IPoIB devices have subinterfaces.
- `mlx5i_get_link_ksettings` queries IB operational width/rate and converts them to ethtool speed/duplex/port/autoneg values.
- `mlx5i_set_rxnfc` rejects `ETHER_FLOW` rules because IPoIB traffic is not Ethernet L2 in the normal sense.
- Exports `mlx5i_ethtool_ops` for parent IPoIB devices and `mlx5i_pkey_ethtool_ops` for child pkey devices.

## Control Flow And State
Etntool calls arrive through the netdev's `ethtool_ops`. Parent devices get broad control over ring/channel/coalesce/RSS/NFC/link settings. Pkey child devices expose only driver info, link state, and timestamp info. Channel changes require RTNL and check `num_sub_interfaces` to avoid breaking child devices sharing parent resources.

## Dependencies And Integration Points
The file depends on `en.h`, `ipoib.h`, `en/fs_ethtool.h`, mlx5e ethtool helpers, IB port operational query, and kernel ethtool structures. It integrates IPoIB netdevs with standard user tools such as `ethtool -S`, `-l`, `-L`, `-c`, `-K`-adjacent stats, flash, and flow steering.

## Risks And Edge Cases
IB width/rate enum conversion must stay current with new link rates. Parent channel reconfiguration while children exist is explicitly blocked; missing RTNL coverage would race child init/uninit. Delegated Ethernet helpers may expose settings that are only partially meaningful for IPoIB, so IPoIB-specific rejection paths matter.

## Test Signals
Run ethtool stats, ring, channel, coalesce, timestamp, RSS hash field, RX NFC, flash, and link-settings commands on parent and pkey devices. Validate speed for SDR through XDR widths, `ETHER_FLOW` rejection, and channel-change rejection when subinterfaces exist.
