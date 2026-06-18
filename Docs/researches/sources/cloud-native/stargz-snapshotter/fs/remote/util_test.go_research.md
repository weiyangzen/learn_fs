# sources/cloud-native/stargz-snapshotter/fs/remote/util_test.go

## Purpose
Validates `regionSet.add` merging behavior for inclusive HTTP byte ranges.

## Important APIs, Types, And Functions
`TestRegionSet` feeds ordered and unordered region sequences into `regionSet.add` and compares the final `rs` slice with expected merged ranges using `reflect.DeepEqual`.

## Control Flow
Each case constructs an empty `regionSet`, inserts all input regions, then asserts merged output. Cases cover partial overlap, total containment, duplicate ranges, end-start adjacency, bridging gaps with a later region, and multiple disjoint outputs.

## State And Persistence
All state is local to each table entry. No persistence or external IO.

## Dependencies And Integration
Depends only on `testing` and `reflect`. The test is small but important because both remote request collapsing and fetched byte accounting depend on this primitive.

## Risks And Test Signals
Passing tests signal correct inclusive-end adjacency behavior such as `{1,3}` plus `{4,6}` merging into `{1,6}`. Gaps remain around empty inputs to `superRegion`, negative ranges, and concurrency, which are handled by caller assumptions rather than this test.
