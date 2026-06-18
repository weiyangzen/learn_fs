# `sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.c`

## Purpose

`dm-exception-store.c` provides the registry and common constructor/destructor logic for snapshot exception-store implementations. Exception stores manage how snapshot copy-on-write metadata records old-to-new chunk mappings and merge progress.

## Important APIs, Types, and Functions

The file maintains `_exception_store_types`, protected by `_lock`. `dm_exception_store_type_register()` and `dm_exception_store_type_unregister()` add and remove implementations. `_get_exception_store_type()` finds a registered type and pins its module. `get_type()` autoloads modules named `dm-exstore-<type_name>`, repeatedly truncating suffixes after `-` to support families such as `clustered-shared`. `put_type()` releases the module reference.

`dm_exception_store_create()` parses snapshot exception-store arguments, chooses persistent (`P`) or transient (`N`) store type, validates chunk size, calls the selected type constructor, and returns a `struct dm_exception_store`. `dm_exception_store_destroy()` calls the type destructor and releases the module. `dm_exception_store_set_chunk_size()` enforces power-of-two chunk sizes that are multiples of both origin and COW logical block sizes.

## Control Flow

Snapshot target construction calls `dm_exception_store_create()`. The first argument selects persistent or transient mode using its first character; any suffix after that character is passed as type-specific options. The second argument is chunk size. Once the type is found and pinned, the common store object records the snapshot pointer and chunk geometry, then delegates to the type constructor. Initialization registers both built-in transient and persistent snapshot store types; exit unregisters them in reverse order.

## State and Persistence Behavior

This file itself persists no metadata. Persistence is delegated to the selected store type, typically persistent snapshot metadata on the COW device or transient in-memory metadata. Common state is the registered type list, module references, chunk size/mask/shift, and the type-specific `context` pointer.

## Dependencies and Integration Points

It integrates with `dm-snap` through `dm_snap_origin()`, `dm_snap_cow()`, and `struct dm_snapshot`, and with store implementations such as the persistent and transient stores. It uses module autoloading, block logical-size queries, exported symbols for external store modules, and device-mapper error reporting via `ti->error`.

## Risks and Edge Cases

Chunk-size validation must match both origin and COW devices or snapshot metadata can become unaligned. Autoload fallback by truncating names can load a broader module than the exact requested type; the subsequent lookup still requires the requested registered type. Registration is protected by a spinlock, but implementation objects must remain valid until unregister. Constructor failure unwinds module references and allocated store state.

## Test Signals

Tests should register duplicate types, unregister missing types, create `P` and `N` stores, reject invalid chunk sizes, verify module autoload naming fallback, and exercise constructor failure unwinding. Snapshot integration tests should confirm chunk geometry matches table status and that store destruction releases module references.
