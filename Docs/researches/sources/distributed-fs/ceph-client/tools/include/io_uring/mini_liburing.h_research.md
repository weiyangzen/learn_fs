# sources/distributed-fs/ceph-client/tools/include/io_uring/mini_liburing.h

## Purpose

`mini_liburing.h` is a small header-only subset of liburing used by kernel tools and tests that need direct `io_uring` setup, submission, completion, and a few operation prep helpers without linking full liburing.

## Important APIs and Flow

The header defines `struct io_sq_ring`, `io_cq_ring`, `io_uring_sq`, `io_uring_cq`, and `io_uring`. `io_uring_setup` and `io_uring_enter` wrap syscalls. `io_uring_queue_init_params` sets up the ring fd and calls `io_uring_mmap`, which maps SQ ring, SQEs, and CQ ring. `io_uring_get_sqe` reserves an SQE in userspace. `io_uring_submit` publishes SQEs to the kernel SQ ring and enters the ring. `io_uring_wait_cqe` waits until a CQE is available, `io_uring_cqe_seen` advances the CQ head, and `io_uring_queue_exit` unmaps and closes. Prep helpers cover `IORING_OP_URING_CMD`, buffer registration, send, and zero-copy send.

## State, Dependencies, and Integration

Ring state is shared with the kernel through mmaped pages and tracked in the `io_uring` struct. The header depends on `<linux/io_uring.h>`, syscalls, mmap, barriers, and UAPI structs. It integrates with tools that need basic io_uring operations in a single include.

## Risks and Test Signals

The implementation is intentionally minimal. `io_uring_queue_exit` unmaps SQ state but does not unmap CQ in the visible code, which callers should audit. Barrier behavior differs by architecture. `IORING_SETUP_NO_SQARRAY` changes SQ size and submit behavior. Tests should create rings with and without `NO_SQARRAY`, submit simple operations, wait and mark CQEs seen, register buffers, and run under leak detection for mmap cleanup.
