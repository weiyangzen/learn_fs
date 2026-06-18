# sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main_test.go

## Purpose
Unit tests for the CSI snapshotter command entrypoint support checks and mock CSI server setup.

Source size: 164 lines, 4555 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Functions/methods: `Test_supportsControllerCreateSnapshot`, `createMockServer`.
- Key imports: `context`, `fmt`, `testing`, `github.com/container-storage-interface/spec/lib/go/csi`, `github.com/golang/mock/gomock`, `github.com/kubernetes-csi/csi-lib-utils/connection`, `github.com/kubernetes-csi/csi-lib-utils/metrics`, `github.com/kubernetes-csi/csi-test/v5/driver`, `github.com/kubernetes-csi/csi-test/v5/utils`, `google.golang.org/grpc`.

## Control Flow
- Creates a mock CSI driver and gRPC connection.
- Programs expected `ControllerGetCapabilities` responses with gomock.
- Calls support-detection helpers and compares errors/results for capability, error, empty, and absent-capability cases.

## State and Persistence
- Test state is in-memory mock server state plus a local gRPC connection; no Kubernetes API state is written.
- Mock expectations are consumed once per test case and verified by gomock at teardown.

## Dependencies and Integration Points
- CSI protobuf APIs, csi-test mock driver, gomock, csi-lib-utils connection and metrics helpers, Go testing package.

## Risks and Edge Cases
- Tests cover snapshot capability detection but not the full `main` startup path.
- Mock server lifecycle must stop and close connections to avoid leaked goroutines.

## Test Signals
- This file is itself the test signal for `supportsControllerCreateSnapshot`.
- Cases include success, gRPC error, missing capability, nil capability, and empty capability list.
