# sources/distributed-fs/ceph-client/crypto/af_alg.c

Purpose: implements the PF_ALG userspace socket family core and shared helpers used by hash, skcipher, AEAD, and RNG AF_ALG adapters. It handles type registration, bind/setkey/accept, socket lifecycle, control messages, TX/RX scatterlists, memory accounting, waits, polling, and async request cleanup.

Important APIs, types, and functions: exported helpers include `af_alg_register_type()`, `af_alg_unregister_type()`, `af_alg_release()`, `af_alg_release_parent()`, `af_alg_accept()`, `af_alg_free_sg()`, `af_alg_count_tsgl()`, `af_alg_pull_tsgl()`, `af_alg_wmem_wakeup()`, `af_alg_wait_for_data()`, `af_alg_sendmsg()`, `af_alg_free_resources()`, `af_alg_async_cb()`, `af_alg_poll()`, `af_alg_alloc_areq()`, and `af_alg_get_rsgl()`.

Control flow and behavior: `alg_create()` creates `SOCK_SEQPACKET` PF_ALG sockets. `bind()` looks up or autoloads an `af_alg_type`, allocates a parent algorithm object, and installs it if no accepted children exist. `setsockopt()` configures keys, AEAD authsize, or DRBG entropy before connection. `accept()` creates operation sockets and may use nokey ops until a key is provided. `af_alg_sendmsg()` stores input pages in a chained TX SGL, parses IV/op/assoclen cmsgs, supports `MSG_MORE` and `MSG_SPLICE_PAGES`, and enforces socket send buffer limits. Receive-side helpers pin/extract output iovecs into RX SGLs and async callbacks release resources.

State and persistence: global `alg_types` is protected by `alg_types_sem`. Parent sockets hold algorithm type/private pointers and refcounts; child sockets hold `af_alg_ctx` state such as TX SGL list, IV, operation, used bytes, more/init flags, receive accounting, and at most one inflight AIO request. Pages may be pinned until request cleanup or socket destruction.

Dependencies and integration points: integrates with Linux sockets, net proto registration, module autoloading (`algif-%s`), keyrings for `ALG_SET_KEY_BY_KEY_SERIAL`, LSM hooks, scatterlists, iov iter extraction, poll/wait queues, and per-type modules `algif_hash`, `algif_skcipher`, `algif_aead`, and `algif_rng`.

Risks and correctness concerns: user-controlled lengths and cmsgs require strict validation. Page pin/unpin, send/receive accounting, SGL chaining, and partial pulls are high-risk for leaks or UAFs. Locking across parent/child sockets and nokey refcounts must prevent setkey races with accepted sockets. Only one AIO request per child is allowed; violating cleanup paths can strand `ctx->inflight`.

Test signals: AF_ALG bind/setkey/accept/sendmsg/recvmsg tests, nokey-to-key transition, keyring-based setkey, splice-page input, nonblocking waits, poll readiness, AIO completion, cancellation/error cleanup, large SGL chains, partial receive buffers, module autoload, and memory leak/pin accounting tests.
