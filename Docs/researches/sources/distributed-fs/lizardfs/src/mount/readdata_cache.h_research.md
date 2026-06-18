## sources/distributed-fs/lizardfs/src/mount/readdata_cache.h

Purpose: header-only per-read-handle cache storing contiguous read buffers by file offset and returning acquired cache entries to callers.

Important APIs/types: `ReadCache::Entry` stores offset, buffer, timer, atomic refcount, and intrusive hooks. `ReadCache::Result` owns acquired entry pointers, releases them on destruction, can expose an input buffer for missing data, serialize data to an iovec, or copy to a flat buffer. `ReadCache::query(offset, size)` returns cached spans and inserts an empty tail entry for missing bytes.

Control flow: `query` garbage-collects a few expired/LRU and reserved entries, seeks to the entry before the requested offset, accumulates nonexpired overlapping entries, erases expired/empty ones, and inserts a new empty entry if bytes remain. Insert clears colliding entries up to the new end offset. Erased entries with outstanding refs move to a reserved list until released.

State and dependencies: uses boost intrusive set/list, `Timer`, `small_vector`, and raw heap allocation. The cache itself has no mutex; it is intended to be owned by a single read record/handle.

Risks: callers must fill `Result::inputBuffer()` only when the last entry is empty and acquired. `Result` is move-only by convention but copy is not explicitly deleted. Expiration and collision rules can discard overlapping cache entries aggressively. Refcount is atomic, but container mutations are not thread-safe.

Test signals: no direct tests in this subset. Important tests are partial hit plus tail fill, collision eviction while a result is alive, expired entry cleanup, EOF empty buffer behavior, and iovec/copy slicing.
