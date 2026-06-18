<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_tx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_tx.c

## Purpose
This minimal XDP fixture transmits every received packet back out the ingress device.

## Important APIs, Types, and Functions
The single `SEC("xdp")` entry point `xdp_tx` returns `XDP_TX`.

## Control Flow
No parsing or branching occurs; all packets take the XDP_TX action.

## State and Persistence
No maps, globals, or packet mutations are present.

## Dependencies and Integration Points
It depends only on BPF headers and is used by XDP tests requiring a simple TX action program.

## Risks
Runtime behavior depends on driver support for XDP_TX. Because no bounds checks are needed, source risk is minimal.

## Test Signals
Successful load/attach and observed packet reflection are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_tx.c -->
