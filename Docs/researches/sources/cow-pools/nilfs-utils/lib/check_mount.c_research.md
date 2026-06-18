# File Research: sources/cow-pools/nilfs-utils/lib/check_mount.c

Implements mounted-device detection. It scans `_PATH_MOUNTED`, compares mount source path strings, block device `st_rdev`, regular file device/inode pairs, and loop device backing files read from `/sys/dev/block/<maj>:<min>/loop/backing_file`.

Return semantics are documented as 1 if mounted, 0 if not mounted, and -1 on error. It handles loop-mounted disk images, which is important for tools operating on NILFS images.
