# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzo.c

Purpose: zram backend adapter for classic LZO1X compression.

Important APIs/types/functions: `lzo_create()` allocates `LZO1X_MEM_COMPRESS` workspace, `lzo_destroy()` frees it, `lzo_compress()` calls `lzo1x_1_compress()`, `lzo_decompress()` calls `lzo1x_decompress_safe()`, and `backend_lzo` publishes zcomp ops.

Control flow and state: no params are used. Each runtime context has one compression workspace. LZO return `LZO_E_OK` maps to zero; other codes pass through.

Dependencies and integration: depends on `linux/lzo.h` and zcomp. It is included together with lzo-rle when LZO backend support is enabled.

Risks: nonzero LZO library error codes are not normalized to Linux errno. Workspace allocation is a write-path prerequisite for every CPU stream.

Test signals: round-trip pages, incompressible data, malformed input, and memory allocation failure.
