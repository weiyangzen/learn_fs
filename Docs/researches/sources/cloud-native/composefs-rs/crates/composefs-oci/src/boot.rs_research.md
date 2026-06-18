## sources/cloud-native/composefs-rs/crates/composefs-oci/src/boot.rs

Purpose: this module manages derived bootable EROFS images for OCI container images. A boot image is stored as metadata linked from the OCI config/manifest, with special filtering to avoid circular references and capture boot resources.

Important APIs: `generate_boot_image` is compiled with the `boot` feature and idempotently creates a boot EROFS image for a manifest. `boot_image` returns an existing boot EROFS object ID, if present. `remove_boot_image` removes the boot image reference from OCI metadata while leaving the actual EROFS object for repository GC.

Control flow: `generate_boot_image` first calls `boot_image`; if one exists, it returns it. Otherwise it delegates to `ensure_oci_composefs_erofs_boot` and expects a container image to produce an EROFS object. `boot_image` delegates to `composefs_boot_erofs_for_manifest`. `remove_boot_image` opens the manifest as an `OciImage`, rejects non-container images, returns early if no boot ref exists, preserves raw config JSON, rewrites config with no boot image through `write_config_raw`, reads raw manifest JSON, and calls `oci_image::rewrite_manifest` with the new config verity and existing layer refs.

State and persistence: generation writes or reuses an EROFS object and updates OCI config/manifest splitstreams so the manifest points at the boot image. Removal rewrites metadata to drop that ref, but object cleanup is deferred to `repo.gc()`. Tags remain associated with the OCI image when metadata is rewritten.

Dependencies and integration: integrates with `composefs::Repository`, `FsVerityHashValue`, `OciDigest`, crate-level EROFS helpers, and `oci_image::OciImage`. With tests, it uses `composefs-boot` to inspect boot resources and `TestRepo` fixtures from `test_util`.

Risks: manifest/config rewriting must preserve enough raw JSON and refs to keep the OCI image valid. Removing a boot ref changes config and manifest verities, so any caller caching old verities must refresh. The `expect` in `generate_boot_image` assumes a container image should always produce boot EROFS once the boot path is requested; non-container or malformed content would panic if lower layers violate that assumption.

Test signals: boot-feature tests cover absent boot images, generation, idempotency, removal, removal idempotency, GC preservation while tagged, GC collection after untag, OCI preservation after boot removal, and boot content differences/resources for both classic kernel/initramfs and UKI-like fixtures.
