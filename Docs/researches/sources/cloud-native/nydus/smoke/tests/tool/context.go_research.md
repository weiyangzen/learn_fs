# sources/cloud-native/nydus/smoke/tests/tool/context.go

## Purpose
This file defines the shared smoke-test context model for binaries, build options, runtime options, and per-test filesystem paths.

## Important APIs, Types, And Functions
`BinaryContext` stores paths and feature flags for builder, daemon, nydusify, and checker binaries. `BuildContext` stores fs version, compressor, chunk size, OCI ref flags, batch size, and encryption. `RuntimeContext` stores cache, mount, RAFS mode, prefetch, amplify I/O, and dedup DB settings. `EnvContext` stores work, blob, cache, mount, bootstrap, and overlay dirs. `Context` embeds those groups. `DefaultContext` initializes binaries from environment/defaults and conservative build/runtime defaults. `PrepareWorkDir` creates a temp workdir tree. `Destroy` removes it.

## Control Flow
Tests call `DefaultContext`, optionally mutate fields, then `PrepareWorkDir` before building images or daemons. `PrepareWorkDir` chooses `WORK_DIR` or `os.TempDir`, creates all subdirectories, and writes paths into `ctx.Env`.

## State And Persistence
The main state is a temporary directory containing blobs, cache, mountpoint, overlay upper/work dirs, and bootstraps. `Destroy` recursively removes the workdir.

## Dependencies And Integration Points
This integrates with `tool.GetBinary`, all pack/convert/daemon helpers, and environment variables such as `NYDUS_BUILDER`, `NYDUS_NYDUSD`, `NYDUS_NYDUSIFY`, and `WORK_DIR`.

## Risks
`Destroy` ignores removal errors. Defaults such as fs version 6, zstd, blobcache, direct mode, prefetch enabled, and amplify I/O shape many tests unless overridden. Mount directories must be unmounted before removal.

## Test Signals
There are no direct assertions beyond directory creation. Failures usually surface as missing binary fatal errors or `require.NoError` from `PrepareWorkDir`.
