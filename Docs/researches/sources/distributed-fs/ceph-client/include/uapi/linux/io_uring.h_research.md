
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring.h

## Purpose

`io_uring.h` is the primary io_uring UAPI header. It defines submission/completion queue entry layouts, operation codes, setup/enter/register flags, ring mmap offsets, feature flags, resource registration structures, restrictions, provided buffers, NAPI controls, wait/cancel arguments, socket uring-command operations, timestamp flags, and zero-copy receive integration. The complete 1065-line file was read.

## Important APIs, Types, and Functions

Key types include `io_uring_sqe`, `io_uring_attr_pi`, `io_uring_cqe`, `io_sqring_offsets`, `io_cqring_offsets`, `io_uring_params`, `io_uring_files_update`, `io_uring_region_desc`, `io_uring_mem_region_reg`, `io_uring_rsrc_register`, `io_uring_rsrc_update`, `io_uring_rsrc_update2`, `io_uring_probe_op`, `io_uring_probe`, `io_uring_restriction`, `io_uring_task_restriction`, `io_uring_clock_register`, `io_uring_clone_buffers`, `io_uring_buf`, `io_uring_buf_ring`, `io_uring_buf_reg`, `io_uring_buf_status`, `io_uring_napi`, `io_uring_reg_wait`, `io_uring_getevents_arg`, `io_uring_sync_cancel_reg`, `io_uring_file_index_range`, `io_uring_recvmsg_out`, and `io_timespec`. Enums cover SQE flags, `io_uring_op`, register operations, worker types, provided-buffer flags, NAPI op/tracking strategy, restriction ops, and socket operations.

## Control Flow

The UAPI models a shared-memory producer/consumer flow: user space calls `io_uring_setup`, mmaps rings/SQEs, writes SQEs, advances SQ tail, calls `io_uring_enter`, and consumes CQEs from the completion ring. Registration operations add buffers, files, rings, personalities, restrictions, NAPI settings, zcrx queues, memory regions, queries, and BPF filters.

## State and Persistence Behavior

Kernel ring state includes SQ/CQ heads/tails, features, registered resources, worker settings, restrictions, provided buffer rings, NAPI state, registered wait regions, zcrx state, and optional eventfd integration. User-visible state is shared through mmap offsets and CQE/SQE fields until ring teardown.

## Dependencies and Integration Points

It includes `linux/fs.h`, `linux/types.h`, `linux/io_uring/zcrx.h`, and optionally `linux/time_types.h`. It is shared with liburing and integrates with most kernel file/socket operations, registered files/buffers, networking, NAPI, BPF filters, zcrx, and memory-region registration.

## Risks and Edge Cases

This is dense ABI. Risks include union field aliasing by opcode, SQE/CQE 64/128 and 16/32 byte mixed-size modes, memory ordering on ring heads/tails, registered fd indexes, buffer-selection lifetime, `IORING_SETUP_SQ_REWIND` constraints, feature/flag probing, 32-bit compat layout, and evolving register opcodes.

## Test Signals

io_uring selftests should cover every opcode class, setup flags, ring mmap offsets, CQ overflow/skip/large CQEs, registered resources, provided buffers including incremental consumption, NAPI, restrictions, sync cancel, socket uring commands, zcrx registration, queries, BPF filters, and 32/64-bit compat.
