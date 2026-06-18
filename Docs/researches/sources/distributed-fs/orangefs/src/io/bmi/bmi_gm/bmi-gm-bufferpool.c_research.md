<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.c

Purpose: Provides a small DMA buffer free-list used by the GM transport for control messages and optional rendezvous I/O bounce buffers.

Important APIs, types, and functions: `bmi_gm_bufferpool_init()` allocates a `struct bufferpool`, then preallocates `num_buffers` DMA buffers of `buffer_size` with `gm_dma_malloc` and links them as `cache_entry` nodes. `bmi_gm_bufferpool_finalize()` drains and frees all cached buffers. `bmi_gm_bufferpool_get()` pops one buffer or returns `NULL`. `bmi_gm_bufferpool_put()` pushes a buffer back. `bmi_gm_bufferpool_empty()` reports whether the free list is empty.

Control flow and state: The pool owns a quicklist of free DMA buffers. Recently returned buffers are reused first via `qlist_add`. On init failure, the function finalizes partially allocated state.

Dependencies and integration points: Uses GM DMA allocation APIs, `quicklist`, `gossip`, and `bmi-gm-bufferpool.h`. Called by `BMI_gm_initialize()` for `ctrl_send_pool` and, when enabled, `io_pool`.

Risks and test signals: No internal locking; callers must hold GM synchronization. `finalize()` assumes `bp` is non-null. Buffer size must be large enough to hold a `cache_entry`, so tiny buffers fail. Tests should simulate pool exhaustion, partial allocation failure, and put/get reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.c -->
