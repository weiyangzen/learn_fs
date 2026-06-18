## sources/cloud-native/buildkit/util/grpcerrors/grpcerrors_test.go

Purpose: regression tests for rich gRPC error conversion.

Important tests: `TestFromGRPCPreserveUnknownTypes` checks unknown `Any` details survive decode and roundtrip. `TestFromGRPCPreserveTypes` joins an unknown-detail status with a typed solve error and verifies both survive. `TestCode` covers explicit `Code`, `GRPCStatus`, wrapped errors, joined errors, and context errors. `TestAsGRPCStatus` covers nil, direct, wrapped, joined, and absent statuses. `TestToGRPCMessage` avoids duplicate code prefixes and keeps extra outer context.

Dependencies: solver errdefs, gRPC status/codes, protobuf Any, standard `errors.Join`, `pkg/errors`, `testify`.

Risks covered: loss of unknown/typed detail and degraded messages across gRPC. Gaps: no direct stack trace assertion and no failure path for unregistered typed details.
