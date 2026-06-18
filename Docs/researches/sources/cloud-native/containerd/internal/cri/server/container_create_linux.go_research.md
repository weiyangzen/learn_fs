# sources/cloud-native/containerd/internal/cri/server/container_create_linux.go

## Purpose

This Linux companion file supplies Linux-only spec options and snapshotter options used by container creation.

## Important APIs, Types, and Functions

`containerSpecOpts(config, imageConfig)` returns Linux-specific OCI spec options for platform spec application after rootfs mount. It handles supplemental group policy, image/user-derived additional groups, AppArmor, seccomp, and CDI enablement. `snapshotterOpts(config)` returns Linux snapshotter options derived from user namespace ID mappings.

## Control Flow

`containerSpecOpts` reads the Linux security context, derives the user string from run-as username, run-as UID, or image user, then applies supplemental-group policy. `Merge` adds image `/etc/group` groups plus requested supplemental groups; `Strict` adds only requested supplemental groups; unknown policies return an error. It generates AppArmor and seccomp profiles from current and deprecated fields, appends their spec opts when present, and either appends CDI injection or errors if CDI devices were requested while CDI is explicitly disabled. `snapshotterOpts` inspects user namespace mappings and builds snapshotter options so rootfs snapshots can be prepared with matching ID mappings.

## State and Persistence Behavior

Spec options mutate in-memory OCI specs. Snapshotter options influence snapshot creation state during container creation, especially user namespace/idmap behavior.

## Dependencies and Integration Points

It depends on CRI runtime types, image config, Linux security helpers, custom opts, containerd OCI/snapshot APIs, and CRI server configuration. `platformSpecOpts` in `container_create.go` calls this for Linux platforms.

## Risks and Edge Cases

Security option ordering matters because base spec defaults, CRI security context, and runtime config interact. User namespace ID mapping mistakes can make mounted rootfs or devices inaccessible. CDI annotation parsing can fail spec generation. Seccomp/AppArmor behavior depends on host support and configured defaults.

## Test Signals

Linux create tests should cover supplemental group policy, seccomp/AppArmor combinations, run-as user/group derivation for additional groups, CDI fields and annotations, CDI-disabled errors, and snapshotter idmap options.
