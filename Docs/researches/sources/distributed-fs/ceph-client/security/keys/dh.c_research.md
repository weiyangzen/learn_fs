# sources/distributed-fs/ceph-client/security/keys/dh.c

Purpose: Implements Diffie-Hellman public/shared secret computation and optional SP800-108 counter-mode KDF using values stored in kernel user keys.

Important APIs/types/functions: Key helpers `dh_data_from_key()` and `dh_free_data()`, KDF helpers `kdf_alloc()`, `kdf_dealloc()`, `keyctl_dh_compute_kdf()`, core `__keyctl_dh_compute()`, and syscall-facing `keyctl_dh_compute()`.

Control flow: The main function validates user pointers, copies DH params, optionally validates KDF spare fields and output/otherinfo length limits, loads the requested hash transform, reads prime/base/private key payloads with `KEY_NEED_READ`, encodes DH inputs, allocates crypto KPP `dh`, sets the secret, determines output length, and either reports required length, rejects too-small buffers, performs DH calculation, optionally appends KDF otherinfo and derives requested bytes, or copies raw DH output to userspace. Cleanup wipes sensitive buffers.

State and persistence: No persistent local state. It copies key payloads into temporary sensitive buffers and frees them before returning.

Dependencies and integration: Depends on key permission/validation, user key type payloads, crypto KPP DH, scatterlists, async crypto wait helpers, shash, and SP800-108 KDF.

Risks and test signals: Risks include side-channel-sensitive buffer handling, user copy failures, key type restrictions, raw output length probing, KDF length limits, and crypto backend errors. Tests should cover permission denial, non-user keys, buffer query/overflow, KDF reserved fields, bad hash names, otherinfo copying, and known DH vectors.
