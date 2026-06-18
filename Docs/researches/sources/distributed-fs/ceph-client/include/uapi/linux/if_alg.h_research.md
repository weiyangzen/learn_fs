<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_alg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_alg.h

## Purpose
`if_alg.h` defines the AF_ALG userspace socket ABI for accessing kernel crypto algorithms.

## Important APIs, types, and functions
`struct sockaddr_alg` selects algorithm type, feature/mask values, and the legacy 64-byte algorithm name field. `struct sockaddr_alg_new` keeps the same prefix but exposes a flexible algorithm name for long names. `struct af_alg_iv` carries IV length and flexible IV bytes. Socket operation constants include `ALG_SET_KEY`, `ALG_SET_IV`, `ALG_SET_OP`, `ALG_SET_AEAD_ASSOCLEN`, `ALG_SET_AEAD_AUTHSIZE`, `ALG_SET_DRBG_ENTROPY`, and `ALG_SET_KEY_BY_KEY_SERIAL`. Operation values include `ALG_OP_DECRYPT` and `ALG_OP_ENCRYPT`.

## Control flow
User space creates an `AF_ALG` socket, binds it to an algorithm type/name, sets key material or a key-serial reference and per-operation controls, accepts an operation socket, then sends data and receives transformed output. AEAD and skcipher operations use control messages for IV, operation direction, associated data length, and auth tag size; DRBG users can provide entropy through the dedicated option.

## State and persistence behavior
The parent socket stores algorithm and key state. Accepted operation sockets carry per-request IV, direction, associated-data length, and buffered data until completion or close.

## Dependencies and integration points
It depends on UAPI socket types and integrates with the kernel crypto API, skcipher, hash, RNG, AEAD, kTLS/userspace crypto tooling, and test suites.

## Risks and test signals
Risks include leaking key material, missing auth tag size, incorrect associated-data length, IV reuse, partial send/recv handling, long algorithm-name compatibility, invalid key serials, and unsupported algorithm names. Test signals include `algif_*` selftests, known-answer crypto vectors, AEAD failure tests, zero-length messages, splice/sendmsg paths, DRBG entropy tests, and key/IV length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_alg.h -->
