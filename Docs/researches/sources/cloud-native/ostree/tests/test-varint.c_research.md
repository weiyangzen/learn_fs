# sources/cloud-native/ostree/tests/test-varint.c

## Purpose
This C unit test validates OSTree variable-length unsigned 64-bit integer encoding and decoding round trips.

## Important APIs, Types, And Functions
It tests `_ostree_write_varuint64()` and `_ostree_read_varuint64()` from `ostree-varint.h`, using `GString`, `GVariant` debug printing in verbose mode, and GLib test APIs.

## Control Flow
`check_one_roundtrip()` writes a value into a string buffer, optionally prints encoded bytes, reads it back, asserts decoding succeeded, asserts no more than ten bytes were read, and compares the value. `test_roundtrips()` runs values including small boundaries, hex constants, `G_MAXUINT64`, `G_MAXUINT64 - 1`, and half max.

## State And Persistence
No persistent state is written. `GIO_USE_VFS=local` is set for deterministic local behavior.

## Dependencies And Integration Points
This integrates private varint helpers used by OSTree metadata such as sizes and deltas. It is also mirrored conceptually by the GJS varint reader in `test-sizes.js`.

## Risks
Boundary values near 127/128 and `G_MAXUINT64` catch continuation-bit and length bugs. Decode byte count must remain bounded to avoid malformed input issues elsewhere.

## Test Signals
The GLib path `/ostree/varint` fails on encode/decode mismatch, unsuccessful decode, or overlong encoded size.
