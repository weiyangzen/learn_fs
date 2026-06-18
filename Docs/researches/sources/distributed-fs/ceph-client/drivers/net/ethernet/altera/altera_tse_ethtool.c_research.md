# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_tse_ethtool.c

Purpose: this file exposes ethtool operations for the Altera TSE netdev. It reports driver/firmware identity, dumps the first 128 MAC registers, exports 31 hardware statistics counters, controls the netdev debug message level, delegates link settings to phylink, and reports timestamping information through the generic helper.

Important APIs, types, and functions: `stat_gstrings` names the ethtool statistics. `tse_get_drvinfo()` reads `megacore_revision` and formats the driver and firmware version. `tse_fill_stats()` reads MAC MIB/RMON counters, including extended 64-bit octet counters assembled from MSB and LSB registers. `tse_get_regs()` returns a versioned 128-register dump. `tse_ethtool_set_link_ksettings()` and `tse_ethtool_get_link_ksettings()` call phylink. `tse_ethtool_ops` wires these callbacks into ethtool, and `altera_tse_set_ethtool_ops()` assigns them to the netdev.

Control flow: probe calls `altera_tse_set_ethtool_ops()` after netdev setup. User ethtool requests enter the relevant callbacks. Statistics and register reads directly sample `priv->mac_dev` through the CSR helpers. Link ksettings are not interpreted locally; they are forwarded to `priv->phylink`, which coordinates with the PHY or PCS.

State and persistence: the only software state modified here is `priv->msg_enable` through get/set message-level callbacks. All statistics are hardware counters in the MAC CSR block and are not cached in the driver. Register dump version is fixed at `1`, documenting the current 128-register layout.

Dependencies and integration points: the file depends on `altera_tse.h`, Linux ethtool, netdevice, PHY, and phylink APIs. It assumes the MAC register block is mapped and powered enough for CSR reads when ethtool calls arrive. It also relies on the main driver to initialize `priv->phylink`.

Risks: statistics are sampled as separate MMIO reads, so extended 64-bit counters can race rollover between MSB and LSB reads. `tse_gstrings()` ignores `stringset` and copies stats strings unconditionally, relying on ethtool to call it only for supported sets. Register dumps expose raw hardware state and can fault or return stale values if called during teardown or while clocks are gated. Link setting behavior depends entirely on phylink setup correctness in the main file.

Test signals: useful checks include `ethtool -i` showing `altera_tse` and a revision, `ethtool -S` returning all 31 named counters, `ethtool -d` returning 512 bytes with version `1`, message-level get/set changing debug output, link ksettings changing through phylink, and clean behavior when the interface is down.
