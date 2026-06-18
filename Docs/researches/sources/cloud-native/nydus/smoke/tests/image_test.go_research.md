# sources/cloud-native/nydus/smoke/tests/image_test.go

## Purpose
This is the main smoke suite for image conversion, checking, copying, saving/loading, encryption flag handling, zran/OCI reference mode, batch conversion options, and chunkdict generation.

## Important APIs, Types, And Functions
`ImageTestSuite` stores `T` and a prepared-image cache. `TestConvertImages` builds a matrix over `nginx:latest`, fs versions 5/6, zran, batch size, and encryption, with skips for unsupported combinations. `TestConvertAndCopyImage` prepares a workdir, constructs `nydusify convert` arguments, runs `nydusify check`, and optionally calls `testNydusifyCopy`. `testNydusifyCopy` copies target-to-target, saves to `file://saved.tar`, loads back, and checks each result. `TestGenerateChunkdicts` prepares three Redis versions and calls `TestChundict`. `TestChundict` converts training images, generates a chunkdict image, converts a test image, and checks it. `prepareImage` caches registry-prepared source images.

## Control Flow
Conversion tests prepare a local registry image, create a unique Nydus target, convert with the selected flags, check against the original, then exercise copy/save/load/check if enabled. Chunkdict tests convert two training Redis images, generate a dictionary image from them, convert the third Redis image, and verify the result.

## State And Persistence
Each conversion uses a temporary workdir for builder/check/copy artifacts. Persistent external state includes registry images and pushed/copied Nydus images. `saved.tar` is written into the workdir and checked for existence before load.

## Dependencies And Integration Points
This depends on `nydusify`, `nydus-image`, `nydusd`, the local registry, Docker/registry preparation, and `tool.RunWithoutOutput`. It is a central integration point for the compatibility suite and performance preparation.

## Risks
Shell command construction is simple string concatenation. Matrix skip logic is an implicit feature-support map and must track CLI/runtime capabilities. The chunkdict conversion command currently does not pass the generated chunkdict reference to the later convert command in this file, so it mainly validates generation and normal conversion/check unless the CLI has implicit behavior elsewhere.

## Test Signals
Signals are successful CLI exit for convert/check/copy/save/load/chunkdict generate and existence of `saved.tar`. Checker success is the behavioral proof that converted images mount and match the source image.
