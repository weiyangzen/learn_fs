## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_solaris.go

Purpose: Solaris placeholder for process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: always returns `-1`.

State and persistence: none.

Dependencies and integration points: keeps package portable where implementation is unsupported.

Risks: callers must treat `-1` as unsupported/unknown.

Test signals: no direct selected tests.
