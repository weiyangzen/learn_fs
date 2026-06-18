# File Research: sources/cow-pools/openzfs/module/zfs/vdev_file.c

## Purpose

Implements file-backed leaf vdevs for OpenZFS and, in userland builds, maps disk vdev operations to the same file-backed implementation. It opens regular files, reports size and ashift, and dispatches asynchronous reads, writes, flushes, and deallocations through a taskq.

## Main APIs And Entry Points

- Module lifecycle: `vdev_file_init()` creates the global `z_vdev_file` taskq, and `vdev_file_fini()` destroys it.
- Open/close and references: `vdev_file_open_mode()`, `vdev_file_open()`, `vdev_file_close()`, `vdev_file_hold()`, and `vdev_file_rele()`.
- I/O workers: `vdev_file_io_strategy()` handles read/write with ABD borrow/return helpers and `zfs_file_pread()`/`zfs_file_pwrite()`, `vdev_file_io_fsync()` handles flush, and `vdev_file_io_deallocate()` handles TRIM/deallocate.
- Vdev dispatch: `vdev_file_io_start()` routes ZIOs to the proper taskq worker, and `vdev_file_io_done()` is a no-op completion hook.
- Operation vectors: `vdev_file_ops` for file vdevs, and `vdev_disk_ops` in non-kernel builds.

## Control Flow And State

`vdev_file_open()` marks file vdevs as non-rotational and not block devices, enables attempted TRIM but disables secure TRIM, validates an absolute path, opens the file when not reopening, verifies regular-file type in kernel builds, then returns file size and tunable logical/physical ashift values. Reopen skips opening a new file and refreshes size from attributes.

`vdev_file_io_start()` handles flushes first, rejecting unreadable devices and honoring `zfs_nocacheflush`; handles TRIM by dispatching deallocation; and otherwise records an I/O delay timestamp before dispatching read/write work. The read path borrows a mutable ABD buffer then copies data back; the write path borrows a copied ABD buffer and writes with vdev ashift. Short residual success becomes `ENOSPC`.

## Dependencies And Integration

This file depends on the platform `zfs_file_*` abstraction, ABD buffer helpers, ZIO completion/interrupt helpers, taskqs, vdev state predicates, and module parameters. `vdev_file_logical_ashift` and `vdev_file_physical_ashift` are module tunables, primarily useful for testing and performance experiments at vdev creation time.

## Risks And Invariants

- File vdev paths must be absolute and backed by regular files in kernel builds.
- Asynchronous taskq workers use `vd->vdev_tsd`; close must not free it while I/O remains active under the wider vdev lifecycle guarantees.
- TRIM is optimistic for files because support depends on the host filesystem and kernel.
- Ashift tunables affect new vdev geometry and should not be treated as safe runtime layout changes.

## Summary

`vdev_file.c` is the simple leaf-vdev adapter from ZIO/ABD operations to host file operations, used for file vdevs and userland disk access.
