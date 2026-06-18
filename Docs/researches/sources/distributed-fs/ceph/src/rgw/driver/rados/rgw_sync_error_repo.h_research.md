# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.h

## Purpose
This header declares the public API for the sync error repository. The repository stores timestamped error state for bucket shards in RADOS omap and exposes both object-operation helpers and coroutine helpers.

## Important APIs, Types, and Functions
- `encode_key()` returns a binary string key for a bucket shard and optional generation.
- `decode_key()` reverses the key encoding and reports invalid binary format errors.
- `decode_value()` converts a stored buffer into `ceph::real_time`.
- `write(ObjectWriteOperation&, key, timestamp)` adds a conditional set to a write operation.
- `write_cr()` allocates a coroutine to submit a conditional write to a raw RADOS object.
- `remove(ObjectWriteOperation&, key, timestamp)` adds a conditional remove.
- `remove_cr()` allocates a coroutine to submit a conditional remove.

## Control Flow
Callers either build a larger librados write operation using `write()`/`remove()` or ask for a standalone coroutine with `write_cr()`/`remove_cr()`. The compare semantics are implemented in the `.cc` file using cls cmpomap.

## State and Persistence Behavior
The header defines timestamp semantics: writes record a key only if the provided timestamp is newer, and removes erase only if no newer timestamp has appeared. The optional generation in the key lets state distinguish different incarnations of the same bucket shard.

## Dependencies and Integration Points
It depends on librados forward declarations, Ceph buffers/time, coroutine declarations, and RGW raw object/bucket shard types. It is suitable for sync code that needs durable, race-aware error bookkeeping.

## Risks
- Callers must use the same key encoding for write and remove.
- Conditional semantics depend on cls cmpomap availability.
- The API does not list/read repository entries; callers need separate omap listing code.

## Test Signals
Unit tests should cover write/remove operation composition and integration tests should race write/remove timestamps.
