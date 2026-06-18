<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux.go -->
# sources/cloud-native/cri-o/server/container_create_linux.go

## Purpose

This file implements Linux-specific container creation helpers for runtime creation, user namespace mapping, bind mounts, image and artifact volume mounts, cgroup/sysfs/systemd mounts, AppArmor, blockio, devices, and base spec generation.

## Important APIs, Types, and Functions

`createContainerPlatform` creates the runtime container and makes bundle/mount paths executable for mapped root. `finalizeUserMapping` remaps process user IDs into user namespaces. `setContainerConfigSecurityContext`, `newLinuxContainerSecurityContext`, and `getSpecGen` initialize Linux spec defaults. `addOCIBindMounts` is the main CRI mount translator. `mountArtifact`, `FilterMountPathsBySubPath`, `mountImage`, and `ensureImageVolumesPath` implement image/artifact volume support. `setupSystemdMounts`, `addSysfsMounts`, `addShmMount`, `specSetApparmorProfile`, `specSetBlockioClass`, and `specSetDevices` complete platform-specific spec configuration.

## Control Flow

Mount setup sorts CRI mounts by path depth, removes default mounts shadowed by user `/dev` or `/sys`, reads host mount propagation data, optionally prepares a clean shared `image-volumes` directory, then iterates CRI mounts. Image mounts prefer OCI artifact mounts when enabled and fall back to mounted storage images; host mounts resolve symlinks, reject dangerous absent paths, create missing sources when not restoring, apply propagation rules, enforce recursive read-only constraints, optionally relabel for SELinux, validate ID-mapped mount runtime support, and return OCI mount specs. If `/sys` was not explicitly mounted, it adds a cgroup mount with RO/RW based on cgroup v2 annotation. Systemd setup adds tmpfs mounts, writable cgroup v2 mount or systemd cgroup bind, and `container=crio`.

## State and Persistence Behavior

This file mutates the OCI spec generator and may write files/directories: FIPS disabling writes `sysctl-fips`, missing host paths are created, image volume root is created and checked for emptiness, storage images are mounted, safe subpath mounts are opened, SELinux labels may be applied, and bundle/mount paths may have execute bits widened for mapped root access. Safe mounts are returned for caller cleanup.

## Dependencies and Integration Points

It depends on Linux cgroup detection, runtime feature probes for ID-mapped and recursive read-only mounts, containers/storage mounts, runtime-tools `generate`, OCI artifact store, image status/signature checks, device annotations, AppArmor config, Intel goresctrl blockio, sandbox annotations, CRI mount fields, and the internal container factory/spec APIs.

## Risks and Edge Cases

Risks cluster around mount safety and runtime feature mismatches. Recursive read-only requires runtime support, read-only source, and private propagation. Image volume overlay lowerdir construction depends on a clean shared lower path. Artifact subpaths must exist and are rewritten relative to the requested subpath. `ensureImageVolumesPath` rejects a non-empty directory, so stale files can block creation. `isSubDirectoryOf` intentionally checks whether the storage root is under a requested host path to force host-to-container propagation. SELinux relabels are skipped for SPC types and may be optional via annotation. User namespace remapping is skipped when default ID mappings are configured.

## Test Signals

The Linux tests cover `/dev` and `/sys` default mount filtering, recursive read-only success and error cases, cgroup RW/RO option selection, idmapped mount support errors, and `isSubDirectoryOf`. Remaining high-value coverage includes artifact and image volume mounts, safe subpath cleanup, SELinux relabel modes, systemd mount choices, AppArmor failure paths, and read-only root tmpfs injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/container_create_linux.go -->
