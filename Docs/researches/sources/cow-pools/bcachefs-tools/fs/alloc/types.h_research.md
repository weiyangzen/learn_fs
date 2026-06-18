# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/types.h

Allocator runtime type header.

Defines:
- Watermark names and `enum bch_watermark`.
- Open-bucket constants:
  - `OPEN_BUCKETS_COUNT = 4096`
  - `WRITE_POINT_HASH_NR = 32`
  - `WRITE_POINT_MAX = 32`
- `open_bucket_idx_t`, with zero reserved as invalid/null.
- `struct open_bucket`, tracking an active bucket’s pin count, freelist/hash links, EC stripe association, data type, flags, device, generation, remaining sectors, bucket number, and EC stripe pointer.
- `struct open_buckets`, a compact list of open-bucket indexes.
- `struct dev_stripe_state`, the weighted fair per-device virtual-time state used for allocation ordering.
- Write point state enum and `struct write_point`.
- `struct write_point_specifier`.
- Capacity accounting structs:
  - `bch_fs_capacity_pcpu`
  - `bch_fs_capacity`
- `struct bch_fs_allocator`, containing RW device masks, free/open-bucket waitlists, open bucket arrays/hash/partial lists, write points, and special btree/reconcile write points.
- `discard_in_flight`, `discard_release`, `discard_state`, and `struct bch_fs_discards`.

Important semantics:
- `open_bucket` entries pin buckets until index updates make newly written data reachable.
- `dev_stripe_state` uses per-device virtual clocks incremented by inverse free space, biasing allocation toward devices with more free buckets.
- `write_point` is cache-line split between allocation state and index-update/work state.
- `bch_fs_capacity.capacity_gen` invalidates outstanding reservations when capacity decreases.
- `bch_fs_discards.refs[]` limits in-flight discards per device and coordinates discard completion waiters.

Role:
- Central shared allocator state used by foreground allocation, discard, cached invalidation, capacity accounting, write path, and shutdown/device-removal logic.
