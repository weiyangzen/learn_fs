# sources/distributed-fs/lustre-release/lustre/mdc/mdc_changelog.c

## Purpose

`mdc_changelog.c` implements MDC-side delivery of Lustre MDT changelog records through per-MDT Linux character devices named from the connected MDT target. It bridges kernel llog changelog catalogs (`LLOG_CHANGELOG_REPL_CTXT`) to user space by opening the changelog catalog, prefetching records in a kernel thread, and exposing read, poll, seek, write-control, and ioctl operations on `/dev/changelog-*` devices. The file also manages global registration of changelog devices so multiple MDC OBDs or mount points that target the same MDT share one char device while preserving OBD references for teardown.

## Important APIs, Types, And Functions

Key state is split between `struct chlg_registered_dev` and `struct chlg_reader_state`. `chlg_registered_dev` owns the `cdev`, embedded `device`, global-list linkage, OBD list, and `kref` lifecycle for one target device. `chlg_reader_state` is per-open-file state: selected OBD, producer thread, error/EOF flags, start offset, wait queues, bounded record queue, llog cursor positions, ioctl flags, and user changelog filter mask. `struct chlg_rec_entry` stores one copied `struct changelog_rec` plus its variable name payload.

Public integration functions are `mdc_changelog_cdev_init()` and `mdc_changelog_cdev_finish()`, called from MDC setup/fini. They allocate or find a shared target device, allocate an IDR minor, initialize `device`/`cdev`, register file operations, link the OBD into `ced_obds`, and later remove that OBD and drop the device reference. The file exports global state declared in `mdc_internal.h`: `mdc_changelog_class`, `mdc_changelog_dev`, and `mdc_changelog_minor_idr`.

The main file operations are `chlg_open()`, `chlg_release()`, `chlg_read()`, `chlg_write()`, `chlg_llseek()`, `chlg_poll()`, and `chlg_ioctl()`. `chlg_ioctl()` handles `OBD_IOC_CHLG_POLL` flags and `OBD_IOC_CHANGELOG_FILTER`, the latter using `mdc_changelog_get_user_info()` to issue `MDS_GET_INFO` with `KEY_CHANGELOG_USER`.

## Control Flow

Open allocates `chlg_reader_state`, increments the registered-device kref, initializes queues and wait queues, and delays starting the producer. The first read or poll calls `chlg_start_thread()`, which spawns `chlg_load()`. The producer grabs a live OBD from the registered device list via `chlg_obd_get()`, opens and initializes the changelog catalog, and calls `llog_cat_process()` with `chlg_read_cat_process_cb()`. The callback validates `CHANGELOG_REC`, updates catalog/index cursors, skips old or masked records, waits while the local queue has `CDEV_CHLG_MAX_PREFETCH` entries, copies the variable-sized record, enqueues it under `crs_lock`, and wakes consumers.

Reads wait for queued records, EOF, or an error. They copy only whole records to user space, move consumed records to a temporary list, advance `crs_start_offset` to the next record index, wake the producer, free consumed entries, and update `file->f_pos`. Nonblocking reads return `-EAGAIN`, EOF, or a producer error when no record is queued. Seeking supports forward-only `SEEK_SET` and `SEEK_CUR` by updating `crs_start_offset` and discarding prefetched records below the new offset. Writes accept a compact control command, currently `clear:cl%u:%llu`, and send `KEY_CHANGELOG_CLEAR` through `obd_set_info_async()`.

If `CHANGELOG_FLAG_FOLLOW` is set, `chlg_load()` closes the current catalog, drops references, sleeps for one second, and reopens the catalog from the saved cursor until stopped. Release stops the thread, frees any queued records, and drops the registered-device reference.

## State And Persistence Behavior

Persistent changelog data lives on MDT llogs; this file does not persist records locally. It keeps only per-open cursors and a bounded in-memory queue. The reader offset is monotonic except initialization; backward seek is rejected. `chlg_clear()` persists progress for a changelog user by asking the MDT to clear records up to a supplied index. Registered-device state is global kernel state protected by `chlg_registered_dev_lock`; minor allocation is protected by `chlg_minor_lock` and the IDR.

Reference management is central: device lifetime uses `kref`, char-device release frees the allocated registered device and minor, OBD access is protected by `class_incref()`/`class_decref()`, and file release stops producer activity before freeing queue memory.

## Dependencies And Integration Points

The file depends on Linux char-device, device, IDR, kthread, poll, wait-queue, and copy-to/from-user APIs. Lustre dependencies include llog catalog APIs, `obd_set_info_async()`, changelog UAPI ioctls, `sptlrpc`/PTLRPC request capsules for `MDS_GET_INFO`, and MDC setup in `mdc_request.c`/`mdc_dev.c`. Naming integrates with Lustre OBD names using `get_target_name()` to convert an MDC OBD name into an MDT-level changelog device name.

## Risks

Concurrency risks center on global device teardown while files are open, producer blocking on a full queue, and OBD list mutation under the registered-device mutex. The code mostly mitigates these with krefs, OBD class refs, wait queues, and thread stop checks, but `mdc_changelog_cdev_finish()` assumes `chlg_registered_dev_find_by_obd()` returns a device and would dereference `NULL` if lifecycle accounting were violated. User record copying is whole-record only, so too-small buffers can make progress stall until a large enough read is issued. The filter mask uses `BIT(rec->cr.cr_type)`, so unexpected record type values would need to remain within the mask width.

## Test Signals

Useful tests are open/read/poll behavior on empty and populated changelogs, nonblocking reads, forward seek with prefetched records, follow mode across later records, `clear:clN:record` writes, filter ioctl behavior with server-provided masks, concurrent mounts sharing one target device, and teardown with open descriptors. Fault-injection signals include OBD disappearance while the producer runs, allocation failure for queued records, `copy_to_user()`/`copy_from_user()` failures, llog open/init/process errors, and minor exhaustion.
