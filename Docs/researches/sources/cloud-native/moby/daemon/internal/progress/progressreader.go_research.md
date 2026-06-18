<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader.go -->
# sources/cloud-native/moby/daemon/internal/progress/progressreader.go

Purpose: wraps an `io.ReadCloser` and emits throttled progress updates as bytes are read.

Important APIs and types: `Reader`, `NewProgressReader`, `Read`, `Close`, and `updateProgress`.

Control flow: `Read` advances `current`, chooses an update threshold of 512 KiB or 1 percent of known size if smaller, emits progress when threshold is exceeded or an error occurs, and marks last update when read returns error with no bytes. `Close` emits a full progress bar if closing before the expected size, then closes the underlying reader. `updateProgress` rate-limits updates to 100 ms unless final or exactly complete.

State and persistence: tracks current bytes, size, last update offset, ID/action, output, and rate limiter in memory.

Dependencies and integration: used by transfer paths to report progress through `progress.Output`.

Risks: when size is small, threshold can become zero and cause frequent updates, mitigated by rate limiter. Close treats premature close as complete for display. Output errors are ignored.

Test signals: `progressreader_test.go` verifies premature close emits progress and complete read closes silently.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progressreader.go -->
