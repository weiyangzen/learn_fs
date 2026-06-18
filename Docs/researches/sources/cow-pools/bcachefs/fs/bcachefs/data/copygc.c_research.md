# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/copygc.c

Implements copy garbage collection: selecting fragmented buckets or stripes, evacuating live data, and pacing the background copygc thread.

Key entry points:
- `bch2_copygc()` selects work from fragmentation LRUs and calls `bch2_evacuate_bucket()`.
- `bch2_copygc_wait_amount()` and `bch2_copygc_dev_wait_amount()` compute how long copygc can sleep based on free/fragmented space.
- `bch2_copygc_thread()` runs the kthread loop with freezer support, io-clock waits, wakeups, and shutdown handling.
- `bch2_copygc_start()`, `bch2_copygc_stop()`, and fs init/exit manage thread/workqueue lifecycle.

Important details:
- Tracks buckets in flight with an rhashtable and FIFO list to avoid duplicate evacuation and to bound outstanding work.
- Bucket movability checks device RW/online state, open bucket status, backpointer mismatch bitmap, alloc state, and LRU race conditions.
- EC-aware copygc can prefer stripe fragmentation LRU when stripe fragmentation is significantly worse than normal bucket fragmentation.
- Uses `BCH_WATERMARK_copygc` for relocation writes.
- Emits trace events with sectors seen/moved and bucket counts.

Dependencies and interactions:
- Depends on alloc LRUs, backpointers, move/evacuate infrastructure, EC trigger helpers, io clocks, and write buffer flushing.
