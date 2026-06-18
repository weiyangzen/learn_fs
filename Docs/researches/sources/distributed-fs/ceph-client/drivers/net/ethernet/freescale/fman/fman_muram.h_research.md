# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_muram.h

## Purpose

`fman_muram.h` declares the MURAM allocator interface used by FMan core and related modules. It keeps `struct muram_info` opaque and exposes offset-based allocation helpers.

## Important APIs, Types, And Functions

The header defines `FM_MURAM_INVALID_ALLOCATION` and forward-declares `struct muram_info`. It declares `fman_muram_init()`, `fman_muram_offset_to_vbase()`, `fman_muram_alloc()`, and `fman_muram_free_mem()`.

## Control Flow

FMan core initializes a MURAM handle from the device-tree MURAM resource, allocates hardware work areas by size, programs returned offsets into hardware registers, converts offsets to virtual addresses only when it must initialize memory directly, and frees offsets on error paths.

## State And Persistence Behavior

State is hidden behind the `muram_info` handle. Allocation identity is an offset relative to the MURAM partition base, matching hardware-visible addressing rather than CPU virtual pointers.

## Dependencies And Integration Points

The header depends only on Linux types. It is included by `fman.c` and any FMan submodule requiring MURAM memory.

## Risks And Edge Cases

`FM_MURAM_INVALID_ALLOCATION` is `-1`, while the implementation returns `-ENOMEM` on allocation failure. Callers must not check only this constant. No destroy API is declared, so lifecycle management is incomplete for full unload scenarios.

## Test Signals

Compile users should verify error checks use `IS_ERR_VALUE()`. Runtime tests should confirm offsets are valid for hardware programming and that frees use exactly the originally allocated size.
