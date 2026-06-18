# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/foreground.h

Public and inline support for the foreground allocator.

Defines:
- `struct dev_alloc_list`, a compact sorted list of candidate device IDs.
- `alloc_trace_entry`, used to diagnose allocation attempts and wake-counter snapshots.
- `struct alloc_request`, the central allocator request state containing replicas, EC options, target, flags, write point, candidate devices, counters, scratch buffers, and trace storage.
- Open bucket helper APIs and iteration macros.
- Write point specifier helpers for hash-based or pointer-based write points.

Important inline behavior:
- `alloc_trace_add()` records allocation attempt metadata and preserves the wake counter sampled before waitlist parking.
- `bch2_open_buckets_reserved()` reserves open-bucket handles by watermark; higher-priority watermarks reserve fewer handles.
- `bch2_open_bucket_put()` drops atomic pins and releases buckets via `__bch2_open_bucket_put()` at zero.
- `bch2_alloc_sectors_done_inlined()` closes/puts open buckets with less than one block remaining, emits sector allocation trace, and unlocks the write point.
- `bch2_bucket_is_open()` checks the open-bucket hash table.
- `bch2_bucket_is_open_safe()` rechecks under freelist lock.
- `bch2_bucket_set_discard_fast()` marks an open bucket for fast discard when it closes.
- `alloc_request_get()` allocates and initializes request state from a btree transaction.
- `bch2_ob_ptr()` constructs an extent pointer for the current offset inside an open bucket.
- `bch2_alloc_sectors_append_ptrs_inlined()` appends device pointers to a bkey and decrements free sectors from write point/open buckets.

Exports:
- Bucket allocation APIs.
- Device stripe ordering APIs.
- Alloc wait/wake helpers.
- Debug text helpers.
- Allocator initialization and open bucket shutdown.

Role:
- This header carries many allocator hot-path inlines used by data write code, journal resizing, btree allocation, and copygc/EC paths.
