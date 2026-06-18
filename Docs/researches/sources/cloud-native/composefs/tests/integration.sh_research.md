# sources/cloud-native/composefs/tests/integration.sh

## Purpose
`integration.sh` is a privileged end-to-end test that builds composefs images from real and generated trees, mounts them with `mount.composefs`, and compares mounted output with source dumps.

## Important APIs, Types, And Functions
Main function `run_test` creates images with `mkcomposefs`, validates digest consistency, optionally runs `fsck.erofs`, mounts with `mount.composefs`, dumps source and mount with `dumpdir`, compares them, re-measures digest from mount, and unmounts.

## Control Flow
It optionally creates an ext4 verity loopback filesystem, initializes object/root/temp dirs, tests `/usr/bin`, checks fsverity support, generates a random privileged tree without whiteouts, and tests it with normalized root nlink.

## State And Persistence
It writes under `${cfsroot}` or `/composefs`, creates images, objects, temp dirs, mounts, and may create a temporary ext4 loopback disk.

## Dependencies And Integration Points
Depends on built tools, root/kernel mount permissions, optional `fsck.erofs`, `fsverity`, `mkfs.ext4`, and helper scripts.

## Risks
Destructive cleanup removes `${cfsroot}/tmp`; default `/composefs` must be safe in the test environment. Requires privileges and kernel features, so it is not a hermetic unit test.

## Test Signals
Strong end-to-end signal for digest stability, mount correctness, object store integration, and source/mount metadata equivalence.
