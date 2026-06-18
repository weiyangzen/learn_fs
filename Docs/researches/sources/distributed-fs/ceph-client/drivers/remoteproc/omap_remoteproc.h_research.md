# sources/distributed-fs/ceph-client/drivers/remoteproc/omap_remoteproc.h

## Purpose

`omap_remoteproc.h` defines the mailbox protocol constants shared by OMAP remoteproc firmware and the Linux OMAP remoteproc driver. It is a small protocol header rather than a driver implementation.

## Important APIs, types, and data

- `enum omap_rp_mbox_messages` reserves high mailbox values beginning at `0xFFFFFF00` so protocol messages do not collide with low virtqueue ids.
- Defined messages include remote ready, pending message, crash, echo request/reply, abort request, system and auto suspend requests, suspend ACK, suspend cancel, and `RP_MBOX_END_MSG`.

## Control flow

The header has no control flow. `omap_remoteproc.c` sends echo and suspend messages and interprets incoming crash, echo, suspend ACK/CANCEL, and reserved message ranges using this enum. Firmware must send the same values for Linux to classify messages correctly.

## State and persistence behavior

No software state is stored here. The enum values define persistent ABI between Linux and remote firmware images; changing values would break deployed firmware.

## Dependencies and integration points

The header is included by `omap_remoteproc.c` and should remain synchronized with TI SYS/BIOS or other OMAP remote firmware mailbox implementations. The BSD-3-Clause license header reflects shared firmware-facing ABI usage.

## Risks and edge cases

- `RP_MBOX_END_MSG` must remain last and bounds the range of known control messages in the driver.
- New messages must stay far from valid vring ids. The current high-value convention is the main collision guard.
- Firmware that sends `RP_MBOX_PENDING_MSG` rather than explicit vqid is currently ignored as a known control message; the rest of the IPC stack must match that behavior.

## Test signals

Protocol tests should inject each mailbox value into `omap_rproc_mbox_callback()` and verify crash reporting, echo logging, suspend completion flags, ignored reserved messages, and normal vqid dispatch for values below the reserved range.
