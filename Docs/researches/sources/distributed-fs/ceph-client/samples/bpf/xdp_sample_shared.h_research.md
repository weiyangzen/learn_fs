<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_shared.h -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_shared.h

## Purpose
`xdp_sample_shared.h` defines the shared counter record layout used by both BPF-side XDP sample programs and userspace statistics readers.

## Important APIs, Types, And Functions
It defines `struct datarec` with `processed`, `dropped`, `issue`, a union of `xdp_pass`/`info`, `xdp_drop`, and `xdp_redirect`, aligned to 64 bytes.

## Control Flow
There is no executable control flow.

## State And Persistence
Instances of `struct datarec` persist in BPF maps and in userspace snapshots. The 64-byte alignment reduces false sharing for per-CPU or mmaped counters.

## Dependencies And Integration Points
The header is included by BPF programs and userspace utilities, forming the ABI for sample statistic maps.

## Risks And Edge Cases
Changing field order, sizes, or alignment would break map value compatibility between BPF and userspace. `size_t` width must be consistent for the target userspace/BPF ABI.

## Test Signals
Correct stats output from `xdp_sample_user.c` consumers verifies that map values are read with the expected layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_sample_shared.h -->
