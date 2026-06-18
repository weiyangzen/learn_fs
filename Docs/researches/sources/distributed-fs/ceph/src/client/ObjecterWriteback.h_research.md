# sources/distributed-fs/ceph/src/client/ObjecterWriteback.h

## Purpose
`ObjecterWriteback.h` adapts `Objecter` operations to the `WritebackHandler` interface used by `ObjectCacher`.

## Important APIs, Types, and Functions
`ObjecterWriteback` implements `read()`, `may_copy_on_write()`, single-buffer `write()`, scattered `write()`, and `can_scattered_write()`. Reads call `Objecter::read_trunc()`. Writes call `Objecter::write_trunc()` or build an `ObjectOperation` with multiple writes and call `Objecter::mutate()`. Completion contexts are wrapped in `C_Lock` and `C_OnFinisher`.

## Control Flow
The object cache invokes this handler on cache miss, flush, or scattered writeback. The handler submits objecter operations and arranges for callbacks to run through the supplied finisher while holding the supplied lock.

## State and Persistence Behavior
The class itself holds only pointers to `Objecter`, `Finisher`, and lock. Persistent effects are OSD object reads/writes submitted through the objecter with snap context, truncate information, and mtime.

## Dependencies and Integration Points
It depends on `osdc/Objecter.h` and `osdc/WritebackHandler.h`. `Client` constructs it for its `ObjectCacher`/writeback path.

## Risks and Edge Cases
`may_copy_on_write()` always returns false, so cache behavior must not rely on handler-side COW. Callback lock ordering must match client/object cache expectations. Scattered writes assume OSD/objecter support and return true from `can_scattered_write()`.

## Test Signals
Object cache read/writeback paths, callback lock/finisher ordering, scattered write correctness, truncate sequence/size propagation, snap context propagation, and OSD error delivery to client writeback completion.
