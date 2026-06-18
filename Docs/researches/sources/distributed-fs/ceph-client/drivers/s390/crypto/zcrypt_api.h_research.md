# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.h

Purpose: declares the private zcrypt API shared by zcrypt card/queue/message-type drivers and pkey/EP11/CCA helpers. It defines device type constants, request operation identifiers, queue/card state objects, provider callbacks, retry tracking, flags, globals, and exported function prototypes.

Important APIs and types: `enum crypto_ops` indexes speed ratings for RSA, CRT, hwrng, and secure-key operations. `struct zcrypt_track` stores retry count, last qid, and last return code for penalized reselection. `ZCRYPT_XFLAG_USERSPACE` and `ZCRYPT_XFLAG_NOMEMALLOC` control buffer interpretation and AP message allocation. `struct zcrypt_ops` is the provider vtable for RSA modexpo, RSA CRT, CCA CPRB, EP11 CPRB, and RNG operations. `struct zcrypt_card` stores card list membership, queues, AP card pointer, online flag, userspace type/name, size limits, speed ratings, load, and request count. `struct zcrypt_queue` stores queue list membership, provider ops, AP queue pointer, online/load/request state, and reply message.

Control flow: the header contributes inline copy helpers `z_copy_from_user()` and `z_copy_to_user()` that switch between userspace copy functions and kernel `memcpy()` depending on flags. Iteration macros walk the global card list and per-card queues.

State and persistence: declares global list/lock state and mempool threshold, but owns no storage itself. Struct fields describe runtime AP card/queue registration state and current load, not persistent configuration.

Dependencies and integration: includes AP bus, s390 zcrypt ABI, and debug support. The prototypes connect card, queue, rng, message-type, and exported CCA/EP11 send paths across the crypto driver directory.

Risks: this header is an internal ABI; changing struct fields or callback signatures affects multiple drivers. Copy-helper misuse can turn a userspace pointer into an unchecked kernel pointer or vice versa. Load/request counters must be updated consistently by API users.

Test signals: build all zcrypt message providers, validate userspace and kernel-call send paths, verify retry tracking updates, exercise queue/card register/unregister paths, and confirm mempool threshold handling.
