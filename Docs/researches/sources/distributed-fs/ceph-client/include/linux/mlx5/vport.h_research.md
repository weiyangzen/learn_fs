# sources/distributed-fs/ceph-client/include/linux/mlx5/vport.h

## Purpose
This header exposes mlx5 virtual port management APIs for PF/VF/ECPF/uplink contexts. It covers vport state, MAC/GUID/MTU/min-inline settings, speeds, RoCE enablement, lists and promiscuity, VLANs, counters, HCA vport attributes, multiport affiliation, local loopback, and other-function capabilities.

## Important APIs, Types, And Data
- `MLX5_VPORT_MANAGER(mdev)` tests whether a device is an Ethernet PF with vport group manager capability.
- Vport ids identify PF (`0`), first VF (`1`), ECPF (`0xfffe`), and uplink (`0xffff`).
- Inline mode constants describe L2, vport-context, and not-required modes.
- Query/modify functions cover vport admin state, max TX speed, MAC address, min inline, MTU, system image GUID, SD group, node GUID, QKey violation counter, GID/PKey/HCA contexts, MAC lists, promiscuity, VLAN lists, down stats, vport counters, HCA vport context, local loopback, multiport affiliation, system image GUID, other function caps, and VHCA id.
- RoCE helpers enable or disable RoCE on the NIC vport.

## Control Flow
PF management and eswitch code first checks manager capability, then queries target vport state and capabilities, applies configuration through modify calls, and reads counters or stats for monitoring. VF and other-vport operations pass `other_vport`/`vf_num`/`vport` selectors. Multiport affiliation links a master device with a port device and later unaffiliates during teardown.

## State And Persistence
Vport configuration is firmware-resident and can affect link behavior, packet steering, RDMA identity, and VF presentation. Driver state tracks the relevant `mlx5_core_dev` and target vport ids, while the header only declares interfaces and constants.

## Dependencies And Integration Points
The file includes `linux/mlx5/driver.h` and `linux/mlx5/device.h` for device, capability, list type, and HCA context definitions. It integrates with SR-IOV, eswitch, representors, netdev address/MTU setup, RDMA GID/PKey handling, devlink, and multiport devices.

## Risks
Most APIs operate on firmware state for a selected vport; incorrect `other_vport`, VF number, or uplink/PF id can change the wrong function. Capability checks are required before manager-only operations. MAC/VLAN list sizes must match firmware limits. RoCE and GUID changes can affect RDMA users. Multiport affiliation must handle device removal and rollback.

## Test Signals
Tests should cover PF manager detection, PF/VF/uplink vport state queries, MAC/MTU/min-inline update and readback, max TX speed changes, MAC list and promiscuity programming, VLAN list updates, RoCE enable/disable, GID/PKey queries, vport counter reads, local loopback toggles, VHCA id lookup, and multiport affiliate/unaffiliate teardown.
