# File Research: sources/cow-pools/nilfs-utils/include/pathnames.h

Centralized path constants borrowed from historical util-linux/BSD style headers. It defines default executable paths, login/account paths, mount files, `/proc` files, device directories, loop device prefix, and udev symlink directories.

NILFS code uses this primarily for mount tables and proc mount paths: `_PATH_MOUNTED`, `_PATH_PROC_MOUNTS`, and related constants.
