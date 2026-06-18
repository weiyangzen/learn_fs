# sources/control-plane/csi-spec/lib/go/Makefile

## Purpose

This Makefile generates Go protobuf and gRPC bindings for the CSI spec.

## Important Targets and Flow

It normalizes `GOPATH` and `GOBIN`, sets `PROTOC_VER` default `25.2`, maps OS/architecture names to protoc release naming, downloads and unzips protoc into `.protoc`, and installs `protoc-gen-go` plus `protoc-gen-go-grpc@v1.3.0`. It prepends `GOBIN` to `PATH` so protoc can find plugins. `$(CSI_GO)` and `$(CSI_GRPC)` depend on `../../csi.proto` and tool binaries, create the output directory, and run protoc with source-relative Go and Go-gRPC outputs into `csi/`. `clean` removes generated package files via `go clean -i ./...` and `rm -rf csi`; `clobber` also removes `.protoc`.

## State, Dependencies, and Integration

Generated state includes `.protoc/` and `lib/go/csi/*.pb.go`/`*_grpc.pb.go`. Dependencies are Make, Go, curl, unzip, protoc, and Go generator modules. It is invoked by the top-level Makefile and build workflow.

## Risks and Test Signals

The protoc architecture mapping handles common `i386` and `arm64` cases but may miss other names. Downloads are network-sensitive. Tool versions define generated-code output and API compatibility. Test signals are successful protoc generation and clean git diffs after `make`.
