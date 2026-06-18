# sources/cloud-native/composefs-rs/crates/composefs/src/mount.rs

## Purpose
This module implements composefs mounting through the modern Linux mount API. It creates detached EROFS mounts from image files, configures overlayfs with composefs data layers and fs-verity options, and exposes a final mount fd that callers can attach with `move_mount`.

## Important APIs, Types, and Functions
`FsHandle` owns a filesystem context fd from `fsopen()` and implements `AsFd`. `mount_at()` moves a detached mount to a target path. `erofs_mount()` prepares an image and mounts it read-only as EROFS. `MountOptions` stores optional overlay upper/work dirs and read-write mode, with `set_overlay()` and `set_read_write()`. `composefs_fsmount()` builds the EROFS lower mount, opens an overlayfs context, configures source/metacopy/redirect_dir/verity/upper/work/lower/data options, creates the filesystem, and returns an `fsmount()` fd.

## Control Flow
The EROFS path calls `make_erofs_mountable()`, configures `ro` and `source=/proc/self/fd/N`, runs `fsconfig_create()`, then `fsmount()`. Composefs mounting first calls `prepare_mount()` on the EROFS mount for kernel compatibility. It configures overlayfs source as `composefs:{name}`, enables metacopy and redirect_dir, optionally requires verity, optionally supplies upperdir and workdir, sets lower and data fds through compatibility helpers, finalizes the config, and chooses read-only mount attributes unless `read_write` is set.

## State and Persistence Behavior
Mount operations create kernel mount state, not repository files. `mount_at()` attaches a detached mount into the namespace. `FsHandle::drop()` drains kernel diagnostic messages from the fs context fd and prints them to stderr as a local lint exception.

## Dependencies and Integration Points
This module depends on `rustix::mount`, `rustix::path`, `mountcompat` helpers for kernel-version differences, and `proc_self_fd()`. It is the runtime consumer of EROFS image outputs and repository object directories and integrates with overlayfs fs-verity enforcement through the `verity=require` option.

## Risks and Edge Cases
The modern mount API requires sufficiently new kernels and privileges; compatibility helpers cover some but not all environment constraints. `FsHandle::drop()` printing can surprise library users but is justified for otherwise lost kernel diagnostics. `MountOptions::set_read_write(true)` only makes sense with a writable overlay; without upper/work dirs, kernel config may fail. `enable_verity` must match object-store integrity expectations or composefs mounts may reject data.

## Test Signals
No direct tests appear in this file. Confidence comes from integration or privileged tests elsewhere. Useful test coverage would mock or isolate fsconfig sequences, validate option emission under feature flags, and exercise read-only/read-write overlay combinations on supported kernels.
