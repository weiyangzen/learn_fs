<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter.go -->
# sources/cloud-native/containers-storage/pkg/archive/filter.go

Purpose: helper for running external compression/decompression filters as streaming subprocesses.

Important APIs/types/functions: package cache `filterPath`, `getFilterPath`, `errorRecordingReader`, and `tryProcFilter`.

Control flow: `getFilterPath` memoizes `exec.LookPath` results in `sync.Map`, using an empty string for missing commands. `tryProcFilter` returns `(nil,false)` when the command is unavailable. Otherwise it builds an `exec.Command`, wires input through an `errorRecordingReader`, stdout to an `io.Pipe`, stderr to a buffer, starts a goroutine, runs the process, prefers input read errors over process errors, includes stderr in process errors, closes the pipe with the final error, and calls caller cleanup.

State/persistence: caches filter executable paths in-process. No durable writes.

Dependencies/integration: used by archive compression paths that can delegate to external tools such as bzip2/xz. Integrates with streaming readers so callers can consume stdout lazily.

Risks: process lifetime is tied to reader consumption; if callers do not drain/close, goroutines and subprocesses can linger. Cached negative lookups mean later PATH changes are ignored. Cleanup is only called after process execution, not when command is missing.

Test signals: `filter_test.go` covers missing commands, successful `cat`, stderr-enriched failure, and cleanup invocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter.go -->
