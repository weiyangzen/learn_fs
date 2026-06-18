<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpbpf.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpbpf.h

## Purpose
`test_tcpbpf.h` defines the shared global statistics structure for TCP BPF sockops selftests.

## Important APIs, Types, And Functions
- `struct tcpbpf_globals` records event-map hits, retransmits, data segments in/out, callback return-value test results, received and acknowledged bytes, listen/close counts, saved SYN state, and window-clamp values.

## Control Flow
There is no executable flow. Kernel BPF programs update instances of `struct tcpbpf_globals`, while user-space tests read and validate the fields after TCP traffic.

## State And Persistence
The structure is usually stored as a BPF map value and persists for the lifetime of the loaded test object.

## Dependencies And Integration Points
It is shared by TCP BPF kernel programs and user-space validators to keep map layout consistent.

## Risks And Edge Cases
Any layout change breaks ABI with precompiled BPF objects. Field sizes are fixed `__u32`/`__u64`; counters can wrap in long-running or high-volume tests, though selftests are bounded.

## Test Signals
Passing tests observe expected nonzero counters, callback return values, saved SYN flags, and byte accounting in this structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcpbpf.h -->
