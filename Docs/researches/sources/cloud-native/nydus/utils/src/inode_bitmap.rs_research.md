# sources/cloud-native/nydus/utils/src/inode_bitmap.rs

Purpose: concurrent bitmap for tracking inode numbers and exporting compact inode ranges.

Important APIs/types/functions: `InodeBitmap` wraps `RwLock<BTreeMap<u64, AtomicU64>>`, where map key is `ino >> 6` and bit mask is `1 << (ino & 0x3f)`. Public methods are `new`, `set`, `is_set`, `clear`, `clear_all`, `bitmap_to_array`, and `bitmap_to_array_and_clear`. `Display`/`Debug` serialize as JSON containing `"inode_range"`.

Control flow: `set` first tries a read lock and atomic OR on an existing bucket; if missing, it drops the read lock, takes a write lock, inserts an `AtomicU64`, and ORs the bit. `clear` atomic-ANDs the inverted mask for existing buckets. `bitmap_to_vec` scans sorted buckets and set bits with `trailing_zeros`, merging adjacent inode values into either singleton `[n]` or range `[start,end]`. `bitmap_to_array_and_clear` uses `fetch_and(0)` as it scans.

State and persistence: in-memory bitmap only. JSON/range output can be persisted by callers.

Dependencies and integration points: depends on serde_json for display and std atomics/locks. Useful for dirty inode tracking or reporting changed inode ranges.

Risks: inode 0 is commented as invalid but can still be set and exported; tests set it indirectly in the 0..100000 loop. Atomic operations are relaxed, which is fine for bitmap counters when protected by map structure locks but gives no ordering for external data. Empty buckets remain after clear, so long-lived instances can retain map entries. `bitmap_to_array_and_clear` may race with concurrent `set`, potentially clearing bits set during scan.

Test signals: tests cover setting, clearing, range merging, clear_all, array-and-clear, display/debug JSON, nonexistent clear/is_set, idempotent set, empty behavior, and range formatting helper.
