# sources/cloud-native/soci-snapshotter/fs/remote/util.go

Purpose: provides range-region utilities for HTTP byte range operations and fetched-size accounting.

Important APIs and flow: `region` stores inclusive byte bounds and `size` returns `e-b+1`. `superRegion` returns the smallest region covering a non-empty list. `regionSet` stores sorted non-overlapping regions. `add` inserts a region while merging overlapping or adjacent regions and ignoring regions already contained by an existing entry. `totalSize` sums merged region sizes.

State and persistence: `regionSet` is an in-memory slice that callers must protect if shared concurrently. The blob implementation wraps it with a mutex.

Dependencies and integration: used by `httpFetcher.fetch` to coalesce requested ranges, `remoteFetcher.fetch` to map custom fetchers to a single super-region, and `blob.FetchedSize` to report fetched coverage.

Risks and test signals: `superRegion` assumes at least one region. The insertion algorithm is O(n) and uses slice splicing/allocations, which is acceptable for small region lists but could cost more with many ranges. Tests cover overlapping, containing, duplicate, adjacent, and disjoint merge cases.
