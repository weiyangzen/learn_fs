# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/overmount_chroot_test.c

## Purpose
Regression test for chrooting into the topmost layer of a repeatedly overmounted mountpoint. It verifies overmount layers remain distinct and lower-layer files are hidden after chroot.

## Important APIs, Types, And Functions
Uses user and mount namespaces, `pivot_root`, tmpfs mounts, repeated `mount("tmpfs", "/newroot")`, `get_unique_mnt_id()`, `statmount_alloc()`, `chroot`, `chdir`, and `count_mounts()`. Helper `setup_root()` creates a tmpfs root and detaches the old root.

## Control Flow
The child enters a user namespace, unshares a private mount namespace, pivots to a tmpfs root, creates `/newroot`, mounts a base tmpfs there, writes a marker, then overmounts it five times, recording each mount id and marker. It verifies the visible `/newroot` is the topmost id, chroots into it, checks `/` has the same id, confirms only the topmost marker is visible, and verifies fs type `tmpfs`.

## State And Persistence
All mounts and files are in the child namespace after pivot_root. No persistent host state is intended.

## Dependencies And Integration Points
Requires user namespace helper, mount namespace privileges, tmpfs, pivot_root syscall, statmount/listmount helpers.

## Risks
Pivot-root and mount privileges are environment-sensitive. The test assumes lower-layer marker files are hidden by overmounts, so any unexpected path traversal behavior fails.

## Test Signals
Success signals include mount count increase, topmost mount-id equality before/after chroot, topmost marker present, lower markers absent, and statmount fs type `tmpfs`.
