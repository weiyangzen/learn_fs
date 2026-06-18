## sources/distributed-fs/ceph-client/drivers/mtd/devices/block2mtd.c

Purpose: emulates an MTD RAM-like device on top of a writable block device. It is useful for testing MTD filesystems on block media or exposing compact-flash-like media through MTD interfaces.

Important APIs, types, and functions: `struct block2mtd_dev` stores the backing block-device file, embedded `mtd_info`, list node, and write mutex. MTD callbacks are `block2mtd_read()`, `block2mtd_write()`, `block2mtd_erase()`, and `block2mtd_sync()`. `add_device()` opens the block device and registers the MTD. `block2mtd_setup()` and `block2mtd_setup2()` parse the `block2mtd=` module/kernel parameter.

Control flow: parameter parsing accepts `<dev>[,[<erasesize>][,<label>]]`, with human-readable size suffixes. During early boot, non-module builds defer parameter handling until `late_initcall`. Reads and writes operate through the block device address-space page cache. Erase reads pages and fills non-0xff pages with 0xff. Writes and erases are serialized by `write_mutex`, dirty pages are rate-limited, and sync calls `sync_blockdev()`.

State and persistence: global `blkmtd_device_list` tracks registered devices. Backing state persists on the block device through the page cache and block layer. Each MTD name is allocated, and the block-device file reference is held until exit.

Dependencies and integration points: depends on block layer file opening, address-space page cache, MTD core registration, kernel parameter plumbing, and early boot device lookup for built-in usage.

Risks: no partition parser is used; the whole block device is exposed. Erase size must divide device size. Using an MTD block device as backing is rejected to avoid recursion. Page-cache manipulation means writeback and invalidation behavior are central correctness risks.

Test signals: module parameter parsing, early-boot deferred creation, read/write/erase across page boundaries, sync flushing, rejection of invalid erase sizes and MTD block backends, custom labels, and clean unregister/free on module exit.
