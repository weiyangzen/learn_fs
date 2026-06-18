# sources/cloud-native/composefs-rs/crates/composefs-oci/src/oci_layout.rs

## Purpose

`oci_layout.rs` implements the direct local OCI layout import path for `oci:`-style references. Instead of spawning skopeo through `containers-image-proxy`, it reads an OCI layout directory with `ocidir`, imports config/layers into the same composefs repository format used elsewhere, and emits progress events for layer import. It also detects delta artifacts in single-manifest layouts and delegates them to the crate delta importer before platform filtering.

## Important APIs, Types, and Functions

- `parse_oci_layout_ref(imgref)` splits a local layout reference into `(path, optional_tag)` using the last colon after the last slash as a tag separator.
- `resolve_manifest` calls `ocidir.open_image_this_platform(tag)` to select a manifest for the current platform.
- `import_oci_layout` is the public async entry point. It opens the layout, detects delta artifacts, resolves the manifest, imports config and layers, stores the manifest splitstream, and returns `(skopeo::PullResult<ObjectID>, ImportStats)`.
- `import_config_and_layers` imports or reuses the config stream, extracts ordered layer identifiers, imports layers concurrently, writes config named refs, and returns ordered layer refs plus stats.
- `import_layer_from_file` imports a single layout blob, emits progress events, decompresses tar layers or stores non-tar blobs, creates the layer/blob splitstream, and returns the stream verity plus stats.
- `OciDirBlobReader` implements `delta::DeltaBlobReader` over an `OciDir` by opening blob files under `blobs/{algorithm}/{digest}`.

## Control Flow

`import_oci_layout` begins by checking repository writability to provide a repository error before any source-layout error. It opens the layout via `cap_std` and `OciDir::open`. Before platform resolution, it reads the index when there is exactly one manifest and checks whether that manifest is a composefs delta artifact. Deltas lack normal platform data, so they are delegated early to `delta::import_delta`.

For normal images, it resolves the manifest for the host platform and emits a message with the layer count. `import_config_and_layers` handles the config and layers. When the config stream already exists, it reads the config splitstream and named refs, extracts diff_ids using the same config/artifact fallback as `lib.rs`, reconstructs ordered layer refs from the existing named refs, emits `Skipped` events for every cached layer, and returns zero stats. This fast path avoids opening layer blobs.

When the config is new, raw config bytes are read from the layout and diff_ids are extracted. Manifest layers are paired with diff_ids, sorted by descriptor size descending, and imported concurrently using `tokio::task::JoinSet` with a semaphore sized to `available_parallelism()`. Each task opens a layer blob file from the layout before spawning, then calls `import_layer_from_file`. Results are merged into a digest-to-verity map and then re-ordered back into config-defined diff_id order before writing the config stream.

Manifest storage mirrors the rest of the crate. If `oci-manifest-{digest}` already exists, it reuses the verity. Otherwise it creates a manifest splitstream, adds the `config:{digest}` named ref, adds layer refs in config-defined order, reads the raw manifest bytes from the layout, writes them as the external payload, and stores the stream without tagging.

`import_layer_from_file` checks for an existing `oci-layer-{diff_id}` stream first and emits `Skipped` when cached. For new layers it emits `Started`, wraps the file in `ProgressRead`, and runs the progress driver concurrently with the actual import. Tar media types are decompressed with `decompress_async` and passed to `import_tar_async`; the resulting stream is registered under the layer content ID. Non-tar media types are stored through `store_blob_async`, object-store-method stats are populated, a small `OCI_BLOB_CONTENT_TYPE` splitstream wrapper is written with a reference to the object, and `Done` is emitted with the stored size.

## State and Persistence Behavior

The import path writes the same repository structures used by registry/skopeo import: config streams under `oci-config-{digest}`, layer streams under `oci-layer-{diff_id}`, manifest streams under `oci-manifest-{digest}`, and single-object blob wrappers for non-tar artifacts. It preserves raw config and manifest bytes from the OCI layout rather than reserializing parsed OCI structures. It does not tag the manifest itself; callers that need refs must add them in the surrounding pull path.

Config named refs are written in diff_id order and are used as the cache boundary. If the config stream already exists, the function trusts its named refs to recover layer verities and does not re-import layers. Import stats only reflect new work in this function; cached config/layer paths return default stats.

Progress state is externalized through `SharedReporter` events: `Message`, `Started`, `Done`, and `Skipped`. `ProgressRead` reports compressed bytes read, matching descriptor sizes.

## Dependencies and Integration Points

The module depends on `ocidir` for OCI layout reading and platform resolution, `cap_std_ext::cap_std` for capability-based directory access, Tokio `Semaphore` and `JoinSet` for bounded async layer import, `available_parallelism` for concurrency sizing, `composefs::repository::Repository` for stream/object persistence, `containers_image_proxy::oci_spec::image` for descriptors and media types, and internal `layer`, `delta`, `progress`, `oci_image`, `skopeo`, and crate-level identifier/stat helpers.

It is the fast path equivalent of the skopeo proxy importer. Its output must remain compatible with `OciImage::open`, `open_config`, fsck, GC, and EROFS generation.

## Risks and Edge Cases

- `parse_oci_layout_ref` treats an empty suffix after a trailing colon as `Some("")`, which callers must handle consistently with `ocidir`.
- Platform resolution rejects layouts that do not match the current platform unless they are detected as single-manifest delta artifacts first.
- The cached-config path assumes config named refs are complete and correct; missing layer refs fail before manifest storage.
- Layer tasks open blob files before spawning. This keeps task bodies simple but can fail serially during task setup.
- Sorting layers by size improves throughput but requires reordering results back to diff_id order. The code uses a map and then rebuilds ordered refs, so duplicate diff_ids would collapse in the map.
- `available_parallelism()` errors propagate and can abort import before any layer tasks start.
- Progress `Done` for tar layers reports descriptor `layer_size` rather than decompressed bytes; this is intentional because progress tracks compressed bytes read.
- Non-tar blob stats use object-store method data from `store_blob_async`; inlined metadata for the wrapper stream is not counted as layer tar inline bytes.

## Test Signals

The local tests cover `parse_oci_layout_ref` across plain paths, tags, Windows-style paths, embedded colons, and empty tags. `test_wrong_platform_rejected` builds a minimal layout for a foreign architecture and verifies the direct import returns a platform-selection error. Additional integration tests in `lib.rs` construct local OCI layouts and verify that fresh imports emit `Started` and terminal progress events, cached reimports emit `Skipped`, and `NullReporter` does not panic.
