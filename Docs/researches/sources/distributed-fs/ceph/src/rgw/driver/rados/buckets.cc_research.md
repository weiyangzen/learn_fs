# sources/distributed-fs/ceph/src/rgw/driver/rados/buckets.cc

Purpose: Implements bucket-list and bucket-stat operations for owners backed by the `cls_user` object class. The same helpers can manage bucket lists for users or accounts, depending on the `rgw_raw_obj` passed by the caller.

Important APIs/types/functions: Internal `set()` wraps `cls_user_set_buckets()`. `add()` converts `rgw_bucket` to `cls_user_bucket_entry` and sets creation time. `remove()` calls `cls_user_remove_bucket()`. `list()` pages through `cls_user_bucket_list()`. `write_stats()` updates an existing bucket entry. `read_stats()` and `read_stats_async()` read owner aggregate stats. `reset_stats()` loops over `reset_user_stats2` until not truncated. `complete_flush_stats()` marks stats sync complete.

Control flow: Most operations first resolve `rgw_raw_obj` to `rgw_rados_ref`, build an object-class read/write operation, and call `ref.operate()`. Listing repeatedly requests remaining capacity until the cls call is not truncated or `max` entries are collected, then sets `next_marker` only when more data remains.

State/persistence: State lives in cls_user omap entries and headers on the owner object. `add()` can create/update bucket entries; `write_stats()` passes `add=false`, so the bucket must already exist. Missing owner objects are treated as empty for list and stats reads. Reset recalculates aggregate stats over potentially truncated batches.

Dependencies/integration: Depends on librados, `cls/user/cls_user_client.h`, RGW bucket conversion, SAL `BucketList` and `ReadStatsCB`, `RGWStorageStats`, and `rgw_get_rados_ref()`. Account and user code provide the actual owner object.

Risks: `list()` computes `max - listing.buckets.size()`; callers should avoid passing `max=0` unless cls behavior is known. Async callback ownership depends on `headercb.release()` only after successful registration. `reset_stats()` returns the last cls return value and treats decode failure as `-EINVAL`; tests should ensure truncated loops converge.

Test signals: Add/remove/list pagination, empty owner object behavior, `write_stats()` on missing bucket, aggregate stats read including timestamps, async callback result propagation, reset over multiple truncated batches, and complete-flush timestamp updates.
