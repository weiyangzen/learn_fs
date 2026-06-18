# sources/cloud-native/composefs/libcomposefs/lcfs-mount.c

## Purpose
`lcfs-mount.c` mounts composefs images by first mounting the embedded EROFS image and then overlaying it with one or more object directories as data lowerdirs. It supports digest verification, idmapped EROFS mounts, new Linux mount APIs, legacy mount fallback, and loop-device fallback.

## Important APIs, Types, And Functions
Public entry points are `lcfs_mount_fd` and `lcfs_mount_image`. Private state is `struct lcfs_mount_state_s`. Helpers wrap `fsopen`, `fsconfig`, `fsmount`, `move_mount`, and optionally `mount_setattr`. Major functions are `lcfs_validate_mount_options`, `lcfs_validate_verity_fd`, `setup_loopback`, `compute_lower`, `lcfs_mount_erofs`, `lcfs_mount_ovl`, `lcfs_mount_ovl_legacy`, and `lcfs_mount_erofs_ovl`.

## Control Flow
Options are validated first, including flags, objdirs, upper/workdir pairing, digest parsing, and idmap fd. If an expected digest is configured, the image fd is measured with kernel fs-verity and compared. The composefs header is read; valid EROFS images mount into a temporary image mountdir. Overlayfs is then mounted over the target with metacopy, redirect_dir, lowerdir/datadir entries, optional upper/workdir, optional verity, and readonly flags. New mount API failures caused by unsupported features fall back to legacy comma-escaped mount options.

## State And Persistence
It creates transient mounts, optional temporary directories, and loop devices with autoclear. It does not alter image contents. Digest expectations are parsed into `expected_digest`.

## Dependencies And Integration Points
It depends on Linux mount, loop, fsverity, and syscall interfaces; internal endian/header helpers; and `digest_to_raw`. CLI mount tooling wraps these APIs.

## Risks
Mount behavior is kernel-version-sensitive. Legacy overlay option construction depends on correct comma escaping. `expected_digest_len` can parse non-32-byte hex strings but comparison uses `LCFS_DIGEST_SIZE`, so callers should pass full SHA-256 strings. Temporary mount cleanup uses detached unmount and rmdir.

## Test Signals
`test-units.sh` checks digest mismatch and valid digest behavior. `integration.sh` mounts real images. Random FUSE tests cover a related user-space path, while kernel mount coverage depends on privileges and host support.
