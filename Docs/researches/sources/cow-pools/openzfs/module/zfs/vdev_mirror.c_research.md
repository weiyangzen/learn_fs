# File Research: sources/cow-pools/openzfs/module/zfs/vdev_mirror.c

## Purpose
Implements mirror-like vdev behavior for `mirror`, `replacing`, and `spare` vdev types. It handles child opening/closing, read replica selection, mirrored writes, scrub/resilver/rebuild behavior, repair I/O, state transitions, and mirror-specific kstats/tunables.

## Main Responsibilities
- Maintain mirror selection statistics through `vdev_mirror_stat_init()` and `vdev_mirror_stat_fini()`.
- Build per-I/O `mirror_map_t` state describing candidate children or root-level DVAs.
- Choose the least costly readable child for normal reads using queue load, last offset, rotational status, DTL state, and dRAID constraints.
- Issue reads to all children during scrub when not resilvering, so copies can be verified or compared.
- Issue writes to all children, with special protection for speculative rebuild repair writes.
- Retry alternate children after read failure and trigger repair writes when good data is available.
- Provide shared `vdev_ops_t` implementations for mirror, replacing, and spare vdevs.

## Key Entry Points
- `vdev_mirror_stat_init()`, `vdev_mirror_stat_fini()`: install/delete mirror kstats.
- `vdev_mirror_open()`: opens children and computes aggregate size and ashift.
- `vdev_mirror_close()`: closes all children.
- `vdev_mirror_io_start()`: maps and dispatches read/write child I/O.
- `vdev_mirror_io_done()`: evaluates child results, retries reads, selects scrub data, and issues repair writes.
- `vdev_mirror_state_change()`: maps child fault/degrade counts to parent state.
- `vdev_mirror_rebuild_asize()`: caps rebuild I/O size.
- `vdev_mirror_ops`, `vdev_replacing_ops`, `vdev_spare_ops`: exported operation vectors.

## Important Algorithms and Semantics
- `vdev_mirror_load()` scores candidates from active queue length plus a seek/linear penalty. Rotating devices distinguish exact continuation, nearby offset, and seek; non-rotating devices still get a seek penalty to preserve aggregation benefits.
- Root-level reads over multiple DVAs are treated as mirror reads across top vdevs. During sorted scrub, only the first DVA is considered until retry, because other sorted I/Os will check their own DVA copies.
- Read-only pool loads validate DVAs and skip invalid ones, allowing import attempts with incomplete or untrusted configs.
- `vdev_mirror_child_select()` skips unreadable children, marks DTL-missing children as speculative `ESTALE`, prefers dRAID distributed spares when present, and randomizes among equally preferred children.
- Scrub reads issue to every readable child and use separate ABDs for all but one child. Without a block pointer, scrub compares raw data copies and returns `ECKSUM` on mismatch.
- Direct I/O read checksum errors stop alternate-copy retries and report suspicious buffer mutation risk through direct-I/O checksum reporting.
- Repair writes are issued after unexpected read errors, resilver reads, or resilvering scrub reads when at least one good copy exists.
- Speculative sequential rebuild repair writes are restricted to rebuilding children when another child’s data is not confirmed.

## Data and State
- `mirror_child_t` tracks child vdev, ABD, offset, error, load, tried/skipped/speculative flags, and rebuilding status.
- `mirror_map_t` tracks preferred child indexes, child count, resilvering/rebuilding/root flags, and an inline child array.
- The preferred index array is allocated immediately after the inline child array by `vdev_mirror_map_alloc()`.

## Dependencies
Uses `vdev_queue_length()` and `vdev_queue_last_offset()` from `vdev_queue.c` for load scoring, DTL routines for missing/partial data checks, dRAID helpers for readable/missing checks, ZIO child I/O APIs, ABD copy/compare APIs, scan state from `dsl_scan`, and vdev state helpers.

## Tunables and Kstats
- Tunables control rotational and non-rotational load penalties:
  `zfs_vdev_mirror_rotating_inc`,
  `zfs_vdev_mirror_rotating_seek_inc`,
  `zfs_vdev_mirror_rotating_seek_offset`,
  `zfs_vdev_mirror_non_rotating_inc`,
  `zfs_vdev_mirror_non_rotating_seek_inc`.
- Kstats count linear/offset/seek classifications and preferred-child selection outcomes.

## Edge Cases and Failure Handling
- A mirror with zero children fails open with `VDEV_AUX_BAD_LABEL`.
- If all children fail open, parent aux state distinguishes all-offline from no-replicas.
- Partial mirrored writes are treated as success when at least one child succeeds, except root-level ditto writes require all copies.
- If no good read copy exists and no child remains to try, the worst non-speculative error is propagated.
