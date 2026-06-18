
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_other.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_other.go

## Purpose

This non-Linux, non-Windows helper file supplies simple fallback implementations for platform hooks required by the shared CRI server code.

## Important APIs, Types, and Functions

It defines `openLogFile`, `ensureRemoveAll`, `modifyProcessLabel`, and `isUnifiedCgroupsMode` for platforms matching `!windows && !linux`.

## Control Flow

`openLogFile` opens or creates the target path in append-write mode with `0640` permissions but does not create parent directories. `ensureRemoveAll` delegates directly to `os.RemoveAll`. `modifyProcessLabel` is a no-op, and `isUnifiedCgroupsMode` always returns false.

## State and Persistence Behavior

The only mutations are log file creation/opening and recursive filesystem removal through the standard library. No CRI store or runtime state is touched.

## Dependencies and Integration Points

The file depends on context, os, and OCI specs. It keeps the shared CRI server package buildable on unsupported Unix-like platforms where Linux security, mount, and cgroup behavior does not apply.

## Risks and Edge Cases

Unlike Linux, parent directories are not created before opening logs. Removal has no busy-mount handling. Returning false for unified cgroups and leaving labels unchanged are conservative but may omit platform capabilities if a future non-Linux platform gains equivalents.

## Test Signals

Platform-specific tests should verify log open behavior, parent-directory expectations, nonexistent-path removal, and no-op process label semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_other.go -->
