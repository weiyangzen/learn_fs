<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamprng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamprng.c

Purpose: exposes CAAM SEC4 RNG hardware through the crypto RNG API as `prng-caam` with the generic `stdrng` name, using short CAAM job descriptors submitted to a job ring for reseed and byte generation.

Important APIs and control flow: `caam_prng_register()` checks the controller's RNG block count from era-dependent CHA/version registers before registering `crypto_register_rng()`. `caam_prng_generate()` allocates a CAAM job ring with `caam_jr_alloc()`, builds a descriptor with `init_job_desc()`, `append_operation(OP_ALG_ALGSEL_RNG)`, and `append_fifo_store(... FIFOST_TYPE_RNGSTORE)`, maps a temporary output buffer for DMA, enqueues the job, waits for the completion callback, unmaps, copies bytes to the caller, and frees the ring. `caam_prng_seed()` requires `slen == 0` and submits a finalize/reseed operation. `caam_prng_done()` converts nonzero JR status through `caam_jr_strstatus()`.

State and persistence behavior: only global software state is `caam_prng_alg.registered`; per-request state is a stack `completion` and error code. Persistent RNG state is in CAAM RNG state handles initialized by `ctrl.c`, not in this file. Each generate/seed call allocates and releases a job ring reference rather than retaining a per-tfm ring.

Dependencies and integration points: depends on `jr.c` for queueing, `desc_constr.h`/`desc.h` for descriptor words, `error.c` for status reporting, `intern.h` for controller private data, and crypto RNG registration. It is invoked from JR algorithm registration in `jr.c`.

Risks and test signals: risks include frequent allocation/free overhead, copying through a temporary zeroed buffer, mapping only `dlen` while allocating `aligned_dlen`, no timeout on job completion, and registration depending on `priv->jr[0]` being valid. Test signals are successful `prng-caam` registration only when RNG hardware exists, `crypto_rng_generate()` returning requested byte counts, zero-length seed acceptance only, CAAM error statuses surfacing as negative errors, and unregister balancing during last JR removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamprng.c -->
