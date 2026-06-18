# sources/distributed-fs/ceph-client/drivers/block/ps3vram.c

## Purpose
Exposes PlayStation 3 GPU video RAM as a Linux block device. The driver allocates RSX/GPU memory through LV1, maps a 2 MiB XDR system-memory buffer into the GPU context, uses the FIFO DMA engine to move pages between XDR and VRAM, and maintains a small write-back cache to service block bios.

## Important APIs, Types, And Functions
`struct ps3vram_priv` owns the gendisk, VRAM size, LV1 memory/context handles, MMIO control/report mappings, XDR buffer, FIFO pointers, cache, spinlock, and queued bio list. `struct ps3vram_cache` stores cache geometry, tags, and hit/miss counters; each `struct ps3vram_tag` records VRAM page address and present/dirty flags.

Hardware/FIFO helpers include `ps3vram_notifier_reset()`, `ps3vram_notifier_wait()`, `ps3vram_init_ring()`, `ps3vram_wait_ring()`, `ps3vram_begin_ring()`, `ps3vram_fire_ring()`, `ps3vram_bind()`, `ps3vram_upload()`, and `ps3vram_download()`. Cache and I/O helpers are `ps3vram_cache_match()`, `ps3vram_cache_evict()`, `ps3vram_cache_load()`, `ps3vram_cache_flush()`, `ps3vram_read()`, `ps3vram_write()`, `ps3vram_do_bio()`, and `ps3vram_submit_bio()`.

## Control Flow
Module init checks PS3 LV1 firmware, registers a dynamic block major, and registers a PS3 GPU RAM disk system-bus driver. Probe allocates private state and a 2 MiB XDR buffer, opens the GPU HV device, allocates as much GPU memory as possible up to the `size` module parameter, allocates a GPU context, maps XDR into the context, ioremaps control and reports areas, initializes and binds FIFO channels, initializes cache tags, creates `/proc/ps3vram`, allocates a no-partition disk, sets capacity to allocated VRAM, and adds the disk.

The block layer calls `ps3vram_submit_bio()` directly through `submit_bio`. Bios are serialized by `priv->list`: the first submitter drains the list synchronously with `ps3vram_do_bio()`, while later bios queue and return. Each bio segment is mapped with `bvec_virt()` and serviced by `ps3vram_read()` or `ps3vram_write()`. Cache misses evict a random entry, write back dirty contents with `ps3vram_upload()`, then load the requested page with `ps3vram_download()`. Writes update the XDR cache copy and set `CACHE_PAGE_DIRTY`; dirty pages reach VRAM on eviction or cleanup.

## State And Persistence Behavior
The block contents live in allocated GPU memory and disappear when the driver releases that memory. Dirty data can remain in XDR cache until eviction or `ps3vram_cache_flush()` during cleanup, so orderly remove/shutdown matters. Runtime state includes FIFO positions, cache tags, hit/miss counters exported through `/proc/ps3vram`, queued bios, LV1 handles, and MMIO mappings. There is no durable metadata or partition scanning (`GENHD_FL_NO_PART`).

## Dependencies And Integration Points
Depends on PS3 platform headers and LV1 GPU APIs (`ps3_open_hv_device`, `lv1_gpu_memory_allocate`, `lv1_gpu_context_allocate`, `lv1_gpu_context_iomap`, `lv1_gpu_fb_blit`), global `ps3_gpu_mutex`, Linux block `submit_bio`, procfs, and system-bus matching `PS3_MATCH_ID_GPU` plus `PS3_MATCH_SUB_ID_GPU_RAMDISK`. Parent block build logic includes it under `CONFIG_PS3_VRAM`.

## Risks
This driver is tightly coupled to RSX FIFO details and big-endian MMIO ordering; regressions are hard to validate without real hardware. I/O is synchronous and serialized, so stalls in notifier or FIFO wait paths can block submitters. Cache replacement uses `jiffies` plus a static counter and is not optimized for performance. Dirty cache writeback errors are logged but cannot reliably recover user data. The code assumes PS3 ppc64 has no highmem for bio segment virtual mapping. Cleanup must preserve ordering across disk deletion, proc removal, cache flush, unmap, context free, memory free, and HV close.

## Test Signals
Signals include successful probe with allocated GPU memory, `/proc/ps3vram` hit/miss changes under read/write workloads, block read/write integrity tests, cache flush on module unload or shutdown, timeout logging from notifier/FIFO waits, and non-PS3 module load returning `-ENODEV`. Hardware-in-the-loop tests are required for DMA correctness.
