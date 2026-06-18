# sources/compression/zstd/programs/windres/verrsrc.h

## Purpose

This tiny header provides the minimal Windows resource constants needed to build `zstd.res` from `zstd.rc` when the normal Windows SDK definitions are unavailable or intentionally minimized.

## Important APIs, Types, and Functions

It defines `VS_VERSION_INFO`, `VS_FFI_FILEFLAGSMASK`, `VOS_NT_WINDOWS32`, `VFT_DLL`, and `VFT2_UNKNOWN`. There are no functions or types.

## Control Flow, State, and Persistence

There is no control flow or runtime state. Constants are consumed at resource compilation time.

## Dependencies and Integration Points

It integrates with the `programs/windres` resource build path for Windows version metadata.

## Risks and Test Signals

The risk is stale or incomplete resource constants causing incorrect Windows version resources. Test signals are successful resource compilation and inspection of generated executable metadata on Windows/MinGW builds.
