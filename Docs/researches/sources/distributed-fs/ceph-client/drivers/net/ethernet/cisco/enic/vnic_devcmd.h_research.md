# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/vnic_devcmd.h

## Purpose
`vnic_devcmd.h` defines the Cisco vNIC firmware command ABI: command encoding macros, command IDs, status/error values, firmware info and notify structures, filter TLVs, devcmd/devcmd2 register/ring formats, overlay feature constants, and feature-version enums.

## Important APIs, types, and functions
- `_CMDC*` macros pack command number, vNIC type, flags, and host-visible direction into `enum vnic_devcmd_cmd` values.
- Command IDs cover firmware info, device-specific config, stats, packet filters, MAC/VLAN, RSS, reset/open/init/enable/deinit, capability, proxy, provisioning, devcmd2 initialization, filters, queue-pair commands, feature versions, overlay offloads, and CQ entry size selection.
- `enum vnic_devcmd_status` and `enum vnic_devcmd_error` define firmware completion state and firmware errno values.
- `struct vnic_devcmd_fw_info` and `struct vnic_devcmd_notify` define coherent command data shared with firmware.
- Filter structures (`struct filter`, `filter_tlv`, `filter_action`) define classifier command payloads.
- `struct vnic_devcmd` is the legacy MMIO command block; `struct vnic_devcmd2` and `struct devcmd2_result` are the ring-based transport descriptors.

## Control flow and state
The header has no executable logic but encodes command semantics that control `vnic_dev.c`. Direction bits drive whether host writes args, reads results, or both. `NOWAIT` flags allow asynchronous/no-result operation. Devcmd2 result color and completed index are part of the transport state machine.

## Dependencies and integration points
Firmware, `vnic_dev.c`, and ENIC resource/configuration code must agree on these packed values and structures. This file also feeds `vnic_nic.h` capability use through `CMD_NIC_CFG` and ENIC extended CQ negotiation through `CMD_CQ_ENTRY_SIZE_SET`.

## Risks and test signals
This is a hardware/firmware ABI header, so any command-number, direction, struct layout, endian, or packed-size change can break device initialization. Test signals include command capability negotiation, devcmd1/devcmd2 interoperability, classifier add/delete, overlay offload setup, RSS and CQ entry-size capability handling, and compatibility with older firmware command variants.
