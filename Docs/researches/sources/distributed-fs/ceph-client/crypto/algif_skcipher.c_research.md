# sources/distributed-fs/ceph-client/crypto/algif_skcipher.c

Purpose: implements the AF_ALG userspace adapter for symmetric key ciphers, converting socket input/output buffers into `skcipher_request`s while supporting streaming state export/import, block-size chunking, synchronous and AIO operation, and nokey transitions.

Important APIs, types, and functions: key functions are `skcipher_sendmsg()`, `algif_skcipher_export()`, `algif_skcipher_done()`, `_skcipher_recvmsg()`, `skcipher_recvmsg()`, `skcipher_check_key()`, nokey send/recv wrappers, `skcipher_bind()`, `skcipher_release()`, `skcipher_setkey()`, `skcipher_sock_destruct()`, accept helpers, and `algif_type_skcipher`.

Control flow and behavior: sendmsg delegates to `af_alg_sendmsg()` with cipher IV size. Receive waits until data exists and, when streaming, at least one chunk is available. It allocates a request, maps RX buffers, limits non-final processing to full chunks, pulls TX SGL bytes, sets crypt parameters, imports saved state if continuing, and runs encrypt/decrypt. If `CRYPTO_SKCIPHER_REQ_NOTFINAL` is set, completion exports cipher state into the child context for the next receive.

State and persistence: child `af_alg_ctx` stores IV, TX SGL list, direction, used bytes, optional exported cipher state, wait object, and inflight flag. Parent stores the `crypto_skcipher` tfm. Exported state persists across multiple recvmsg calls on the same child stream.

Dependencies and integration points: depends on AF_ALG core, skcipher API, scatterlists, socket ops, and cmsgs for IV and encrypt/decrypt direction. It registers AF_ALG type name `skcipher`.

Risks and correctness concerns: streaming partial-block handling must never process incomplete chunks unless final. Exported state allocation uses `GFP_ATOMIC` in completion and must be cleaned on import or destruction. Partial user receive buffers affect how much TX data is consumed. AIO allows only one inflight request per child.

Test signals: AF_ALG skcipher vectors for CBC/CTR/XTS-style algorithms, `MSG_MORE` streaming, short receive buffers, non-final state export/import, nokey transition, AIO completion path, invalid partial block rejection, IV sizes, and cleanup of exported state on errors and socket close.
