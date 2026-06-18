<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata2.c

## Purpose
This freplace program tests that calling XDP metadata kfuncs from a replacement program attached to `rx` is safe and does not crash.

## Important APIs, Types, and Functions
It declares `bpf_xdp_metadata_rx_hash` as a kfunc and a global `called` counter. Entry point `freplace_rx` is placed in `SEC("freplace/rx")`.

## Control Flow
The replacement program initializes local hash/type variables, calls the metadata hash kfunc, increments `called`, and returns `XDP_PASS`.

## State and Persistence
Persistent state is the BSS `called` counter observed by userspace. No packet metadata or maps are modified.

## Dependencies and Integration Points
It integrates with freplace attachment to the `rx` program from the metadata test and depends on metadata kfunc availability in replacement context.

## Risks
The program intentionally ignores kfunc return value; it only validates safe invocation. Attachment target naming must match the original program.

## Test Signals
Userspace should observe `called` increment after packets execute the replacement path, and the load/attach should not fail due to metadata kfunc use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_metadata2.c -->
