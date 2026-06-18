# sources/cloud-native/containerd/api/buf.gen.yaml

## Purpose
This Buf generation config defines how containerd API protobufs generate Go, gRPC, ttrpc, and fieldpath code.

## Important APIs, Types, And Functions
It uses remote plugins `buf.build/protocolbuffers/go:v1.28.1` and `buf.build/grpc/go:v1.2.0`, plus local plugins `protoc-gen-go-ttrpc` and `protoc-gen-go-fieldpath`. All outputs use `paths=source_relative`; Go generation maps `google/rpc/status.proto` to the genproto package.

## Control Flow
`make protos` runs `buf generate` in `api`, which reads this config and emits generated files alongside sources.

## State And Persistence
Generated `.pb.go`, grpc/ttrpc, and fieldpath files are persistent source artifacts.

## Dependencies And Integration Points
It integrates with Buf, generated API Go code, local generator binaries in `bin/`, and CI proto checks.

## Risks
Remote plugin version bumps can change generated output broadly. Local plugins must be installed before generation.

## Test Signals
`make protos`, clean git diff expectations, and `make check-protos` are the main signals.
