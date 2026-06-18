# sources/distributed-fs/openafs/src/external/heimdal/krb5/n-fold.c

Purpose: implements the Kerberos n-fold operation used by RFC3961 key derivation.

Important APIs/types/functions: internal `rr13()` rotates a bitstring right by 13 bits while duplicating into two buffers. `add1()` adds one's-complement byte arrays with carry handling optimized over aligned 32-bit chunks. `_krb5_n_fold()` folds an input byte string into an output key-sized byte string.

Control flow: `_krb5_n_fold()` allocates temporary storage sized to twice the larger of input and output plus rotation buffers, zeroes the output, copies the input, repeatedly adds output-sized chunks into the result, rotates the source by 13 bits, and continues until the cycle completes with no remainder.

State and persistence behavior: stateless. Temporary buffers are zeroed before free because they may contain key derivation material.

Dependencies and integration points: called by `_krb5_derive_key()` in `crypto.c`. Uses network-byte-order helpers for aligned arithmetic.

Risks: bit-level correctness is critical and hard to review. `add1()` assumes inputs are aligned to 4 bytes, which is true for malloc-backed buffers but important to preserve. Length zero inputs are not guarded here and should be rejected by callers.

Test signals: RFC3961 n-fold known-answer vectors for multiple input/output sizes, valgrind/ASan coverage for non-multiple-of-4 sizes, and derived-key known answers.
