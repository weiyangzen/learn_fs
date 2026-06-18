# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_disk.c

## Purpose

Linux block-device implementation for the OpenZFS leaf disk vdev. It opens and closes Linux block devices, translates ZFS `zio_t` read/write/flush/TRIM requests into Linux BIO operations, reports capacity and ashift data, handles block-layer compatibility across kernel versions, and registers `vdev_disk_ops`.

## Main Structures And Tunables

- `zfs_bdev_handle_t` abstracts kernel-version differences between `struct bdev_handle`, `struct file`, and older raw `struct block_device *` handles.
- `vdev_disk_t` stores the current block-device handle plus `vd_lock`, a reader/writer lock protecting concurrent I/O versus close/reopen.
- `zfs_vdev_disk_max_segs` limits BIO segment count when nonzero, clamped against the device queue and a minimum of 4.
- `zfs_vdev_open_timeout_ms` controls retry time for transient udev path disappearance or zvol `ERESTARTSYS`.
- `zfs_vdev_failfast_mask` maps the vdev failfast property into Linux BIO failfast flags.

## Open/Close And Capacity

- `vdev_bdev_mode()` converts SPA read/write mode into Linux block open flags and always requests exclusive access.
- `bdev_capacity()` and `bdev_max_capacity()` calculate current usable bytes and potential expansion bytes. Whole-disk expansion accounts for EFI reserved space, `NEW_START_BLOCK`, and partition end alignment.
- `vdev_disk_open()` validates absolute `vdev_path`, handles reopen by dropping the old handle under writer lock, optionally rereads partition tables during expansion, retries opens for transient `ENOENT` and zvol `ERESTARTSYS`, then records block size, write-cache, TRIM, secure TRIM, rotational, capacity, and ashift properties.
- `vdev_disk_close()` skips close during `vdev_reopening`; otherwise it takes writer lock, releases the block device, clears `vdev_tsd`, destroys the lock, and frees `vdev_disk_t`.

## BIO Compatibility And Submission

The file contains compatibility code for Linux block API changes, including `bio_alloc()` signatures, `bio_set_dev()`, cgroup `blkg_tryget()`, and GPL-only symbol avoidance. `vdev_submit_bio()` temporarily clears `current->bio_list` around `submit_bio()` to avoid unwanted bio recursion/plugging effects.

`vdev_bio_max_segs()` combines device queue limits, kernel limits, and the tunable. `vdev_bio_max_bytes()` uses queue max sectors.

## Read/Write Data Path

- `vbio_t` is a ZFS-side wrapper for one ZIO translated into one or more chained BIOs.
- `vbio_alloc()` captures the parent ZIO, target block device, max segments/bytes, logical block-size mask, starting offset, current BIO, optional bounce ABD, and flags.
- `vbio_add_page()` allocates BIOs, sets sector/op/flags, adds page segments respecting logical-block-size alignment and max BIO byte constraints, chains and submits full BIOs, and advances offsets.
- `vbio_submit()` starts a block plug, iterates ABD pages via `abd_iterate_page_func()`, sets the final BIO completion callback/private pointer, submits the chain, and finishes the plug.
- `vbio_completion()` converts BIO status to `zio->io_error`, logs errors via `vdev_disk_error()`, releases the BIO, stashes `vbio` in `zio->io_bio`, and uses `zio_delay_interrupt()` so cleanup happens outside interrupt context.

Before submission, `vdev_disk_io_rw()` rejects accesses beyond `bdev_capacity()`, resolves inherited/default failfast policy, applies failfast flags unless retrying/tryhard, and checks whether the ABD page layout can be submitted directly. If the ABD has data that would force unsafe LBS/page-boundary splits, it allocates an aligned ABD bounce buffer, copies write data into it, verifies alignment, and saves it on the `vbio`.

`vdev_disk_io_done()` frees the `vbio`, copies read data back from a bounce ABD if needed, frees the bounce ABD, and on `EIO` revalidates disk status. Failed media checks invalidate the block device, mark removal wanted, and request `SPA_ASYNC_REMOVE`.

## Flush And TRIM

- `vdev_disk_io_flush()` allocates an empty BIO, installs `vdev_disk_io_flush_completion()`, sets flush operation attributes, submits, and invalidates the block device cache.
- Flush start logic respects `vdev_readable()`, `zfs_nocacheflush`, and `vdev_nowritecache`, returning `ENXIO`, success, or `ENOTSUP` without issuing a BIO when appropriate.
- `vdev_bdev_issue_secure_erase()` and `vdev_bdev_issue_discard()` wrap kernel-version-specific secure discard and discard APIs.
- `vdev_disk_io_trim()` chooses secure erase versus discard, maps ZIO offset/size to sectors, handles sync success by interrupting the ZIO immediately, or installs `vdev_disk_discard_end_io()` for async completion.

## Vdev Ops And Parameters

`vdev_disk_io_start()` dispatches ZIO types under `vd_lock`: flush, TRIM, read/write, and a defensive `ENOTSUP` default. `vdev_disk_ops` wires disk vdev behavior into the core vdev layer, including open, close, I/O start/done, hold/release stubs, default sizing/xlate helpers, and `vdev_disk_kobj_evt_post()`.

The file also defines setters for min/max auto ashift that validate against `ASHIFT_MIN`, `ASHIFT_MAX`, and the counterpart tunable before delegating to `param_set_uint()`.

## Notable Edges

- Uses retry windows to mask transient udev path churn.
- Uses writer/read locks to prevent I/O against a closing or failed reopen device handle.
- Uses bounce ABDs only when Linux page/LBS splitting constraints require them.
- Errors in completion paths are logged with pool/vdev/type/offset/size context via `printk()`, because some completions may run in interrupt context.
