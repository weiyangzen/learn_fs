# sources/cloud-native/containerd/internal/cri/opts/spec_opts_test.go

## Purpose

This test file validates the shared mount ordering helper used by platform mount options.

## Important APIs, Types, and Functions

`TestOrderedMounts` constructs CRI mounts with different destination depths, sorts them with `orderedMounts`, and verifies the expected order.

## Control Flow

The test builds a slice, calls Go sort using the `orderedMounts` methods, and asserts the destination order.

## State and Persistence Behavior

The test is purely in-memory and does not touch host mounts.

## Dependencies and Integration Points

It targets the `orderedMounts` implementation in `spec_opts.go`, which is consumed by Linux, Windows, and Darwin mount option builders.

## Risks and Edge Cases

It tests path-depth sorting, but not equal-depth stability, path cleaning, platform-specific path separators, or named-pipe paths.

## Test Signals

Passing tests signal that broad parent mounts are processed before deeper child mounts, reducing mount shadowing regressions.
