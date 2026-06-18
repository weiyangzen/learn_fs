<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/util.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/util.go

## Purpose
Provides a small random byte helper for tests.

## Important APIs, Types, And Functions
- `RandomBytes(n int)` allocates `n` bytes and fills them with cryptographic randomness.

## Control Flow
The function allocates a slice, calls `rand.Read`, and returns bytes or error.

## State And Persistence
No persistent state. Randomness comes from the OS crypto random source.

## Dependencies And Integration Points
Used by tests that need non-repetitive content payloads.

## Risks And Edge Cases
Can fail if the OS random source fails. Negative sizes panic through slice allocation semantics.

## Test Signals
Expected tests verify length and error-free generation for normal sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/util.go -->
