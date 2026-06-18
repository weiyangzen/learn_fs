# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.h

## Purpose
Declares CDC compression translator state, constants, macros, and helper APIs.

## Important APIs, types, and functions
Defines `cdc_priv_t`, `cdc_info_t`, vector macros, zlib defaults, client/server mode constants, min chunk size, validation trailer size, gzip OS id, canary key, debug dump path, mode string macros, and prototypes for `cdc_compress()` and `cdc_decompress()`.

## Control flow
`cdc.c` fills `cdc_info_t` per read/write operation and calls helper APIs declared here. Mode macros are used during initialization.

## State and persistence behavior
`cdc_priv_t` is translator lifetime state; `cdc_info_t` is per-operation state. Constants define the wire trailer and canary behavior.

## Dependencies and integration points
Includes GlusterFS xlator headers and zlib. Shared by main CDC translator and helper implementation.

## Risks and test signals
Risks include fixed `MAX_IOVEC` array in `cdc_info_t` and raw string mode comparison. Tests should cover vector count boundaries and option parsing.
