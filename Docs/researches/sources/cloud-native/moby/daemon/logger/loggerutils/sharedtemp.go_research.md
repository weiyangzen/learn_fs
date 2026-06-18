# sources/cloud-native/moby/daemon/logger/loggerutils/sharedtemp.go

Purpose: shares temporary converted file contents, primarily decompressed rotated log files, across concurrent readers.

Important APIs/types/functions: `sharedTempFileConverter`, `Do`, `openNew`, `openExisting`, `convert`, `sharedFileReader`, and `Close`.

Control flow/state/persistence: state lives in a one-slot channel. `Do` stats source files and reuses an existing conversion when `os.SameFile` and modtime match. Concurrent requests for an in-progress conversion wait on result channels. `convert` writes to a temp file, reopens it read-only, removes the name immediately, and returns section readers with reference counting. Last reader closes the shared fd and removes state.

Dependencies/integration: used by `LogFile` compressed-file reader with gzip decompression.

Risks: assumes source files are immutable after conversion. `os.SameFile` false positives are mitigated with modtime but not content hashing. Incorrect ref counting can leak fds or close active readers.

Test signals: `sharedtemp_test.go` covers reuse, waiting, errors, close, and cleanup.
