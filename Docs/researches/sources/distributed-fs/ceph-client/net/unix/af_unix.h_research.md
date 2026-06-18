<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.h -->
# sources/distributed-fs/ceph-client/net/unix/af_unix.h

## Purpose
`af_unix.h` is the local header shared by AF_UNIX implementation files. It defines hash table sizing, skb control-block metadata, and cross-file prototypes for peer lookup, SCM_RIGHTS garbage collection, diagnostics, sysctl, and BPF sockmap integration.

## Important APIs, Types, and Functions
- `UNIX_HASH_MOD`, `UNIX_HASH_SIZE`, and `UNIX_HASH_BITS` define hash table layout.
- `struct unix_skb_parms` overlays `skb->cb` via `UNIXCB(skb)` and stores sender pid/uid/gid, passed file list, optional security ID, and consumed byte count.
- GC prototypes connect `af_unix.c` with `garbage.c`: `unix_add_edges()`, `unix_del_edges()`, `unix_update_edges()`, `unix_prepare_fpl()`, `unix_destroy_fpl()`, `unix_peek_fpl()`, and `unix_schedule_gc()`.
- Diagnostic helpers `unix_inq_len()` and `unix_outq_len()` are shared with `diag.c`.
- Sysctl registration has real or stub implementations based on `CONFIG_SYSCTL`.
- BPF hooks expose base protos and proto-update functions under `CONFIG_BPF_SYSCALL`.

## Control Flow
This header has no runtime flow, but its conditional declarations choose whether sysctl and BPF call sites compile to real functions or no-op stubs.

## State and Persistence
No state is allocated here. The notable state contract is `UNIXCB(skb)`, which persists per skb while queued and is consumed by receive, SCM, and GC paths.

## Dependencies and Integration Points
It depends on uid/gid types, SCM file pointer lists, `struct unix_sock`, `struct sk_psock`, and shared AF_UNIX internals. It is included by `af_unix.c`, `diag.c`, `garbage.c`, `sysctl_net_unix.c`, and `unix_bpf.c`.

## Risks and Edge Cases
`struct unix_skb_parms` must fit inside `skb->cb`; `af_unix.c` enforces this with `BUILD_BUG_ON`. Changes to the control block affect every send/receive and GC path. Conditional stubs must match real function signatures to avoid config-only build failures.

## Test Signals
Compile all relevant config combinations and run SCM_RIGHTS, diag, sysctl, and sockmap tests to validate the shared contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.h -->
