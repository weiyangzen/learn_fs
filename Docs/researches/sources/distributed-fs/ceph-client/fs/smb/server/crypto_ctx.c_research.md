# sources/distributed-fs/ceph-client/fs/smb/server/crypto_ctx.c

Purpose: implements a small pool of reusable AEAD crypto contexts for SMB3 encryption/decryption, reducing repeated allocation of AES-GCM/AES-CCM transform objects under request load.

Important APIs/types/functions: internal `struct crypto_ctx_list` tracks a spinlock, available context count, idle context list, and waitqueue. Public APIs are `ksmbd_crypto_create()`, `ksmbd_crypto_destroy()`, `ksmbd_crypto_ctx_find_gcm()`, `ksmbd_crypto_ctx_find_ccm()`, and `ksmbd_release_crypto_ctx()`. Helpers allocate/free AEAD transforms for `gcm(aes)` and `ccm(aes)`.

Control flow: module initialization calls `ksmbd_crypto_create()` to initialize the pool and seed one idle context. Encryption code calls a find function, which removes an idle context if available or allocates a new context while the count is at or below `num_online_cpus()`. If the pool is over the CPU-count cap, callers wait for an idle context. The requested AEAD transform is lazily allocated within the borrowed context. Release returns contexts to the idle list when under the cap or frees them when above it. Destroy frees idle contexts during shutdown.

State and persistence behavior: `ctx_list` is process-wide runtime state. It persists only while the module/server is initialized. Individual `struct ksmbd_crypto_ctx` objects cache AEAD transform pointers for reuse across requests; keys are set per operation by `auth.c`, so no stable key material should persist as pool state beyond crypto transform internals.

Dependencies and integration points: depends on Linux crypto AEAD API, spinlocks, waitqueues, CPU count, lists, and KSMBD allocation flags. It is consumed by `ksmbd_crypt_message()` for SMB3 transform handling.

Risks: wait paths assume a context will eventually be returned; leaks in encryption error paths can stall future requests. `avail_ctx` accounting must remain balanced across allocation failure, wait, release, and destroy. Context reuse requires every operation to set key/authsize before use. Destroy only walks idle contexts, so shutdown ordering must ensure no borrowed contexts remain.

Test signals: concurrent encrypted I/O across more workers than CPUs, allocation-failure injection, both AES-GCM and AES-CCM paths, AES-128 and AES-256 key setting, server shutdown while encrypted requests drain, and lockdep/refcount/leak checks.
