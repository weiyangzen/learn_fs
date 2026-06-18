# sources/distributed-fs/seaweedfs/weed/filer/interval_list.go

## Purpose

`interval_list.go` implements a generic, locked interval list used to model visible byte ranges and overwritten write regions. It keeps ordered half-open intervals with timestamps and value payloads that can be cloned and retargeted when intervals split.

## Important APIs, Types, and Functions

`IntervalValue` requires `SetStartStop` and `Clone`. `Interval[T]` stores `StartOffset`, `StopOffset`, `TsNs`, `Value`, and linked-list pointers. `IntervalList[T]` has sentinel head/tail nodes and an `RWMutex`. Public methods include `NewIntervalList`, `Front`, `AppendInterval`, `Overlay`, `InsertInterval`, and `Len`; private methods implement ordered insertion, splitting, and overwrite behavior.

## Control Flow

`Overlay` inserts a new interval by replacing all overlapping visible ranges regardless of timestamp. It finds the first interval ending after the new start and the last interval starting before the new stop, preserves left/right fragments around the overlay, and splices the new interval between them. `InsertInterval` is timestamp-aware: newer intervals split or replace older overlaps, while older intervals are inserted only into gaps not covered by newer ranges.

`insertInterval` iterates through the ordered list while the candidate still has uncovered range. It clones values for left/right fragments, calls `SetStartStop` when fragment boundaries change, and uses `insertBetween` to preserve list links.

## State and Persistence Behavior

The structure is in-memory only. It persists no data beyond the process and is protected by the list mutex for modifications and length calculation. `Front` returns an internal pointer without locking, so callers must coordinate if concurrent mutation is possible.

## Dependencies and Integration Points

The file depends only on `math` and `sync`. It integrates with SeaweedFS filer chunk visibility/read paths, where intervals represent file chunk views and overwrite generations.

## Risks and Edge Cases

Pointer/link correctness is critical because sentinels are partly linked lazily. `Overlay` reuses existing `Value` pointers for preserved fragments, while `InsertInterval` clones values for fragments, so value mutability semantics differ. Zero-length overlays are ignored, but zero/negative `InsertInterval` input is not explicitly rejected. `Len` counts from head and subtracts one, so broken links could hide corruption.

## Test Signals

Tests should exercise overlapping left/right splits, complete replacement, timestamp ordering, adjacent intervals, zero-length input, struct payload clone behavior, and concurrent access patterns where callers hold the appropriate lock.
