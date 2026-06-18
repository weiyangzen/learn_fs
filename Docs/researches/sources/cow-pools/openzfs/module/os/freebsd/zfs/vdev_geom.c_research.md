# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_geom.c

## Scope

FreeBSD GEOM-backed disk vdev implementation. It attaches ZFS vdevs to GEOM providers, reads labels, finds devices by path or GUIDs, handles provider events, translates ZIO reads/writes/trims/flushes into BIOs, and exposes `vdev_disk_ops`.

## Main Interfaces

- GEOM class: `zfs_vdev_class` with attrchanged callback.
- Attach/open helpers: `vdev_geom_attach()`, `vdev_geom_detach()`, `vdev_geom_open_by_path()`, `vdev_geom_open_by_guids()`, `vdev_geom_open()`, `vdev_geom_close()`.
- Label scanning: `vdev_geom_read_pool_label()`, `vdev_geom_read_config()`, `vdev_attach_ok()`, `process_vdev_config()`.
- I/O: `vdev_geom_io_start()`, `vdev_geom_io_intr()`, `vdev_geom_io_done()`.
- Unmapped I/O helpers: `vdev_geom_check_unmapped()` and `vdev_geom_fill_unmap_cb()`.
- Exported ops table: `vdev_disk_ops`.

## State And Control Flow

A shared GEOM named `zfs::vdev` owns consumers for providers. Each consumer private list tracks all `vdev_t` instances using that provider. Provider physpath changes update `vdev_physpath` and request config updates. Resize events autoexpand healthy vdevs when the pool requests it. Orphan events mark vdevs for async removal instead of closing under GEOM topology lock.

Opening sets a TSD marker so lower zvol probing can avoid recursion, validates `/dev/` paths, then either opens by path ignoring GUIDs for new/add/split cases or validates path labels and falls back to all-provider GUID search. On success it records provider size, sector ashift, stripe ashift, rotation rate, block-device status, and TRIM capability.

I/O start handles policy skips for disabled flush/delete, allocates a `bio`, maps ZIO type to BIO command, and for read/write either supplies unmapped page arrays for suitable scatter ABDs or borrows/copies a linear buffer. Completion records BIO errors/residuals, detects device removal, destroys non-data BIOs immediately, and delays ZIO interrupt. `io_done` returns borrowed buffers or frees unmapped page arrays.

## Dependencies

Uses FreeBSD GEOM provider/consumer APIs, BIOs, topology locking, VM page extraction, ABD iteration/borrowing, ZIO delay/error paths, SPA async requests, vdev config/label helpers, sysctl tunables, and TSD key from module init.

## Correctness Notes

Lock ordering is critical: provider orphan handling avoids taking SPA config locks while holding GEOM topology. Device discovery releases topology while reading labels, then reacquires it to detach. BIO offsets/sizes are sector-aligned for label probing. Unmapped I/O is used only when the provider accepts it and ABD chunk layout can be represented as a virtually contiguous page array. Close may be delayed during reopen unless the provider is orphaned or errored.
