# sources/distributed-fs/ceph-client/drivers/mtd/mtd_blkdevs.c

Purpose: common block-layer bridge for MTD translation drivers such as `mtdblock`. It lets a translation driver register `struct mtd_blktrans_ops`, creates blk-mq disks for each matching MTD, routes block requests to sector callbacks, and tracks devices through MTD add/remove notifiers.

Important APIs/types/functions: `register_mtd_blktrans()`, `deregister_mtd_blktrans()`, `add_mtd_blktrans_dev()`, `del_mtd_blktrans_dev()`, `do_blktrans_request()`, `mtd_queue_rq()`, `blktrans_open()`, `blktrans_release()`, `mtd_blktrans_work()`, and notifier callbacks. It depends on `mtd_table_mutex`, `__get_mtd_device()`, blk-mq tag sets, `gendisk`, request queues, and translation callbacks (`readsect`, `writesect`, `discard`, `flush`, `background`).

Control flow: registering a translation major installs the MTD notifier, registers a block major, adds the ops to `blktrans_majors`, and scans existing MTDs. Each added device gets a devnum, tag set, disk, queue limits, disk name, capacity, and sysfs attributes. Requests are queued under `queue_lock` and synchronously drained by `mtd_blktrans_work()`, which serializes actual I/O under `dev->lock` and can run one background pass per idle period. Removal deletes the disk, freezes/quiesces the queue, releases any open MTD, nulls `dev->mtd`, and drops references.

State and persistence: runtime state is lists of translation majors/devices, request lists, open counts, krefs, queue locks, and writable flags. Persistent data lives behind underlying MTDs.

Risks and test signals: request code maps only the first bio page for read/write loops, so assumptions about request segment layout matter. Removal races are controlled through queue freezing and `queuedata = NULL`. Tests should cover open/remove races, dynamic MTD add/remove, readonly devices, flush/discard errors, background stop behavior, devnum allocation, and module refcounting.
