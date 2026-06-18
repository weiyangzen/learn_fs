<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external_test.go

## Purpose

This test file verifies local and remote external snapshotter handling at the file-output level using mock backend handlers.

## Important APIs, Types, and Functions

`mockHandler` implements local `backend.Handler`. `mockRemoteHandler` implements the remote handler interface. `TestHandle`, `TestRemoteHandle`, `TestBuildEmptyFiles`, and `TestBuildAttr` validate artifact creation and attribute helper behavior.

## Control Flow

The local test creates temp output paths and a handler returning a mock backend with no chunks, then checks that all three output files exist. The remote test returns one `FileAttribute`, runs `RemoteHandle`, and checks backend, attribute, and context placeholder files. `TestBuildEmptyFiles` verifies directory creation and file modes.

## State and Persistence Behavior

All outputs are under temporary directories. The tests intentionally assert creation side effects rather than parsing content in detail.

## Dependencies and Integration Points

The tests depend on `backend.FileAttribute`, `backend.Backend`, and `testify/assert`. They show that `RemoteHandle` is expected to materialize empty context files in addition to backend and attribute metadata.

## Risks and Test Signals

The tests prove output creation for basic cases, but they do not assert exact attribute text, JSON contents, metadata binary shape, or error paths for failed writes and invalid remote paths. That leaves formatting regressions and path-safety issues as residual risks.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/external_test.go -->
