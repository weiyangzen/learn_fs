# File Research: sources/block-storage/util-linux/sys-utils/mountpoint.c

This file implements `mountpoint(1)`, checking whether a path is a mountpoint or printing device numbers. It supports quiet mode, no-follow symlink behavior, filesystem device number output, block-device major:minor output, and `--show` to print the mountpoint for a path.

The primary check is `dir_to_device()`. On systems with statmount support it first uses `mnt_id_from_path()` and `mnt_fs_fetch_statmount()` to compare the kernel-reported mountpoint with the requested path and to obtain the filesystem device number. Otherwise it falls back to parsing `/proc/self/mountinfo` with libmount and finding a target match. If mountinfo is unavailable, it uses the traditional parent-directory stat heuristic, which cannot detect bind mounts.

`--devno` validates that the path is a block device and prints `st_rdev`. `--show` requires statmount support in this implementation. Exit status uses `32` for “not a mountpoint,” matching the utility’s historical behavior.
