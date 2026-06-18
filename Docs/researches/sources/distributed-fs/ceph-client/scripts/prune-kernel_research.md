<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/prune-kernel -->
# sources/distributed-fs/ceph-client/scripts/prune-kernel

## Purpose

`prune-kernel` removes installed kernel boot and module artifacts for supplied kernel release strings, while preserving the running kernel and kernels owned by RPM packages.

## Important APIs, Types, and Functions

The script loops over command-line release names. For each release it checks `rpm -qf /lib/modules/<release>` and compares against `uname -r`.

## Control Flow

For removable releases it deletes `/boot/initramfs-<release>.img`, `/boot/System.map-<release>`, `/boot/vmlinuz-<release>`, `/boot/config-<release>`, and `/lib/modules/<release>`, then calls `new-kernel-pkg --remove` or `kernel-install remove` when available.

## State and Persistence Behavior

It intentionally mutates system boot/module locations by deleting files. There is no automatic restore.

## Dependencies and Integration Points

It depends on Bash, `rpm`, `uname`, `rm`, and optionally `new-kernel-pkg` or `kernel-install`. It is a local maintenance helper outside the normal Kbuild compile path.

## Risks and Edge Cases

Deletion is destructive and targets absolute system paths. It assumes RPM ownership is the right preservation signal and may be unsafe on non-RPM systems. It must not be run with release names the user still needs.

## Test Signals

Test on a disposable root or container with fake release names, RPM-owned module directories, the running kernel release, and optional `kernel-install` hooks. Verify only intended boot/module paths are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/prune-kernel -->
