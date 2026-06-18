# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bpf_sockopt_helpers.h

Purpose: small BPF helper routine to validate that a context supports `bpf_getsockopt` and `bpf_setsockopt`.

Important APIs and functions: `get_set_sk_priority(ctx)` reads `SOL_SOCKET/SO_PRIORITY` into `prio` and writes it back.

Control flow: returns 0 on either helper failure and 1 if both get and set succeed.

State and persistence: reads and writes socket priority with the same value, so intended to preserve observable socket state.

Dependencies and integration points: includes `<sys/socket.h>` and `bpf_helpers.h`; used by sockopt/cgroup program tests.

Risks: context must permit both helpers; socket option semantics can vary by hook; preserving value still exercises a write path that may be rejected.

Test signals: callers can assert return 1 in allowed contexts and 0 or verifier failure in disallowed contexts.
