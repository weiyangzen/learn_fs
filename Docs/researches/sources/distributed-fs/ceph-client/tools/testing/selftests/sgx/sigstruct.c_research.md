# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sigstruct.c

## Purpose
Computes SGX enclave measurement (`MRENCLAVE`) and populates a test `sgx_sigstruct` signed by the embedded RSA key.

## Important APIs, types, and functions
OpenSSL helpers allocate and free `q1q2_ctx`, reverse byte order, calculate Q1/Q2 values for SGX signature verification, drain crypto errors, and parse the RSA key from `sign_key`. Measurement helpers model ECREATE, EADD, and EEXTEND records using `mrenclave_ecreate()`, `mrenclave_eadd()`, `mrenclave_eextend()`, and `mrenclave_segment()`. Public entry `encl_measure()` fills SIGSTRUCT headers, attributes, modulus, mrenclave, signature, q1, and q2.

## Control flow
`encl_measure()` clears the sigstruct, seeds SGX header constants, loads the RSA key, initializes SHA256 measurement, commits ECREATE based on source size, iterates all enclave segments and pages, extends measured pages, finalizes `mrenclave`, hashes the header/body payload, signs it with RSA/SHA256, calculates Q1/Q2, and converts signature/modulus from big-endian to little-endian SGX layout.

## State and persistence
State is transient OpenSSL `BIGNUM`, `BN_CTX`, `EVP_MD_CTX`, `RSA`, digest buffers, and the output `encl->sigstruct`. No files are written.

## Dependencies and integration points
Depends on OpenSSL legacy RSA APIs, SGX UAPI struct layouts, the embedded key from `sign_key.S`, and segment metadata from `load.c`.

## Risks
OpenSSL 3 deprecations are suppressed; future API removal could break build. Measurement correctness depends on 64-byte record sizes, page iteration, byte-order conversions, and exact SGX struct packing. Unmeasured heap pages are intentionally added but skipped for EEXTEND.

## Test signals
Any crypto, measurement, signing, Q1/Q2, or digest-size failure makes `setup_test_encl()` fail, causing SGX tests to abort with initialization diagnostics.
