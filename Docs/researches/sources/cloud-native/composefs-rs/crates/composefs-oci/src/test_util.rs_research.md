# sources/cloud-native/composefs-rs/crates/composefs-oci/src/test_util.rs

## Purpose
This file provides test utilities for building deterministic OCI images and filesystems from composefs dumpfile strings. It is the fixture layer for integration and unit tests that need realistic multi-layer container images, bootable OS images, SELinux policy content, xattrs, deduplication behavior, and generated EROFS references.

## Important APIs, Types, and Functions
`dumpfile_to_tar()` converts composefs dumpfile lines into tar bytes. `create_multi_layer_image()` imports each dumpfile layer, builds OCI config and manifest objects, stores config splitstreams with named layer refs, and writes a tagged manifest. `TestImage` returns manifest digest, manifest verity, and config digest. The builder API is `OsImage` with `minimal()`, `bootable()`, `with_selinux()`, `with_layer()`, `build_oci()`, and `build_filesystem()`. Compatibility helpers include `create_base_image()`, `create_bootable_image()`, `create_test_oci_image()`, `create_test_bootable_oci_image()`, `ensure_erofs_for_image()`, and test-only `build_oci_layout()`.

## Control Flow
`dumpfile_to_tar()` parses each non-empty dumpfile line, skips root, strips leading slash for tar paths, collects xattrs, and creates directory, regular file, or symlink tar entries. Inline regular files use literal content; external dumpfile regular files get deterministic pseudo-random bytes seeded by size. Xattrs are encoded by `append_with_xattrs()` as PAX `SCHILY.xattr.*` records before the real entry. `create_multi_layer_image()` hashes tar bytes for diff IDs, imports each layer through `crate::import_layer()`, builds an OCI image config with ordered diff IDs, writes a config splitstream referencing layer verities, builds the manifest descriptors, hashes the manifest JSON, and calls `write_manifest()`. `OsImage::layer_strings()` assembles base, boot, version-specific, shared, SELinux, and caller-provided layers before delegating to the multi-layer builder.

## State and Persistence
The utilities write into a composefs test repository: imported layer streams, config stream, manifest stream, optional tag refs, generated EROFS objects, and optional boot image objects. They also create temporary OCI layout directories for tests. Shared layer constants intentionally produce identical content across boot image versions so GC and deduplication behavior can be tested.

## Dependencies and Integration Points
The file integrates `composefs::dumpfile_parse`, repository APIs, `containers_image_proxy` OCI spec builders, `sha2`, `tar`, `tar_core` PAX builder, `rand`, `ocidir`, `cap-std-ext`, `composefs_boot` transform tests, and crate-local image/layer/boot helpers.

## Risks
These helpers panic on malformed fixture input, which is acceptable for tests but not production. Path and xattr handling assumes UTF-8 dumpfile paths and xattr keys. The fake external content is deterministic by size, so same-sized external files can have identical generated content unless differentiated elsewhere. The module bypasses full pull paths, so tests using it should call `ensure_erofs_for_image()` when they need mountable image refs.

## Test Signals
Tests validate dumpfile-to-tar conversion for directories, files, executables, and symlinks; creation of base and bootable images; SELinux layer inclusion; custom layer injection into a merged filesystem; bootable filesystem shape; and GC behavior when versioned boot images share most layers but differ in kernel/initramfs/modules/UKI layers.
