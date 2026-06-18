<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_windows.go -->
# sources/cloud-native/buildkit/session/filesync/diffcopy_windows.go

Purpose: Windows implementation of sending a diffcopy stream with temporary backup privilege.

Important APIs, types, and functions: `sendDiffCopy` enables `winio.SeBackupPrivilege`, defers disabling it, and calls `fsutil.Send`.

Control flow and state: temporarily changes process privileges for the duration of send so fsutil goroutines can copy special Windows metadata files.

Dependencies and integration: compiled on Windows, depends on `github.com/Microsoft/go-winio` and fsutil. Called through the shared filesync protocol table.

Risks and test signals: privilege enablement is security-sensitive and has a TODO to review exploitability. Windows tests should cover copying metadata files and privilege cleanup after errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/filesync/diffcopy_windows.go -->
