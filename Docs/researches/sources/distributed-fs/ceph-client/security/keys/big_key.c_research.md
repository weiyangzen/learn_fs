# sources/distributed-fs/ceph-client/security/keys/big_key.c

Purpose: Implements the `big_key` key type for payloads up to 1 MiB, storing small payloads in memory and large payloads encrypted in shmem so they can be swapped.

Important APIs/types/functions: Defines `struct big_key_payload`, `key_type_big_key`, and operations `big_key_preparse()`, `big_key_free_preparse()`, `big_key_revoke()`, `big_key_destroy()`, `big_key_update()`, `big_key_describe()`, `big_key_read()`, and `big_key_init()`.

Control flow: Preparse rejects empty, oversized, or missing data and charges a small quota. Payloads larger than `BIG_KEY_FILE_THRESHOLD` are encrypted with a per-key random ChaCha20-Poly1305 key, stored in an anonymous shmem file, and pinned by path; smaller payloads are copied into kmalloc memory. Read returns required length when no/too-small buffer is supplied, otherwise decrypts from shmem or copies memory payload. Revoke truncates shmem and clears quota; destroy drops path references and wipes key material; update destroys old positive payload after reserving quota.

State and persistence: Key payload stores data pointer or encryption key, shmem path, and plaintext length. Large ciphertext persists in tmpfs while the key lives.

Dependencies and integration: Uses key type framework, shmem, kernel read/write, random bytes, and ChaCha20-Poly1305.

Risks and test signals: Risks include nonce reuse if update semantics changed, encrypted file read/write size mismatches, sensitive buffer wiping, path reference leaks, and quota mismatch. Tests should cover threshold boundary, read length query, update/revoke/destroy, bad authentication tag, OOM/error cleanup, and swap-backed storage.
