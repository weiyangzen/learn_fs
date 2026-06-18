# File Research: sources/block-storage/kvdo/vdo/sparse-cache.h

This header declares the opaque `struct sparse_cache` API for caching complete sparse chapter indexes. It documents that searches are unsynchronized and cache updates require coordinated participation from all index-zone threads through barrier messages.

Public functions:
- `make_sparse_cache()` / `free_sparse_cache()` allocate and destroy the cache.
- `get_sparse_cache_memory_size()` reports chapter-index page memory.
- `sparse_cache_contains()` is the zone-thread membership query.
- `update_sparse_cache()` must be called by all zones with the same virtual chapter for safe mutation.
- `invalidate_sparse_cache()` marks cached entries invalid while preserving membership semantics expected by callers.
- `search_sparse_cache()` searches cached sparse indexes for a chunk name and returns matching virtual chapter and record page.

The API intentionally avoids exposing cache internals so callers follow the barrier discipline described in the header.
