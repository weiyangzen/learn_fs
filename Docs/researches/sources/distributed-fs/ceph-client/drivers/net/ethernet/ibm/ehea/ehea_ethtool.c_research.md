# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_ethtool.c

Purpose: Provides ethtool operations for eHEA netdevices: link settings, driver info, message level, driver-private statistics, and autonegotiation restart.

Important APIs and functions: `ehea_get_link_ksettings()` refreshes port attributes through `ehea_sense_port_attr()`, converts eHEA speed/duplex state to ethtool `SPEED_*` and `DUPLEX_*`, and populates supported/advertising link modes. `ehea_set_link_ksettings()` maps requested ethtool speed/duplex/autoneg settings to PHYP speed constants and calls `ehea_set_portspeed()`. `ehea_nway_reset()` requests autonegotiation. `ehea_get_drvinfo()`, `ehea_get_msglevel()`, and `ehea_set_msglevel()` expose metadata and debug mask state. `ehea_get_strings()`, `ehea_get_sset_count()`, and `ehea_get_ethtool_stats()` expose 24 statistics including reset count, checksum errors, receive errors, queue stops, and per-port-resource free SWQEs. `ehea_set_ethtool_ops()` installs the static ops table.

Control flow: `ehea_setup_single_port()` calls `ehea_set_ethtool_ops()` before registering the netdev. Userspace ethtool calls enter this file, then delegate hardware-sensitive operations to `ehea_main.c` helpers that perform PHYP queries/modifications. Statistics are aggregated over `EHEA_MAX_PORT_RES`, not only active queues, with inactive queue counters reading as zero.

State and persistence: Reads and writes runtime `struct ehea_port` fields: `port_speed`, `full_duplex`, `autoneg`, `msg_enable`, `sig_comp_iv`, `resets`, and each `port_res[].p_stats`/`swqe_avail`. No persistent storage. `set_msglevel` persists only for the lifetime of the netdev.

Dependencies and integration: Depends on `ehea.h`, `ehea_phyp.h`, ethtool link-mode conversion helpers, and netdevice carrier state. It integrates tightly with PHYP-backed port sensing and speed modification.

Risks: `ehea_get_link_ksettings()` reports different supported modes based on the current sensed speed; unusual hardware may have capabilities broader than the current link. `ehea_set_link_ksettings()` rejects half-duplex 1G/10G but relies on PHYP for authority checks. Stats read concurrent counters without locking, so values are approximate.

Test signals: `ethtool <dev>`, `ethtool -s` for autoneg/10/100/1000/10000 combinations, permission-denied speed changes from hypervisor, `ethtool -S` after RX/TX/checksum errors, and msglevel get/set round trips.
