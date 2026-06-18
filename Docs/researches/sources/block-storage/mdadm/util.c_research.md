# File Research: sources/block-storage/mdadm/util.c

## Purpose
Large shared utility module for mdadm. It covers md ioctl wrappers, device and partition helpers, metadata-supertype dispatch, mdmon/systemd integration, cluster library hooks, sizing/layout utilities, random IDs, file descriptor handling, and miscellaneous checks.

## Main Responsibilities
- Provides wrappers for md array/disk ioctls and sysfs fallbacks.
- Parses sizes, layouts, cluster-confirm args, mdadm/Linux version strings, major/minor strings, and RAID10/faulty layouts.
- Checks whether enough disks are available for different RAID levels.
- Detects existing ext2, reiserfs, RAID, MBR, and GPT signatures/partition overlap.
- Opens block devices by path or major:minor using temporary device nodes.
- Maps md device names to device IDs and validates md device names.
- Maintains the global `superlist` of metadata handlers: `super0`, `super1`, DDF, IMSM, MBR, GPT.
- Guesses metadata type, duplicates supertype state, opens subarrays, and maps metadata strings to superswitches.
- Gets device size and sector size.
- Adds/removes disks through sysfs for external metadata or ioctls for native arrays.
- Starts and waits for `mdmon`, with systemd delegation first and direct execution fallback.
- Handles metadata update queues for monitor communication.
- Loads DLM and corosync cmap hooks dynamically for clustered md.
- Provides zeroing, sleep, directory/file checks, md module loading, and md module parameter setup.

## Integration
This is a central dependency for the mdadm codebase. It ties together:
- `super0.c`/`super1.c` and other metadata backends;
- `sysfs.c` for modern kernel control;
- mdmon monitor/control socket paths;
- systemd service templates;
- cluster libraries loaded with `dlopen`;
- test and create/assemble/manage/grow operations.

## Notable Behavior
- `super_by_fd()` derives metadata version from sysfs, including external-subarray container resolution.
- `guess_super_type()` probes all registered metadata loaders and chooses the newest creation time.
- `continue_via_systemd()` forks and runs `systemctl restart <service>@<dev>.service`, then falls back to direct daemon startup if needed.
- `init_md_mod()` loads `md_mod` if absent and sets `legacy_async_del_gendisk` behavior for newer kernels.

## Risks and Edge Cases
- Many helpers operate on real block devices and can create temporary block nodes or issue destructive ioctls.
- Dynamic cluster hooks can leave allocated hook structs even when `dlopen` or `dlsym` partially fails.
- `open_dev()` forces `O_DIRECT`, which affects callers expecting buffered IO.
- Partition-table parsing manually reads MBR/GPT structures and depends on sector-size conversion.
