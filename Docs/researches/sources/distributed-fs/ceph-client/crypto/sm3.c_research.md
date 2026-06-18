# sources/distributed-fs/ceph-client/crypto/sm3.c

`sm3.c` registers SM3 as a shash algorithm backed by the shared SM3 library. It exposes Crypto API aliases `"sm3"` and `"sm3-lib"`.

The descriptor context is `struct sm3_ctx`, accessed through `SM3_CTX(desc)`. The module defines `crypto_sm3_init()`, `crypto_sm3_update()`, `crypto_sm3_final()`, `crypto_sm3_digest()`, `crypto_sm3_export_core()`, `crypto_sm3_import_core()`, and `sm3_alg`.

Module init registers `sm3_alg` with `crypto_register_shash()`. Runtime hash operations delegate directly to `sm3_init()`, `sm3_update()`, `sm3_final()`, or one-shot `sm3()`. Core export/import memcpy the full `struct sm3_ctx`. State is per shash descriptor, with no key material or persistent storage. Dependencies are `<crypto/sm3.h>`, `<crypto/internal/hash.h>`, and the generic shash frontend. Risks are context layout compatibility for export/import and keeping one-shot and incremental behavior equivalent. Test signals include known-answer vectors, incremental versus one-shot equivalence, export/import resume tests, alias allocation, and `tcrypt` SM3 modes.
