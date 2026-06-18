# sources/cloud-native/moby/daemon/logger/loggerutils/file_unix.go

Purpose: Unix implementations of open/unlink helpers used by `LogFile`.

Important APIs/types/functions: `openFile`, `open`, and `unlink`.

Control flow/state/persistence: thin wrappers around `os.OpenFile`, `os.Open`, and `os.Remove`.

Dependencies/integration: selected by `!windows` build tag; used by rotation, compression, and read paths.

Risks: POSIX unlink semantics allow deleting open files, which differs from Windows and is abstracted by the platform layer.

Test signals: loggerutils log file tests exercise these helpers on Unix.
