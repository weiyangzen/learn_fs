# sources/cloud-native/moby/daemon/logger/loggerutils/sharedtemp_test.go

Purpose: tests shared temp-file conversion and cleanup behavior.

Important APIs/types/functions: `TestSharedTempFileConverter` plus helpers for creating files, converting paths, reading all, checking directories, and copy transforms.

Control flow/state/persistence: tests use temp dirs/files, multiple readers, conversion functions, and cleanup assertions.

Dependencies/integration: validates the decompression-cache primitive used by `LogFile`.

Risks: temp-file behavior can be platform-sensitive; tests help catch Windows/POSIX differences.

Test signals: strong signal for conversion reuse, reference counting, waiters, and error cleanup.
