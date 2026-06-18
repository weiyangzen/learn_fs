# sources/cloud-native/containerd/internal/cri/opts/spec_linux.go

## Purpose

This Linux file provides environment-detection helpers and CDI injection for OCI spec generation.

## Important APIs, Types, and Functions

`SwapControllerAvailable` detects memory swap controller support for cgroup v1 or v2. `isHugetlbControllerPresent`, `cgroupv1HasHugetlb`, and `cgroupv2HasHugetlb` detect hugetlb controller support. `IsCgroup2UnifiedMode` detects cgroup v2 by statfs. `WithCDI` injects CDI devices from CRI `CDIDevices` and legacy CDI annotations, deduplicating names.

## Control Flow

Detection helpers cache results with `sync.Once`. Swap detection checks `/sys/fs/cgroup/memory/memory.memsw.limit_in_bytes` on v1 or `memory.swap.max` under the current cgroup on v2. Hugetlb checks either `/sys/fs/cgroup/hugetlb` or `cgroup.controllers`. `WithCDI` gathers field-based devices first, parses annotations, appends unseen annotation devices, logs duplicates/deprecation, and delegates to CDI spec injection.

## State and Persistence Behavior

Only process-local cached booleans are stored. `WithCDI` mutates the in-memory OCI spec by adding device/mount/env/hook content from CDI specs.

## Dependencies and Integration Points

It depends on cgroups v3, Unix statfs, CDI libraries, CRI runtime types, containerd logging, and CRI CDI spec opts. Linux container spec construction invokes `WithCDI` through platform spec opts.

## Risks and Edge Cases

Cached controller detection may become stale if cgroup mounts change during process lifetime. `IsCgroup2UnifiedMode` panics if `/sys/fs/cgroup` cannot be statfs’d. Annotation parsing errors abort spec generation. Duplicate CDI devices are skipped silently at debug level.

## Test Signals

Tests should mock cgroup files where possible, validate CDI deduplication and annotation parsing errors, and assert spec mutation for field-based and annotation-based devices.
