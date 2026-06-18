# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftInputStream.java

## Purpose
`SwiftInputStream` reads Swift objects through ranged JOSS downloads and Alluxio's multi-range stream abstraction.

## Important APIs, Types, And Functions
It extends `MultiRangeObjectInputStream`. Constructors accept JOSS `Account`, container name, object path, optional initial position, retry policy, and multi-range chunk size. `createStream(long startPos, long endPos)` creates ranged download instructions and returns the object input stream.

## Control Flow
For each requested range, the stream copies the retry policy, gets the container/object, sets a `MidPartLongRange(startPos, endPos - 1)`, and downloads an input stream. `NotFoundException` is retried and logged; after retries, the last exception is thrown.

## State And Persistence
State includes JOSS account, container, object path, inherited cursor, retry policy, and chunk size. Data is fetched from Swift on demand and not buffered persistently by this class.

## Dependencies And Integration Points
It depends on JOSS account/container/object APIs, `DownloadInstructions`, `MidPartLongRange`, and Alluxio retry/multi-range stream support. Swift UFS open paths construct it.

## Risks
Only `NotFoundException` is retried; other transient network errors are not. Throwing `lastException` can produce null if retry policy never attempts. Range boundary correctness depends on `MidPartLongRange`.

## Test Signals
No direct test is included here. Comparable OBS/OSS input-stream tests provide pattern-level signals, but Swift-specific JOSS behavior lacks coverage in this subset.
