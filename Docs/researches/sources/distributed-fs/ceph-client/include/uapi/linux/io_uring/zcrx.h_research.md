
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/zcrx.h

## Purpose

`io_uring/zcrx.h` defines the io_uring zero-copy receive UAPI, including refill/completion entries, area registration, queue offsets, registration flags, feature flags, interface-queue registration, and control operations. The complete 115-line file was read.

## Important APIs, Types, and Functions

Types are `io_uring_zcrx_rqe`, `io_uring_zcrx_cqe`, `io_uring_zcrx_offsets`, `io_uring_zcrx_area_reg`, `io_uring_zcrx_ifq_reg`, `zcrx_ctrl_flush_rq`, `zcrx_ctrl_export`, and `zcrx_ctrl`. Enums define area flags, registration flags `ZCRX_REG_IMPORT`/`NODEV`, features such as `ZCRX_FEATURE_RX_PAGE_SIZE`, and control ops `ZCRX_CTRL_FLUSH_RQ` and `ZCRX_CTRL_EXPORT`. Offset area encoding uses `IORING_ZCRX_AREA_SHIFT` and `IORING_ZCRX_AREA_MASK`.

## Control Flow

User space registers a memory area and network receive queue through io_uring registration, mmaps or manages refill queue offsets, posts refill entries, receives zero-copy completions carrying offsets, and uses control ops to flush or export zcrx instances.

## State and Persistence Behavior

Zcrx state includes registered areas, optional DMABUF/imported memory, ifindex/RX queue binding, refill queue head/tail, zcrx ID, and rx buffer length. It persists until unregister/control teardown or ring close.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `io_uring.h`, netdev RX queues, memory-region descriptors, DMABUF import, NAPI/driver receive paths, and zcrx query reporting.

## Risks and Edge Cases

Zero-copy memory lifetime, DMA ownership, offset area encoding, nodev fallback, queue flush behavior, and rx page-size negotiation are high-risk. Reserved fields need zeroing for forward compatibility.

## Test Signals

Tests should register normal, imported, DMABUF, and nodev zcrx areas; validate refill/completion offsets; query features; flush queues; export instances; and exercise teardown while buffers are outstanding.
