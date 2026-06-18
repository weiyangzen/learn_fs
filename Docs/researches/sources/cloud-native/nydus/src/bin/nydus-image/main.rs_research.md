# sources/cloud-native/nydus/src/bin/nydus-image/main.rs

## Purpose
`main.rs` is the `nydus-image` CLI entrypoint. It builds, merges, validates, inspects, stats, compacts, optimizes, unpacks, and exports RAFS/Nydus image artifacts by translating Clap arguments into `nydus_builder`, `nydus_rafs`, `nydus_storage`, and `nydus_service` operations.

## Important APIs, Types, And Functions
`OutputSerializer` writes optional JSON results for build and check commands, including build version, bootstrap/blob outputs, trace summaries, RAFS version, and compressor. `prepare_cmd_args` defines the complete CLI surface: `create`, `chunkdict generate`, `merge`, `check`, `optimize`, Linux-only `export`, `inspect`, `stat`, `compact`, and `unpack`. `init_log` wires the shared logger. `Command` is a namespace for command handlers and argument helpers. Key handlers are `create`, `chunkdict_generate`, `merge`, `compact`, `unpack`, `check`, `optimize`, `inspect`, `stat`, and Linux `export_block`. Helper functions validate paths, parse storage/backend/configuration, blob ids, chunk/batch sizes, prefetch policy, blob offsets, and RAFS version.

## Control Flow
`main` builds the Clap parser, initializes logging and tracing, then dispatches to the matching `Command` method. `create` performs the most complex flow: parse conversion type, storage targets, compression/digest settings, whiteout behavior, parent bootstrap, feature flags, encryption, and attributes; validate per-conversion conflicts; create `BuildContext`, `BlobManager`, optional chunk dictionary, optional blob-cache generator, and `BootstrapManager`; choose `DirectoryBuilder`, `TarballBuilder`, or `StargzBuilder`; run `Builder::build`; then serialize output. `merge` loads source bootstraps, optional blob metadata lists, parent bootstrap, and chunk dictionary before calling `Merger::merge`. `check` loads a `Validator`, prints referenced blob metadata, and writes check JSON. `unpack`, `compact`, `optimize`, `inspect`, and `stat` mostly build backend/configuration state and delegate to their specialized modules.

## State And Persistence
The command writes bootstrap files, blob files, blob cache files, chunk-dictionary bootstraps, compacted/optimized bootstraps, exported block images, unpacked tar files, stat JSON, and optional output JSON. It mutates `ConfigV2.internal.blob_accessible` and cache validation flags to match backward compatibility and command behavior. Tracing state is collected through root/event/timing tracers. It does not keep daemon state, except for Linux block export through service APIs.

## Dependencies And Integration Points
The file is the user-facing integration point for `nydus_builder` builders, deduplication database/chunkdict logic, `RafsSuper` metadata loading, storage backends from `BlobFactory`, localfs backends, unpack/stat/validator/inspect modules, shared `nydus` logging/build-info helpers, and Linux `nydus_service` block export. It relies on Clap value sources for default-vs-user option decisions and uses `anyhow` context for command errors.

## Risks
The large option matrix is the main risk. Conversion-type conflict checks must stay synchronized with builder capabilities, RAFS format limits, blob-cache behavior, encryption requirements, and feature flags. Several list parsing paths use `expect`, so malformed comma-separated numeric metadata can panic. `Arc::get_mut(...).unwrap()` assumes configuration references are not cloned before mutation. Backend config JSON parsing has unwraps in deprecated localfs compatibility. `merge` exits with code 2 for inconsistent filesystems, which callers may depend on. Linux-only export builds JSON strings from paths, so quoting and validation matter.

## Test Signals
This file has a small unit test for accepting `/dev/stdin` as a source file. Most behavioral coverage is indirect through builder, validator, stat, unpack, inspect, and service tests. Important manual or integration test signals include CLI conflict matrices, create output JSON, RAFS v5/v6 builds, chunk dictionary generation from SQLite, merge failure exit codes, unpack with localfs and remote backends, stat over blob directories, and Linux export block mode.
