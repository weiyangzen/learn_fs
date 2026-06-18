# sources/cloud-native/containerd/core/snapshots/testsuite/helpers.go

## Purpose
Provides shared helpers for snapshotter conformance tests that create, mount, mutate, commit, view, and compare snapshot chains.

## APIs, Flow, State, Dependencies, Risks, And Tests
`applyToMounts` creates a temp target, mounts provided mounts, applies a `fstest.Applier`, and unmounts. `createSnapshot` prepares a random active key, applies changes, commits it to a generated name, and returns that committed name. `checkSnapshot` creates a view of a committed snapshot, mounts it, and compares it to an expected directory. `checkSnapshots` applies a sequence of layers to both a real snapshotter and a flat temp directory, checking every committed layer. `checkInfo` compares snapshot metadata fields exactly.

State includes temp directories, active/view/committed snapshots in the supplied snapshotter, and mount lifecycle. Dependencies include mount helpers, fstest, randutil, os, and internal snapshot types.

Integration is with the broader snapshotter testsuite. Risks include leaked mounts on error, generated name collisions being unlikely but possible, and strict timestamp equality in `checkInfo`. Test signals are successful layered filesystem equality checks and cleanup of views/mounts.
