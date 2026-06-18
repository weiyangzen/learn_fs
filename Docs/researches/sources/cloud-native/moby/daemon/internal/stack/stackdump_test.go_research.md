<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump_test.go -->
# sources/cloud-native/moby/daemon/internal/stack/stackdump_test.go

Purpose: validates stack dump helpers.

Important APIs and types: `TestDump`, `TestDumpToFile`, and `TestDumpToFileWithEmptyInput`.

Control flow: tests call `Dump`, write a dump to a temp directory and check file contents include `goroutine`, and call `DumpToFile("")` expecting stderr name.

State and persistence: creates a temp diagnostic file in one test and writes to stderr in others.

Dependencies and integration: uses gotest assertions.

Risks: `Dump` writes to test stderr. Tests do not cover file open/write failures or timestamp collisions.

Test signals: basic coverage for successful dump paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump_test.go -->
