# sources/cloud-native/nydus/builder/src/core/context.rs

Purpose: central builder context module. It defines conversion modes, artifact storage/writers, blob cache writers, blob contexts/managers, bootstrap context/manager, build configuration, and build output reporting.

Important APIs/types/functions: `ConversionType`, `ArtifactStorage`, `Artifact`/`ArtifactWriter`/`NoopArtifactWriter`, `BlobCacheGenerator`, `BlobContext`, `BlobManager`, `BootstrapContext`, `BootstrapManager`, `BuildContext`, and `BuildOutput`. `BlobContext` tracks blob ids, digests, compression/encryption, offsets, sizes, chunk metadata, ToC data, and cache fields. `BlobManager` manages blob indices, current blob, chunk dictionaries, blob table import/export, and external blob behavior.

Control flow: `BuildContext::new` converts CLI-style options into RAFS blob feature flags and crypto settings. `ArtifactWriter::new/finalize` handles direct single-file writes or temp-file-in-directory writes with rename-on-finalize. `BlobContext::from` reconstructs build-time blob state from existing `BlobInfo`, including special fixes for inlined metadata and optional backend reads. `BlobManager` lazily creates blob contexts, imports parent/chunkdict blobs, maps chunkdict blob indexes, and emits v5/v6 `RafsBlobTable`. `BootstrapContext` allocates inode numbers and v6 metadata block space.

State and persistence: this file owns most mutable build state. It writes artifact files, renames temp files, removes empty single-file outputs, writes blob cache data/meta files, and stores in-memory bootstrap writer data when no storage is configured.

Dependencies and integration points: used across builder core, blob dumping, bootstrap generation, compaction, chunkdict generation, and node processing. It integrates `nydus_api::ConfigV2`, RAFS layouts, storage `BlobInfo`, tar headers, compression, digest, encryption, CRC, prefetch, features, and attributes.

Risks: many invariants are enforced by assertions, including blob meta index order and compressed offset assumptions. `ArtifactWriter::finalize` does not overwrite an existing digest-named file. `BlobManager::take_blob` removes by index. External blob id validation happens elsewhere. `ConversionType::Display` maps `TargzToStargz` to `"targz-ref"`, which may be a display bug.

Test signals: tests cover blob context reconstruction from metadata/backend config, conversion parsing/display/ref checks, artifact storage suffix/default behavior, and noop writer position/finalize behavior.
