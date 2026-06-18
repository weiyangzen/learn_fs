# File Research: sources/cow-pools/bcachefs-tools/fs/data/copygc.c

Implements copy-on-write garbage collection: relocating live data out of fragmented buckets/stripes so buckets can be reused.

Key responsibilities:
- Documents copygc behavior, reserve pressure, and fragmentation LRU usage.
- Tracks buckets in flight with an rhashtable, FIFO list, sector counts, and evacuation array.
- Determines whether a bucket is movable by checking device state, open-bucket status, backpointer mismatch state, alloc metadata, generation, and LRU race.
- Selects normal fragmented buckets from `BTREE_ID_lru` / `BCH_LRU_BUCKET_FRAGMENTATION`.
- Selects stripe buckets from stripe-fragmentation LRU when EC stripe fragmentation is more urgent.
- `should_do_ec_copygc()` compares stripe and bucket fragmentation ratios.
- `bch2_copygc()` flushes write buffers, selects candidates, evacuates buckets via `bch2_evacuate_bucket()`, tracks move stats, and frees temporary state.
- Computes per-device and whole-fs wait amounts based on free space and fragmented movable data.
- Provides diagnostic text including wait state and copygc task backtrace.
- Runs a freezable kernel thread that waits on io-clock thresholds, copygc enable state, kicks, and allocator pressure.
- Starts/stops copygc thread and workqueue; initializes waitqueue/running state.

Important interactions:
- Depends on allocation LRUs, backpointers, moving context, EC trigger helpers, allocator watermarks, and io-clock waiting.
- `bch2_copygc_can_make_progress()` uses hysteresis tuned to avoid allocator hangs just below reserve thresholds.
- Copygc wakeups increment `kick_count` in `copygc.h`.

Notable concerns:
- Copygc avoids devices not RW/online and buckets still open for writes.
- EC-aware copygc may evacuate stripe data blocks, not only standalone buckets.
- Near-full filesystems can see write latency increase while copygc frees space.
