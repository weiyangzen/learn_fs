# sources/cloud-native/nydus/smoke/tests/compatibility_test.go

## Purpose
This suite verifies cross-version compatibility among `nydus-image`, `nydusify`, `nydusd`, RAFS fs versions, and modern checker binaries. It reuses the main image conversion/check path while varying stable, legacy, and latest binaries.

## Important APIs, Types, And Functions
`CompatibilityTestSuite` stores `t` and a `preparedImages` cache. `TestConvertImages` requires `NYDUS_STABLE_VERSION`, builds a Cartesian matrix for image, RAFS version, nydus-image version, nydusify version, and nydusd version, and skips invalid legacy combinations. It resolves versioned binaries through `tool.GetBinary`, configures `tool.BinaryContext`, sets lz4 block compression, and delegates to `ImageTestSuite.TestConvertAndCopyImage` with copy disabled. `prepareImage` caches the registry-prepared image reference.

## Control Flow
For each valid matrix row, the generator resolves all binaries, builds a context that uses the selected converter and daemon but latest nydusify for checking, prepares the image once, then performs conversion and check in a subtest.

## State And Persistence
Prepared registry images are cached in memory for the suite. Each conversion gets a workdir from `ImageTestSuite` and creates target images in the registry/container runtime. No local persistent state is intentionally retained by this file.

## Dependencies And Integration Points
The test depends on environment variables for versioned binaries such as `NYDUS_BUILDER_<version>` and `NYDUS_NYDUSD_<version>`, plus `NYDUS_STABLE_VERSION`. It integrates directly with the main `ImageTestSuite`, making image conversion behavior the compatibility contract.

## Risks
The scenario matrix can be large and slow. Legacy v0.1.0 rules are hard-coded, and future compatibility constraints may need updates. Because it calls into another suite method, failures can be reported under compatibility names while originating in image conversion/check mechanics.

## Test Signals
A passing matrix row proves the selected image builder, converter, checker, daemon, and RAFS version can produce and validate a Nydus image for `nginx:latest`. Skipped rows document known unsupported combinations.
