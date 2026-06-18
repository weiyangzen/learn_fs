# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/MidPartLongRange.java

## Purpose
`MidPartLongRange` is a Swift/JOSS range helper for requesting a byte range from the middle of an object.

## Important APIs, Types, And Functions
It extends JOSS `MidPartRange` semantics for long offsets. The constructor stores start and end positions, and range formatting is used by `DownloadInstructions.setRange`.

## Control Flow
There is no complex control flow. It represents an inclusive byte range suitable for HTTP range downloads.

## State And Persistence
State is the requested start and end offsets. No data is persisted.

## Dependencies And Integration Points
`SwiftInputStream.createStream` constructs it with `startPos` and `endPos - 1` so JOSS downloads a bounded chunk for `MultiRangeObjectInputStream`.

## Risks
Inclusive/exclusive boundary mistakes can cause off-by-one reads. Long-range support must match JOSS and Swift HTTP range expectations.

## Test Signals
No direct test is present in this subset; `SwiftInputStream` behavior depends on it indirectly.
