# sources/distributed-fs/beegfs/common/source/common/nodes/OpCounter.h

## Purpose
Defines atomic filesystem operation counters and concrete metadata/storage counter classes.

## Important APIs, Types, And Functions
`OpCounter` stores an `AtomicUInt64Vector` with element zero as the total sum. `increaseOpCounter()`, `increaseStorageOpBytes()`, `getOpCounter()`, `getNumCounter()`, and `addCountersToVec()` are the key APIs. `MetaOpCounter` and `StorageOpCounter` size the base by their enum sentinel.

## Control Flow
Incrementing validates the operation index, increments the specific counter, and increments the sum. Storage read/write byte accounting first increments the read/write op counter and then updates the corresponding byte counter.

## State, Persistence, And Dependencies
State is atomic counters only. Dependencies include `Atomics`, `LogContext`, `OpCounterTypes`, and common vector typedefs.

## Integration Points
Used by `NodeOpStats` maps and operation handlers in metadata/storage services.

## Risks
Passing the sum element as an operation is rejected only under debug for that specific case, while out-of-range is always rejected. Directly incrementing READBYTES/WRITEBYTES through `increaseOpCounter()` would skew op counts, so callers should use `increaseStorageOpBytes()`.

## Test Signals
Validate sum increments, invalid operation logging, byte counter coupling, vector export order, and enum-count compatibility.
