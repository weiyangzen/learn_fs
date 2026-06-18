# sources/distributed-fs/ceph-client/net/sctp/auth.c

Purpose: implements SCTP-AUTH: HMAC selection, endpoint/association shared keys, association secret derivation, chunk authentication policy, HMAC computation, and key-management socket API helpers.

Important APIs/types/functions: `sctp_hmac_list` supports SHA1 and SHA256. `sctp_auth_key_put/create_key`, `sctp_auth_shkey_create/hold/release/destroy`, and `sctp_auth_destroy_keys()` manage key bytes and containers. Key-vector helpers implement RFC vector concatenation and ordering. `sctp_auth_asoc_copy_shkeys()` and `sctp_auth_asoc_init_active_key()` copy endpoint keys and compute active association secrets. Lookup helpers select shared keys and HMACs. `sctp_auth_send_cid()`/`recv_cid()` check chunk authentication policy. `sctp_auth_calculate_hmac()` writes SHA1/SHA256 digests. Endpoint/API helpers add chunk ids, set HMACs, set/activate/delete/deactivate keys, and initialize/free auth parameter buffers.

Control flow: endpoint init creates HMAC and CHUNKS parameters plus a null key. Association init copies endpoint keys and local AUTH parameters. After peer parameters are known, active-key init creates local/peer vectors, orders them numerically, concatenates endpoint key plus vectors, installs the association secret, and marks queued chunks requiring AUTH. Send/receive paths query chunk policy; AUTH chunk generation computes the digest over the AUTH chunk and subsequent packet bytes.

State and persistence: key state is volatile linked lists of `sctp_shared_key` plus sensitive `sctp_auth_bytes`, freed with `kfree_sensitive()`. Associations cache active key id, selected key, association secret, default HMAC, and peer auth parameters. Deactivated keys can remain until references drain and can notify user space.

Dependencies/integration: kernel SHA1/SHA256 HMAC helpers, SCTP endpoint/association/chunk structs, AUTH parameter ABI, outqueue chunk lists, ulpevents, socket option paths, and debug object counters.

Risks: parameter lengths must be validated before helper use. `sctp_auth_get_hmac()` trusts hmac ids enough to index the table. `sctp_auth_set_key()` duplicates a `memcpy()` into the new key, likely harmless but suspicious. Active-key replacement rollback must be correct on allocation failure. Forbidden chunk ids in CHUNKS parameters are ignored intentionally.

Test signals: auth init/free, HMAC list validation requiring SHA1, unsupported HMAC rejection, key add/replace/delete/activate/deactivate for endpoint/association, active-key recomputation rollback, vector ordering with leading zeros, SHA1/SHA256 digest generation, forbidden chunk id handling, queued chunk auth marking, and sensitive key refcount/free.
