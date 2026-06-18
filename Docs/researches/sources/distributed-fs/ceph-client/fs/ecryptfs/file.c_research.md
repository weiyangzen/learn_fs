# sources/distributed-fs/ceph-client/fs/ecryptfs/file.c

## Purpose

`file.c` implements eCryptfs file operations for regular files and directories. It opens and releases lower files, initializes or reads encryption metadata at open time, forwards generic reads/writes/mmap/fsync/ioctl/fasync behavior to lower or generic VFS helpers, and translates encrypted lower directory names back to upper plaintext names during readdir.

## Important APIs, types, and functions

The exported operation tables are `ecryptfs_dir_fops` and `ecryptfs_main_fops`. Important functions include `ecryptfs_read_update_atime()`, `ecryptfs_splice_read_update_atime()`, `ecryptfs_readdir()`, `ecryptfs_filldir()`, `read_or_initialize_metadata()`, `ecryptfs_open()`, `ecryptfs_dir_open()`, `ecryptfs_flush()`, `ecryptfs_release()`, `ecryptfs_dir_release()`, `ecryptfs_fsync()`, and ioctl forwarding helpers. `struct ecryptfs_getdents_callback` wraps a lower `dir_context` with upper caller state.

## Control flow

Regular open allocates `struct ecryptfs_file_info`, marks policy as applied/encrypted if not already set, obtains the per-inode lower file through `ecryptfs_get_lower_file()`, rejects writable upper opens when the cached lower file is read-only, stores the lower file in upper private data, and calls `read_or_initialize_metadata()`. Metadata initialization first returns early when policy and key are already valid, otherwise calls `ecryptfs_read_metadata()`. If metadata read fails and plaintext passthrough is enabled, it clears encrypted state. If the lower file is empty and header metadata mode is active, it calls `ecryptfs_initialize_file()` to write a new header.

Directory open allocates file private data and opens the lower path directly with current credentials. Directory readdir calls `iterate_dir()` on the lower file with `ecryptfs_filldir()` as the actor. Each lower name is decoded/decrypted through `ecryptfs_decode_and_decrypt_filename()` before being emitted to the upper caller; malformed plaintext lower names under filename encryption are skipped/masked for common mixed-directory cases.

Regular reads use generic page-cache reads plus lower atime updates. Writes use `generic_file_write_iter()`, relying on eCryptfs address-space operations in `mmap.c` and lower I/O helpers for encryption. `fsync`, `flush`, selected ioctls, compat ioctls, and fasync are forwarded to the lower file when supported.

## State and persistence behavior

The file owns per-open `struct ecryptfs_file_info` and references the per-inode cached lower file. Persistent changes happen indirectly through metadata initialization and writeback, not through this file alone. It synchronizes lower atime after successful upper reads and copies lower attributes after selected ioctls.

## Dependencies and integration points

It depends on generic VFS file helpers, lower path helpers from `ecryptfs_kernel.h`, metadata and filename functions from `crypto.c`, inode initialization from `inode.c`, lower-file lifetime functions from `main.c`, and address-space operations declared externally. Inode interposition in `inode.c` installs these operation tables based on file type.

## Risks

Open-time metadata failures determine whether a file is usable, initialized, or treated as plaintext passthrough; regressions here can either deny valid files or expose plaintext unexpectedly. Directory listing intentionally masks some filename-decode errors, so tests must distinguish harmless lower plaintext names from real corruption. Lower file reference counting must remain balanced between `ecryptfs_get_lower_file()` and release. Ioctl forwarding is intentionally restricted; adding commands can expose lower filesystem behavior not meaningful for encrypted upper files.

## Test signals

Tests should cover regular open for existing encrypted files, empty-file initialization, plaintext passthrough mounts, read-only lower mounts, directory listing with encrypted names, mixed lower plaintext entries, read/splice atime propagation, fsync/flush forwarding, selected ioctls, mmap support rejection when lower mmap is unavailable, and lower file reference cleanup on failed opens.
