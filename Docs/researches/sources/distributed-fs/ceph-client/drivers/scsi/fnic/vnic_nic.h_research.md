# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_nic.h

## Purpose

`vnic_nic.h` provides a small helper for packing Cisco vNIC NIC configuration bits, mainly RSS, TSO IPID split, and ingress VLAN strip settings.

## Important APIs, types, and data

- `NIC_CFG_*` masks and shifts define fields for RSS default CPU, RSS hash type, RSS hash bits, RSS base CPU, RSS enable, TSO IPID split enable, and ingress VLAN strip enable.
- `vnic_set_nic_cfg()` packs caller-provided values into a 32-bit NIC configuration word.
- The generic helper name is aliased to `fnic_set_nic_cfg` to avoid symbol clashes.

## Control flow

Callers pass desired field values and receive a packed configuration word suitable for a firmware command or NIC config register.

## State and persistence behavior

The header owns no state. The packed value persists only when written by a caller to firmware/hardware.

## Dependencies and integration points

It is shared vNIC NIC configuration code. FNIC may use it when configuring Ethernet/FCoE-facing vNIC behavior.

## Risks and edge cases

- Inputs are masked and silently truncated.
- The helper only builds the word; it does not validate whether a feature is supported by the current firmware.

## Test signals

Encode tests should verify each field's shift and truncation behavior. Firmware tests should validate that the resulting NIC configuration produces expected RSS/offload/VLAN behavior.
