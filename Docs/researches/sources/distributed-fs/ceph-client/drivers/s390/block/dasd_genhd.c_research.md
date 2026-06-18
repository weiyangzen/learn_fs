# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_genhd.c

Purpose: provides the DASD driver's Linux block-device registration glue: disk naming, blk-mq tag-set/disk allocation, major registration, readonly propagation, and partition scan/destruction helpers.

Important APIs/types/functions: `dasd_name_format()` generates `dasda...` names from `devindex`; `dasd_gendisk_alloc()` configures `struct blk_mq_tag_set`, queue limits, `struct gendisk`, minors, `dasd_device_operations`, sysfs links, and `device_add_disk()`; `dasd_gendisk_free()` tears down disk/tag state; `dasd_scan_partitions()` opens the whole disk and calls `bdev_disk_changed()`; `dasd_destroy_partitions()` forces partition invalidation and drops the scan-time open; `dasd_gendisk_init()`/`exit()` register major 94.

Control flow: a DASD block object reaches this file during online setup. The code allocates blk-mq resources, assigns the fixed DASD major/minor range, derives the disk name, marks readonly if the device or feature map says so, publishes the disk, then later scans partitions by temporarily opening the disk. Offline paths remove partitions before freeing the disk and tag set.

State and persistence behavior: persistent state is kernel block-layer state only: `block->gdp`, `block->tag_set`, and `block->bdev_file`. `queue_depth` and `nr_hw_queues` are read-only module parameters for newly allocated disks. No on-disk metadata is changed here.

Dependencies and integration points: depends on Linux blk-mq, gendisk, partition rescan, DASD devmap/indexing, `dasd_mq_ops`, `dasd_device_operations`, and ccw device parent objects.

Risks and test signals: name formatting and minor exhaustion must be tested near `DASD_PER_MAJOR`; error paths must free tag sets exactly once. Partition scan/offline race behavior hinges on `block->bdev_file` and open-count accounting. Test with readonly devices, failed `blk_mq_alloc_disk()`, failed `device_add_disk()`, hot offline while partition scanning, and high devindex values.
