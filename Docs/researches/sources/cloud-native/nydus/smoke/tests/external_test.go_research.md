# sources/cloud-native/nydus/smoke/tests/external_test.go

## Purpose
This file smoke-tests Nydus external backend/model artifact support. It validates both library-level modctl metadata generation and binary `nydusify convert` modes for `modelfile` and `model-artifact` sources, then mounts and compares the resulting external-backed filesystem against a model context directory.

## Important APIs, Types, And Functions
Global environment-backed variables define model work/context directories, registry auth, and image reference. `proxy` models runtime external proxy settings. `walk` builds `tool.File` maps while skipping files larger than 128 MiB. `check` compares target files to source files. `verify` launches `nydusd` with an `ExternalBackendConfigPath` and compares mounted content. `packWithAttributes` packs a source directory with external blob attributes and returns internal/external blob digests. `parseReference` extracts registry host, repository path, and tag. `TestModctlExternal` generates `.nydusattributes`, backend metadata/config, builds an external bootstrap, checks it, rewrites runtime backend config, and mounts. `TestModctlExternalBinary` invokes `nydusify convert` using source-backend types `modelfile` and `model-artifact`. `convertAndCheck`, `buildFsViewer`, and `buildRuntimeExternalBackendConfig` pull bootstraps from converted images, check them, and inject runtime backend/proxy/auth configuration.

## Control Flow
Tests skip unless `NYDUS_MODEL_IMAGE_REF` is set. The library path either uses an existing `NYDUS_BOOTSTRAP`/`NYDUS_EXTERNAL_BACKEND_CONFIG` or generates external metadata, packs the model context into Nydus/external blobs, unpacks the bootstrap, checks it, rewrites backend runtime settings, and mounts. The binary path runs two subtests with different source backend types, then pulls and checks the produced bootstrap before mounting.

## State And Persistence
Temporary workdirs hold generated attributes, backend meta/config JSON, external blobs, bootstraps, and pulled artifacts. Runtime backend config is mutated in place by `buildRuntimeExternalBackendConfig` with auth, host, repo, timeout, proxy URL, and cache directory. Optional `NYDUS_ONLY_MOUNT=true` intentionally keeps the mount alive for five hours for debugging.

## Dependencies And Integration Points
This file integrates with `contrib/nydusify` packages (`modctl`, external backend handlers, parser, provider, viewer, checker tools), `snapshotter-converter`, `nydus-image check`, and `nydusd`. It requires external registry/model credentials and proxy/cache environment variables for real model artifacts.

## Risks
The tests depend heavily on external services, registry auth, local model directories, and large model contents. `walk` skips large files, so content verification is metadata-oriented for big artifacts. `convertAndCheck` uses `assert.NoError`, so later steps may run after an earlier command failure and produce secondary errors.

## Test Signals
Signals include successful external metadata generation, bootstrap extraction and `nydus-image check`, successful mount with external backend config, and file metadata/content comparison against `NYDUS_MODELCTL_CONTEXT_DIR` for non-huge files.
