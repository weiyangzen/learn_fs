# sources/cloud-native/moby/daemon/libnetwork/bitmap/sequence.go

## Purpose
Implements a fixed-length, non-concurrent bitmap using run-length encoded 32-bit blocks. It supports efficient allocation/free operations, range allocation, selected-bit counting, copying, and binary/JSON persistence.

## Important APIs, Types, And Functions
`Bitmap` stores total bits, unselected count, RLE `head`, and serial scan cursor. Public APIs include `New`, `Copy`, `Set`, `Unset`, `SetAny`, `SetAnyInRange`, `IsSet`, `OnesCount`, `MarshalBinary`, `UnmarshalBinary`, JSON marshal/unmarshal, `Bits`, `Unselected`, and `String`. Internal helpers include `sequence`, `findSequence`, `getFirstAvailable`, `getAvailableFromCurrent`, `checkIfAvailable`, `pushReservation`, and `mergeSequences`.

## Control Flow
Allocation finds an unset bit, then `pushReservation` splits or merges RLE nodes depending on whether the affected block is first, last, or middle of a sequence. Release clears a bit through the same path. Serial allocation starts scanning at `curr` and rolls over to the requested start.

## State And Persistence
Bitmap state is mutable and explicitly not safe for concurrent use. Binary persistence stores `bits`, `unselected`, and sequence nodes; `curr` is not persisted or reset by unmarshal.

## Dependencies And Integration Points
Used by libnetwork allocators for long ordinal spaces. JSON serialization preserves on-disk compatibility through base64-encoded binary data.

## Risks And Test Signals
Boundary math is complex around non-32-bit lengths, range ends, and RLE splitting. Tests are extensive, including random allocation/deallocation, golden JSON, rollover, and property-based `OnesCount`.
