# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_linux.go

## Purpose
Registers Linux-specific daemon builtins for runc options, cgroup metrics, diff, mounts, and snapshotters.

## Important APIs, Control Flow, And State
Blank imports register runc option type support, cgroups metrics collectors, EROFS/walking diff plugins, EROFS mount support, and blockfile, EROFS, native, and overlay snapshotters. The file has no runtime functions; state is plugin/type registry side effects.

## Dependencies And Integration
Selected for Linux builds and included through `cmd/containerd/builtins`.

## Risks And Test Signals
Risks include missing overlay/native snapshotter registrations, cgroup metrics omissions, or duplicate registration conflicts. Linux build and plugin graph tests should assert expected plugin IDs and typeurl registrations.
