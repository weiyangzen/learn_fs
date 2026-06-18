# sources/distributed-fs/ceph-client/drivers/mtd/devices/mtdram.c

Purpose: synthetic RAM-backed MTD device mainly for testing MTD users. It allocates vmalloc memory, initializes it to erased state, and exposes it as `MTD_RAM`.

Important APIs/types/functions: module parameters `total_size`, `erase_size`, and `writebuf_size`; global `mtd_info`; callbacks `ram_erase()`, `ram_point()`, `ram_unpoint()`, `ram_read()`, `ram_write()`; reusable initializer `mtdram_init_device()`; lifecycle `init_mtdram()`/`cleanup_mtdram()`.

Control flow: module init validates nonzero size, allocates `mtd_info` and vmalloc storage, calls `mtdram_init_device()`, then fills storage with `0xff`. MTD callbacks directly `memcpy` or `memset` over `mtd->priv`. `ram_point()` can return virtual and optional physical address information, trimming retlen to contiguous physical vmalloc pages.

State and persistence: all data is volatile vmalloc memory. The only module-global state is the single supported `mtd_info` pointer. Erase state is represented by bytes set to `0xff`.

Dependencies/integration: uses vmalloc, `vmalloc_to_pfn()` for physical point support, MTD registration, and configuration defaults from `CONFIG_MTDRAM_TOTAL_SIZE` and `CONFIG_MTDRAM_ERASE_SIZE`.

Risks: callbacks rely on MTD core range validation; only one device is supported; total/erase sizes are module parameters in KiB but writebuf size is bytes; physical contiguity from vmalloc is limited and carefully clipped.

Test signals: load with valid/invalid sizes, verify `/proc/mtd` registration, erase alignment failures through `check_offs_len()`, read/write round trips, `mtd_point()` behavior across non-contiguous vmalloc pages, and cleanup freeing storage.
