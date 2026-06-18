<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/idset.go -->
# sources/cloud-native/containers-storage/idset.go

## Purpose
`idset.go` implements interval-set operations for UID/GID mapping management and conflict detection.

## Important APIs, Types, And Functions
`idSet` wraps `intervalset.ImmutableSet`. `newIDSet`, `getHostIDs`, `getContainerIDs`, `subtract`, `union`, `iterator`, `size`, `findAvailable`, and `zip` compose and consume ID intervals. `interval` implements `intervalset.Interval` through `Intersect`, `Before`, `IsZero`, `Bisect`, `Adjoin`, and `Encompass`. `hasOverlappingRanges` detects overlapping host or container ID mappings.

## Control Flow
Input ID maps are converted to half-open intervals. Set operations delegate to `github.com/google/go-intervals/intervalset`. Iteration launches a goroutine that streams intervals over a channel until exhausted or canceled. `findAvailable` walks intervals and truncates the final interval to allocate exactly the requested size. `zip` walks host and container sets in parallel to produce contiguous `idtools.IDMap` entries.

## State And Persistence
All state is in-memory and immutable once an `idSet` is constructed. No disk state is written.

## Dependencies And Integration Points
The code integrates with storage ID-map allocation logic, idtools mappings, and public storage errors. It uses `types.ErrNoAvailableIDs` and wraps `ErrInvalidMappings` for conflicts.

## Risks And Edge Cases
The iterator requires callers to call cancel unless it returns nil; the implementation uses `defer cancel` in local methods. Negative or zero-length intervals collapse to empty sets. `hasOverlappingRanges` reports the incoming mapping that conflicts, but it accumulates conflicts after mutating interval sets.

## Test Signals
`idset_test.go` is extensive: it covers construction, host/container extraction, set operators, sizing, allocation, zipping, interval interface behavior, and overlapping mapping detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/idset.go -->
