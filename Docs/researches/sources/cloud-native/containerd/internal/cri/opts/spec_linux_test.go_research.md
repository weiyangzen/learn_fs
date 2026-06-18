# sources/cloud-native/containerd/internal/cri/opts/spec_linux_test.go

## Purpose

This test file validates selected Linux spec option behavior: supplemental group merging, OOM score restriction, and cgroup namespace-related mount options.

## Important APIs, Types, and Functions

`TestMergeGids` checks sorted de-duplicated GID merging. `TestRestrictOOMScoreAdj` checks preferred OOM score clamping against the daemon score. `TestWithMountsCgroupNamespaceOptions` checks mount generation when cgroup namespace options vary.

## Control Flow

The tests construct inputs, call the helper/spec option, and assert expected values in returned slices or generated OCI specs. They use Linux-only package access to unexported helpers.

## State and Persistence Behavior

OOM tests read `/proc/self/oom_score_adj` indirectly. Mount tests rely on mocked or controlled OS interfaces rather than changing real host mounts.

## Dependencies and Integration Points

The tests target `spec_opts.go` and `spec_linux_opts.go`, using CRI runtime config and OCI spec structures.

## Risks and Edge Cases

Coverage is focused and does not cover all mount propagation, devices, resources, CDI, or SELinux paths. OOM expectations depend on the current process OOM score.

## Test Signals

Passing tests signal stable group merging, safe OOM clamping, and correct cgroup mount options under tested namespace conditions.
