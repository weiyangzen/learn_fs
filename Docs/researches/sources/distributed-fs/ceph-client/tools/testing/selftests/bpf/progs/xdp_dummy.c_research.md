<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_dummy.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_dummy.c

## Purpose
This minimal XDP program is a pass-through fixture used by tests that only need a valid attachable XDP program.

## Important APIs, Types, and Functions
The single `SEC("xdp")` function `xdp_dummy_prog` takes `struct xdp_md *` and returns `XDP_PASS`. It declares GPL license metadata.

## Control Flow
There is no parsing or branching; every packet is passed to the network stack.

## State and Persistence
No maps, globals, or packet mutations are present.

## Dependencies and Integration Points
It depends on `linux/bpf.h` and `bpf_helpers.h` and integrates with any selftest needing a simple XDP attachment target.

## Risks
The main risk is not behavioral but fixture availability: attach failures would usually reflect environment or kernel support rather than this source.

## Test Signals
Successful load and attach are the only meaningful signals; runtime action is always `XDP_PASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_dummy.c -->
