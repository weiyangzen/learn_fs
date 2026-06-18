# sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence_test.go

## Purpose
Exhaustively tests the RLE bitmap implementation's bit search, sequence mutation, allocation/deallocation, serialization, rollover, and counting behavior.

## Important APIs, Types, And Functions
Tests cover internal helpers (`getAvailableBit`, `equal`, `getCopy`, `getFirstAvailable`, `findSequence`, `checkIfAvailable`, `mergeSequences`, `pushReservation`, `getAvailableFromCurrent`) and public APIs (`Set`, `Unset`, `SetAny`, `SetAnyInRange`, `Bits`, `Unselected`, JSON marshal/unmarshal, `OnesCount`).

## Control Flow
The suite uses large table-driven cases for masks and sequence shapes, randomized allocation/deallocation patterns with logged seeds, a golden JSON serialization for backward compatibility, and `rapid` property checks comparing `OnesCount` to a straightforward selected-ordinal count.

## State And Persistence
All bitmaps are in-memory except JSON serialization bytes. Random tests mutate bitmaps heavily and verify final compressed sequence strings.

## Dependencies And Integration Points
Uses `gotest.tools` and `pgregory.net/rapid`. These tests protect libnetwork address/ordinal allocation behavior and persisted bitmap compatibility.

## Risks And Test Signals
Randomized tests can be seed-sensitive, but seeds are logged. The golden JSON test is a strong signal that persisted sequence encoding remains backward compatible. The property test covers many range-count edge cases.
