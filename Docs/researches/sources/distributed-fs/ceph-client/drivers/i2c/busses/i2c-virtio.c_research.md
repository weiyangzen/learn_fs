# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-virtio.c

## Purpose

`i2c-virtio.c` implements the virtio I2C adapter specified by the OASIS virtio I2C specification. It queues each I2C message as virtqueue scatterlists and exposes the remote controller through a standard I2C adapter.

## Important APIs, Types, and Functions

`struct virtio_i2c` stores the virtio device, adapter, and single virtqueue. `struct virtio_i2c_req` holds a completion, outbound header, DMA-safe message buffer pointer, and inbound status header. `virtio_i2c_prepare_reqs()` builds scatterlists and queues requests. `virtio_i2c_complete_reqs()` waits and copies buffers back. `virtio_i2c_xfer()` orchestrates allocation, queueing, kicking, completion, and return count.

## Control Flow

Probe requires `VIRTIO_I2C_F_ZERO_LENGTH_REQUEST`, allocates state, finds the single `msg` virtqueue, configures adapter/ACPI companion, and registers the adapter. For each transfer, requests are allocated for all messages, queued with out header, optional data buffer, and in header, then the virtqueue is kicked. Completion callback drains used buffers and completes each request.

## State and Persistence Behavior

No cache exists. Per-transfer request arrays are allocated and freed per call. `i2c_get_dma_safe_msg_buf()` and `i2c_put_dma_safe_msg_buf()` handle message buffer lifetime and copy-back. Freeze removes virtqueues; restore recreates them.

## Dependencies and Integration Points

The driver depends on virtio core, virtqueue scatter-gather APIs, `linux/virtio_i2c.h`, I2C DMA-safe buffer helpers, and ACPI companion propagation from the virtio parent. It advertises I2C and SMBus emulation.

## Risks

Only 7-bit addressing is implemented. Interruptible waits turn into partial completion counts rather than negative errno. If queueing fewer than all requested messages succeeds, the driver still kicks and waits for queued messages to drain to keep the virtqueue usable. Status failures stop copy-back for subsequent messages.

## Test Signals

Check mandatory feature negotiation, 7-bit read/write messages, zero-length messages, multi-message partial queue failure, remote status failure, signal interruption, DMA-safe buffer copy-back, virtqueue callback completion, freeze/restore, and ACPI child enumeration through companion setup.
