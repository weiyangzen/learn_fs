## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.c

Purpose: supplies v2 ethtool operations for driver information, PHY-backed link settings, statistic names, statistic values, and link reporting.

Important APIs, types, and functions: `struct xge_gstrings_stats` maps generic netdev stats to offsets in `rtnl_link_stats64`; `struct xge_gstrings_extd_stats` maps hardware statistic names to register addresses. `xge_get_drvinfo` reports driver name `xgene_enet`. `xge_get_link_ksettings` and `xge_set_link_ksettings` delegate to PHYLIB. `xge_get_strings`, `xge_get_sset_count`, and `xge_get_ethtool_stats` expose basic and extended counters. `xge_set_ethtool_ops` installs the static `ethtool_ops`.

Control flow, state, and persistence: ethtool reads netdev statistics through `dev_get_stats`, then reads hardware counters directly from CSR offsets. There is no accumulation array in v2, so values reflect current hardware counter reads plus software stats maintained in `main.c`.

Dependencies and integration points: depends on `ethtool.h` register constants, `xge_rd_csr`, `get_stats64` in `main.c`, and PHY device setup in `mdio.c`. It is installed during probe before netdev registration.

Risks: direct hardware reads may clear or wrap counters depending on hardware behavior; the code does not mask all widths. Link settings fail with `-ENODEV` if the PHY did not attach. The driver string differs from the module name, which can confuse tests that expect `xgene-enet-v2`.

Test signals: `ethtool -i`, `ethtool <dev>`, `ethtool -S`, and `ethtool -s` via PHY should work. Traffic should increment both software and hardware counters.
