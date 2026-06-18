# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures_test.go

## Purpose
Tests the `mergeIter` helper used by dynamic predefined pool allocation.

## Important APIs, Types, And Functions
- `TestMergeIter` constructs allocated and reserved prefix slices and advances `newMergeIter`.

## Control Flow
The test expects the iterator to return allocated and reserved equal prefixes in comparator order, then subsequent allocated prefixes, then the zero prefix sentinel after exhaustion.

## State And Persistence
No persistent state. The iterator mutates only its internal indices.

## Dependencies And Integration Points
Uses `netiputil.PrefixCompare`, matching the comparator used in `address_space.go`.

## Risks
The test is narrow and does not cover all merge iterator edge cases, but broader dynamic allocation tests exercise it through allocator behavior.

## Test Signals
Confirms duplicate equal prefixes across allocated/reserved streams are both visible to the dynamic allocation algorithm.
