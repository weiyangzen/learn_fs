# sources/cloud-native/cri-o/internal/factory/container/container_log_path_test.go

Purpose: tests container log path resolution from CRI container and sandbox configuration.

Important APIs/types/functions: exercises `SetConfig`, `SetNameAndID`, `LogPath`, and constants `configLogPath`, `configLogDir`, `providedLogDir`.

Control flow: tests verify that sandbox-config `LogDirectory` takes precedence over the provided sandbox log dir, that the provided log dir is used when sandbox config lacks one, and that an empty container log path falls back to `<container-id>.log`.

State and persistence behavior: in-memory container config only; no log files are written.

Dependencies/integration points: Ginkgo/Gomega and CRI API types.

Risks: tests check substrings rather than exact joined paths and do not cover path traversal or invalid log paths; those are delegated to `utils.EnsureSaneLogPath`.

Test signals: focused coverage for log path precedence and defaulting.
