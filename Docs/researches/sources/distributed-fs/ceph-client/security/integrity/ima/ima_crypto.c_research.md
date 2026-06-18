<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_crypto.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_crypto.c

## Purpose
Implements IMA cryptographic hashing for file data, in-memory buffers, template field arrays, and the boot aggregate. It also initializes hash transforms for the configured IMA algorithm and TPM PCR banks.

## Important APIs, Types, And Functions
- Initialization: `ima_init_crypto()`, internal `ima_init_ima_crypto()`, `ima_alloc_tfm()`, `ima_free_tfm()`.
- Hashing: `ima_calc_file_hash()`, `ima_calc_buffer_hash()`, `ima_calc_field_array_hash()`.
- Boot aggregate: `ima_calc_boot_aggregate()`, internal TPM PCR read and aggregate helpers.
- Global state: `ima_shash_tfm`, `ima_sha1_idx`, `ima_hash_algo_idx`, `ima_extra_slots`, `ima_algo_array`.

## Control Flow
Initialization allocates the default hash transform, maps TPM allocated banks to hash algorithms, and reserves extra slots for SHA1 and the IMA default algorithm when missing from TPM banks. File hashing reopens non-readable files read-only when possible, rejects O_DIRECT consistently, reads page-sized chunks with `integrity_kernel_read()`, and finalizes the digest. Template hashing serializes fields in native or canonical format and computes digests for SHA1 plus all mapped TPM banks. Boot aggregate reads PCRs 0-7 and, for non-SHA1, PCRs 8-9.

## State And Persistence
Crypto transforms and algorithm descriptors are boot-lifetime state. Hash results are stored by callers in `ima_digest_data`, template entries, or `ima_iint_cache`. TPM PCR values are external hardware state that influences the boot aggregate.

## Dependencies And Integration Points
Depends on Linux crypto shash APIs, TPM bank metadata and PCR reads, IMA canonical format, template descriptors, `integrity_kernel_read()`, and hash algorithm tables. `ima_api.c`, `ima_init.c`, and `ima_main.c` rely on these functions.

## Risks And Edge Cases
Unsupported TPM algorithms fall back to padded SHA1 template digests. Missing SHA1 transform is fatal because SHA1 remains required for legacy template output. Very large or changing files can cause read/hash mismatch behavior. O_DIRECT returns `-EINVAL` and is later conditionally tolerated only by policy.

## Test Signals
Boot logs for allocated hash algorithms, measurement entries with expected per-bank digests, correct canonical binary output, O_DIRECT audit behavior, successful boot aggregate as first measurement, and failure logs for unavailable crypto transforms or TPM communication errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_crypto.c -->
