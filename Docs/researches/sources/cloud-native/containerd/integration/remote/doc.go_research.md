# sources/cloud-native/containerd/integration/remote/doc.go

## Purpose

`doc.go` declares package `remote` and documents it as legacy-style CRI client adapters for containerd integration tests and stress tooling.

## Important APIs, Types, and Functions

The file exports no code symbols beyond the package-level documentation and `package remote`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The file has no state or persistence behavior.

## Dependencies and Integration Points

It integrates only through Go documentation and package compilation. The implementation surface lives in `remote_image.go` and `remote_runtime.go`.

## Risks and Edge Cases

The package comment is the primary overview for these adapters; if behavior changes in the implementation, this short description must remain accurate.

## Test Signals

Compilation and documentation tooling are the only direct signals.
