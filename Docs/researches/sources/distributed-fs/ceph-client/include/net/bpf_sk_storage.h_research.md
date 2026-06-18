# sources/distributed-fs/ceph-client/include/net/bpf_sk_storage.h

## Purpose
This header declares BPF socket-local storage integration for `struct sock`. It exposes helper prototypes for BPF programs, lifecycle hooks for socket clone/free, and inet_diag serialization helpers, with no-op fallbacks when `CONFIG_BPF_SYSCALL` is disabled.

## Important APIs, Types, And Constants
- `bpf_sk_storage_free(struct sock *sk)` releases local storage attached to a socket during destruction.
- `bpf_sk_storage_get_proto`, `bpf_sk_storage_delete_proto`, and tracing variants expose BPF helper function metadata.
- `bpf_sk_storage_clone()` copies inheritable socket storage from a listener/parent to a new socket.
- `struct bpf_sk_storage_diag` is an opaque diagnostic context allocated from netlink attributes.
- `bpf_sk_storage_diag_alloc()`, `bpf_sk_storage_diag_free()`, and `bpf_sk_storage_diag_put()` support inet_diag dumping of selected or all socket storage values.
- When `CONFIG_BPF_SYSCALL` is off, clone and diag-put return success and allocation returns NULL, keeping callers buildable without BPF syscall support.

## Control Flow And State
Socket creation/destruction paths call clone/free hooks from core socket code. BPF programs use helper prototypes selected by verifier/program type to get or delete per-socket storage. Diagnostic dump paths allocate a `bpf_sk_storage_diag` from request attributes, iterate sockets, append storage data to sk_buffs through `bpf_sk_storage_diag_put()`, and free the diag context when the dump completes.

## State And Persistence Behavior
The actual storage is per-socket runtime state owned by BPF local-storage maps. It follows socket lifetime, may be cloned to accepted child sockets, and is released at socket destruction. No durable persistence exists. The header intentionally hides internal element/layout details behind opaque declarations.

## Dependencies And Integration Points
The header depends on BPF map/helper infrastructure, local storage support, RCU/list/hash/spinlock types, sockets, sock_diag UAPI, BTF UAPI, sk_buffs, and netlink attributes. Implementations are in `net/core/bpf_sk_storage.c`; socket lifecycle calls are in `net/core/sock.c`; inet_diag integration appears in `net/ipv4/inet_diag.c`; BPF program helper selection occurs in networking BPF code.

## Risks
- Callers must invoke `bpf_sk_storage_free()` on all destruction paths or storage leaks and stale map references can result.
- Clone failures must be handled by socket creation paths; partially cloned storage must be unwound correctly in implementation.
- Diagnostic dump sizing is error-prone because values are serialized into sk_buffs under netlink size limits.
- Config-disabled stubs silently skip diagnostic content, so tests must cover both enabled and disabled builds.

## Test Signals
- BPF selftests should cover helper get/delete from socket and tracing contexts, clone inheritance on accepted sockets, deletion/free on close, and map iteration.
- inet_diag tests should cover requested storage IDs, duplicate requests, large value payloads, and disabled `CONFIG_BPF_SYSCALL` builds.
