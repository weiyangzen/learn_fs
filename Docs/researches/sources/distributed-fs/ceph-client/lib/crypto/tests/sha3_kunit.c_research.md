# sources/distributed-fs/ceph-client/lib/crypto/tests/sha3_kunit.c

Purpose: KUnit suite for SHA3-256 template tests plus explicit SHA3-224/256/384/512 and SHAKE128/SHAKE256 one-shot and streaming-squeeze behavior.

Important APIs/types/functions: binds the shared template to `sha3_256_init()`, `sha3_update()`, and `sha3_final()`. Local tests cover `sha3_224()`, `sha3_256()`, `sha3_384()`, `sha3_512()`, `shake128()`, `shake256()`, `shake128_init()`, `shake256_init()`, `shake_update()`, and `shake_squeeze()`.

Control flow: basic SHA3/SHAKE tests hash a repeated sample sentence into output buffers padded with 8-byte guard regions and compare the full guarded arrays. NIST SHAKE tests check empty and 1600-bit sample inputs. The all-lengths test runs input lengths 0 through 4096, derives varied output lengths, hashes concatenated SHAKE outputs with SHA3-256, and compares a consolidated digest. The multi-squeeze test compares one-shot output to randomized sequences of `shake_squeeze()` calls. Guard-buffer tests run in-place SHAKE on buffers ending at the shared test buffer boundary.

State and persistence: temporary KUnit allocations and the shared random test buffer only; no persistent state. The SHAKE context is local per randomized trial.

Dependencies: `<crypto/sha3.h>`, generated vectors, KUnit, random helpers and lifecycle from `hash-test-template.h`.

Integration points: suite name `sha3`; validates both hash and extensible-output APIs in the crypto library.

Risks: consolidated all-length failures need bisection to find the exact bad length. Guard-buffer testing protects against overrun but only within the shared buffer model, not true unmapped pages.

Test signals: strong coverage for SHA3 digest sizes, SHAKE output-length handling, repeated squeeze semantics, NIST examples, and output overwrite boundaries.
