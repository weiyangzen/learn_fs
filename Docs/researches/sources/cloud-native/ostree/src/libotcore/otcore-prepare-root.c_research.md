# sources/cloud-native/ostree/src/libotcore/otcore-prepare-root.c

## Purpose
Implements shared early-boot root preparation helpers: parse kernel command lines, load prepare-root config, determine OSTree boot targets, mount `/boot`, mount `/etc`, and optionally mount composefs-backed root filesystems with verity/signature validation and runtime metadata emission.

## Important APIs, Types, And Functions
Public functions are `otcore_find_proc_cmdline_key`, `otcore_get_ostree_target`, `otcore_load_config`, `otcore_free_rootfs_config`, `otcore_load_rootfs_config`, `otcore_mount_boot`, `otcore_mount_etc`, and `otcore_mount_rootfs`. Internal composefs-enabled helpers include `load_variant`, `get_base_digest_for_bootc_commit`, `load_commit_for_deploy`, `validate_signature`, and `composefs_error_message`.

## Control Flow
Cmdline parsing scans space-separated arguments for exact `key=` matches or Android boot keys. `otcore_get_ostree_target` prefers Android A/B slot information, falls back to non-A/B Android default, then to the normal `ostree=` argument. `otcore_load_config` overlays config from `usr/lib/<filename>` and `etc/<filename>`. `otcore_load_rootfs_config` reads root transient flags, composefs mode (`true`, `false`, `maybe`, `verity`, `signed`), key path, optional public keys, and cmdline overrides.

`otcore_mount_boot` bind-mounts physical `/boot` into a deployment only when `/boot/loader` shows boot is on the physical root and the deployment has a `boot` directory. `otcore_mount_etc` either creates a transient overlay for `/etc` backed by `/run/ostree/transient-etc.*` or bind-remounts deployment `etc` writable. `otcore_mount_rootfs` records the backing deployment device/inode and root transient flags, then if composefs is compiled and enabled it prepares libcomposefs options, optional transient upper/work dirs, validates ed25519 commit signatures and composefs digest when requested, mounts `.ostree.cfs`, records composefs metadata, or tolerates a missing image only in `maybe` mode.

## State And Persistence Behavior
The code reads `/proc/cmdline`-style input, config from deployment `usr/lib` and `etc`, public key files, and OSTree commit/commitmeta objects. It writes no durable config, but creates runtime mount state, `/run/ostree` temporary overlay directories, private composefs lower mount directories, and metadata entries such as backing root device/inode, composefs usage, verity, signature key, transient root, transient-ro root, and transient `/etc` path.

## Dependencies And Integration Points
Integrates with GLib key files and variants, libglnx, Linux mount API, OSTree commit object formats, otcore ed25519 verification, libcomposefs when compiled, bootc commit metadata conventions, Android boot command-line conventions, and ostree-prepare-root/boot-complete runtime metadata consumers.

## Risks
This code runs in sensitive early-boot contexts. Incorrect cmdline parsing can choose the wrong deployment. Transient root and transient-ro are mutually exclusive except that transient-ro implies transient. Composefs signature validation requires commitmeta and public keys; bootc-imported commits may require base commit fallback. Mount failures can leave partial runtime directories. `load_variant` reads object files directly and assumes correct object path/digest conventions without linking libostree.

## Test Signals
Tests should cover cmdline parsing for normal OSTree, Android A/B, non-A/B Android, invalid slot suffixes, config precedence, composefs mode parsing and cmdline overrides, missing/empty public key files, good/bad ed25519 signatures, bootc base commit fallback, missing composefs image in maybe/yes modes, transient root directory creation, `/etc` overlay metadata, and `/boot` bind-mount conditions.
