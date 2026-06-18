# sources/cloud-native/nydus/builder/src/core/feature.rs

Purpose: defines opt-in builder feature flags parsed from strings.

Important APIs/types/functions: `Feature` currently has one variant, `BlobToc`, for appending a Table of Contents footer to RAFS v6 data blobs. `TryFrom<&str> for Feature` accepts `"blob-toc"` and rejects unknown names with an upgrade-oriented error. `Features` wraps a `HashSet<Feature>` and exposes `new`, `Default`, `is_enabled`, and `TryFrom<&str>` for comma-separated feature lists.

Control flow: parsing trims the full string, splits on commas, ignores empty entries, trims each feature token, converts it to `Feature`, and inserts it into the set. Duplicate entries collapse naturally via `HashSet`.

State and persistence: state is an in-memory feature set. The enabled flags influence `BuildContext::new` and blob metadata output, especially `BlobFeatures::HAS_TOC` and tar-header behavior.

Dependencies and integration points: used by `BuildContext`, `Blob::finalize_blob_data`, and `Blob::dump_meta_data` to decide whether to write ToC entries and digest arrays.

Risks: there is no public insert method, so callers must construct from strings or internal code. Unknown features are hard errors rather than ignored for forward compatibility. `is_enabled` takes `Feature` by value, which is fine for the current enum but can be less ergonomic as variants grow.

Test signals: tests cover accepted `"blob-toc"`, rejection of unknown features, trailing commas, and whitespace around feature names.
