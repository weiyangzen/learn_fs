# sources/distributed-fs/ceph-client/crypto/algif_hash.c

Purpose: implements the AF_ALG userspace adapter for hash algorithms, supporting streaming sendmsg, digest recvmsg, accepted-state cloning, keyed hash nokey transitions, and hash result buffering.

Important APIs, types, and functions: defines `struct hash_ctx` and functions `hash_alloc_result()`, `hash_free_result()`, `hash_sendmsg()`, `hash_recvmsg()`, `hash_accept()`, `hash_check_key()`, nokey wrappers, `hash_bind()`, `hash_release()`, `hash_setkey()`, `hash_sock_destruct()`, accept helpers, and `algif_type_hash`.

Control flow and behavior: sendmsg extracts user pages into a temporary SG table, initializes the request when starting a new stream, then chooses digest/update/finup depending on whether data continues and `MSG_MORE` is set. Zero-length sends can finalize a pending stream. Recvmsg allocates a digest buffer, finalizes if needed, truncates user length with `MSG_TRUNC`, copies the digest, then frees the result. `accept()` can clone an in-progress hash by exporting state from the existing request and importing it into the new child.

State and persistence: each child socket holds one `ahash_request`, optional result buffer, temporary SG state, wait object, context length, and `more` flag. Parent holds the `crypto_ahash` tfm. Exported hash state is temporary during accept cloning.

Dependencies and integration points: depends on `af_alg.c`, ahash APIs, socket proto ops, iov extraction into SG tables, and keyed hash flags. It registers AF_ALG type name `hash`.

Risks and correctness concerns: result lifetime is subtle: previous non-stream results are discarded on a new request, and errors must free partial results. Export/import during accept must hold the source socket lock while preserving state consistency. Pinned SG pages must always be released. Nokey refcounting must avoid racing parent key updates.

Test signals: AF_ALG hash digest and streaming vectors, `MSG_MORE` boundaries, zero-length send/recv behavior, short receive with `MSG_TRUNC`, accept clone of in-progress HMAC/hash, nokey keyed hashes, nonblocking behavior, and SG extraction error cleanup.
