<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer_test.go

## Purpose

This test file verifies viewer construction, bootstrap extraction, external backend handling, mount setup, and retry behavior with monkey-patched dependencies.

## Important APIs, Types, and Functions

`failingJSON` exercises marshal errors. `buildBootstrapArchive` creates a gzip tar archive. Tests include `TestNewFsViewer`, `TestNewFsViewerErrors`, `TestPrettyDump`, `TestPullBootstrap`, `TestPullBootstrapWithoutNydusImage`, `TestGetBootstrapFile`, `TestHandleExternalBackendConfig`, `TestMountImage`, `TestViewParseError`, and `TestViewHTTPRetry`.

## Control Flow

Tests use `gomonkey` to patch parser methods, private methods, `utils.BuildRuntimeExternalBackendConfig`, `tool.NewNydusd`, and `Nydusd.Mount`. They assert wrapped errors and success paths without launching real nydusd or accessing a real registry.

## State and Persistence Behavior

Tests write temporary work directories and bootstrap/backend files; some hard-coded `/tmp/nydusify/fsviwer` and `/tmp/backend.json` paths are used. Monkey patches are reset with defers.

## Dependencies and Integration Points

The tests depend on parser, remote, checker/tool, backend config structs, utils constants, gzip/tar primitives, `gomonkey`, and `testify`. They are strong integration signals for viewer orchestration boundaries.

## Risks and Test Signals

Monkey patching can be brittle across compiler/runtime changes. Tests do not perform an end-to-end successful `View` because it blocks on signals, and they do not verify cleanup after signal or real nydusd process behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/viewer/viewer_test.go -->
