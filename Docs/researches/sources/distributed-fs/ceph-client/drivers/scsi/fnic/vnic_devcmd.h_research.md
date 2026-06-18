# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_devcmd.h

## Purpose

`vnic_devcmd.h` defines the firmware command ABI for Cisco vNIC devices. It encodes command number, vNIC type, flags, direction, status/error codes, legacy MMIO command registers, and devcmd2 descriptor/result formats.

## Important APIs, types, and data

- `_CMDC()` and `_CMDCNW()` build commands from direction, vNIC type, flags, and command number.
- `_CMD_DIR()`, `_CMD_FLAGS()`, `_CMD_VTYPE()`, and `_CMD_N()` decode command fields.
- `enum vnic_devcmd_cmd` lists commands for firmware info, device spec, stats, packet filters, MAC/address/VLAN, reset/open/init/enable, notification, capabilities, persistent binding, default VLAN, devcmd2 initialization, and other vNIC features.
- `enum vnic_devcmd_status` and `enum vnic_devcmd_error` define status and firmware error values.
- `struct vnic_devcmd_fw_info`, `struct vnic_devcmd_notify`, and `struct vnic_devcmd_provinfo` define command payloads.
- `struct vnic_devcmd` is the legacy MMIO register block.
- `struct vnic_devcmd2` and `struct devcmd2_result` define the queued command interface.

## Control flow

Command users build or select an enum value and pass it with up to 15 arguments to `vnic_dev_cmd()`. The implementation writes arguments for host-to-device commands, posts the command, polls or returns immediately for no-wait commands, and reads arguments for device-to-host commands. Devcmd2 carries the same command enum in WQ descriptors and reads results from a host result ring.

## State and persistence behavior

The header defines on-wire and MMIO layouts only. Persistent command state lives in firmware, MMIO registers, coherent command/result rings, and notification buffers.

## Dependencies and integration points

This ABI is shared by `vnic_dev.c`, queue setup, firmware, and potentially multiple Cisco drivers. The vNIC type bits allow commands to be scoped to Ethernet, FC, SCSI, or all.

## Risks and edge cases

- Command comments are the contract; implementation and firmware must agree on argument sizes and directions.
- `_CMD_NBITS`, `_CMD_VTYPEBITS`, `_CMD_FLAGSBITS`, and `_CMD_DIRBITS` define a packed ABI; changing them would break firmware compatibility.
- Some commands are deprecated but remain defined for compatibility.
- Devcmd2 result errors are stored in an 8-bit field, so error-code space is limited.

## Test signals

Compile-time checks should validate structure sizes and command encoding. Runtime tests should query `CMD_CAPABILITY`, exercise representative read/write/nowait commands, and verify devcmd2 initialization and result color handling.
