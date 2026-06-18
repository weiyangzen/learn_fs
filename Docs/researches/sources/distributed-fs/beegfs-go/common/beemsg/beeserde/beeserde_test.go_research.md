# sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde_test.go

## Purpose
This Go test suite validates BeeSerde serialization/deserialization primitives with round trips and error checks.

## Important Tests
`TestInt` round-trips signed and unsigned integer widths. `TestCStr` serializes/deserializes C strings with multiple alignments. `TestCStrAlignment` checks expected buffer lengths for empty and short strings under alignments. `TestStringSeq` round-trips string sequences and verifies null bytes cause serialization error. `TestNestedSeq` and `TestNestedMap` round-trip nested sequence and map structures. `TestErrorOnNonPointerDeserialization` verifies deserializing into a non-pointer records an error.

## Dependencies and Integration
The tests use `stretchr/testify/assert` and the public functions in `beeserde.go`.

## Signals and Gaps
The suite covers core happy paths and some errors. It does not test truncated buffers, leftover bytes, map ordering determinism, nil destination pointers, feature flag use, or deserialization of string sequences with malformed terminators beyond buffer read errors.
