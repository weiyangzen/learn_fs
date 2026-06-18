# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_log_backing.h

## Purpose
Declares the abstraction layer that lets RGW log users operate over omap-backed or FIFO-backed logs and transition between multiple log generations. It also provides cursor encoding helpers and a lazily initialized FIFO wrapper for producers/consumers.

## Important APIs And Types
`log_type` is a serializable enum with `omap` and `fifo`, plus `to_log_type()` and stream formatting. `logback_generation` encodes `gen_id`, `type`, and optional `pruned` timestamp. `logback_generations` is an abstract base class that owns neorados handles, metadata object id, generation-to-shard oid callback, shard count, watch cookie, version, strand, and current entries. Derived classes implement `handle_init()`, `handle_new_gens()`, and `handle_empty_to()`.

Public coroutine methods are `init<T>()`, `update()`, `new_backing()`, `empty_to()`, `remove_empty()`, and `shutdown()`. Free functions `log_backing_type()` and `log_remove()` operate over all shards. `gencursor()` and `cursorgen()` encode/decode cursors as `G<20-digit-gen>@<cursor>`. `LazyFIFO` wraps `neorados::cls::fifo::FIFO` with synchronous-yield and coroutine methods for `push`, `list`, `trim`, and `last_entry_info`.

## Control Flow And State
`logback_generations::init()` constructs a derived instance and calls `setup()`, after which callbacks receive the active generation set. The class hides metadata reads/writes and watch handling behind protected/private methods. `LazyFIFO` protects the optional FIFO pointer with a mutex and allows races to create the FIFO because FIFO creation is designed to be multi-client safe; the first completed initializer wins.

## Dependencies And Integration
The header depends on Boost.Asio coroutines/strands, `boost::container::flat_map`, function2 unique functions, neorados RADOS/FIFO APIs, cls version types, Ceph encoding, and config parsing helpers. It is intended for RGW log subsystems such as metadata/data/bilog implementations that need to select backing stores and consume generation updates.

## Risks And Test Signals
The main API risk is derived classes failing to call `shutdown()` before destruction or overriding `shutdown()` without calling the base at the end. Cursor parsing intentionally falls back to generation zero when malformed, which preserves backward compatibility but can hide invalid cursor input. `LazyFIFO` initialization can duplicate creation work under concurrency, though only one pointer is retained. Unit tests should cover encoding compatibility, cursor edge cases, derived callback sequencing, and FIFO lazy initialization under parallel push/list calls.
