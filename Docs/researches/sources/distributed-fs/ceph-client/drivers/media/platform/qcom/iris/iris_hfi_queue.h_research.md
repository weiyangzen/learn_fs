# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.h

## Purpose
`iris_hfi_queue.h` defines the host-firmware shared queue layout, sizing constants, queue headers, queue table header, per-queue descriptor, and queue API.

## Important APIs, Types, And Functions
Constants define maximum queued buffers, maximum parallel sessions, default queue header type, maximum packet size, SFR size, per-queue size, and queue ids. `struct iris_hfi_queue_header` mirrors firmware-visible queue metadata and indices. `struct iris_hfi_queue_table_header` describes the table plus three queue headers. `struct iris_iface_q_info` holds the driver-side qhdr pointer, device address, and kernel virtual address. Public functions initialize/deinitialize queues and write/read command/message/debug queues.

## Control Flow
The memory layout comment documents a table header followed by command, message, and debug queue headers and three queue data areas. Queue ids index both header array and data offsets in `iris_hfi_queue.c`.

## State And Persistence Behavior
Queue header fields are shared mutable state between host and firmware. SFR memory gives firmware a place to store subsystem failure reason data.

## Dependencies And Integration Points
The header forward-declares `struct iris_core` and is included by core and HFI queue users. `IFACEQ_CORE_PKT_SIZE` from `iris_core.h` bounds response packet copies.

## Risks And Test Signals
Sizing constants drive DMA allocation and packet validation. Tests should validate total queue allocation size, queue alignment, header offsets, and compatibility with firmware expectations for 16 sessions and 64 buffers.
