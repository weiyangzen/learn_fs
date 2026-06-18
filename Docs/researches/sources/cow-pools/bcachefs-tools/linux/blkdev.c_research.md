# File Research: sources/cow-pools/bcachefs-tools/linux/blkdev.c

Maps kernel bio submission onto userspace file descriptors. `generic_make_request()` handles preflush, read/write through iovecs, flush, and discard via hole punching. It supports synchronous `preadv`/`pwritev2` and libaio with a completion kthread.

Also provides `submit_bio_wait`, open/close helpers for block devices/files, capacity and logical block size queries, nonrotational detection via sysfs, and `blkdev_init()`. Zeroout is explicitly unimplemented and calls `BUG()`.
