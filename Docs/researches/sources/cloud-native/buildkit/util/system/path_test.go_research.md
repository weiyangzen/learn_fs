<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_test.go -->
# sources/cloud-native/buildkit/util/system/path_test.go

Purpose: validates platform path normalization and Windows drive handling.

Important APIs and types: `TestNormalizeWorkdir`, `TestCheckSystemDriveAndRemoveDriveLetter`, `TestNormalizeWorkdirWindows`, `TestNormalizeWorkdirUnix`, and `TestIsAbs`.

Control flow: table tests cover relative/absolute workdirs, empty current/new workdir, parent-directory cleanup, Windows mixed slashes, C-drive stripping, non-C drive errors, bare drive errors, `C:relative` behavior, UNC rejection, and Windows absolute path detection.

State and persistence: pure string tests.

Dependencies and integration: uses `testify/require`.

Risks: tests are extensive for exposed behavior but do not cover `NormalizePath` keepSlash directly outside drive-removal helper cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_test.go -->
