# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.c

Purpose: implements the ARCFOUR/RC4 stream cipher.

Important APIs/types/functions: `RC4_set_key` performs key scheduling over a 256-entry permutation; `RC4` generates keystream bytes and XORs input to output while updating key stream indices.

Control flow: key setup initializes the state array to identity, then walks 256 entries swapping based on key bytes modulo key length. Encryption/decryption repeatedly advances `x`, updates `y`, swaps state entries, selects a keystream byte from `state[state[x] + state[y]]`, and XORs it with input. The same operation decrypts.

State and persistence: `RC4_KEY` stores mutable `x`, `y`, and permutation state; every `RC4` call advances it, so the context is not reusable for independent messages without rekeying.

Dependencies and integration points: includes `rc4.h` and is exposed through EVP RC4 descriptors and validation tests.

Risks and test signals: RC4 is cryptographically obsolete, key length zero would divide by zero, and state reuse is dangerous. Tests should cover published ARCFOUR vectors, incremental calls matching one-shot output, in-place operation, and rejection or caller avoidance of zero-length keys.
