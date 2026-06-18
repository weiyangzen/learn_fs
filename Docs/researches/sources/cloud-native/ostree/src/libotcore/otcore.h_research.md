# sources/cloud-native/ostree/src/libotcore/otcore.h

## Purpose
Private/shared otcore header for signature constants, crypto verification APIs, prepare-root helpers, root configuration, mount helpers, and runtime path/metadata constants.

## Important APIs, Types, And Functions
Defines ed25519 and SPKI signature metadata keys and variant types, ed25519 public key/signature sizes, max metadata size, `otcore_ed25519_init`, `otcore_validate_ed25519_signature`, `otcore_spki_init`, `otcore_validate_spki_signature`, command-line/config helpers, `RootConfig`, `otcore_load_rootfs_config`, `otcore_mount_rootfs`, `otcore_mount_boot`, and `otcore_mount_etc`.

The header also defines runtime and layout constants: `/run/ostree`, `/run/ostree/.private`, `PREPARE_ROOT_CONFIG_PATH`, deployment backing and overlay directory names, composefs names and lower mount path, prepare-root config keys, `/run/nextroot`, `/run/ostree-booted`, `/run/ostree/nextroot-booted`, and metadata keys for composefs, verity, signatures, transient roots, sysroot-ro, backing root device/inode, and transient `/etc`.

## Control Flow
No implementation flow is present, but it documents the call sequence used by prepare-root: parse cmdline/config into `RootConfig`, mount rootfs, mount boot, mount `/etc`, and publish runtime metadata for later sysroot/load code.

## State And Persistence Behavior
`RootConfig` owns composefs and transient-root settings plus signature key paths and loaded public keys. Constants describe transient `/run` state and deployment backing directories that must remain stable across prepare-root, sysroot, unlock, boot-complete, and soft-reboot code.

## Dependencies And Integration Points
Conditionally includes libsodium and OpenSSL headers, uses GLib/GIO, libglnx/otutil, and is included by libotcore sources and libostree sysroot code that consumes runtime metadata constants.

## Risks
Changing metadata key strings or paths breaks cross-component handoff. `RootConfig` ownership must match `otcore_free_rootfs_config`. Compile-time crypto feature macros select available signature backends.

## Test Signals
Compile coverage across feature combinations, metadata key compatibility tests, prepare-root/sysroot integration tests, and memory ownership tests for `RootConfig` are useful.
