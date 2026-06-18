# sources/distributed-fs/ceph-client/drivers/char/hw_random/optee-rng.c

Purpose: OP-TEE trusted application RNG driver that bridges the Linux hwrng core to a TEE RNG TA.

Important APIs, types, and functions: `struct optee_rng_private`, global `pvt_data`, `get_optee_rng_data()`, `optee_rng_read()`, `optee_rng_init()`, `optee_rng_cleanup()`, `get_optee_rng_info()`, and TEE client probe/remove.

Control flow: probe opens an OP-TEE context, opens a session using the device UUID, queries data rate and quality, registers hwrng, and stores the device pointer. hwrng init allocates a shared memory buffer. Reads cap requests at 4 KiB, invoke `TA_CMD_GET_ENTROPY` with shared memory, copy returned bytes, and optionally sleep once based on reported data rate.

State and persistence: global singleton state stores TEE context/session, data rate, shared memory pool, quality, and hwrng object. Remove closes session/context; hwrng cleanup frees shared memory.

Dependencies and integration: TEE client bus, OP-TEE implementation matching, shared memory APIs, UUID matching, and hwrng core.

Risks and test signals: singleton state limits multi-device safety; `pvt_data.dev` is assigned after registration, so early init/read error logging may see NULL if ordering changes. Tests should cover TA errors including health-test failure, shared memory allocation/free, session open unwind, max request capping, wait timing, and remove while hwrng is registered.
