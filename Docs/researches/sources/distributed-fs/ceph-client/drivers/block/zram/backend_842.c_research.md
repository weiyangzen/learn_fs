# sources/distributed-fs/ceph-client/drivers/block/zram/backend_842.c

Purpose: zram compression backend adapter for the kernel software 842 compressor.

Important APIs/types/functions: implements `const struct zcomp_ops backend_842`. `create_842()` allocates `SW842_MEM_COMPRESS` workspace, `destroy_842()` frees it, `compress_842()` calls `sw842_compress()`, and `decompress_842()` calls `sw842_decompress()`.

Control flow and state: setup/release params are no-ops; each per-CPU zcomp context has a private compression workspace. Compression updates `req->dst_len` only on success; decompression uses a local output length.

Dependencies and integration: depends on `linux/sw842.h` and the common zcomp request/ops abstraction. Compiled only when the 842 backend is enabled.

Risks: return codes are passed through directly from sw842, unlike some backends that normalize to `-EINVAL`; callers must tolerate that. Decompression does not write the final decompressed length back to `req->dst_len`, matching zram's fixed-page expectation.

Test signals: backend creation under memory pressure, round-trip compression/decompression of pages, incompressible data behavior, and error-code propagation.
