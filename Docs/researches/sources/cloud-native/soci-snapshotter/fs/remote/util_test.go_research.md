# sources/cloud-native/soci-snapshotter/fs/remote/util_test.go

Purpose: tests `regionSet.add` merge behavior for overlapping, contained, duplicate, adjacent, and disjoint byte ranges.

Important APIs and flow: `TestRegionSet` iterates table cases, adds each input region to a fresh set, and compares the resulting sorted merged slice with `reflect.DeepEqual`. Cases explicitly note that `region.e` is inclusive, so `{1,3}` and `{4,6}` merge into `{1,6}`.

State and persistence: pure in-memory table test.

Dependencies and integration: protects range coalescing used by remote HTTP fetch requests and fetched-size accounting.

Risks and test signals: good branch coverage for merge semantics. It does not test `totalSize`, `superRegion`, negative bounds, or concurrent access, which are handled by callers or assumed invalid.
