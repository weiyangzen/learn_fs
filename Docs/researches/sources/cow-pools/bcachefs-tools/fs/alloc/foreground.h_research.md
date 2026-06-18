# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/foreground.h

Public and inline support for the foreground allocator.

Defines:
- `struct dev_alloc_list`, a compact sorted list of candidate device IDs.
- `alloc_trace_entry`, used to diagnose allocation attempts and wake-counter snapshots.
- `struct alloc_request`, the central allocator request object containing requested replicas, EC options, target, write flags, write point, candidate masks, device list, counters, scratch fields, and preallocated trace storage.
- Open bucket helper APIs, iteration macros, hash lookup helpers, and pin/put logic.
- Sector allocation append/done inline helpers.
- Write point specifier helpers for hash-based and pointer-based write points.

Important inline behavior:
- `alloc_trace_add()` records allocation attempt state, including retry flags, device, error, wake-counter snapshot, free buckets, and copygc progress.
- `bch2_open_buckets_reserved()` reserves different amounts of open-bucket capacity by watermark.
- `bch2_bucket_is_open_safe()` checks open-bucket state with a lock-protected recheck.
- `bch2_bucket_set_discard_fast()` marks an open bucket for fast discard when it is later closed.
- `alloc_request_get()` initializes allocator request state and disables EC when too few EC replicas are requested.
- `bch2_alloc_sectors_append_ptrs_inlined()` appends extent pointers from open buckets and advances per-bucket free-sector counters.
- `bch2_alloc_sectors_done_inlined()` drops empty open buckets and emits sector allocation tracing.
- `bch2_wait_on_allocator()` only enters the full wait loop when the closure still has outstanding waits.

Exports:
- Device allocation ordering and stripe increment helpers.
- Bucket/open-bucket allocation APIs.
- Sector allocation start/done APIs.
- Open bucket shutdown and diagnostic text APIs.
- Allocator stuck wait helper.
