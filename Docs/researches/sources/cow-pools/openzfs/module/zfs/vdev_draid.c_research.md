# File Research: sources/cow-pools/openzfs/module/zfs/vdev_draid.c

## Purpose

Implements OpenZFS dRAID top-level vdev behavior plus the distributed spare pseudo-leaf vdev. dRAID spreads raidz-style redundancy groups across many children using fixed, deterministic permutation maps, reserves distributed spare capacity across those children, supports failure-domain layouts wider than a single child set, and exposes `vdev_draid_ops` / `vdev_draid_spare_ops` to the generic vdev layer.

## Main APIs And Entry Points

- Fixed layout generation: `vdev_draid_generate_perms()`, `vdev_draid_lookup_map()`, `vdev_draid_shuffle_perms()`, `vdev_draid_get_perm()`, and `vdev_draid_permute_id()` build and query the immutable child permutation table.
- Size and allocation geometry: `vdev_draid_psize_to_asize()`, `vdev_draid_asize_to_psize()`, `vdev_draid_get_astart()`, `vdev_draid_min_asize()`, `vdev_draid_min_alloc()`, `vdev_draid_rebuild_asize()`, and `vdev_draid_metaslab_init()` define full-stripe, group-aligned allocation behavior.
- dRAID I/O mapping: `vdev_draid_logical_to_physical()`, `vdev_draid_map_alloc_row()`, `vdev_draid_map_alloc()`, `vdev_draid_map_alloc_write()`, `vdev_draid_map_alloc_read()`, `vdev_draid_map_alloc_scrub()`, `vdev_draid_map_alloc_empty()`, and `vdev_draid_map_verify_empty()` turn a logical dRAID I/O into one or two raidz rows with parity, data, and empty skip-sector ABDs.
- Top-level vdev lifecycle and operations: `vdev_draid_init()`, `vdev_draid_fini()`, `vdev_draid_open()`, `vdev_draid_close()`, `vdev_draid_io_start()`, `vdev_draid_io_done()`, `vdev_draid_state_change()`, `vdev_draid_xlate()`, `vdev_draid_config_generate()`, `vdev_draid_nparity()`, and `vdev_draid_ndisks()`.
- Resilver and DTL helpers: `vdev_draid_missing()`, `vdev_draid_partial()`, `vdev_draid_readable()`, `vdev_draid_group_degraded()`, `vdev_draid_group_missing()`, `vdev_draid_need_resilver()`, and `vdev_draid_rebuilding()`.
- Distributed spare operations: `vdev_draid_spare_create()`, `vdev_draid_spare_get_parent()`, `vdev_draid_spare_get_child()`, `vdev_draid_fail_domain_allowed()`, `vdev_draid_spare_open()`, `vdev_draid_spare_io_start()`, `vdev_draid_read_config_spare()`, `vdev_draid_spare_lookup()`, `vdev_draid_spare_init()`, and config/fini helpers.

## Control Flow And Data Model

The top comment documents the on-disk layout contract: rows are 16 MiB-per-child chunks, groups are `ndata + nparity` columns, slices hold an LCM-based group count, and permutation rows spread groups across children and distributed spare slots. The hard-coded `draid_maps[]` table is part of the storage format; changing seeds, child counts, permutation counts, or checksums would change physical placement and make existing pools unreadable.

`vdev_draid_init()` validates the nvlist geometry (`ndata`, `nparity`, `nspares`, `ngroups`, child count, and optional failure-domain width), looks up the fixed map for the child count, generates the permutation array with the private PRNG, optionally shuffles slices for failure-domain layouts, and fills derived constants such as group width, usable disk count, group size, and per-device slice size. `vdev_draid_open()` then opens normal children before distributed spares, checks parity/failure-domain tolerance, calculates allocatable size from the smallest non-spare child minus reflow reserve, and rounds capacity to row/group or big-slice boundaries.

Normal I/O starts in `vdev_draid_io_start()`. It creates a `raidz_map_t` that may contain two rows if a logical block crosses a dRAID group boundary. `vdev_draid_map_alloc_row()` calculates quotient/remainder sectors across data columns, records empty columns, assigns each column a permuted child id and physical offset, allocates parity ABDs, and maps data ABDs differently for writes, normal reads, and scrub/resilver reads. Writes always write full columns with zero-backed skip sectors included in parity. Normal reads read only needed data columns until error handling requires parity/empty-sector expansion. Scrub/resilver reads allocate backing ABDs for empty sectors so those bytes can be verified and repaired.

Read startup reverse-iterates columns, marks unreadable or DTL-missing columns, expands empty-column backing if reconstruction may be needed, applies latency-outlier skipping when parity can recover the omitted column, and sets repair policy flags for active distributed spare and replacing/spare rebuild trees. Completion is delegated to raidz via `vdev_raidz_io_done()`, while `vdev_draid_map_verify_empty()` protects against corrupt skip sectors being used as authoritative parity input.

The distributed spare vdev is a virtual leaf. It has no normal label contents on disk, opens by locating its parent dRAID by GUID, sizes itself from the parent dRAID child capacity, and maps each non-label I/O offset through the parent dRAID permutation table to the actual child device. Label writes are accepted only for probe/config-writer initialization cases; label reads are accepted only for probes, and real config reads are handled by `vdev_draid_read_config_spare()`.

## Dependencies And Integration

This file sits directly between the generic vdev layer, raidz math/reconstruction, ZIO, ABDs, DTLs, pool config nvlists, vdev rebuild, failure-management ereports, and SPA feature/config plumbing. It relies on `vdev_draid_rand()` from `vdev_draid_rand.c` for deterministic permutation generation and on `vdev_raidz_*` helpers for parity generation, child completion, and final reconstruction. The exported `vdev_draid_ops` and `vdev_draid_spare_ops` are consumed by vdev construction and dispatch code elsewhere in OpenZFS.

## Risks And Invariants

- The permutation table and PRNG output are on-disk compatibility data. Any behavioral change breaks existing dRAID pools.
- Group alignment is mandatory: dRAID allocations and rebuild chunks must start on `vdev_draid_get_astart()` boundaries and avoid spanning more than the expected group boundary split.
- Empty skip sectors are part of parity but not protected by the user data checksum. Verification must zero and flag corrupt empty sectors before parity repair.
- Distributed spare DTL behavior is not the same as a normal leaf. Missing/partial/readable checks recurse through spare/replacing/dRAID-spare trees at the target physical offset.
- Failure-domain support counts multiple same-position child failures as one only while no failure group exceeds parity tolerance; used spares can reduce domain-failure tolerance.
- Repair during sequential rebuild is deliberately constrained because rebuild I/O may not have an end-to-end checksum.

## Summary

`vdev_draid.c` is the dRAID layout and dispatch engine. It deterministically maps logical dRAID space to raidz-style rows across permuted child devices, provides full-stripe write/read/scrub semantics, integrates dRAID-specific resilver decisions, and implements distributed spares as virtual leaves backed by parent dRAID child offsets.
