# sources/distributed-fs/ceph-client/include/crypto/if_alg.h

Purpose: defines the in-kernel support contract for the AF_ALG user-space crypto socket family. It bridges sockets to crypto API transforms, scatter-gather buffering, synchronous waits, and asynchronous AEAD/skcipher requests.

Important APIs, types, and flow: `struct alg_sock` extends `struct sock` and tracks the parent listener, selected `af_alg_type`, transform-private data, and key/no-key references. `struct af_alg_type` is the per-algorithm vtable for bind, key/entropy/authsize setup, accept, release, proto ops, and module ownership. `af_alg_ctx` tracks TX SGLs, IV/state, AEAD associated-data length, send/receive accounting, operation direction, write/init/more flags, and in-flight AIO. Helpers such as `af_alg_sndbuf()`, `af_alg_rcvbuf()`, `af_alg_sendmsg()`, `af_alg_get_rsgl()`, `af_alg_alloc_areq()`, `af_alg_async_cb()`, and `af_alg_poll()` implement the common sendmsg/recvmsg/request lifecycle used by algorithm-specific AF_ALG frontends.

State and persistence: state is per socket and per request only. Buffer accounting is held in `ctx->used` and atomic `rcvused`; async lifetime is guarded by request ownership and socket references. No filesystem persistence exists.

Dependencies and integration: depends on `linux/if_alg.h`, net sockets, scatterlists, `crypto/aead.h`, `crypto/skcipher.h`, `crypto_wait`, and module ownership. It integrates with `algif_*` implementations and user ABI behavior for `sendmsg`, `recvmsg`, `accept`, AIO, and polling.

Risks and test signals: risks center on pinned-page lifetime, SGL accounting, no-key accept behavior, async completion races, and user-triggered memory growth. Signals include AF_ALG socket tests for key/no-key accept, large and fragmented iovecs, AEAD AAD lengths, partial reads/writes, AIO cancellation/completion, poll readiness, and memory-leak/pin accounting under error paths.
