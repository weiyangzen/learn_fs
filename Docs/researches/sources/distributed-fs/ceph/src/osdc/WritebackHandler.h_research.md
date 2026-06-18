# sources/distributed-fs/ceph/src/osdc/WritebackHandler.h

## Purpose

`WritebackHandler.h` declares the abstract writeback interface consumed by `ObjectCacher`. It separates cache management from the concrete backend that reads, writes, performs copy-on-write checks, and optionally supports scattered writes.

## Important APIs, types, and functions

`WritebackHandler` is an abstract base class with virtual `read()`, `may_copy_on_write()`, and object write methods. `read()` takes object id, object number, locator, offset/length, snap id, output buffer, truncate metadata, op flags, trace, and completion context. The primary `write()` takes object id, locator, extent, `SnapContext`, buffer, mtime, truncate metadata, journal tid, trace, and commit context. `overwrite_extent()` is an optional hook for remapping a journal tid after overwrite. `can_scattered_write()` defaults false, and the vector write overload defaults to returning 0 without doing work.

## Control flow

`ObjectCacher` calls this interface when dirty or missing cached object ranges need backend IO. Implementations such as `client/ObjecterWriteback.h` bridge these calls to `Objecter` operations. The scattered-write overload is available only when an implementation advertises support through `can_scattered_write()`.

## State and persistence behavior

The interface stores no state. Backend implementations determine durability by submitting writes to RADOS/Objecter and completing the supplied contexts. `journal_tid` and `overwrite_extent()` tie cache writeback to higher-level journaling/order tracking.

## Dependencies and integration points

The header depends on `Context`, Ceph core types, Zipkin tracing, and OSD object types. It is included by `ObjectCacher.cc` and implemented by client-side objecter writeback code. It connects cache, CephFS client, tracing, snap context, and RADOS object IO.

## Risks and edge cases

Because completions are raw `Context*`, implementations must define ownership and always complete or safely cancel callbacks. The default scattered write overload returns success-looking `0` without committing anything; callers must honor `can_scattered_write()` before using it. `may_copy_on_write()` correctness matters for snapshot isolation and cache coherency.

## Test signals

Tests should exercise `ObjectCacher` with a concrete `WritebackHandler`: read miss fill, dirty writeback, truncation metadata, snapshot copy-on-write decisions, journal tid overwrite tracking, and both unsupported and supported scattered-write paths.
