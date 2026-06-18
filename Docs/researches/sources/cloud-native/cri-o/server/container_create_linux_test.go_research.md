<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux_test.go -->
# sources/cloud-native/cri-o/server/container_create_linux_test.go

## Purpose

This file unit-tests Linux-specific mount helper behavior used during container creation.

## Important APIs, Types, and Functions

Tests directly exercise `addOCIBindMounts` and `isSubDirectoryOf` with factory containers and minimal `storage.ContainerInfo`. Cases include explicit `/dev`, explicit `/sys`, recursive read-only mounts, cgroup mount flags, and ID-mapped mount support.

## Control Flow

Each test constructs a container with targeted CRI mount fields, invokes `addOCIBindMounts`, and inspects returned bind mounts or generated spec mounts. Table-driven recursive read-only tests verify exact error strings for missing runtime support, conflicting read-write mode, and non-private propagation.

## State and Persistence Behavior

The tests mutate in-memory OCI specs only. They intentionally use host paths like `/mnt` or `/sys` without requiring real mount operations, because `addOCIBindMounts` builds specs and only creates missing sources when necessary.

## Dependencies and Integration Points

They depend on `internal/factory/container`, CRI types, and `internal/storage.ContainerInfo`. Because tests are in package `server`, they can call unexported helpers.

## Risks and Edge Cases

The tests verify several mount-safety invariants but do not cover image volume mounting, artifact subpaths, SELinux labels, propagation shared/slave validation, safe mount lifecycle, or systemd-specific behavior. Some tests are sensitive to host path existence and cgroup behavior.

## Test Signals

These tests are strong signals for the path-shadowing and recursive read-only rules. They also lock down the intended behavior that idmapped CRI mounts fail unless the runtime reports support.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux_test.go -->
