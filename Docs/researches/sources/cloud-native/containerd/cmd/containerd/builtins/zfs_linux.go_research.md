# Research: sources/cloud-native/containerd/cmd/containerd/builtins/zfs_linux.go

## Purpose
Registers the ZFS plugin in Linux daemon builds.

## Important APIs, Control Flow, And State
The Linux-only file blank-imports `github.com/containerd/zfs/v2/plugin`, which registers through package init. No direct functions or local state are present.

## Dependencies And Integration
Included through the daemon builtins package. It exposes ZFS snapshotter functionality where supported.

## Risks And Test Signals
Risks include platform dependency failures and missing plugin registration. Linux build and plugin graph tests should verify ZFS registration under supported build environments.
