# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.h

## Purpose
This header defines the CUDBG zlib compression format constants, compression header layout, workspace sizing helper, and compression function prototype.

## Important APIs, Types, And Functions
- `CUDBG_ZLIB_COMPRESS_ID`, `CUDBG_ZLIB_WIN_BITS`, and `CUDBG_ZLIB_MEM_LVL` identify and parameterize zlib compression.
- `struct cudbg_compress_hdr` records compression ID, decompressed size, compressed size, and reserved space.
- `cudbg_get_workspace_size()` wraps `zlib_deflate_workspacesize()`.
- `cudbg_compress_buff()` is implemented in `cudbg_zlib.c`.

## Control Flow
The inline helper computes workspace size for the configured zlib parameters. The rest of the header declares data used by compression flow in `cudbg_zlib.c` and allocation flow in `cxgb4_cudbg.c`.

## State And Persistence
The compression header is serialized before each compressed chunk. Workspace size is transient and used to allocate per-dump compression memory.

## Dependencies And Integration Points
It includes Linux `zlib.h` and is included by `cxgb4_cudbg.c`, `cudbg_lib.c`, and `cudbg_zlib.c`. Dump decoders need to recognize `CUDBG_ZLIB_COMPRESS_ID` and the header layout.

## Risks
Changing zlib parameters changes workspace requirements and may affect decoder expectations. The large reserved array in `struct cudbg_compress_hdr` is part of the serialized format and should not be casually resized.

## Test Signals
Compile tests with zlib enabled, workspace allocation tests, compressed dump decode tests, and compatibility checks for `struct cudbg_compress_hdr` size/field interpretation.
