# sources/distributed-fs/ceph-client/include/linux/bpf_mprog.h

Purpose: Defines the generic BPF multi-program attachment framework used by hook sites that can host ordered sets of BPF programs, such as TC classifier links. It provides a double-buffered RCU-friendly array model plus attach/detach/query APIs with relative insertion semantics.

Important APIs/types/functions: `BPF_MPROG_MAX` caps array slots at 64, with one sentinel slot, so `bpf_mprog_max()` returns 63. `struct bpf_mprog_fp` stores fast-path program pointers; `struct bpf_mprog_cp` stores control-plane links. `struct bpf_mprog_entry` is one active array view, and `struct bpf_mprog_bundle` contains two entries, shared link metadata, a pending reference to release, revision counter, and count. Iteration macros `bpf_mprog_foreach_prog()` and `bpf_mprog_foreach_tuple()` use `READ_ONCE()` for fast-path program access. Inline helpers initialize bundles, select peer buffers, track count/revision, copy/clear/grow/shrink entries, write tuples with `WRITE_ONCE()`, and defer non-link program ref drops until after RCU grace. Core APIs are `bpf_mprog_attach()`, `bpf_mprog_detach()`, and `bpf_mprog_query()`.

Control flow: Callers hold an external hook-specific lock, fetch the active entry, call attach/detach to prepare `entry_new`, swap the hook pointer if needed, wait for inflight RCU readers, then call `bpf_mprog_commit()` to complete releases and bump revision. Fast paths enter RCU, iterate programs until NULL, run each program, and process return values.

State/persistence: The bundle persists for the attach location. Active entry pointers are RCU-published by the caller. Revision tracks observable updates and count tracks attached programs. Detached non-link program refs are held in `ref` until post-swap commit.

Dependencies/integration: Depends on core BPF program/link types, RCU discipline supplied by users, external locks such as RTNL for TCX, and capability checks via `bpf_net_capable()` for empty detach behavior.

Risks/test signals: Risks include forgetting external locking, swapping entries without a grace period, count/sentinel off-by-one errors, releasing program refs too early, and revision mismatch handling. Test signals include TC link/order selftests with BEFORE/AFTER/prepend/append, concurrent packet fast-path traffic during attach/detach, revision query tests, detach-empty permission tests, and KCSAN/RCU diagnostics.
