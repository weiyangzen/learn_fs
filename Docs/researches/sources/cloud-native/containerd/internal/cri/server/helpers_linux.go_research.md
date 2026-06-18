
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_linux.go

## Purpose

This Linux-specific helper file provides Linux implementations for security feature checks, container log opening, robust recursive removal with mount cleanup, SELinux label adjustment for VM-based runtimes, cgroup mode detection, and user-namespace snapshot remap options.

## Important APIs, Types, and Functions

Key functions are `(*criService).apparmorEnabled`, `(*criService).seccompEnabled`, `openLogFile`, `unmountRecursive`, `ensureRemoveAll`, `isVMBasedRuntime`, `modifyProcessLabel`, `isUnifiedCgroupsMode`, and `snapshotterRemapOpts`. The `vmbasedRuntimes` list currently recognizes Kata-style runtime type substrings.

## Control Flow

AppArmor returns false when disabled in config and otherwise delegates to host support detection. Seccomp delegates to runtime support detection. `openLogFile` creates parent directories and opens append-only logs with mode `0640`. `unmountRecursive` canonicalizes a target, finds all mounts under it, sorts deepest first, and uses detached unmounts. `ensureRemoveAll` first attempts recursive unmount, then retries `os.RemoveAll`, treating subpath `ENOENT` races as retryable and attempting detached unmount on `EBUSY` paths up to 50 times.

`modifyProcessLabel` leaves non-VM runtimes unchanged; VM-based runtimes convert the SELinux process label to a KVM label. `snapshotterRemapOpts` parses user namespace mappings and, for pod user namespace mode, emits `containerd.WithRemapperLabels`.

## State and Persistence Behavior

The file performs filesystem mutations through directory creation, log file creation, unmounts, and recursive removal. It does not persist CRI store state. Snapshotter remap options are returned to callers for snapshot metadata labeling.

## Dependencies and Integration Points

Dependencies include Linux cgroups, mountinfo, containerd mount helpers, snapshots options, AppArmor/seccomp helpers, SELinux utilities, CRI runtime API, and OCI specs. The functions are used by container lifecycle cleanup, log setup, sandbox/container security setup, and user namespace snapshot handling.

## Risks and Edge Cases

`ensureRemoveAll` is intentionally aggressive and can hide transient cleanup races, but wrong target paths would be destructive. Detached unmounts may defer cleanup. VM runtime detection is substring-based. Snapshot remapping supports only the single mapping line allowed by shared userns parsing. Security feature probes depend on host capabilities and configuration.

## Test Signals

Existing shared tests cover `ensureRemoveAll` for nonexistent paths, directories, and files. Stronger Linux-specific signals would include mount cleanup with busy mounts, AppArmor disabled config, SELinux KVM relabeling, cgroup v1/v2 detection, and remapper label output for pod user namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_linux.go -->
