# sources/distributed-fs/lizardfs/src/common/goal.cc

Purpose: implements goal slice type metadata, slice merging, validity, expected-copy counting, and string rendering.

Important APIs/types/functions: static slice type parts/names, `Goal::Slice::getExpectedCopies`, `Slice::mergeIn`, `Slice::isValid`, `makeLabelsUnion`, `labelsDistance`, `Goal::mergeIn`, `Goal::getExpectedCopies`, and `to_string` overloads.

Control flow: `Slice::mergeIn` builds a cost matrix comparing every local part to every incoming part, uses `linear_assignment::auctionOptimization` to assign compatible parts, then unions assigned label maps. `makeLabelsUnion` merges sorted label counts, special-casing wildcard labels so total copy requirements are preserved with minimal explicit labels. `Goal::mergeIn` inserts missing slices or merges matching slice types.

State and persistence: mutates in-memory `Goal` and `Slice` flat storage. String functions expose config-like rendering; serialization is not in this file.

Dependencies and integration: depends on `goal.h`, `linear_assignment_optimizer.h`, `exceptions.h`, and media labels. It is central to chunk placement policy and goal parsing/rendering.

Risks: correctness depends on sorted `flat_map` label ordering and wildcard being ordered last as assumed by `makeLabelsUnion`. Merging uses assertions for slice compatibility. Cost formula uses `10 * kMaxExpectedCopies`; changes to max copy limits can affect assignment scoring.

Test signals: `goal_unittest.cc` covers basic operations, standard/xor merges, repeated merges, and goal merge across slice types.
