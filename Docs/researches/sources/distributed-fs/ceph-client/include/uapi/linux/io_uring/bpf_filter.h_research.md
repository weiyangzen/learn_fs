
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/bpf_filter.h

## Purpose

`io_uring/bpf_filter.h` defines the UAPI for registering BPF filters that can inspect or gate io_uring operations. The complete 68-line file was read.

## Important APIs, Types, and Functions

Types are `io_uring_bpf_ctx`, `io_uring_bpf_filter`, and `io_uring_bpf`. The context exposes `user_data`, opcode, SQE flags, PDU size, and opcode-specific socket/open fields. Flags include `IO_URING_BPF_FILTER_DENY_REST` and `IO_URING_BPF_FILTER_SZ_STRICT`; command type `IO_URING_BPF_CMD_FILTER` selects filter registration.

## Control Flow

User space passes an `io_uring_bpf` registration command through io_uring registration. The kernel installs classic/eBPF-style filter instructions for the specified opcode, then supplies `io_uring_bpf_ctx` when evaluating submissions.

## State and Persistence Behavior

Installed filters persist on the ring until replaced, removed, or ring teardown. Deny-rest behavior can make unfiltered opcodes fail by default.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `IORING_REGISTER_BPF_FILTER` from `io_uring.h`, BPF instruction validation, and opcode-specific io_uring submission paths.

## Risks and Edge Cases

Strict PDU size matching can reject registrations across kernel/application version mismatches. Deny-rest can unexpectedly block operations. Opcode-specific context must stay synchronized with SQE interpretation.

## Test Signals

Tests should register allow/deny filters, use deny-rest mode, verify strict/non-strict PDU behavior, cover socket/open context fields, and confirm rejected submissions return expected errors.
