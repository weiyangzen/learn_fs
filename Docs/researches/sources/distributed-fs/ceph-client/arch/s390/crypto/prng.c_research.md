<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/prng.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/prng.c

Purpose: Provides the legacy s390 `/dev/prandom` interface backed by CPACF TDES PRNG or SHA512 PRNO DRNG, with optional TRNG seeding, FIPS conditional tests, sysfs attributes, reseeding controls, and module parameters.

Important APIs/types/functions: Defines module parameters `mode`, `chunksize`, and `reseed_limit`; structs `prng_ws_s`, `prno_ws_s`, and `prng_data_s`; global `prng_data`, `trng_available`, and `prng_errorflag`. Key functions include `generate_entropy()`, TDES seed/instantiate/read/deinstantiate paths, SHA512 selftest/instantiate/reseed/generate/read paths, `prng_open()`, sysfs show/store handlers, and `prng_init()/exit()`.

Control flow: Init requires KMC PRNG support, detects TRNG and SHA512 PRNO support, selects SHA512 unless TDES is forced or SHA512 unavailable, validates chunk/reseed limits, instantiates state, and registers the matching miscdevice. SHA512 mode runs a NIST-vector selftest, seeds from TRNG or generated entropy plus TOD nonce, optionally records a previous block for FIPS conditional testing, reseeds when the PRNO reseed counter exceeds the limit, and serves reads in locked chunks. TDES mode mixes generated entropy into the KMC PRNG parameter block and serves reads with FIPS duplicate-block checks.

State and persistence: Persistent module state includes PRNG workspace, output buffer, previous-block buffer in FIPS mode, byte counter, mutex, mode, chunk size, reseed limit, and error flag. Sysfs exposes mode, strength, chunksize, byte counter, error flag, and reseed controls.

Dependencies and integration points: Integrates with CPACF KMC/PRNO/TRNG, miscdevice registration, sysfs device attributes, FIPS mode, user-copy helpers, TOD clock, and module CPU feature matching.

Risks: This interface is legacy and security-sensitive. Entropy estimation differs between TRNG and generated entropy paths. FIPS duplicate-block testing depends on chunk sizing. User reads must hold the mutex around shared state. Reseed controls and error flags must not mask failed selftests or generation failures.

Test signals: Module load in SHA512, TDES-forced, and unsupported modes; NIST selftest success/failure injection; FIPS conditional self-test; concurrent reads; sysfs reseed and reseed_limit behavior; byte counter accounting; and miscdevice cleanup.

Source read size: 910 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/prng.c -->
