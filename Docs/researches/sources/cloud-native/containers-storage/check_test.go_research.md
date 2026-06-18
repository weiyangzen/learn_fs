<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/check_test.go -->
# sources/cloud-native/containers-storage/check_test.go

- Purpose: Unit tests for `checkDirectory` and writable/read-only store detection helpers.
- Important tests: `TestCheckDirectory` builds expected directory trees from tar headers and validates whiteout/remove/replace semantics; `TestCheckDetectWriteable` checks read-write detection behavior.
- Control flow and state: In-memory test construction with temporary directories or store fixtures as needed; no persistent production state.
- Dependencies and integration: Uses Go `testing`, tar header helpers, and check.go internals because it is in package `storage`.
- Risks: Coverage is focused on comparison primitives, not full `Check`/`Repair` destructive workflows.
- Test signals: `go test` for the storage package.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/check_test.go -->
