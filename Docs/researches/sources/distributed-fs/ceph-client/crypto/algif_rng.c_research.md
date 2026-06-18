# sources/distributed-fs/ceph-client/crypto/algif_rng.c

Purpose: implements the AF_ALG userspace adapter for RNG algorithms, including normal random generation, optional CAVP test additional-data handling, seeding through setkey, and privileged entropy injection for DRBG validation.

Important APIs, types, and functions: structures are `struct rng_ctx` and `struct rng_parent_ctx`. Main functions include `rng_recvmsg()`, `rng_test_recvmsg()`, `rng_test_sendmsg()`, `rng_bind()`, `rng_release()`, `rng_sock_destruct()`, `rng_accept_parent()`, `rng_setkey()`, optional `rng_setentropy()`, and `algif_type_rng`.

Control flow and behavior: bind allocates a parent context and `crypto_rng`. Accept creates a child context sharing the parent DRNG state; if CAVP entropy was configured, it switches the child socket ops to test mode. Normal recvmsg generates at most 128 bytes per call. Test sendmsg stores additional input for the next generation; test recvmsg passes it to `crypto_rng_generate()` then wipes it.

State and persistence: parent context stores the DRNG pointer and optional entropy buffer. Child context stores DRNG pointer, context length, and one additional-data buffer for test mode. RNG state itself is inside the algorithm tfm and may be shared by multiple accepted sockets.

Dependencies and integration points: depends on AF_ALG core, `crypto/rng.h`, capability checks for `CAP_SYS_ADMIN`, optional `CONFIG_CRYPTO_USER_API_RNG_CAVP`, and userspace `ALG_SET_DRBG_ENTROPY`.

Risks and correctness concerns: output is capped to a stack buffer of 128 bytes; callers must loop for larger reads. CAVP entropy injection is intentionally privileged and test-only. Shared DRNG state across accepted sockets is documented but can surprise users expecting independent streams. Sensitive seed/additional/entropy buffers must be wiped on free.

Test signals: AF_ALG RNG read lengths 0, 1, 128, and larger; setkey seeding; CAVP additional data one-shot consumption; `CAP_SYS_ADMIN` enforcement for entropy; shared-state behavior across accepts; and failure propagation from unseeded RNG implementations.
