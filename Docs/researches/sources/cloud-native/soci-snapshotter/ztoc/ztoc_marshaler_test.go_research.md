# sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler_test.go

## Purpose
This test file focuses on TOC FlatBuffer round-trip behavior and validation.

## Important APIs, Types, and Functions
`roundtrip(toc)` serializes a `TOC` to FlatBuffers and immediately deserializes it with `flatbufferToTOC`. `TestPositiveTOCRoundtrip` checks preservation and sorting by uncompressed offset. `TestNegativeTOCRoundtrip` checks overlapping entries return `ErrInvalidTOCEntry`.

## Control Flow, State, and Persistence
The tests build in-memory FlatBuffers only. They model tar header/data placement and use `FileMetadata.Equal` for comparison.

## Dependencies and Integration Points
Dependencies are Go testing/errors, generated FlatBuffers code, and `flatbuffers/go`. The test isolates TOC conversion rather than full zTOC marshal.

## Risks and Test Signals
The negative test has an unused `anyError` variable but still checks `errors.Is(err, expected)`. The tests do not cover xattrs, mod time parse failure, span digests, or compression info; those are covered more broadly in `ztoc_test.go`.
