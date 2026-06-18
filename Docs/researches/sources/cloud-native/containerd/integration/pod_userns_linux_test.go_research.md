# sources/cloud-native/containerd/integration/pod_userns_linux_test.go

## Purpose

This Linux file validates pod/container user namespace support, idmapped host and image volumes, rootfs ownership, host network compatibility, a stdout/stderr permission regression, and volume copy-up behavior in user namespaces.

## Important APIs, Types, And Functions

- `supportsUserNS`, `supportsIDMap`, and `supportsRuncIDMap` gate tests by kernel/filesystem/runtime capability.
- `traversePath` adjusts temporary directory permissions so idmapped volume paths can be traversed.
- `TestPodUserNS` table-tests UID/GID maps, host network, rootfs permissions, idmapped host volumes, and rejection of multiple mappings.
- `TestIssue10598` validates non-root userns init processes can open `/dev/stdout` or `/dev/stderr` using Nginx startup logs.
- `TestUsernsVolumeCopyUp` validates image-defined volume copy-up contents, ownership, and host-path updates under user namespaces.

## Control Flow

Capability helpers check `/proc/self/ns/user`, clone a mount tree and apply `MOUNT_ATTR_IDMAP`, and inspect `runc features`. `TestPodUserNS` creates userns sandbox configs, starts short-lived containers that print maps or stat paths, and checks log output; volume cases pass ID mappings into mounts. `TestIssue10598` starts Nginx in a userns with SELinux options adjusted, then waits for startup logs while ensuring the container remains running. `TestUsernsVolumeCopyUp` starts the volume-copy-up image in a userns, discovers bind volume host paths via helpers from elsewhere, checks copied files and `stat` ownership inside the container, modifies a file inside the container, and verifies the host file changed.

## State And Persistence Behavior

The tests create user namespace mappings in CRI sandbox/container configs, idmapped mounts, temporary host volume directories, and container logs. Volume copy-up creates host-side volume directories populated from image-declared volumes and then mutates one file from inside the container.

## Dependencies And Integration Points

They integrate Linux user namespaces, mount idmapping syscalls, runc feature reporting, CRI user namespace fields, SELinux options, Nginx and volume-copy-up images, host volume mapping helpers, and BusyBox/stat commands.

## Risks And Edge Cases

Coverage is highly host-dependent: kernel, filesystem, runtime, pid/user namespace, and SELinux policy all matter. `traversePath` assumes the temp directory path is under `os.TempDir`. Multiple-mapping behavior is expected to fail but only checks that an error occurs.

## Test Signals

Passing confirms CRI user namespace configuration, idmapped rootfs/volumes, stdio permissions, and volume copy-up behavior work together on capable Linux hosts.
