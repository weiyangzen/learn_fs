# sources/cloud-native/containerd/internal/cri/server/sandbox_run_linux.go

## Purpose

This Linux file provides CRI service helpers for loopback setup and network namespace creation inside a pod user namespace.

## Important APIs, Types, and Functions

`bringUpLoopback` enters a netns and sets link `lo` up. `setupNetnsWithinUserns` validates pod user namespace settings and uses `sys.UnshareAfterEnterUserns` with UID/GID maps and `CLONE_NEWNET` to create a network namespace whose mount is captured by `netns.NewNetNSFromPID`.

## Control Flow

User namespace netns setup requires pod mode, exactly one non-nil UID mapping, and exactly one non-nil GID mapping. It formats mapping strings, unshares network after entering userns, mounts the new netns from the child PID, and returns it.

## State and Persistence Behavior

It can create and mount a network namespace under the requested mount directory and change loopback state inside a netns.

## Dependencies and Integration Points

It integrates with CNI setup, CRI user namespace options, containerd netns helpers, Linux netlink, and containerd sys userns helpers.

## Risks and Test Signals

Risks include invalid mappings, kernel permission failures, and netns mount leaks. This behavior needs root/integration tests on Linux userns-capable kernels.
