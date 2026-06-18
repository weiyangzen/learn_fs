<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bonding.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_bonding.h

## Purpose
`if_bonding.h` defines userspace constants and structures for Linux bonding driver modes, link states, MII monitor results, LACP state, and legacy bonding ioctls.

## Important APIs, types, and functions
The header exports `BOND_ABI_VERSION`, old private ioctl numbers for enslave/release/sethwaddr/info/change-active, `BOND_CHECK_MII_STATUS`, bond modes such as round-robin, active-backup, XOR, broadcast, 802.3ad, TLB, and ALB, link and slave states, default max bonds/tx queues/resend IGMP values, transmit hash policy constants, and LACP state bits. Structures include `ifbond` for aggregate mode/miimon/slave count, `ifslave` for slave id/name/link/state/failure count, and `struct ad_info` for 802.3ad aggregator details. Xstats enums expose bond and 802.3ad statistic attributes.

## Control flow
User space creates/configures a bond, enslaves or releases lower devices, queries bond/slave state, and sets hardware address through legacy ioctls or newer netlink/sysfs paths. The bonding driver then applies mode-specific transmit selection, failover control, and optional 802.3ad aggregation.

## State and persistence behavior
Bond mode, hash policy, slave list, LACP state, link monitoring, active slave, 802.3ad aggregator information, xstats, and failure counters are live bond-device state and often persisted by network configuration tools.

## Dependencies and integration points
It integrates with netdevice ioctls, rtnetlink bonding attributes, sysfs bonding controls, switch LACP peers, and network managers.

## Risks and test signals
Risks include legacy ioctl/netlink divergence, invalid mode/slave combinations, MAC address changes during enslave/release, LACP state mismatch, xstats schema drift, and failover races. Test signals include bond mode creation, enslave/release cycles, link-down failover, LACP partner tests, hash policy packet distribution, ioctl query compatibility, 802.3ad xstats dumps, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_bonding.h -->
