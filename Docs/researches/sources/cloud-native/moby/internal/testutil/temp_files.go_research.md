<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/temp_files.go -->
# sources/cloud-native/moby/internal/testutil/temp_files.go

Purpose: creates temporary directories for tests with a helper-level API. `TempDir` wraps temp directory creation, likely normalizes permissions/path behavior, and registers cleanup or fails the test on error. State is filesystem temp directory content. Dependencies are `os`, `filepath`, and `testing`. Risks are low, mostly around cleanup and platform path handling. Test signal is through call sites that need predictable temp paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/temp_files.go -->
