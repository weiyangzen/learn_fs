# sources/distributed-fs/ceph-client/io_uring/bpf-ops.c

## Purpose
`bpf-ops.c` registers BPF struct-ops support for io_uring loop customization and exposes BPF kfuncs that can submit SQEs or access mapped io_uring regions under verifier constraints.

## Important APIs, Types, And Functions
- `bpf_io_uring_submit_sqes()` kfunc calls `io_submit_sqes(ctx, nr)`.
- `bpf_io_uring_get_region()` kfunc returns validated pointers to parameter, CQ, or SQ mapped regions and asserts `ctx->uring_lock`.
- `struct io_uring_bpf_ops` instances are installed through BPF struct_ops registration.
- `io_install_bpf()` validates ring setup flags and installs `ctx->bpf_ops` and `ctx->loop_step`.
- `io_unregister_bpf_ops()` safely ejects installed ops during ring teardown.
- `io_uring_bpf_init()` registers the struct_ops type at initcall time.

## Control Flow
BPF subsystem initialization finds the BTF type for `iou_loop_params`, registers kfunc IDs, and registers struct_ops. Registration from userspace resolves a ring fd, takes a global control mutex and the ring lock, then installs ops if the ring is defer-taskrun and not SQPOLL/IOPOLL. Unregistration or ring teardown clears the ops with the same lock ordering.

## State And Persistence
Global state includes `io_bpf_ctrl_mutex` and cached `loop_params_type`. Per-ring state is `ctx->bpf_ops` and `ctx->loop_step`; the BPF ops object stores `ring_fd` and `priv`.

## Dependencies And Integration Points
The file depends on BPF verifier, BTF, struct_ops, io_uring registration/memmap/loop internals, and `DEBUG_INFO_BTF`/JIT/syscall Kconfig dependencies. It integrates with ring lifetime cleanup through `io_unregister_bpf_ops()`.

## Risks And Edge Cases
Lock ordering between the global BPF mutex and `uring_lock` is critical. Region pointer exposure must remain bounded by `io_region_size()`. Verifier access only permits reads from expected context arguments and selected scalar fields. Rings using SQPOLL or IOPOLL are explicitly unsupported.

## Test Signals
BPF struct_ops registration tests should cover valid/invalid ring fds, unsupported ring flags, kfunc verifier access, region size rejection, and ring teardown while a BPF link exists.
