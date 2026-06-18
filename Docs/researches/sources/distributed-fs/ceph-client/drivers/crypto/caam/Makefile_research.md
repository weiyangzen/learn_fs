# sources/distributed-fs/ceph-client/drivers/crypto/caam/Makefile

Purpose: CAAM driver build recipe. It maps Kconfig symbols to controller, job-ring, descriptor, Crypto API, RNG, public-key, blob, queue-interface, debugfs, and DPAA2 object files.

Important build targets: `error.o`, `caam.o`, `caam_jr.o`, `caamalg_desc.o`, `caamhash_desc.o`, `ctrl.o`, `jr.o`, `key_gen.o`, `caamalg.o`, `caamalg_qi.o`, `caamhash.o`, `caamrng.o`, `caamprng.o`, `caampkc.o`, `pkc_desc.o`, `blob_gen.o`, `qi.o`, `debugfs.o`, `dpaa2_caam.o`, `caamalg_qi2.o`, `dpseci.o`, and `dpseci-debugfs.o`.

Control flow: `obj-*` lines create modules or built-ins based on configuration. Composite objects (`caam-y`, `caam_jr-y`, `dpaa2_caam-y`) collect feature objects under the main module target. Debug builds add `-DDEBUG`; all builds define an empty `VERSION`.

State and persistence: no runtime state; affects build graph and compilation flags.

Dependencies and integration points: synchronized with `Kconfig` symbols and source files in this directory. `caamalg.c` is included only in `caam_jr` when `CRYPTO_DEV_FSL_CAAM_CRYPTO_API` is enabled.

Risks: object inclusion order determines which features are present in each module; stale Kconfig/Makefile mapping can produce missing symbols. Debug flag changes can expose verbose dumps and alter timing.

Test signals: all relevant Kconfig combinations should link, especially CAAM_JR with/without Crypto API, blob generation, debugfs, QI, and DPAA2.
