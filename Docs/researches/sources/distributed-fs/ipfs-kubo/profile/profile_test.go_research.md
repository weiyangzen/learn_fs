# sources/distributed-fs/ipfs-kubo/profile/profile_test.go

Purpose: validates `WriteProfiles` end-to-end by creating an in-memory zip archive and checking expected profile members are present and non-empty.

Important APIs and control flow: `TestProfiler` defines a table over all collectors, OS-specific binary naming, disabled sampling profiles, disabled mutex and block profiles, and a single-collector case. Each case temporarily overrides the package-level `goos` when needed, runs `WriteProfiles`, closes the zip writer, reopens the zip, and checks file count plus non-zero file size.

State and persistence: all output is in memory through `bytes.Buffer`; the test does exercise process-level profiling collectors with very short durations, and the binary collector opens the test binary or `/proc/<pid>/exe`.

Dependencies and integration: uses `archive/zip`, `testing`, `stretchr/testify`, and package globals from `profile.go`.

Risks and test signals: coverage confirms collector gating and Windows `.exe` behavior, but does not cover unknown collector errors, context cancellation, concurrent profiler calls, zip write failures, or global profiling interference.
