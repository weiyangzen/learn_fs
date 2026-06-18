# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_port.h

## Purpose
Declares the original HiNIC port-management ABI structures, enums, constants, and public helper prototypes. It is the interface between the netdevice/ethtool/DCB/SR-IOV layers and firmware management commands for MAC, VLAN, link, offload, RSS, stats, pause, loopback, LED, and SFP operations.

## Important APIs And Types
The header defines command payload structs such as `hinic_port_mac_cmd`, `hinic_port_mtu_cmd`, `hinic_port_vlan_cmd`, `hinic_port_link_cmd`, `hinic_port_cap`, `hinic_tso_config`, `hinic_checksum_offload`, `hinic_lro_config`, RSS structures, stats structures, `hinic_pause_config`, `hinic_set_pfc`, loopback/LED/SFP commands, and firmware update payloads. Enums cover Rx mode bits, port/link/function state, speed, link modes, port type, autoneg, duplex, TSO state, LED mode/type, and link-setting valid bits.

## Control Flow And State
No code executes here; it defines persistent command state and exposes functions implemented in `hinic_port.c` and `hinic_main.c`. The structures generally begin with firmware `status/version/rsvd` fields followed by function ID or port-specific configuration. RSS constants define the 40-byte hash key and 256-entry indirection table sizes. Large stats structs mirror firmware counter blocks.

## Dependencies And Integration Points
It includes Linux ethtool/etherdevice/bitops headers and `hinic_dev.h`. `hinic_main.c`, `hinic_port.c`, `hinic_sriov.c`, and ethtool code include it to share command layouts. Because these layouts cross the firmware boundary, compatibility depends on exact field order and size.

## Risks And Test Signals
Main risks are ABI drift, duplicated constants (`STD_SFP_INFO_MAX_SIZE` appears twice), spelling mistakes that propagate into public helpers such as `hinic_set_vlan_fliter()`, and unsupported commands on older firmware. Test signals are compile coverage, ethtool link/settings/stats/RSS tests, VLAN/MAC operations, offload feature toggles, and firmware-version compatibility checks.
