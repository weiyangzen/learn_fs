# Chunk Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/authzone.c lines 8714-8828

## Scope

This chunk covers the tail of `auth_addrs_get_mem()`, the complete memory-accounting helpers for authoritative-zone transfer state, the public `auth_zones_get_mem()` entry point, and `xfr_disown_tasks()` for worker-specific task release. It is within the `sources/os/bsd/openbsd-src` source tree included by `Docs/research_subset_a.md`.

The range starts inside `auth_addrs_get_mem()`; the function signature and local initialization are immediately before the chunk. The range ends at the end of `xfr_disown_tasks()`.

## APIs and Entry Points

- `auth_primaries_get_mem(struct auth_master *list)` sums one linked list of upstream/notify masters, including each `struct auth_master`, resolved `auth_addr` entries via `auth_addrs_get_mem()`, and optional `host`/`file` strings.
- `auth_chunks_get_mem(struct auth_chunk *list)` sums buffered transfer chunks as `sizeof(*chunk) + chunk->len` for each linked node.
- `auth_xfer_get_mem(struct auth_xfer *xfr)` is the internal accumulator for one zone transfer object, including the `auth_xfer` object, zone name storage, task timers/comm points, transfer chunks, configured master lists, and `allow_notify_list`.
- `auth_zones_get_mem(struct auth_zones *zones)` is the exported memory-usage API declared in `authzone.h`; it returns zero for `NULL`, otherwise accounts the shared auth-zone container and both zone and transfer rbtrees.
- `xfr_disown_tasks(struct auth_xfer *xfr, struct worker *worker)` is the exported worker-lifecycle helper declared in `authzone.h`; it releases any next-probe, probe, or transfer task currently owned by the given worker.

## Control Flow

Memory accounting is a set of straight-line tree/list walks. `auth_primaries_get_mem()` iterates `auth_master->next`, recursively counts `auth_master->list` address nodes, and conditionally adds C-string storage. `auth_chunks_get_mem()` iterates `auth_chunk->next` and adds each payload allocation length.

`auth_xfer_get_mem()` assumes a valid, fully initialized `auth_xfer`: it dereferences `task_nextprobe`, `task_probe`, and `task_transfer` unconditionally. It counts timer memory for next-probe, probe and transfer master lists, probe and transfer comm points/timers, transfer chunk buffers, and the allow-notify master list.

`auth_zones_get_mem()` establishes the top-level lock order by taking `zones->rpz_lock` for reading, then `zones->lock` for reading. It walks `ztree` with `az_ztree_get_mem()`, which takes each zone's read lock while calling `auth_zone_get_mem()`, and walks `xtree` with `az_xtree_get_mem()`, which takes each transfer's basic lock while calling `auth_xfer_get_mem()`. Locks are released in reverse order.

`xfr_disown_tasks()` checks each task's `worker` pointer against the supplied `worker`. Matching tasks are passed to `xfr_nextprobe_disown()`, `xfr_probe_disown()`, or `xfr_transfer_disown()`. Those helpers delete task-local event objects and clear ownership/env fields.

## State and Data Flow

- Shared container state: `struct auth_zones` owns `ztree`, `xtree`, `lock`, and `rpz_lock`; this chunk reports aggregate memory for that container and the nodes below both trees.
- Zone state: `az_ztree_get_mem()` relies on `auth_zone_get_mem()` from the previous lines, which accounts zone name storage, optional zonefile string, auth data tree, and optional RPZ state.
- Transfer state: `auth_xfer_get_mem()` reads `xfr->namelen`, `task_nextprobe->timer`, `task_probe->{masters,cp,timer}`, `task_transfer->{chunks_first,masters,cp,timer}`, and `allow_notify_list`.
- Master/address state: `auth_primaries_get_mem()` counts configured or copied master lists plus resolved address lists, but only by allocation shape visible in `struct auth_master` and `struct auth_addr`.
- Worker task ownership: `xfr_disown_tasks()` uses `task_*->worker` identity to decide which event resources belong to the worker being detached.

## Dependencies

This chunk depends on local auth-zone structures from `authzone.h`: `auth_zones`, `auth_zone`, `auth_xfer`, `auth_nextprobe`, `auth_probe`, `auth_transfer`, `auth_master`, `auth_addr`, and `auth_chunk`.

It also depends on local helpers defined earlier in `authzone.c`: `auth_zone_get_mem()`, `auth_addrs_get_mem()` prologue, `xfr_nextprobe_disown()`, `xfr_probe_disown()`, and `xfr_transfer_disown()`. Event memory accounting is delegated to libunbound comm helpers `comm_timer_get_mem()` and `comm_point_get_mem()`. Tree traversal and synchronization use `RBTREE_FOR`, `lock_rw_rdlock()`, `lock_rw_unlock()`, `lock_basic_lock()`, and `lock_basic_unlock()`.

## Risks and Edge Cases

- `auth_xfer_get_mem()` unconditionally dereferences all three task pointers and their timer/comm fields. It relies on construction invariants that these task objects exist even if their worker-owned event handles are `NULL`.
- `auth_zones_get_mem()` reports an approximate live allocation total while holding read locks; it does not include allocator overhead and depends on each helper matching the ownership model of its structures.
- `auth_chunks_get_mem()` adds `chunk->len` rather than inspecting `chunk->data`; this is correct only if `len` is the allocated payload length, as documented in `authzone.h`.
- `xfr_disown_tasks()` does not take `xfr->lock` itself. The disown helpers' comments state their caller must hold `xfr.lock`, so callers of this exported helper must preserve that locking contract.
- `xfr_disown_tasks()` does not delete transfer chunks before disowning a transfer task. Nearby `auth_zones_cleanup()` deletes chunks before `xfr_transfer_disown()`, so callers must decide whether buffered transfer data should be retained or freed.
- The disown path assumes `task_nextprobe`, `task_probe`, and `task_transfer` are non-NULL before checking their `worker` fields.

## Cross-Chunk References

- The beginning of `auth_addrs_get_mem()` and the full `auth_zone_get_mem()` implementation are immediately before this chunk.
- Earlier chunks define the auth-zone data-tree memory helpers used by `auth_zone_get_mem()`.
- Earlier transfer code defines `xfr_nextprobe_disown()`, `xfr_probe_disown()`, and `xfr_transfer_disown()`; those helpers delete timers/comm points and clear task ownership.
- Earlier lifecycle code such as `auth_zones_cleanup()` shows the same disown helpers used while holding `xfr->lock`, and also shows that transfer chunks may need explicit deletion before transfer-task disowning.
- `authzone.h` declares the exported APIs `auth_zones_get_mem()` and `xfr_disown_tasks()` and documents the task ownership model: task `worker == NULL` means unowned, and worker-owned event resources live on that worker's event base.