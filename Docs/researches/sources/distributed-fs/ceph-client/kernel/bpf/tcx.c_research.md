# sources/distributed-fs/ceph-client/kernel/bpf/tcx.c

## Purpose

`tcx.c` implements BPF TCX attach, detach, query, and bpf_link support for ingress and egress classifier programs on net devices. It is the syscall/link-facing glue between generic multi-program BPF attachment infrastructure and TCX per-device hook storage.

## Important APIs, Types, And Functions

- Legacy attach path: `tcx_prog_attach()`, `tcx_prog_detach()`, and `tcx_prog_query()` serve `BPF_PROG_ATTACH`, `BPF_PROG_DETACH`, and `BPF_PROG_QUERY`.
- Device cleanup: `tcx_uninstall()` removes all TCX programs/links from one net-device direction during netdevice teardown.
- Link attach path: `tcx_link_attach()` allocates a `struct tcx_link`, primes a generic `bpf_link`, attaches it to the TCX mprog entry, and settles the link FD.
- Link ops: `tcx_link_release()`, `tcx_link_detach()`, `tcx_link_update()`, `tcx_link_dealloc()`, `tcx_link_fdinfo()`, and `tcx_link_fill_info()`.
- TCX helpers from `net/tcx.h`: `tcx_entry_fetch_or_create()`, `tcx_entry_fetch()`, `tcx_entry_update()`, `tcx_entry_sync()`, `tcx_entry_free()`, `tcx_entry_is_active()`, `tcx_skeys_inc()`, and `tcx_skeys_dec()`.
- Multi-program helpers: `bpf_mprog_attach()`, `bpf_mprog_detach()`, `bpf_mprog_commit()`, `bpf_mprog_clear_all()`, `bpf_mprog_query()`, and tuple iteration.

## Control Flow

All public operations take `rtnl_lock()` and look up the target net device by `target_ifindex` in the caller's network namespace. Attach optionally resolves a replacement program if `BPF_F_REPLACE` is set, fetches or creates the ingress/egress TCX entry, and delegates ordering/revision/relative-FD semantics to `bpf_mprog_attach()`. If a new entry object is returned, the device pointer is updated, TCX static keys are incremented, and the mprog transaction is committed. Errors free a newly-created empty entry.

Detach fetches the current entry and calls `bpf_mprog_detach()`. If the resulting entry is inactive it updates the device direction to `NULL`, syncs, decrements static keys, commits, and frees the old entry. Query is a locked lookup followed by `bpf_mprog_query()`.

`tcx_link_attach()` creates a persistent link around the same mprog attach operation. Link release detaches the link-owned program. Link update replaces the program in-place with `BPF_F_REPLACE | BPF_F_ID`, swaps `link->prog` on success, and drops the old program ref.

`tcx_uninstall()` clears all programs for a direction during device teardown, sets link `dev` pointers to `NULL` so future release/update reports a dead link, drops program refs for non-link tuples, and decrements static keys per tuple.

## State And Persistence Behavior

TCX state lives on `struct net_device` through ingress/egress mprog entries. Entries hold ordered programs and/or links plus revision state managed by the generic mprog layer. `struct tcx_link` stores the generic `bpf_link` and a raw `net_device *` that is valid only while protected by RTNL and cleared by uninstall. TCX static keys track active ingress/egress hooks and are incremented/decremented when entries become active or inactive.

## Dependencies And Integration Points

`syscall.c` dispatches SCHED_CLS programs with `BPF_TCX_INGRESS` or `BPF_TCX_EGRESS` to this file for both legacy attach and `BPF_LINK_CREATE`. The implementation depends on netdevice lookup, RTNL locking, generic bpf_link lifecycle, generic bpf_mprog ordered attachment semantics, and TCX hook update/sync helpers.

## Risks And Edge Cases

RTNL locking must cover device lookup, entry replacement, and link `dev` access. Replacement paths must put the replacement program on all exits. Static key accounting must match entry activation and uninstall behavior; missed decrements would leave hooks enabled, while extra decrements could disable live hooks. `tcx_uninstall()` must handle both link-backed and prog-backed tuples without double-putting link programs. Link update must reject stale `old_prog` and dead-device cases.

## Test Signals

Tests should cover ingress and egress attach/detach/query, link attach/release/detach/update, relative ordering flags, expected revision mismatch, replacement by ID, device-not-found errors, device teardown while links are alive, fdinfo/link-info ifindex reporting before and after teardown, and concurrent attach/detach serialized by RTNL.
