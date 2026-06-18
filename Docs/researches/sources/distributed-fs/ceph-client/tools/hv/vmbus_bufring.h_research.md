# sources/distributed-fs/ceph-client/tools/hv/vmbus_bufring.h

## Purpose

`vmbus_bufring.h` defines the user-space ABI structures and constants used by `vmbus_bufring.c` for Hyper-V VMBus ring buffers, channel packets, and integration-component message negotiation.

## Important APIs and Types

The header defines packet types and flags such as `VMBUS_CHANPKT_TYPE_INBAND`, `VMBUS_CHANPKT_FLAG_RC`, and `VMBUS_CHANPKT_HLEN_MIN`. `struct vmbus_bufring` mirrors the shared ring header, including volatile write/read indexes, interrupt mask, pending-send feature state, page-sized padding, and flexible `data[]`. `struct vmbus_br` is the local ring handle. Packet and integration-service structures include `vmbus_chanpkt_hdr`, `vmbus_chanpkt`, `vmbuspipe_hdr`, `ic_version`, `icmsg_negotiate`, and `icmsg_hdr`. Inline helpers expose available write and read space.

## State, Dependencies, and Integration

The persistent state is shared memory owned by the VMBus channel, not this header. Consumers must map a buffer whose layout matches `struct vmbus_bufring`. The prototypes connect to `vmbus_bufring.c`; the negotiation structures are used by Hyper-V integration-service tools that need to form or parse IC messages.

## Risks and Test Signals

This header encodes wire and shared-memory layout. Packing, volatile fields, padding size, and flexible-array placement must remain compatible with the kernel and host. `vmbus_br_availwrite` deliberately leaves one byte/slot distinction to identify full versus empty rings; off-by-one changes can deadlock or corrupt data. Tests should compile users on supported architectures, assert structure offsets and sizes, and run send/receive interoperability against a real or simulated VMBus ring.
