<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_user.c

## Purpose
`tc_l2_redirect_user.c` is the tiny userspace companion that updates a pinned BPF array map with a tunnel interface index for the tc L2 redirect sample.

## Important APIs, Types, And Functions
`main()` parses `-U <pinned-file>` and `-i <ifindex>`, opens the map with `bpf_obj_get()`, and writes key zero with `bpf_map_update_elem()`. `usage()` prints command syntax.

## Control Flow
The program validates required arguments, opens the pinned map path, updates array key `0` with the parsed ifindex, closes the fd, and returns the libbpf update status.

## State And Persistence
It persists exactly one integer in a pinned BPF map shared with tc programs. The process owns no durable local state after exit.

## Dependencies And Integration Points
It depends on libbpf's low-level BPF syscall wrappers and on the map created and pinned by iproute2 under `/sys/fs/bpf/tc/globals/tun_iface`. It is invoked by `tc_l2_redirect.sh`.

## Risks And Edge Cases
The code uses `atoi()` without strict validation, so malformed ifindex input can become zero. It assumes the pinned object is a compatible array map. A stale or wrong map path results in update failure without modifying kernel state.

## Test Signals
Successful execution returns zero and subsequent tc traffic is redirected to the target tunnel. Failure signals are `bpf_obj_get()` or `bpf_map_update_elem()` diagnostics and unchanged redirect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_user.c -->
