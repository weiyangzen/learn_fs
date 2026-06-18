# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_nic.h

## Purpose
`vnic_nic.h` defines the packed NIC configuration word used by Cisco vNIC firmware for RSS, TSO IP ID splitting, and ingress VLAN stripping.

## Important APIs, types, and functions
- Field masks/shifts cover RSS default CPU, RSS hash type, RSS hash bits, RSS base CPU, RSS enable, TSO IPID split enable, and ingress VLAN strip enable.
- `NIC_CFG_RSS_HASH_TYPE_*` values enumerate UDP/IP/TCP IPv4/IPv6 hash type bits.
- `vnic_set_nic_cfg()` packs caller-supplied values into a `u32` command argument.

## Control flow and state
The inline function is used before issuing `CMD_NIC_CFG` or `CMD_NIC_CFG_CHK`. It does not retain state; the resulting word becomes firmware state after a successful devcmd.

## Dependencies and integration points
`enic_set_nic_cfg()` in `enic_res.c` uses this helper. Firmware capability reporting for `CMD_NIC_CFG` determines which hash-type bits are legal.

## Risks and test signals
Mask/shift errors change RSS behavior or VLAN stripping. Test RSS indirection behavior, UDP RSS capability fallback, checksum/offload interactions, and firmware rejection through `CMD_NIC_CFG_CHK`.
