# sources/distributed-fs/ceph-client/include/crypto/mldsa.h

Purpose: declares ML-DSA algorithm identifiers, public key and signature sizes, and verification entry point.

Important APIs, types, and flow: `enum mldsa_alg` selects ML-DSA-44, ML-DSA-65, or ML-DSA-87. Macros define public-key and signature byte sizes for each parameter set. `mldsa_verify()` validates a signature over a message with the chosen parameter set and public key.

State and persistence: verification is stateless from the header perspective; caller-provided key, message, and signature buffers are transient.

Dependencies and integration: depends on `linux/types.h` style crypto types and integrates with public-key signature verification paths that need post-quantum ML-DSA support.

Risks and test signals: risks include parameter-set size mismatch, signature malleability/encoding validation, and large stack/heap use in implementations. Signals include NIST/PQC known-answer vectors, wrong-size key/signature rejection, corrupted signature tests, and integration with `crypto_sig` or public-key verification paths.
