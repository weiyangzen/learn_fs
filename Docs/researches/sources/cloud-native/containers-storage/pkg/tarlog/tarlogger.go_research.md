# sources/cloud-native/containers-storage/pkg/tarlog/tarlogger.go

Purpose: provides an `io.WriteCloser` that observes a tar stream and invokes a callback for each tar header while preserving write behavior for callers.

Important APIs/types/functions: unexported `tarLogger` with pipe writer, close mutex, and closed flag; exported `NewLogger(logger func(*tar.Header)) (io.WriteCloser, error)`; methods `Write` and `Close`.

Control flow: `NewLogger` creates an `io.Pipe`, starts a goroutine with a tar reader, calls the logger for each header until `Next` errors, closes the reader, and unlocks a mutex so `Close` waits for completion. `Write` forwards bytes to the pipe and treats closed-pipe errors as successful full writes to avoid changing tar digest behavior.

State/persistence: holds in-memory pipe state and logs headers through caller-provided side effects; no persistent data.

Dependencies/integration: uses `github.com/vbatts/tar-split/archive/tar` and `logrus`. It integrates with archive/diff pipelines that want progress or audit logging while streaming tar bytes.

Risks: `closed` is accessed without synchronization between `Write` and the reader goroutine. Tar parse errors stop logging silently except reader close errors. `Close` locks the mutex but does not unlock it afterward, relying on object finality.

Test signals: `tarlogger_test.go` verifies all header names are observed for a generated archive.
