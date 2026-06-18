# File Research: sources/block-storage/linux-dm/drivers/md/dm-bufio.c

Implements Device Mapper's buffered I/O cache library. A `dm_bufio_client` owns rb-tree indexed buffers, clean/dirty LRU lists, reserved buffers, a dm-io client, shrinker integration, and per-client locking. Each `dm_buffer` tracks block number, data allocation mode, hold count, dirty/write ranges, read/write state bits, errors, and optional debug stack traces.

Memory policy limits global cached bytes by RAM/vmalloc percentages, retains a configurable minimum, ages out old buffers, and triggers background replacement work when global allocation exceeds the cache limit. Buffer data may come from a slab cache, `__get_free_pages`, or `vmalloc`, selected by block size and allocation constraints.

Lookup/new/read paths use the rb-tree and LRU lists under the client mutex. `dm_bufio_get()` returns only an existing non-reading buffer; `dm_bufio_read()` allocates and reads; `dm_bufio_new()` allocates fresh without disk read; `dm_bufio_prefetch()` submits asynchronous reads. Allocation is failure-tolerant through reserved buffers, reclaiming unheld buffers, and waiting on a free-buffer queue.

Writeback tracks partial dirty byte ranges and aligns writes to 4 KiB. Small direct-mapped buffers use bios; vmalloc or too-large buffers fall back to dm-io. Dirty writes can be launched async, then synchronously waited and followed by a device flush. Discard and flush helpers issue dm-io operations directly.

Lifecycle code creates per-client slab caches, reserved buffers, dm-io client, shrinker, and global client registration. Destroy flushes/drops buffers, unregisters shrinkers, checks leaks, and frees caches. Module init creates the global workqueue and periodic cleanup; exit cancels work and BUGs on leaked clients or allocated memory.
