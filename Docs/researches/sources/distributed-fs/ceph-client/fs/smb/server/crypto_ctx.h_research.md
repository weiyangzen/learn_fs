# sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.h

Purpose: declares KSMBD's reusable AEAD crypto context type and pool APIs for SMB3 encryption.

Important APIs/types/functions: enum values identify `CRYPTO_AEAD_AES_GCM`, `CRYPTO_AEAD_AES_CCM`, and `CRYPTO_AEAD_MAX`. `struct ksmbd_crypto_ctx` contains a list node and an array of cached `struct crypto_aead *`. `CRYPTO_GCM(ctx)` and `CRYPTO_CCM(ctx)` select the cached transform. Public functions create/destroy the pool, acquire GCM/CCM-capable contexts, and release borrowed contexts.

Control flow: callers initialize the pool at server startup, acquire a context for each encrypted/decrypted message, use the transform selected by cipher type, then release the context after the crypto request completes.

State and persistence behavior: the header declares a runtime cache object only. Contexts are not persistent storage and should not be assumed to retain request-specific keying safely.

Dependencies and integration points: depends on `<crypto/aead.h>` and list infrastructure through includers. It integrates with `auth.c` and KSMBD server startup/shutdown.

Risks: enum values start at 16, so the `ccmaes` array is sparse; any code iterating or sizing must use `CRYPTO_AEAD_MAX`, not a count of two. Callers must handle NULL acquisition on unsupported IDs or allocation failure.

Test signals: build coverage, encrypted SMB3 requests for CCM and GCM, pool create/destroy paths, and failure injection around transform allocation.
