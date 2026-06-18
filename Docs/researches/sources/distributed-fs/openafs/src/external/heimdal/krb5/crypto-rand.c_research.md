# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-rand.c

Purpose: provides krb5 random block generation backed by OpenSSL/hcrypto RAND with one-time seeding.

Important APIs/types/functions: `seed_something()` loads an optional RAND seed file, probes `RAND_status()`, optionally reads an EGD socket path from krb5 config, writes the seed file back, and reports success/failure. `krb5_generate_random_block()` is the public generator.

Control flow: first generator call locks `crypto_mutex`, seeds once, sets `rng_initialized`, unlocks, and then calls `RAND_bytes()`. Subsequent calls skip seeding and directly request random bytes. Failure to seed or generate aborts the process with `krb5_abortx()`.

State and persistence behavior: `rng_initialized` is a static process-local flag protected during initialization. The RAND seed file may be read and rewritten, so host-level RNG persistence can be affected.

Dependencies and integration points: uses RAND APIs, file I/O with `O_CLOEXEC` and `rk_cloexec()`, krb5 config lookup for `libdefaults/egd_socket`, and the Heimdal mutex abstraction. All random key, confounder, and checksum confounder generation flows depend on this function.

Risks: fatal abort on RNG failure is deliberate but high impact. Seed-file entropy is explicitly added with zero entropy estimate. The EGD path is legacy and config-sensitive. Correct mutex use is important for threaded callers.

Test signals: single and concurrent first-call initialization, RAND failure injection, seed-file open/read/write behavior, and generation of requested byte lengths.
