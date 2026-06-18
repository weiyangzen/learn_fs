# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_unix.go

Purpose: supplies non-Windows default GC cap constants used by `DetectDefaultGCCap`.

Important constants: Unix builds reserve 10% up to 10 GB, set max cache use to 60% up to 100 GB, and target 20% free disk space.

State and dependencies: no runtime state or imports. The constants feed daemon worker GC policy defaulting.

Risks and test signals: these defaults directly influence automatic cache deletion behavior on Unix systems when users omit explicit GC thresholds. There are no direct tests for these exact constants in this subset.
