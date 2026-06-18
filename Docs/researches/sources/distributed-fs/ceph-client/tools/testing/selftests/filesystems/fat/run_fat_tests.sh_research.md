# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/run_fat_tests.sh

## Purpose

`run_fat_tests.sh` creates a tiny vfat filesystem image, mounts it through a loop device, and verifies `RENAME_EXCHANGE` for files in the same directory and across a subdirectory.

## Important APIs, Types, and Functions

Shell helpers are `cleanup`, `create_loopback`, `mount_image`, `rename_exchange_test`, `rename_exchange_subdir_test`, and `unmount_image`. The script uses `mktemp`, `truncate`, `mkfs.vfat`, `sudo mount -o loop`, `tee`, the compiled `rename_exchange` helper, `sync -f`, `grep`, and `sudo umount`.

## Control Flow, State, and Persistence

With `set -euo pipefail`, any failed command aborts. A temporary directory holds `fat.img` and mountpoint `mnt`. Cleanup is trapped for signals and exit, unmounting if still mounted and removing the temp tree. After formatting and mounting, the script writes `old` and `new` file contents, performs an exchange, syncs the mount, and checks that path contents swapped. The subdir variant repeats with the new file inside `subdir`. Persistent state is limited to the temporary image and mounted filesystem, removed at exit.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `mkfs.vfat`, loop device support, sudo privileges, vfat kernel support, and the helper binary path relative to the script. Risks include sudo prompts in automation, unavailable loop devices, `chattr +C` being best-effort, and cleanup depending on mountpoint detection. Passing signals are successful mount, both exchange operations, synced data, and grep confirming swapped contents.
