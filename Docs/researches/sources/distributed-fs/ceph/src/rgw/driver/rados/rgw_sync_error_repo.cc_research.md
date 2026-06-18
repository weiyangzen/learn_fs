# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.cc

## Purpose
This file implements a RADOS omap-backed repository for bucket shard sync error timestamps. It provides binary key encoding/decoding, timestamp value decoding, compare-and-set writes, compare-and-remove deletes, and coroutine wrappers for asynchronous RADOS operations.

## Important APIs, Types, and Functions
- `binary_key_prefix` is `0x80`, chosen to distinguish binary keys from legacy string keys.
- Internal `key_type` encodes `rgw_bucket_shard` plus optional generation.
- `encode_key()` serializes prefix and key data into a string.
- `decode_key()` validates prefix, decodes key data, rejects trailing bytes, and returns `-EINVAL` or `-EIO` for invalid encodings.
- `decode_value()` decodes an omap value as a `uint64_t` duration from epoch into `ceph::real_time`, treating decode errors as zero.
- `write()` uses `cls::cmpomap::cmp_set_vals()` in U64 greater-than mode so newer timestamps overwrite older or missing values.
- `remove()` uses `cmp_rm_keys()` in U64 greater-than-or-equal mode so removal only succeeds when the caller's timestamp is at least as new as the stored one.
- `RGWErrorRepoWriteCR` and `RGWErrorRepoRemoveCR` submit these operations asynchronously.

## Control Flow
Synchronous helpers build an object write operation but do not submit it. Coroutine wrappers call the helper, resolve the `rgw_raw_obj` to a RADOS reference, submit `aio_operate()`, and complete with the librados return value. `write_cr()` and `remove_cr()` allocate the corresponding coroutine.

## State and Persistence Behavior
The repository stores one omap key per encoded bucket shard/generation and stores the timestamp as a U64 buffer. Compare operations make updates monotonic by timestamp: older writers cannot overwrite newer errors, and stale removers cannot erase newer reports.

## Dependencies and Integration Points
It depends on buffer encoding, `rgw_bucket_shard`, `rgw_raw_obj`, SAL RADOS reference lookup, coroutine infrastructure, librados object operations, and `cls/cmpomap/client.h`. Consumers can compose the synchronous helpers with other object operations or use coroutine wrappers.

## Risks
- `decode_value()` converts decode errors to zero, which can hide corrupt omap values.
- Key compatibility depends on the binary prefix remaining distinct from old string keys.
- Timestamp comparisons use raw `time_since_epoch().count()`, so all writers must use the same representation.

## Test Signals
Tests should cover encode/decode round trips, invalid prefix, truncated and trailing-byte decode failures, monotonic write behavior, stale remove rejection, newer remove success, and coroutine operation against a test RADOS object.
