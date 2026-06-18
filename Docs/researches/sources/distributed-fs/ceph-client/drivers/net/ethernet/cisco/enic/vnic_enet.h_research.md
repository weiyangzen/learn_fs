# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_enet.h

## Purpose
`vnic_enet.h` defines the firmware-provided ENIC Ethernet configuration region and feature/interrupt constants.

## Important APIs, types, and functions
- `struct vnic_enet_config` contains flags, WQ/RQ descriptor counts, MTU, interrupt timer/mode/type fields, device name, loop tag, VF RQ count, aRFS count, maximum RQ/WQ/CQ ring sizes, and reserved RDMA LKey.
- `VENETF_*` feature bits advertise TSO, LRO, RX/TX checksum, RSS hash types, loopback, and VXLAN.
- `VENET_INTR_TYPE_*` and `VENET_INTR_MODE_*` encode firmware interrupt preferences.

## Control flow and state
The structure is read field-by-field through `CMD_DEV_SPEC` in `enic_get_vnic_config()`. Its values seed persistent ENIC configuration state and constrain resource allocation and netdev feature setup.

## Dependencies and integration points
It integrates firmware configuration with `enic_res.c`, `enic.h`, and netdev feature decisions. The `ENIC_SETTING()` macro in `enic_res.h` consumes the flags defined here.

## Risks and test signals
Layout drift is the core risk because offsets are used for firmware reads. Test with devices reporting default/zero ring maxima, unusual MTUs, RSS/VXLAN flags, and different interrupt-mode requests.
