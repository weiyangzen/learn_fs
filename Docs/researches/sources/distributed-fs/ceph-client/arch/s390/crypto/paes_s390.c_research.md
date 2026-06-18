<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/paes_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/paes_s390.c

Purpose: Implements s390 protected-key AES algorithms for ECB, CBC, CTR, and XTS through the async crypto-engine skcipher API.

Important APIs/types/functions: Defines `struct paes_protkey`, `struct s390_paes_ctx`, `struct s390_pxts_ctx`, mode parameter/request structs, global CPACF masks, `paes_crypto_engine`, `ctrblk`, and module parameter `clrkey`. Key helpers are `make_clrkey_token()`, `paes_ctx_setkey()`, `pxts_ctx_setkey()`, `convert_key()`, `paes_convert_key()`, `pxts_convert_key()`, per-mode setkey/do_crypt/crypt/init/exit/do_one_request functions, and `paes_s390_init()/fini()`.

Control flow: Module init registers a `/dev/paes` pseudo miscdevice, starts a crypto engine, queries KM/KMC/KMCTR masks, and registers each protected-key algorithm only if hardware supports it. Setkey accepts protected-key tokens, and optionally clear keys when `clrkey=Y`, converting them through pkey APIs into protected keys. Requests are enqueued to the crypto engine and executed by per-mode `do_one_request()` callbacks. Each mode converts/refetches protected keys as needed and invokes CPACF functions; XTS supports full-key and two-key protected forms.

State and persistence: Module state includes the crypto engine, miscdevice, CPACF masks, shared CTR block page/mutex, and registered algorithm state. Transform contexts persist protected key blobs, key type/length, and fallback/conversion status; request contexts hold mode parameters and asynchronous completion state.

Dependencies and integration points: Integrates with s390 pkey token conversion/verification, CPACF PAES/PXTS functions, Linux crypto engine, skcipher API, miscdevice core, and crypto selftests.

Risks: Protected-key validity can change, so conversion and retry handling are security and correctness sensitive. Allowing clear-key input is gated by a module parameter and must remain explicit. Async engine lifecycle must be unwound correctly on partial registration failure. CTR shared buffer locking and XTS key-size/token interpretation are high-risk areas.

Test signals: Crypto selftests for PAES modes with protected tokens, clear-key-token mode when enabled, invalid/stale pkey token errors, async request cancellation/completion, partial CPACF support, module load/unload, and pkey subsystem integration tests.

Source read size: 1729 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/paes_s390.c -->
