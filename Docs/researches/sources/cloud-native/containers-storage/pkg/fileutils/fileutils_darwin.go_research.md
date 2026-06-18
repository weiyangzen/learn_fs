## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_darwin.go

Purpose: Darwin implementation of process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: resolves current PID, runs `lsof -p <pid>`, trims output, splits by lines, and subtracts one header line.

State and persistence: spawns an external process and reads its output; no persistent mutation.

Dependencies and integration points: diagnostic helper for resource usage on macOS.

Risks: requires `lsof` in PATH; failure returns `-1`. Line-counting assumes standard `lsof` output with one header.

Test signals: no direct selected tests for this platform-specific implementation.
