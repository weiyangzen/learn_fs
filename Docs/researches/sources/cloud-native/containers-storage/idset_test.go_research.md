<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/idset_test.go -->
# sources/cloud-native/containers-storage/idset_test.go

## Purpose
This test file validates interval and ID-map set logic used by storage mapping allocation.

## Important APIs, Types, And Functions
Helpers `allIntervals`, `idSetsEqual`, and `assertIntervalSame` normalize comparisons. Test groups cover `newIDSet`, `getHostIDs`, `getContainerIDs`, `subtract`, `union`, `size`, `findAvailable`, `zip`, interval methods, and `hasOverlappingRanges`.

## Control Flow
Large table-driven cases exercise nil, empty, invalid, overlapping, adjacent, unordered, and multi-interval inputs. Operator tests also verify that original sets are unchanged after operations. Reflective interval tests check behavior in both operand orders.

## State And Persistence
Tests are pure in-memory and write no durable state.

## Dependencies And Integration Points
The tests depend on `idtools.IDMap`, `intervalset`, and Go's testing/reflect packages.

## Risks And Test Signals
The suite is strong for mathematical behavior and edge cases. It does not directly test goroutine leaks from missed iterator cancellation, but production methods consistently defer cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/idset_test.go -->
