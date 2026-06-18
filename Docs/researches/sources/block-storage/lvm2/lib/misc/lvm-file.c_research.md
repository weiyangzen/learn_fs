# File Research: sources/block-storage/lvm2/lib/misc/lvm-file.c

This file implements filesystem utility helpers for temporary files, NFS-safe rename, path checks, recursive directory creation, directory sync, fcntl locks, fclose diagnostics, and stat timestamp extraction.

Main entry points:
- `create_temp_name()`: creates `.lvm_hostname_pid_num` temp file with `O_EXCL` and grabs an fcntl write lock.
- `lvm_rename()`: creates a hard link to destination and checks link count before unlinking source.
- `path_exists()`, `dir_exists()`, `dir_create_recursive()`.
- `sync_dir()`: fsyncs containing directory.
- `fcntl_lock_file()`, `fcntl_unlock_file()`.
- `lvm_fclose()`: reports write errors after stream close.
- `lvm_stat_ctim()`.

Dependencies:
- POSIX file APIs, `dm_prepare_selinux_context()`, `dm_create_dir()`, project logging.

Correctness notes:
- Temp file generation sanitizes `/` in hostname.
- `lvm_rename()` is designed not to overwrite an existing destination and to work safely on NFS.
- Recursive directory creation walks slash-separated prefixes.
- `sync_dir()` tolerates `EROFS` and `EINVAL`.
- `fcntl_lock_file()` creates parent directory before opening/locking.

Risks:
- Temp file generation tries only 20 candidates.
- `fcntl_lock_file()` opens lock files mode `0777`, relying on umask and context.
