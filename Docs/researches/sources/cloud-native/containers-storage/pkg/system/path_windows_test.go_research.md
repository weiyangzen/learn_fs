# sources/cloud-native/containers-storage/pkg/system/path_windows_test.go

Purpose: Windows unit tests for `CheckSystemDriveAndRemoveDriveLetter`.

Important APIs/types/functions: `TestCheckSystemDriveAndRemoveDriveLetter` exercises `d:\`, single-character and two-character relative paths, drive-less absolute paths, Linux-style slash input, `c:\`/`c:/`, and bare `c:`/`d:` failures.

Control flow: each case calls the helper and compares either returned path or exact error string.

State/persistence: none beyond temporary test state.

Dependencies/integration: validates Windows path normalization behavior expected by higher-level copy and extraction code.

Risks: the expected error strings differ in capitalization from the current implementation (`The/No` versus `specified/relative`), which would fail exact-string assertions on Windows. Exact error string checks are brittle for user-message changes.

Test signals: strong coverage for common drive-letter cases; missing coverage for UNC paths, extended-length paths, and non-`C:` system drives.
