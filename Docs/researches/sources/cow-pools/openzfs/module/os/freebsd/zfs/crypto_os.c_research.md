# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/crypto_os.c

## Scope

FreeBSD OpenCrypto backend for ZFS encryption and HMAC. It implements SHA-512 HMAC helpers, creates AEAD crypto sessions for AES-GCM/AES-CCM, dispatches uio-backed cryptographic operations, and waits for async OpenCrypto completion.

## Main Interfaces

- HMAC: `crypto_mac_init()`, `crypto_mac_update()`, `crypto_mac_final()`, `crypto_mac()`.
- Session lifecycle: `freebsd_crypt_newsession()` and `freebsd_crypt_freesession()`.
- Dispatch: `freebsd_crypt_uio()` encrypts/decrypts authenticated uio payloads.
- Completion callbacks: `freebsd_zfs_crypt_done()` and synchronous no-op callback.

## State And Control Flow

`crypto_mac_init()` implements HMAC-SHA512 key normalization, ipad/opad setup, and inner/outer SHA512 context initialization. `crypto_mac_final()` completes inner and outer hashes, zeroes context/digest storage, and supports `mdsize == 0` for full digest output.

`freebsd_crypt_newsession()` maps ZFS crypt modes to OpenCrypto AEAD algorithms, validates AES key sizes, forces software crypto capability, initializes a mutex, and increments `crypt_sessions`. `freebsd_crypt_uio()` optionally creates a one-shot session, sets `crp_op`, `CRYPTO_F_CBIFSYNC`, `CRYPTO_F_IV_SEPARATE`, uio storage, AAD/payload/digest offsets, IV bytes, dispatches, frees the request, and frees temporary sessions.

`zfs_crypto_dispatch()` loops over `EAGAIN` and `ENOMEM`, sleeps briefly on memory pressure, and waits on `fs_done` for async sessions.

## Dependencies

Uses FreeBSD OpenCrypto, SHA512, ZFS `zio_crypt_info`, `crypto_key_t`, SPL UIO accessors, and kernel mutex/sleep APIs.

## Correctness Notes

Hardware crypto drivers are deliberately avoided because common FreeBSD offload drivers have AAD-length constraints unsuitable for ZFS. `session->fs_done` is reset on retry; async completion wakes sleepers on the `cryptop`. Sensitive key/HMAC intermediate buffers are zeroed after use.
