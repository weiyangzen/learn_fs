<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/blktrans.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/blktrans.h

## Purpose
`mtd/blktrans.h` declares the MTD block translation layer, which exposes MTD devices through block-device style disks backed by translation drivers.

## Important APIs, Types, and Functions
It defines `struct mtd_blktrans_dev`, `struct mtd_blktrans_ops`, `register_mtd_blktrans()`, `deregister_mtd_blktrans()`, `add_mtd_blktrans_dev()`, `del_mtd_blktrans_dev()`, `mtd_blktrans_cease_background()`, and `module_mtd_blktrans()`.

## Control Flow and State
Translation drivers register operations. When matching MTD devices appear, `add_mtd()` creates `mtd_blktrans_dev` instances with request queues, disks, tag sets, locks, references, and optional background workers. Block requests are translated to `readsect`, `writesect`, `discard`, `flush`, and geometry callbacks. Removal calls `remove_dev()` and tears down disks/queues.

## State and Persistence Behavior
State is runtime block/MTD translation state. Data persistence is provided by underlying MTD storage. `open`, `readonly`, `writable`, `bg_stop`, kref, and queue fields track live block-device behavior.

## Dependencies and Integration Points
It depends on mutexes, krefs, sysfs, block layer types, request queues, `gendisk`, MTD core, and module ownership. Users include translation drivers such as block2mtd/ftl-style components.

## Risks
Open/release and add/remove callbacks run under `mtd_table_mutex`. Queue locking, background worker stop, and kref lifetime are critical during hot removal. Sector size/shift mismatches can corrupt I/O. Writable/readonly flags must match hardware state.

## Test Signals
Register/deregister translation drivers, hot-add/remove MTD devices, block read/write/discard/flush tests, background worker shutdown, open-during-remove races, and module unload with active disks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/blktrans.h -->
