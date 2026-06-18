# sources/cloud-native/containerd/plugins/snapshots/blockfile/blockfile_test.go

## Purpose
This file runs containerd's generic snapshotter conformance suite against the blockfile snapshotter.

## Important APIs, Types, And Functions
`newSnapshotter` obtains platform-specific setup options and returns a factory compatible with `testsuite.SnapshotterSuite`. `TestBlockfile` requires root and invokes the suite with name `Blockfile`.

## Control Flow
Test setup builds a snapshotter with `NewSnapshotter(root, opts...)` and returns a closer that calls `Close`.

## State And Persistence
Test state is created below temporary roots and cleaned by the suite/closer where possible.

## Dependencies And Integration Points
It depends on the generic snapshotter testsuite, testutil root gating, and platform-specific `setupSnapshotter`.

## Risks
The generic suite does not specifically assert blockfile sparse-file usage accounting, scratch recreation, or mount option slice mutation.

## Test Signals
Passing the suite validates core snapshotter lifecycle behavior: prepare, view, commit, remove, stat, walk, mounts, and usage expectations.
