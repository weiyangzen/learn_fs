# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members.h

This header is the central inline/API surface for bcachefs superblock member devices. It covers on-disk member record access, live device iteration, refcount acquisition, missing-device handling, member property conversion, btree allocation bitmap helpers, and member-management declarations.

Key responsibilities:
- Provides v1/v2 superblock member accessors:
  - `__bch2_members_v2_get_mut()`
  - `bch2_members_v2_get()`
  - `members_v1_get_mut()`
  - `bch2_members_v1_get()`
- Exposes conversion and formatting APIs:
  - `bch2_member_to_text()`
  - `bch2_member_to_text_short*()`
  - `bch2_devs_mask_to_text_locked()`
- Defines online/member iteration macros:
  - RCU-only: `for_each_member_device_rcu`, `for_each_online_member_rcu`, `for_each_rw_member_rcu`
  - Refcounted: `for_each_member_device`, `for_each_online_member`, `for_each_rw_member`, `for_each_readable_member`
- Wraps device lifetime and I/O references:
  - `bch2_dev_get()`, `bch2_dev_put()`
  - `bch2_dev_get_ioref()`
  - `enumerated_ref_tryget()`/`put()` on per-device read/write I/O refs
- Implements device lookup variants:
  - no-error RCU lookup
  - checked lookup with missing-device accounting
  - refcounted tryget
  - bkey-aware and bucket-aware tryget
- Converts on-disk `struct bch_member` into CPU-side `struct bch_member_cpu` through `bch2_mi_to_cpu()`.
- Provides inline btree allocation bitmap sector tests and declares mutation/GC helpers.

Important invariants:
- Device masks are fixed to `BCH_SB_MEMBERS_MAX`, currently 64.
- `bucket_valid()` checks bucket offset against `first_bucket` and `nbuckets_minus_first`; bucket-based lookups release refs and fail on invalid buckets.
- Debug builds use explicit atomic device refs and underflow panic diagnostics; non-debug builds use `percpu_ref`.
- I/O refs distinguish READ/WRITE and caller-supplied reference categories.
- `bch2_member_alive()` treats zero UUID and `BCH_SB_MEMBER_DELETED_UUID` as non-live.
- Btree bitmap helpers assume a 64-bit bitmap plus `btree_bitmap_shift`; sectors outside representable range are not marked.

Dependencies:
- Uses `util/enumerated_ref.h` for I/O reference accounting.
- Uses `util/darray.h` for fixed small device lists.
- Depends on bcachefs btree key and superblock types.

Research notes:
- This file is heavily inline because device lookup and iteration are hot paths.
- Error-reporting lookup variants are intentionally distinct from no-error paths, allowing callers to avoid noisy accounting during speculative or validation probes.
- `bch2_prt_member_name()` is safe for invalid IDs and handles `BCH_SB_MEMBER_INVALID` specially.
