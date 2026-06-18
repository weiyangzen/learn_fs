<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/aes_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/aes_s390.c

Purpose: Implements CPACF-accelerated clear-key AES algorithms for s390: ECB, CBC, CTR, XTS, full-XTS, and GCM AEAD.

Important APIs/types/functions: Uses `struct s390_aes_ctx`, `struct s390_xts_ctx`, and `struct gcm_sg_walk`; registers `skcipher_alg` instances for `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `xts(aes)`, and `__xts(aes)`, plus `aead_alg gcm(aes)`. Key functions include `*_set_key()`, `*_crypt()`, fallback init/exit helpers, CTR block helpers, GCM scatterlist walkers, `gcm_aes_crypt()`, `aes_s390_register_skcipher()`, `aes_s390_init()`, and `aes_s390_fini()`.

Control flow: Module init queries CPACF KM, KMC, KMCTR, and KMA masks, registering only algorithms with matching hardware functions. ECB/CBC/CTR/XTS paths validate keys, choose function codes by key length, and run CPACF instructions over skcipher walks, falling back where needed. GCM builds the CPACF KMA parameter block, walks AAD and payload scatterlists, sets last-AAD/last-payload flags when final chunks are reached, writes tags on encrypt, and compares tags on decrypt.

State and persistence: Persistent module state includes CPACF function masks, the global CTR block page protected by `ctrblk_lock`, registered algorithm pointers, and per-transform AES key material/function codes. GCM parameter blocks and tags are stack-local and explicitly zeroed.

Dependencies and integration points: Integrates with the Linux crypto skcipher/AEAD APIs, CPACF instruction wrappers, scatterwalk/skcipher walk helpers, fallback crypto allocations, module CPU feature matching, and crypto selftests.

Risks: Scatterlist boundary handling in GCM is delicate because CPACF requires block-size progress and correct final flags. CTR uses a shared buffer and mutex. XTS key validation and fallback naming must match crypto API expectations. Tag comparison must remain constant-time via `crypto_memneq()`.

Test signals: Kernel crypto selftests for all AES modes and key sizes, GCM AAD-only/empty-payload/tag-failure cases, scatterlist fragmentation tests, FIPS mode, CPU masks with partial CPACF support, and module unload cleanup.

Source read size: 1046 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/aes_s390.c -->
