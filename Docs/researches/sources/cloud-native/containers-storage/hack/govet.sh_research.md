<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/govet.sh -->
# sources/cloud-native/containers-storage/hack/govet.sh

## Purpose
This helper runs `go vet` for all non-vendor packages.

## Important APIs, Types, And Functions
It uses `go list ./... | grep -v /vendor/` and runs `go vet` for each package.

## Control Flow
The script exits immediately with an error message if any package fails vet; otherwise exits 0.

## State And Persistence
No files are modified.

## Dependencies And Integration Points
It depends on the Go toolchain and package list resolution.

## Risks And Test Signals
Package names with whitespace are not handled, though Go import paths normally avoid that. It runs packages sequentially and may be slower than `go vet ./...`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/hack/govet.sh -->
