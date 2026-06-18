<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.cpp

Purpose: Manages OCF cache/core lifecycle and submits aligned read IO through OCF.

APIs and control flow: `start` creates OCF context, registers volume type, sets write-through cache mode and cache-line size, starts cache, creates management and IO queues, initializes queues, loads or attaches media, and reloads or adds the core. `stop` disables logging, stops cache asynchronously, releases queues, cleans volumes, and releases context. `prepare_aligned_iov` and `copy_aligned_iov` adapt unaligned caller buffers to 512-byte sector-aligned IO. `ocf_pread` builds `ease_ocf_io_data`, creates an OCF read IO against the core, sets data/completion, submits, waits on a semaphore, handles errors, and copies padding-adjusted data back.

State and persistence: OCF metadata lives on media file via volume implementation; provider owns context, cache, core, queues, and volume params pointer.

Dependencies and integration: Used by OCF cached filesystem factory selected by `ImageService` for `cacheType=ocf`.

Risks and test signals: Error exits in `start` can leak partially created OCF objects. Tests should cover fresh attach, reload existing media, unaligned reads, prefetch flag path, and stop after failed start.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.cpp -->
