# sources/distributed-fs/ceph-client/io_uring/bpf_filter.h

## Purpose
The header exposes BPF filter registration, execution, cloning, and cleanup to io_uring restriction and submission paths, with stubs for disabled builds.

## Important APIs, Types, And Functions
- `io_uring_run_bpf_filters()` inline wrapper returns success when no filter table exists.
- `__io_uring_run_bpf_filters()`, `io_register_bpf_filter()`, `io_put_bpf_filters()`, and `io_bpf_filter_clone()` are available under `CONFIG_IO_URING_BPF`.
- Disabled builds reject registration with `-EINVAL` and make execution/cleanup no-ops.

## Control Flow
The enabled wrapper checks whether `filters` is non-NULL before calling the full runner. Disabled stubs avoid conditional compilation at call sites.

## State And Persistence
No state is defined here. It references RCU filter arrays owned by restriction state.

## Dependencies And Integration Points
It includes the UAPI BPF filter definition and is used by request initialization/filtering and restriction registration code.

## Risks And Edge Cases
Callers must pass opcode-validated requests because the implementation indexes by `req->opcode`. Stub behavior must preserve semantics for kernels without BPF filter support.

## Test Signals
Builds with `CONFIG_IO_URING_BPF` off validate stubs; enabled runtime filter tests validate wrapper behavior.
