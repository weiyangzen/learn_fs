# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.h

## Purpose
`wr.h` declares the mlx5 work-request posting interface and inline helpers for safely writing send WQEs into fragmented SQ buffers. It is the small public boundary used by verbs code and UMR helpers to post sends and receives.

## Important APIs, types, and functions
The header defines `MLX5_IB_SQ_UMR_INLINE_THRESHOLD`, `struct mlx5_wqe_eth_pad`, `get_sq_edge()`, `handle_post_send_edge()`, and `mlx5r_memcpy_send_wqe()`. It declares `mlx5r_wq_overflow()`, WQE begin/finish helpers, `mlx5r_ring_db()`, and post-send/post-recv functions plus drain/nodrain wrappers.

## Control flow
WQE writers get the current contiguous SQ edge with `get_sq_edge()`, append 16-byte-aligned segments, call `handle_post_send_edge()` whenever the write cursor reaches an edge, and use `mlx5r_memcpy_send_wqe()` for variable inline bytes that can cross fragments. Higher-level callers begin a WQE, fill segments, finish metadata, and ring the doorbell.

## State and persistence
The helpers mutate caller-provided segment pointers, WQE size counters, and cached edge pointers. They do not persist state themselves, but they protect the integrity of hardware-visible SQ memory and the QP SQ `cur_edge` cache maintained by `wr.c`.

## Dependencies and integration points
It depends on `mlx5_ib.h`, fragmented buffer helpers, mlx5 WQE block sizing, RDMA QP/CQ types, and GSI integration. The declarations are consumed by normal verbs posting and specialized UMR posting paths.

## Risks
Pointer arithmetic is central here. Incorrect edge detection or alignment can wrap to the wrong SQ fragment, corrupt WQEs, or make the posted size disagree with the hardware descriptor size. The inline copy helper assumes callers pass a 16-byte-aligned cursor and maintain accurate `wqe_sz`.

## Test signals
Validate WQE writes at every boundary around fragment ends and SQ wrap, inline copies with 1-byte through multi-fragment lengths, UMR descriptor sizes at the inline threshold, drain/nodrain wrapper binding, and compile coverage for all users of the declared posting functions.
