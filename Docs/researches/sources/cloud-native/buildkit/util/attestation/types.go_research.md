# sources/cloud-native/buildkit/util/attestation/types.go

## Purpose
Constants for Docker attestation manifest annotations. They name reference type, digest, description, and the default reference type value.

## Important APIs, Types, And Functions
Package: `attestation`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow or state; other exporter/attestation code consumes these strings when annotating OCI artifacts.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is annotation key compatibility with Docker consumers. No local tests.
