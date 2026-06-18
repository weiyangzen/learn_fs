<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows_test.go

Purpose: validates Windows `platformCopy` excludes protected folders only when copying from snapshot root.

Important APIs and types: `TestPlatformCopy_RootOnlyProtectedExcludes`.

Control flow: the test creates a source root with a normal folder plus `System Volume Information` and `WcSandboxState`, copies `/`, asserts normal file copied and protected folders absent, then creates a nested protected-named folder under `foo`, copies `/foo`, and asserts the nested folder is copied.

State and dependencies: Windows-only test using temporary directories and files. Depends on `context`, `os`, `filepath`, and testify.

Integration points: protects Windows file-op behavior on container snapshot mounts.

Risks and test signals: good coverage for the intended filter boundary, but it does not simulate actual Windows ACL denial behavior; it verifies path filtering semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/backend_windows_test.go -->
