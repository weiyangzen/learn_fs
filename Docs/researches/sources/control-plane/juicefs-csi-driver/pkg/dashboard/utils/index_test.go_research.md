# sources/control-plane/juicefs-csi-driver/pkg/dashboard/utils/index_test.go

## Purpose
This test file validates insertion, ordering, duplicate suppression, and stale-entry cleanup for `TimeOrderedIndexes`.

## Important APIs, Types, And Functions
It defines `TestIndexAdd` and `TestIndexAddNoDuplicateWhenStaleEntryRemoved`, using corev1 Pod fixtures and simple metadata/resource getter callbacks.

## Control Flow
`TestIndexAdd` adds newer and older pods, asserts chronological order, then re-adds the same pod twice and verifies length/order are unchanged. `TestIndexAddNoDuplicateWhenStaleEntryRemoved` creates an index with two pods, changes the getter so one existing entry returns nil, re-adds the remaining pod, and asserts the stale entry is removed without duplicating the live pod.

## State And Persistence
State is an in-memory index and local pod fixtures. No external state is used.

## Dependencies And Integration Points
The tests cover the utility used by all cached dashboard services. They depend on Kubernetes metadata types and Go reflection equality.

## Risks
The tests do not cover `Iterate` cancellation, reverse iteration, `RemoveIndex`, or recreated same-name/different-UID behavior. They also do not exercise concurrent access.

## Test Signals
Passing tests give focused confidence that cached service indexes remain creation-time ordered and can clean stale entries during add operations.
