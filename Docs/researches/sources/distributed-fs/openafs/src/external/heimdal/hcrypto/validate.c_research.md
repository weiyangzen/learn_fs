# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/validate.c

Purpose: performs built-in hcrypto self-validation before public EVP factory use.

Important APIs/types/functions: static `hc_tests` contains known-answer vectors for AES-256-CBC, 3DES-CBC, and RC4, with some AES-CFB8 and Camellia vectors disabled. `test_cipher` runs one vector through EVP encrypt/decrypt. `check_hmac` validates HMAC-SHA1 over four zero bytes with key `hello-world`. `hcrypto_validate` runs tests once.

Control flow: public EVP factories call `hcrypto_validate`. The function uses a static `validated` flag, increments it before running tests to avoid recursion, then tests each configured cipher vector and HMAC. Failures call `errx`, terminating the process. The comment states races are acceptable and duplicate runs are tolerated.

State and persistence: only the static `validated` flag persists. Test vectors are immutable static data. No output artifacts are written.

Dependencies and integration points: depends on `evp.h`, `hmac.h`, `roken`, and `err.h`. It is tightly coupled to EVP provider descriptors and guards broad hcrypto use inside the process.

Risks and test signals: self-validation can terminate production processes on mismatch, is not thread-synchronized, covers only a subset of algorithms, and sets `validated` before tests complete. Useful signals are successful process startup using EVP factories, deliberate failure injection proving abort behavior, expanded known-answer vectors, and multi-thread first-use tests.
