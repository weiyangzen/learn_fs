# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sock_addr.c

## Purpose
`verifier_sock_addr.c` validates allowed return ranges for cgroup socket-address program types. It covers IPv4, IPv6, and Unix variants for recvmsg, sendmsg, getpeername, getsockname, bind, and connect hooks.

## Important APIs, Types, and Functions
Each function is a simple C BPF program taking `struct bpf_sock_addr *ctx` and returning a constant. The file includes `<linux/bpf.h>`, `<bpf/bpf_helpers.h>`, `<bpf_sockopt_helpers.h>`, and `bpf_misc.h`. The annotations are the main API: `SEC("cgroup/...")`, `__success`, `__failure`, and `__msg` encode the verifier contract for each hook's allowed return interval.

## Control Flow
Control flow is intentionally straight-line. For recvmsg and getname hooks, success cases return 1 while bad cases return 0, expecting the verifier to require exactly `[1, 1]`. For sendmsg and connect hooks, valid cases return 0 or 1 and invalid cases return 2, expecting `[0, 1]`. For bind hooks, valid cases return 0 through 3 and invalid cases return 4, expecting `[0, 3]`.

## State and Persistence
There is no map state, stack state beyond the function frame, or persistent behavior. The `ctx` parameter is unused in all tests. The only meaningful state is the verifier's exit-register range tracking for `R0`.

## Dependencies and Integration Points
The file integrates with cgroup socket-address verifier policy. It depends on the kernel verifier assigning hook-specific return constraints and the test runner matching errors such as `At program exit the register R0 has smin=... should have been in [...]`.

## Risks and Test Signals
The main risk is accepting an invalid action code for a cgroup hook or rejecting a valid one, which would break program-type semantics for bind/connect/message hooks. Test signals are simple and strong: a successful load for every valid boundary value, and deterministic verifier rejection for one out-of-range return per hook family.
