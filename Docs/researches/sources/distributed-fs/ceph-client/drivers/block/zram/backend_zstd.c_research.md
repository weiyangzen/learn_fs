# sources/distributed-fs/ceph-client/drivers/block/zram/backend_zstd.c

Purpose: zram backend adapter for Zstandard compression, supporting default compression contexts and optional dictionaries.

Important APIs/types/functions: `struct zstd_ctx` owns per-CPU compression/decompression contexts and optional workspace memory. `struct zstd_params` stores shared custom allocator, prepared cdict/ddict, and compression parameters. `zstd_setup_params()` chooses level, computes params, and creates dictionaries by reference. `zstd_create()` builds per-CPU contexts using embedded vmalloc workspaces without a dictionary or advanced allocation with dictionaries. `zstd_compress()` and `zstd_decompress()` dispatch to dictionary or non-dictionary APIs.

Control flow and state: shared params live in `params->drv_data`; per-CPU contexts are separate. Custom allocation uses `GFP_NOIO | __GFP_NOWARN`. Destroy frees embedded workspaces or explicit zstd contexts based on which allocation path was used.

Dependencies and integration: depends on kernel zstd APIs, zcomp, vmalloc, and kvfree/kzalloc helpers.

Risks: dictionary objects are by-reference, so the dictionary buffer lifetime must exceed backend use. In `zstd_create()` error handling calls `zstd_release_params(params)`, which releases shared params from a per-context creation failure and can affect other contexts during initialization cleanup. Memory use can be high for zstd workspaces.

Test signals: no-dictionary and dictionary round trips, default level behavior, invalid dictionary setup, allocation failure at each context stage, malformed input, and teardown after partial CPU context creation failure.
