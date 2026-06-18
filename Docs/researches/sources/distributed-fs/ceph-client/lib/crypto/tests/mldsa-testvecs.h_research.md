# sources/distributed-fs/ceph-client/lib/crypto/tests/mldsa-testvecs.h

## Purpose
This header provides ML-DSA verification known-answer fixtures extracted from leancrypto. It defines a shared vector struct and one valid signature/public-key/message tuple for each supported parameter set: ML-DSA-44, ML-DSA-65, and ML-DSA-87.

## Important APIs, Types, and Data
- `struct mldsa_testvector` stores `enum mldsa_alg alg`, signature length, message length, public-key length, and pointers to signature, message, and public key byte arrays.
- `mldsa44_testvector`, `mldsa65_testvector`, and `mldsa87_testvector` each contain inline compound-literal byte arrays sized with the corresponding public-key and signature constants.
- Each vector uses a 64-byte message (`.msg_len = 64`) and parameter-specific `.pk_len` and `.sig_len` constants.
- The header uses `MLDSA44_PUBLIC_KEY_SIZE`, `MLDSA44_SIGNATURE_SIZE`, `MLDSA65_*`, and `MLDSA87_*` constants from `<crypto/mldsa.h>` through the including C file.

## Control Flow
The header has no executable code. `mldsa_kunit.c` includes it after defining parameter metadata, then passes each vector to common verification, mutation, malformed-signature, and benchmark helpers.

## State and Persistence Behavior
All fixtures are static const objects and immutable byte arrays in the test module. There is no runtime state and no persistence beyond the loaded module.

## Dependencies and Integration Points
The data integrates directly with `mldsa_verify()` tests in `mldsa_kunit.c`. It depends on ML-DSA enum and size constants, and on the signature encoding layout expected by the verifier and the negative tests: `ctilde || z || h`.

## Risks and Edge Cases
The negative tests in `mldsa_kunit.c` assume structural properties of these valid signatures, including enough nonzero hints for swapping and fewer than `omega` nonzero hints for extra-index testing. If vectors are replaced, those assumptions must be revalidated. Since only one valid vector per parameter set is present, this header is a correctness anchor but not exhaustive coverage of signature distributions.

## Test Signals
The vectors support positive verification for all three security levels, length validation, malformed `z` coefficient checks, malformed hint-vector checks, random bit mutation rejection, and benchmark measurements.
