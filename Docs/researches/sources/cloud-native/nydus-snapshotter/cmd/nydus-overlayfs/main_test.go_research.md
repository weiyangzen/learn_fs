# sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main_test.go

Purpose: unit tests for overlayfs helper parsing and path compaction.

Flow: tests longest common prefix cases, lowerdir compaction with two and many layers, disjoint path fallback, real-world size savings under 4096 bytes, and option filtering for Nydus/Kata metadata.

State/dependencies: pure in-memory tests using testify; no mounts are performed.

Integration points: protects the helper logic used when containerd mount data exceeds kernel page-size limits.

Risks/signals: verifies compaction savings but not `run` chdir or syscall behavior. Invalid argument coverage is limited to fs type in the shown cases.
