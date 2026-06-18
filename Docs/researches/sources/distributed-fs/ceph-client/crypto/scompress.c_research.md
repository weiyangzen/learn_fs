# sources/distributed-fs/ceph-client/crypto/scompress.c

Purpose: implements the synchronous compression crypto type (`scomp`) and an async-compatible acomp bridge over scomp algorithms.

Important APIs, types, and functions: exported APIs include `crypto_init_scomp_ops_async()`, `crypto_register_scomp()`, `crypto_unregister_scomp()`, `crypto_register_scomps()`, and `crypto_unregister_scomps()`. `struct scomp_scratch` and per-CPU `scomp_scratch` provide fallback source buffers. Main acomp bridge path is `scomp_acomp_comp_decomp()`.

Control flow: scomp tfm init allocates algorithm streams and lazily allocates per-CPU scratch storage. The acomp bridge validates source/destination, maps virtual buffers directly when possible, maps single SG buffers when contiguous and safe, or copies SG input into a per-CPU scratch page. It locks an algorithm stream, calls `crypto_scomp_compress()` or `crypto_scomp_decompress()`, updates `req->dlen`, unmaps pages, and flushes destination dcache. Missing per-CPU scratch pages are requested via a work item.

State and persistence: algorithm stream pools persist per registered algorithm while tfms use them. Per-CPU scratch pages persist while at least one async wrapper user exists and are freed when the last user exits.

Dependencies and integration points: depends on acomp/scomp internals, scatterwalk copying, highmem, per-CPU data, workqueues, and crypto user reporting.

Risks: the async bridge supports only buffer shapes it can map or copy; complex highmem multi-page SG cases return `-ENOSYS`. Scratch fallback is page-sized, so callers must respect sizes accepted by this path. Locking combines spinlocks, mutexes, streams, and workqueues, so teardown ordering matters.

Test signals: direct scomp registration, acomp wrapper with virtual and SG buffers, highmem rejection paths, per-CPU scratch allocation on first use and fallback work, stream locking under concurrency, and cleanup after last tfm.
