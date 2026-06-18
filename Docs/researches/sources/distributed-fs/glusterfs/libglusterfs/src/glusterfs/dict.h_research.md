# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/dict.h

## Purpose
Defines GlusterFS dictionaries, the dynamic key/value container used for xdata, options, RPC metadata, xattrs, and cross-translator annotations.

## APIs, Types, and Functions
Core types are `data_t`, `data_pair_t`, and `dict_t`. `data_t` stores a byte pointer, atomic refcount, typed `gf_dict_data_type_t`, length, and static/dynamic ownership flag. `dict_t` tracks count, total serialized key/value length, refcount, lock, linked members, and extra allocation. APIs cover creation/ref/unref/reset, `dict_setn()`/`dict_addn()`/`dict_get()`/`dict_deln()`, serialization/unserialization, copying, foreach and match traversal, typed conversions for signed/unsigned integers, doubles, strings, dynamic/static pointers, binary data, UUIDs, `iatt`, and mdata. `GF_PROTOCOL_DICT_SERIALIZE` and `GF_PROTOCOL_DICT_UNSERIALIZE` wrap RPC conversion with logging and errno assignment.

## Control Flow, State, and Persistence
Dictionaries are mutable refcounted in-memory state. Members are a linked list protected by `gf_lock_t`; serialized form is used across RPC and persisted metadata paths. Static data wrappers do not own payload memory, while dynamic wrappers transfer/free ownership.

## Dependencies and Integration
Depends on `common-utils.h`, atomics, pthread locking, `glusterfs-fops.h` data type enums, `iatt`, UUIDs, logging, and message IDs. Nearly every translator uses `dict_t` for xdata and configuration.

## Risks and Test Signals
Risks include static/dynamic ownership confusion, serialization size limits (`DICT_KEY_VALUE_MAX_SIZE`), unchecked typed getter failures, refcount leaks, and lockless inline iteration misuse. Test signals include serialize/unserialize round trips, typed getter/setter tests, refcount/leak tests, fuzzing malformed dict buffers, xdata propagation tests, and concurrency checks around set/delete/foreach.
