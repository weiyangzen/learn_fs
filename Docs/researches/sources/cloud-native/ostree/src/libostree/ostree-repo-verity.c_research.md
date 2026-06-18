# sources/cloud-native/ostree/src/libostree/ostree-repo-verity.c

## Purpose

This file handles repository fs-verity configuration and enabling. It parses repo config into desired support levels, enables fs-verity on temporary files before they become objects, and ensures fs-verity on existing regular files when requested.

## Important APIs, Types, and Functions

- `_ostree_repo_parse_fsverity_config()` reads modern `[integrity]` `composefs` and `fsverity` tristate keys, plus legacy `[ex-fsverity]` boolean keys.
- `_ostree_fsverity_enable()` is the low-level `FS_IOC_ENABLE_VERITY` ioctl wrapper.
- `_ostree_tmpf_fsverity_core()` reopens a tmpfile read-only and attempts fs-verity based on requested support.
- `_ostree_tmpf_fsverity()` applies repo-level wanted/supported caching and required-versus-opportunistic behavior.
- `_ostree_ensure_fsverity()` enables fs-verity on an existing path if it is a regular file.

## Control Flow

Config parsing sets compile-time support to maybe or no depending on `HAVE_LINUX_FSVERITY_H`. Composefs implies a default fs-verity setting of maybe unless explicitly disabled. If modern fsverity is not enabled, legacy required/opportunistic booleans are used. Requiring fs-verity while compiled without support fails early.

The ioctl wrapper prepares `struct fsverity_enable_arg` with SHA256, block size 4096, optional signature bytes, and no salt. `ENOTTY` and `EOPNOTSUPP` mean unsupported and are not fatal. `EEXIST` is allowed only when the caller requested `allow_existing`.

Temporary-file enabling first checks the repo desired state. Required mode fails if cached support is known no. Maybe mode attempts the ioctl; if unsupported, it caches `fs_verity_supported` as no under `txn_lock` to avoid repeated ioctls. Success caches yes. Existing-file ensuring stats the path, optionally ignores missing files, skips non-regular files, opens regular files read-only, calls the ioctl allowing existing verity, and fails if required support is unavailable.

## State and Persistence Behavior

The persistent effect is the filesystem fs-verity flag and Merkle tree metadata maintained by the kernel for regular files. Repo in-memory fields `fs_verity_wanted` and `fs_verity_supported` cache policy and observed filesystem support. Config is read but not written here. Optional signatures can be passed into the ioctl for signed fs-verity files.

## Dependencies and Integration Points

The file depends on Linux `fsverity.h` when available, `ioctl()`, libglnx tmpfile helpers, OSTree repo-private feature support enums, config parsing helpers, and fd-relative filesystem utilities. It integrates with object writing paths that operate on `GLnxTmpfile` and with composefs/integrity policy.

## Risks and Edge Cases

Support can vary by filesystem and kernel, so caching unsupported status is important but also means a repo object path moving across filesystems would need careful handling. Required mode must fail closed. Opportunistic mode should not turn unsupported ioctls into hard errors. Block size and hash algorithm are currently fixed. Non-regular files are skipped. Build configurations without `HAVE_LINUX_FSVERITY_H` must never reach required runtime enabling.

## Test Signals

Tests should cover config precedence between composefs, modern fsverity, and legacy ex-fsverity keys; build-without-header behavior; required versus maybe versus no policy; unsupported ioctl handling; existing verity with `EEXIST`; missing path handling with `allow_enoent`; non-regular-file skipping; signature pointer plumbing; and support-cache transitions under repeated tmpfile writes.
