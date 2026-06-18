<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/bpf_crypto_skcipher.c -->
# sources/distributed-fs/ceph-client/crypto/bpf_crypto_skcipher.c

## Purpose

`bpf_crypto_skcipher.c` exposes linear skcipher operations to the BPF crypto framework. It is an adapter from `struct bpf_crypto_type` callbacks to the kernel `crypto_lskcipher` API.

## Important APIs, Types, and Flow

The callback table `bpf_crypto_lskcipher_type` provides allocation, free, algorithm availability, setkey, encrypt, decrypt, IV size, state size, and flag access. Allocation calls `crypto_alloc_lskcipher(algo, 0, 0)`, and availability checks `crypto_has_skcipher()` constrained to `CRYPTO_ALG_TYPE_LSKCIPHER`. Encrypt and decrypt forward directly to `crypto_lskcipher_encrypt()` and `crypto_lskcipher_decrypt()` with source, destination, length, and state/IV pointer.

Module init registers the type as `"skcipher"` with `bpf_crypto_register_type()`, and exit unregisters it, warning if unregister fails.

## State, Dependencies, and Integration

The file has no independent cryptographic state. Transform lifetime is owned by BPF crypto callers through the callback interface. Dependencies are `linux/bpf_crypto.h`, `crypto/skcipher.h`, and the lskcipher subsystem. Integration points are BPF programs/helpers that request symmetric cipher support.

## Risks and Test Signals

Risks are type mismatch between skcipher and lskcipher names, lifetime handling across BPF object references, and surfacing child transform flags correctly. Test signals include BPF crypto selftests for allocation failure, unknown algorithms, key errors, IV/state size reporting, encrypt/decrypt round trips, and module unregister while no live references remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/bpf_crypto_skcipher.c -->
