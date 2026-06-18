<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/phmac_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/phmac_s390.c

Purpose: Implements asynchronous protected-key HMAC-SHA224/256/384/512 using CPACF PHMAC/KMAC functions and the Linux crypto engine.

Important APIs/types/functions: Defines `struct hash_walk_helper`, `struct phmac_protkey`, `struct phmac_tfm_ctx`, `union kmac_gr0`, `struct kmac_sha2_ctx`, `enum async_op`, `struct phmac_req_ctx`, and `struct hmac_clrkey_token`. Key functions include hash-walk helpers, `hash_key()`, `make_clrkey_token()`, `phmac_tfm_ctx_setkey()`, `convert_key()`, `phmac_convert_key()`, `phmac_kmac_update()`, `phmac_kmac_final()`, request operations `phmac_init/update/final/finup/digest`, `phmac_setkey()`, export/import, tfm init/exit, `phmac_do_one_request()`, and module init/exit.

Control flow: Init verifies SHA KLMD support for selftests, registers a `/dev/phmac` miscdevice, starts a crypto engine, and registers variants with available PHMAC KMAC subfunctions. Setkey accepts protected keys or optional clear-key tokens, normalizes overlong keys, converts to protected form, and prepares ipad/opad state. Async update/final/digest operations store request context and are completed by the crypto engine, which walks scatterlists and feeds CPACF KMAC/PHMAC.

State and persistence: Per-transform context stores protected key material, converted state, and digest sizes. Per-request context tracks the current async operation, hash state, partial scatterlist walk, and result buffer. Module state includes the engine, miscdevice, registered flags, and `clrkey` policy.

Dependencies and integration points: Depends on pkey APIs, CPACF KMAC/PHMAC/KLMD, ahash crypto-engine APIs, scatterlist kmap handling, miscdevice core, and crypto selftests.

Risks: Async hash continuation and export/import must maintain exact state across split updates. Protected-key conversion failures must not leak clear key material. Scatterlist walking in sleep/non-sleep contexts is subtle. Engine teardown must not race in-flight requests.

Test signals: ahash selftests for PHMAC variants, incremental and one-shot requests, export/import, invalid protected tokens, clear-key parameter coverage, high-fragmentation scatterlists, async completion stress, and module unload under load.

Source read size: 1074 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/phmac_s390.c -->
