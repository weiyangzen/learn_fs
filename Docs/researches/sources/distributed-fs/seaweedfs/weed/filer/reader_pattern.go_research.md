# sources/distributed-fs/seaweedfs/weed/filer/reader_pattern.go

## Purpose

`reader_pattern.go` classifies reads as sequential or random so higher-level reader code can decide whether to cache whole chunks or fetch requested ranges. It was read as a complete 41-line file.

## Important APIs, Types, and Functions

`ReaderPattern` stores `isSequentialCounter` and `lastReadStopOffset` atomically. `NewReaderPattern` initializes the tracker. `MonitorReadAt(offset, size)` compares the new read offset with the previous stop offset. `IsRandomMode` returns true when the counter is negative. `ModeChangeLimit` caps drift at 3.

## Control Flow

Sequential adjacent reads increment the counter until the positive cap; non-adjacent reads decrement it until the negative cap. `IsRandomMode` then uses only the sign.

## State and Persistence Behavior

All state is transient per reader and atomic for concurrent read monitoring. Nothing is stored on disk or in the filer store.

## Dependencies and Integration Points

It depends only on `sync/atomic` and feeds reader cache/stream decisions documented by comments: streaming reads cache first chunks, random reads fetch only ranges.

## Risks and Edge Cases

The heuristic is intentionally simple, so interleaved concurrent reads can swing the counter and short bursts of random access may flip mode. The cap prevents overflow but not misclassification.

## Test Signals

No direct test is listed in this subset. Useful tests would exercise adjacent reads, gaps, backwards reads, and concurrent calls around the `ModeChangeLimit` boundary.
