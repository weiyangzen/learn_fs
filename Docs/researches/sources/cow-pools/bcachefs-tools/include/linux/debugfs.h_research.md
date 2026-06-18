# File Research: sources/cow-pools/bcachefs-tools/include/linux/debugfs.h

This header declares a tiny debugfs interface: `debugfs_create_file()`, `debugfs_create_dir()`, `debugfs_remove()`, and `debugfs_remove_recursive()`. It includes file, seq-file, type, and compiler compatibility headers.

The declarations let kernel-origin code expose debugfs-like nodes in bcachefs-tools. Behavior and storage are implemented elsewhere.
