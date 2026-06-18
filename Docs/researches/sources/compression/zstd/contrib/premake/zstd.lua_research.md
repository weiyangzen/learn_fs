<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/premake/zstd.lua -->
# sources/compression/zstd/contrib/premake/zstd.lua

## Purpose
`zstd.lua` provides a reusable premake function for defining zstd as a static C library project.

## Important APIs, Types, And Functions
The exported function is `project_zstd(dir, compression, decompression, deprecated, dictbuilder, legacy)`. It normalizes the source directory, defaults feature toggles, declares project `zstd`, adds common/compress/decompress/dictBuilder/deprecated/legacy files conditionally, sets include directories, and defines `XXH_NAMESPACE=ZSTD_` plus `ZSTD_LEGACY_SUPPORT`.

## Control Flow
Feature booleans are normalized first. Disabling compression also disables dictbuilder/deprecated; disabling decompression disables legacy/deprecated. Premake file globs are then registered in feature order.

## State And Persistence
State is premake project metadata emitted during generation, not runtime state.

## Dependencies And Integration Points
It integrates zstd's `lib` layout with GENie/premake4-based consumers.

## Risks
Glob patterns and legacy version selection must stay synchronized with zstd's source tree. Optional feature interactions can surprise users expecting deprecated code without both compression/decompression.

## Test Signals
Successful project generation and compilation with varied feature combinations validate this helper.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/premake/zstd.lua -->
