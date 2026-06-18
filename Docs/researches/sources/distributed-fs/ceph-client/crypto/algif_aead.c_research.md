# sources/distributed-fs/ceph-client/crypto/algif_aead.c

Purpose: implements the AF_ALG userspace adapter for AEAD algorithms, translating socket sendmsg/recvmsg operations into `aead_request`s with TX/RX scatterlists, associated data, IVs, tags, synchronous and AIO completion paths, and nokey handling.

Important APIs, types, and functions: main functions are `aead_sendmsg()`, `_aead_recvmsg()`, `aead_recvmsg()`, `aead_check_key()`, nokey send/recv wrappers, `aead_bind()`, `aead_release()`, `aead_setauthsize()`, `aead_setkey()`, `aead_sock_destruct()`, accept helpers, and `algif_type_aead`.

Control flow and behavior: parent bind allocates a `crypto_aead`; accepted children allocate `af_alg_ctx` and IV storage. Sendmsg delegates to `af_alg_sendmsg()` with the AEAD IV size. Receive waits for data, verifies AAD/tag minimums, computes output length, allocates an async request, maps user output buffers to RX SGLs, pulls the relevant TX SGL bytes, copies AAD to output, sets crypt/ad fields, and runs encrypt/decrypt either synchronously or through AIO. Nokey ops re-check the parent tfm and switch the child out of nokey state once a key is available.

State and persistence: child socket context stores IV, TX SGL list, assoclen, operation direction, used bytes, wait object, and inflight state inherited from AF_ALG. Parent socket stores the AEAD tfm and nokey refcounts.

Dependencies and integration points: depends on `af_alg.c` helpers, AEAD core APIs, socket proto ops, scatterlist copy helpers, and userspace cmsgs `ALG_SET_IV`, `ALG_SET_OP`, and `ALG_SET_AEAD_ASSOCLEN`.

Risks and correctness concerns: AEAD length arithmetic must handle encryption tag expansion and decryption tag consumption without underflow. AAD is copied into output separately, so in-place expectations are subtle. Auth failure `-EBADMSG` must propagate even after partial loop progress. AIO supports only one inflight request per child.

Test signals: AF_ALG AEAD known-answer tests for encrypt/decrypt, AAD-only and empty payload cases, short tag/input rejection, partial receive buffers, nokey accept then setkey, authsize setsockopt, AIO path, in-place userspace buffers, and authentication failure propagation.
