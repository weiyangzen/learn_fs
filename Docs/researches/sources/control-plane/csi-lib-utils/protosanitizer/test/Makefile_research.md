# sources/control-plane/csi-lib-utils/protosanitizer/test/Makefile

## Purpose
This Makefile generates Go bindings for a test protobuf schema used by protosanitizer tests to simulate future CSI secret-field layouts.

## Important APIs, Types, And Functions
Targets include `all`, `$(GOBIN)/protoc-gen-go`, `$(PROTOC)`, generated `$(CSI_GO)`, `build`, `clean`, and `clobber`. Variables configure GOPATH, `PROTOC_VER=25.2`, OS/arch mapping, download URL, and paths.

## Control Flow
The Makefile ensures `protoc-gen-go` is installed from the parent module, downloads a platform-specific protoc zip into `.protoc`, unzips it, and runs protoc over `csitest.proto` with source-relative Go output into the `csitest` package. `clean` removes generated Go package files and `clobber` also removes downloaded protoc.

## State, Persistence, And Dependencies
It writes `.protoc/`, installs `protoc-gen-go` into `GOBIN`, and generates `csitest/csitest.pb.go`. Dependencies include curl, unzip, Go, protoc releases, and the parent `go.mod`.

## Integration Points
The generated package is imported by `protosanitizer_test.go`.

## Risks And Test Signals
The download URL depends on platform naming and external GitHub availability. `GOBIN` must be set or Go's install path behavior must be acceptable. Signal is successful generation of `csitest.pb.go`.
