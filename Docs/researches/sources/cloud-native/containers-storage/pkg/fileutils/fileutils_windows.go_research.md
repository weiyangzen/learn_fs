## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_windows.go

Purpose: Windows placeholder for process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: always returns `-1`.

State and persistence: none.

Dependencies and integration points: portable API stub.

Risks: callers must handle unsupported value.

Test signals: no direct selected tests.
