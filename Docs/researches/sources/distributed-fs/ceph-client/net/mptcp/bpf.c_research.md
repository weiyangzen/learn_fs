<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/bpf.c -->
# sources/distributed-fs/ceph-client/net/mptcp/bpf.c

## Purpose
Provides BPF-facing MPTCP helpers and registers an fmodret BTF kfunc allowlist for MPTCP-related protocol selection.

## Important APIs, Types, and Functions
`bpf_mptcp_sock_from_subflow()` returns the owning `struct mptcp_sock` for a full TCP MPTCP subflow socket. `bpf_mptcp_fmodret_ids` includes `update_socket_protocol` as a function-modify-return target. `bpf_mptcp_kfunc_init()` registers the BTF fmodret ID set at late init.

## Control Flow
The helper validates that the supplied socket is non-null, full, TCP, and MPTCP, then follows `mptcp_subflow_ctx(sk)->conn` to return the MPTCP meta-socket. Late init registers the static BTF set with the BPF subsystem.

## State and Persistence
Persistent state is the registered BTF kfunc ID set owned by this module/object. No per-socket state is mutated.

## Dependencies and Integration Points
Depends on BPF BTF kfunc registration and MPTCP protocol internals from `protocol.h`. It is built only under `CONFIG_BPF_SYSCALL` and exposes MPTCP context to BPF programs that operate on subflow sockets.

## Risks
The helper assumes a valid MPTCP subflow context after `sk_is_mptcp()`. Any future socket state where `conn` is unavailable would need guarding. BTF registration failures propagate only from late init; users relying on the kfunc need build/runtime registration coverage.

## Test Signals
BPF selftests should confirm helper return on MPTCP subflows and NULL on plain TCP, non-full, or null sockets. Boot logs or BTF queries can validate fmodret registration for `update_socket_protocol`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/bpf.c -->
