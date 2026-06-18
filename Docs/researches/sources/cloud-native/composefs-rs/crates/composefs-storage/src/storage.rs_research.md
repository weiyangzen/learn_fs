# sources/cloud-native/composefs-rs/crates/composefs-storage/src/storage.rs

## Purpose
This module provides the main read-only `Storage` handle for containers-storage overlay roots. It opens and validates storage roots, discovers default and additional image stores, resolves overlay links and diff IDs, lists/finds images, opens image layers, reads layer metadata, and computes image size.

## Important APIs, Types, and Functions
`Storage` wraps a capability-scoped root `Dir`. Public methods include `open()`, `discover()`, `discover_all()`, `from_root_dir()`, `root_dir()`, `resolve_link()`, `list_images()`, `get_image()`, `get_image_layers()`, `find_image_by_name()`, `resolve_diff_ids()`, `resolve_diff_id()`, `get_layer_metadata()`, and `calculate_image_size()`. Internal helpers include `default_search_paths()`, `validate_storage()`, `additional_image_stores_from_env()`, `parse_additional_image_stores()`, `extract_layer_id_from_link()`, and `read_layer_entries()`. Data structs are internal `LayerEntry` and public `LayerMetadata`.

## Control Flow
`open()` opens a root path with ambient authority and validates required directories: `overlay`, `overlay-layers`, and `overlay-images`. `discover()` tries `$CONTAINERS_STORAGE_ROOT`, rootless XDG/home paths, and `/var/lib/containers/storage`. `discover_all()` combines primary discovery with valid `STORAGE_OPTS=additionalimagestore=<path>` entries. Link resolution reads `overlay/l/<link-id>` symlink targets and extracts the second-to-last component from `../<layer-id>/diff`. Image listing opens every directory under `overlay-images`. Name lookup scans `images.json` for exact names, suffix matches with slash boundary, and short names with implicit `:latest`. Diff ID resolution parses `overlay-layers/layers.json` once, builds a normalized digest map, and returns same-length `Option<String>` results. Image size calculation resolves layers and sums available `diff_size` values with saturating addition.

## State and Persistence
The module is read-only over persistent containers-storage directories and JSON files: `overlay`, `overlay/l`, `overlay-layers/layers.json`, `overlay-images`, and `overlay-images/images.json`. It stores only a root directory handle in memory. Environment variables affect discovery but are not mutated.

## Dependencies and Integration Points
It uses `cap_std` for fd-relative operations, standard environment/path/io APIs, `serde_json`, and crate `Image`, `Layer`, and `StorageError`. It integrates with `image.rs` for image opening and diff ID extraction, and with `layer.rs` for layer opening and metadata.

## Risks
Validation only checks required directories, not `layers.json` or `images.json`, so later calls can fail after `open()` succeeds. `discover()` silently skips invalid existing paths and reports a generic failure if none work. Additional image stores from `STORAGE_OPTS` silently skip inaccessible paths. `extract_layer_id_from_link()` is string-based and assumes the usual `../<layer-id>/diff` target shape. Name suffix matching is convenient but can be ambiguous if multiple names share suffixes. `calculate_image_size()` ignores layers with missing `diff_size`.

## Test Signals
Tests cover default search path generation, minimal storage validation with required directories, and parsing additional image stores from `STORAGE_OPTS` including empty, single, multiple, nonexistent, and unrelated options. There are no direct tests for `images.json` name matching, symlink target parsing, diff ID resolution, layer metadata, or size calculation.
