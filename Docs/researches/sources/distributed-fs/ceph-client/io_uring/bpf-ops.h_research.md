# sources/distributed-fs/ceph-client/io_uring/bpf-ops.h

## Purpose
This header defines the BPF struct-ops interface shape and mapped region identifiers for io_uring BPF operations.

## Important APIs, Types, And Functions
- Region enum values `IOU_REGION_MEM`, `IOU_REGION_CQ`, and `IOU_REGION_SQ`.
- `struct io_uring_bpf_ops` with `loop_step`, `ring_fd`, and private `priv`.
- `io_unregister_bpf_ops()` declaration or no-op stub when the feature is disabled.

## Control Flow
No runtime logic except the disabled-feature stub.

## State And Persistence
The struct stores per-registered-link state. `priv` points back to the owning ring while installed.

## Dependencies And Integration Points
It depends on `io_uring_types.h` and is used by ring teardown and BPF registration code.

## Risks And Edge Cases
ABI-sensitive struct layout must match BTF expectations. The no-op stub must remain safe for builds without `CONFIG_IO_URING_BPF_OPS`.

## Test Signals
Builds with and without BPF ops enabled validate stubs/prototypes; BPF struct_ops tests validate layout.
