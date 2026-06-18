# sources/distributed-fs/glusterfs/xlators/features/compress/src/Makefile.am

## Purpose
Builds the `cdc.la` compression translator.

## Important APIs, types, and functions
Defines sources `cdc.c` and `cdc-helper.c`, headers `cdc.h` and `cdc-mem-types.h`, links against `libglusterfs` and `ZLIB_LIBS`, and installs the module under GlusterFS feature xlator directory.

## Control flow
Automake compiles the translator with zlib include flags, `_FILE_OFFSET_BITS=64`, `_GNU_SOURCE`, and GlusterFS RPC/libglusterfs include paths.

## State and persistence behavior
Build output is `cdc.so`; no runtime state here.

## Dependencies and integration points
Depends on zlib and GlusterFS xlator infrastructure. Runtime module is identified as `cdc` in `cdc.c`.

## Risks and test signals
Build risks center on zlib discovery and PIC/link flags. Tests should build with compression enabled and run read/write paths in client and server mode.
