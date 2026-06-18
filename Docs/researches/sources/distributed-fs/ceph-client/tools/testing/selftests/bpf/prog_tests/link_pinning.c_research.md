
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/link_pinning.c

## Purpose

`link_pinning.c` validates BPF link pinning to BPFFS, reopening pinned links, unpinning, and attachment lifetime after FD destruction.

## Important APIs, Types, and Functions

The test uses `test_link_pinning.skel.h`, `bpf_program__attach()`, `bpf_link__pin()`, `bpf_link__pin_path()`, `bpf_link__open()`, `bpf_link__unpin()`, `bpf_link__destroy()`, `stat()`, and BSS `in`/`out` trigger fields.

## Control Flow and Data Flow

For raw tracepoint and tp_btf programs, it attaches, verifies BSS output follows input, pins to `/sys/fs/bpf/pinned_link_test`, verifies path and file, destroys the original FD while expecting the pinned link to remain active, reopens it, unpins while FD remains open, verifies continued activity, then destroys the final FD and loops until output stops changing.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is a pinned BPFFS link path, open link FDs, and BSS input/output values. Dependencies include mounted/writable BPFFS at `/sys/fs/bpf`, raw_tp and tp_btf attach support, and trigger timing. Integration is link pin persistence and libbpf pin path tracking. Risks are stale pinned path from prior failures, delayed detach, and permission issues on BPFFS. Test signals are BSS output tracking through pin/destroy/open/unpin phases and eventual detachment after final destroy.
