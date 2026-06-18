# sources/control-plane/csi-lib-utils/protosanitizer/protosanitizer.go

## Purpose
This package provides a safe `fmt.Stringer` wrapper for logging CSI protobuf messages as one-line JSON while stripping fields marked with the CSI secret protobuf extension.

## Important APIs, Types, And Functions
Public API is `StripSecrets(msg interface{}) fmt.Stringer`. Internal type `stripSecrets` implements `String`. Helpers are `stripSingleValue`, `stripValue`, `stripMessage`, and `isCSI1Secret`.

## Control Flow
`StripSecrets` returns a lightweight wrapper. When stringified, scalar values are marshaled directly; protobuf messages are reflected field-by-field. Secret fields are replaced with `"***stripped***"`. Non-secret message, enum, list, and map values are recursively converted into JSON-marshalable Go values. Unknown enum values are emitted numerically.

## State, Persistence, And Dependencies
The package is stateless and does not mutate the original message. Dependencies include CSI protobuf definitions and `google.golang.org/protobuf` reflection.

## Integration Points
`connection.LogGRPC` uses this for request/response logging to avoid leaking CSI secrets.

## Risks And Test Signals
`isCSI1Secret` type-asserts the extension value to bool, so it assumes CSI 1.0+ descriptors with the extension available. Unknown protobuf fields are not emitted through normal reflection, which is a privacy advantage but may omit debugging detail. Tests cover current CSI, future secret fields, maps/lists/oneofs, scalar values, immutability, and benchmarks.
