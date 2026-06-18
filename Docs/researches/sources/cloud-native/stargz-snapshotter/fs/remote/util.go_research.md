# sources/cloud-native/stargz-snapshotter/fs/remote/util.go

## Purpose
Defines range primitives used by remote blob and resolver code. Regions model inclusive HTTP byte ranges, and `regionSet` maintains sorted, minimally merged coverage.

## Important APIs, Types, And Functions
`region` stores beginning `b` and inclusive end `e`; `size` returns `e-b+1`. `superRegion` spans a non-empty slice of regions. `regionSet.add` inserts and merges overlapping or adjacent ranges, and `totalSize` sums merged region sizes.

## Control Flow
`regionSet.add` scans from the tail of the sorted slice. It returns early if an existing range contains the new one, expands the new range while removing overlapped entries, inserts once no further overlap is possible, or prepends if the new region belongs before all existing entries.

## State And Persistence
State is the in-memory sorted `[]region`; there is no persistence. The add operation mutates the slice in place and is documented as O(n).

## Dependencies And Integration
Used by `blob.go` to track fetched coverage and by `resolver.go` to collapse requested ranges before HTTP or custom fetches. Its inclusive-end semantics match HTTP `Range` and `Content-Range` headers.

## Risks And Test Signals
Risks are off-by-one errors around adjacency and inclusive ends, which would cause overfetch, underfetch, or incorrect `FetchedSize`. `util_test.go` covers containment, overlap, adjacency, ordering, and multi-region merging.
