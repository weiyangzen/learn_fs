# sources/cloud-native/composefs-rs/crates/composefs-storage/src/image.rs

## Purpose
This module represents and reads images from containers-storage `overlay-images/<image-id>/`. It provides raw and parsed manifest access, config access from base64-keyed metadata files, diff ID extraction, storage layer ID resolution, metadata reads, and image name lookup.

## Important APIs, Types, and Functions
`Image` stores an image ID and a `cap_std::fs::Dir` handle to its image directory. Public methods include `open()`, `id()`, `read_manifest_raw()`, `manifest()`, `config()`, `layers()`, `storage_layer_ids()`, `read_metadata()`, `image_dir()`, and `names()`. `ImageJsonEntry` models `overlay-images/images.json` entries with `id` and optional `names`.

## Control Flow
`Image::open()` strips a leading `sha256:` prefix, opens `overlay-images`, then opens the image ID directory or returns `ImageNotFound`. `read_manifest_raw()` preserves exact manifest bytes; `manifest()` parses JSON. `config()` constructs the key `sha256:<id>`, base64-encodes it, reads the corresponding `=<key>` metadata file, and parses `ImageConfiguration`. `layers()` extracts rootfs diff IDs from config and strips `sha256:` prefixes. `storage_layer_ids()` resolves all diff IDs across a slice of `Storage` values, allowing layers to span additional stores. `names()` scans `images.json` for matching ID and returns stored names.

## State and Persistence
The module is read-only. Persistent state lives in containers-storage: manifest files, base64-prefixed metadata files, and `images.json`. Open `Dir` handles maintain capability-scoped access to image directories.

## Dependencies and Integration Points
It uses `base64`, `cap_std`, `oci_spec::image`, `serde_json`, and crate `Storage`/`StorageError`. It integrates with `Storage::resolve_diff_ids()` and is used by storage listing, image lookup, layer lookup, and size calculation paths.

## Risks
Config metadata lookup assumes the config key is based on `sha256:<image-id>`, which follows the documented layout but can fail for layout variants. `layers()` returns normalized diff IDs without `sha256:`, while `resolve_diff_ids()` re-adds the prefix; callers must understand the distinction between OCI diff IDs and storage layer IDs. `storage_layer_ids()` ignores stores whose `layers.json` cannot be read, which helps multi-store fallback but can hide broken stores if another store resolves all layers. `names()` returns empty if the image directory exists but the index lacks the ID.

## Test Signals
The local test validates OCI manifest JSON parsing. Runtime behavior is also indirectly covered by storage tests and any integration tests using real or mocked containers-storage layouts. There are no direct tests for config metadata base64 lookup, multi-store resolution, or names lookup.
