# sources/cloud-native/containerd/internal/cri/util/deep_copy.go

## Purpose
Provides a generic deep-copy helper for CRI data structures by JSON round-tripping from source to destination.

## Important APIs, Types, And Functions
`DeepCopy(dst any, src any) error` rejects nil arguments, marshals `src` with `encoding/json`, then unmarshals into `dst`, wrapping marshal/unmarshal errors.

## Control Flow
The caller supplies a pointer destination. Successful marshal output replaces destination fields according to JSON semantics.

## State And Persistence
No persistent state. Destination object is mutated on successful unmarshal and can be partially changed if JSON unmarshalling fails after writing earlier fields.

## Dependencies And Integration Points
Uses `encoding/json`, `errors`, and `fmt`. It is appropriate for JSON-compatible CRI structs but not for values with unexported fields, channels, funcs, or non-JSON representation requirements.

## Risks
JSON conversion may lose type information, skip unexported fields, coerce numbers, and allocate heavily. It is not a general Go object graph copier.

## Test Signals
`deep_copy_test.go` verifies nested slices, maps, and pointer values are replaced with source-equivalent values.
