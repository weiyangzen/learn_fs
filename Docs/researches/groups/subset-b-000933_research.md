# Research: subset-b-000933

Grouped research for crypto sources under `sources/distributed-fs/ceph-client/crypto`. Each section is bounded for reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_user.c -->
# sources/distributed-fs/ceph-client/crypto/crypto_user.c

## Purpose
`crypto_user.c` implements the userspace configuration and reporting API for the Linux kernel crypto subsystem over `NETLINK_CRYPTO`. It lets privileged userspace add, remove, and reprioritize crypto algorithms or instances, delete the default RNG, and query or dump algorithm metadata. It is control-plane code, not data-plane cryptography.

## Important APIs, Types, And Functions
- `struct crypto_dump_info` carries the input skb, output skb, netlink sequence, and reply flags used by single and dump reports.
- `crypto_alg_match()` scans `crypto_alg_list` under `crypto_alg_sem`, filters by `cru_type`/`cru_mask`, skips larvals, matches by driver name for exact requests or by algorithm name for non-exact lookups, and takes a module reference with `crypto_mod_get()`.
- `crypto_report_one()`, `crypto_report_alg()`, `crypto_report()`, and `crypto_dump_report()` format `CRYPTO_MSG_GETALG` replies, including priority and type-specific reports via `alg->cra_type->report` or the local cipher report fallback.
- `crypto_update_alg()`, `crypto_del_alg()`, `crypto_add_alg()`, and `crypto_del_rng()` implement the mutating netlink commands. Mutations require `CAP_NET_ADMIN`.
- `crypto_user_rcv_msg()` dispatches messages through `crypto_dispatch[]`, handles multipart dump setup with `netlink_dump_start()`, and parses attributes with `nlmsg_parse_deprecated()`.
- Per-net operations `crypto_netlink_init()` and `crypto_netlink_exit()` create and release `net->crypto_nlsk`.

## Control Flow
Incoming netlink packets enter `crypto_netlink_rcv()`, which serializes all configuration handling with `crypto_cfg_mutex`, then passes messages to `crypto_user_rcv_msg()`. GETALG with `NLM_F_DUMP` computes a conservative dump allocation from the number of registered algorithms and starts a netlink dump. Non-dump requests are size-checked against `crypto_msg_min[]`, parsed against `crypto_policy[]`, and dispatched to the selected `doit` handler. Reply generation builds one netlink message per algorithm and appends algorithm-specific attributes until the skb is full.

Add, update, and delete operations all find algorithms through `crypto_alg_match()`. `NEWALG` forces module lookup/loading through `crypto_alg_mod_lookup()` and optionally sets priority. `UPDATEALG` removes dependent spawns before modifying priority so templates are refreshed. `DELALG` only unregisters crypto template instances and refuses core algorithms or busy instances.

## State And Persistence
Persistent state is the global crypto algorithm registry and each net namespace's `crypto_nlsk` socket. The file does not persist data across reboot. It mutates in-memory algorithm priority, algorithm instance registration, and default RNG selection. References acquired by `crypto_alg_match()` are released with `crypto_mod_put()`.

## Dependencies And Integration Points
The file depends on kernel netlink, per-net namespaces, `crypto_alg_list`, `crypto_alg_sem`, template instance unregister helpers, RNG helpers, and type-specific crypto report callbacks. Userspace sees this through `NETLINK_CRYPTO` and `struct crypto_user_alg`/`CRYPTOCFGA_*` attributes from `<linux/cryptouser.h>`.

## Risks And Edge Cases
The main risk is control-plane privilege and registry integrity. The code explicitly rejects non-null-terminated `cru_name` and `cru_driver_name`, checks `CAP_NET_ADMIN` for mutations, refuses priority changes without exact driver matching, and prevents unregistering non-instance core algorithms. Dumping walks the global algorithm list under read lock; large registries can still lead to multi-message output and `-EMSGSIZE` driven pagination. Refcount threshold `> 2` is used to detect busy instances, so changes to reference ownership semantics would need careful review.

## Test Signals
Test coverage is indirect through crypto self-tests and userspace netlink tooling. Useful signals include successful `CRYPTO_MSG_GETALG` single and dump paths, rejection of malformed unterminated names, privilege failures for mutating commands, priority update effects on algorithm selection, and delete failures for busy or non-instance algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ctr.c -->
# sources/distributed-fs/ceph-client/crypto/ctr.c

## Purpose
`ctr.c` registers the `ctr` skcipher template and the `rfc3686` wrapper template. CTR turns a block cipher into a stream cipher by encrypting a counter block and XORing the keystream with input. RFC3686 adapts CTR for IPsec-style nonce/IV/counter layout and key format.

## Important APIs, Types, And Functions
- `crypto_ctr_crypt()` is both encrypt and decrypt for the base CTR template.
- `crypto_ctr_crypt_segment()`, `crypto_ctr_crypt_inplace()`, and `crypto_ctr_crypt_final()` handle out-of-place full blocks, in-place full blocks, and final partial blocks.
- `crypto_ctr_create()` allocates a simple skcipher instance, validates child block size, forces blocksize to 1, sets `chunksize`, and registers the instance.
- `struct crypto_rfc3686_ctx` stores the spawned child skcipher and the per-key nonce suffix.
- `crypto_rfc3686_setkey()` splits the last `CTR_RFC3686_NONCE_SIZE` bytes from the key as nonce and sets the remaining key on the child.
- `crypto_rfc3686_crypt()` builds the 16-byte RFC3686 counter block as nonce || request IV || big-endian 1 and forwards to child CTR encryption.
- `crypto_ctr_tmpls[]` registers `ctr` and `rfc3686`.

## Control Flow
The CTR walk starts with `skcipher_walk_virt()`. For each walk segment, it processes full blocks using the child's raw cipher encrypt function, increments the IV/counter with `crypto_inc()`, and returns any residual bytes to the skcipher walk. A trailing partial block is handled by encrypting one counter block into an aligned temporary keystream and XOR-copying only the remaining bytes.

The RFC3686 template is layered over an already-stream-like child, normally `ctr(aes)`. Setkey saves the nonce and forwards the key. Each request allocates an aligned subrequest context, synthesizes a fresh IV/counter block, and calls `crypto_skcipher_encrypt()` on the child for both encryption and decryption.

## State And Persistence
CTR state is request-local except for the child transform and, for RFC3686, the nonce saved in the transform context. The request IV is updated by the skcipher walk as the counter advances. No state is persisted outside the transform/request lifetime.

## Dependencies And Integration Points
The file depends on simple skcipher instance helpers, raw cipher APIs, `crypto_inc()`, and CTR constants from `<crypto/ctr.h>`. It is used by algorithms such as `ctr(aes)` and `rfc3686(ctr(aes))`, including AEAD compositions in testmgr such as `authenc(...,rfc3686(ctr(aes)))`.

## Risks And Edge Cases
CTR security depends on never reusing key/nonce/IV counter streams. The code enforces block size >= 4 and 4-byte alignment for `crypto_inc()`, and RFC3686 enforces a 16-byte IVsize child and stream-cipher blocksize. The implementation does not detect counter wrap or nonce reuse; callers and protocols must guarantee uniqueness. Partial blocks are allowed because CTR is registered as blocksize 1.

## Test Signals
`testmgr.h` contains CTR vectors for AES, DES, DES3, SM4, and other ciphers, plus RFC3686 AES/SM4 vectors. Useful tests cover in-place and out-of-place skcipher operation, non-block-multiple lengths, request splitting, and RFC3686 key suffix nonce parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ctr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cts.c -->
# sources/distributed-fs/ceph-client/crypto/cts.c

## Purpose
`cts.c` implements the `cts` skcipher template for CBC ciphertext stealing as described by RFC2040 and used by RFC3962. It permits CBC-like encryption of messages that are at least one block but not necessarily a multiple of the block size, without expanding ciphertext length.

## Important APIs, Types, And Functions
- `struct crypto_cts_ctx` holds the spawned CBC child skcipher.
- `struct crypto_cts_reqctx` stores temporary scatterlists, the final-block offset, and the embedded child request.
- `crypto_cts_encrypt()` and `crypto_cts_decrypt()` are the public skcipher operations.
- `cts_cbc_encrypt()` performs the stealing transform after the prefix CBC operation.
- `cts_cbc_decrypt()` reconstructs the penultimate ciphertext block, recovers the final partial plaintext, and decrypts the final full block.
- `crypto_cts_init_tfm()` computes request size for child request context plus aligned scratch block space.
- `crypto_cts_create()` only accepts child algorithms whose name begins with `cbc(` and whose IV size equals block size.

## Control Flow
Encryption rejects messages smaller than one block. A one-block message is delegated directly to the CBC child. Longer messages first encrypt the prefix through the last full block boundary before the partial tail. Completion continues in `cts_cbc_encrypt()`, which reads the last encrypted full block, overlays the partial plaintext, writes the stolen ciphertext layout, and encrypts the adjusted final full block in place.

Decryption also delegates exact one-block requests. For longer inputs, it saves the IV or previous ciphertext block into aligned scratch, decrypts the full-block prefix, and then `cts_cbc_decrypt()` uses the saved block and partial tail to reconstruct and decrypt the penultimate block. Async child completions are bridged through `crypto_cts_encrypt_done()`, `crypto_cts_decrypt_done()`, and `cts_cbc_crypt_done()`.

## State And Persistence
The transform context owns the child skcipher. Request-local state includes final offset, temporary scatterlist, embedded request, and aligned scratch for the saved block. Sensitive stack buffer `d` is wiped with `memzero_explicit()`.

## Dependencies And Integration Points
The template wraps CBC skciphers and uses scatterwalk helpers for offsets and partial block copies. It integrates with the crypto template registry as `cts(...)`, and testmgr lists `cts(cbc(aes))`, `cts(cbc(paes))`, and `cts(cbc(sm4))` style entries.

## Risks And Edge Cases
The implementation is careful about the one-block case and rejects sub-block messages. The stealing logic is scatterlist-sensitive and depends on correct `offset = rounddown(nbytes - 1, bsize)`. Bugs here tend to appear only with partial tails, in-place requests, split scatterlists, or async child completion. The template assumes a CBC child; non-CBC names are rejected by prefix check rather than deeper semantic validation.

## Test Signals
`testmgr.h` includes `cts_mode_tv_template` and SM4 CTS vectors. High-value tests include exact block length, one byte over a block, multiple blocks plus partial tail, in-place/out-of-place operation, fragmented scatterlists, and async child behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/deflate.c -->
# sources/distributed-fs/ceph-client/crypto/deflate.c

## Purpose
`deflate.c` registers an asynchronous compression API (`acomp`) implementation for raw DEFLATE, primarily for IPCOMP. It adapts kernel zlib deflate/inflate streams to crypto scatterlist compression requests.

## Important APIs, Types, And Functions
- `struct deflate_stream` embeds `struct z_stream_s` followed by a flexible workspace.
- `deflate_alloc_stream()` allocates enough workspace for either inflate or deflate with the configured raw-deflate parameters.
- `deflate_compress_one()` walks source and destination scatterlists and drives `zlib_deflate()` until `Z_STREAM_END`.
- `deflate_decompress_one()` similarly drives `zlib_inflate()` and detects destination exhaustion.
- `deflate_compress()` and `deflate_decompress()` lock a percpu/shared `crypto_acomp_stream`, initialize zlib state, run the operation, and unlock.
- `deflate_init()` lazily allocates stream contexts under `deflate_stream_lock`.
- `acomp` registers the algorithm as `deflate` / `deflate-generic`.

## Control Flow
Compression locks a stream with bottom halves disabled, initializes zlib with `zlib_deflateInit2()` using negative window bits for raw DEFLATE, then alternates destination chunks and source chunks through `acomp_walk_virt()`. It uses `Z_NO_FLUSH` while more source remains and `Z_FINISH` on the final input. Decompression initializes inflate with negative window bits and feeds source while repeatedly taking destination chunks. It treats lack of progress with no destination as `-ENOSPC`.

## State And Persistence
Zlib state and workspace are retained in allocated stream contexts, but each operation reinitializes zlib before use. The algorithm-level `deflate_streams` pool persists until module exit, then `crypto_acomp_free_streams()` releases it. Request output length is persisted to `req->dlen`.

## Dependencies And Integration Points
The file depends on `<linux/zlib.h>`, crypto acomp stream pooling, and `acomp_walk_*` scatterwalk helpers. It registers with the crypto compression API and is tested by generic compression test descriptors for `deflate`.

## Risks And Edge Cases
The main operational risks are destination exhaustion and zlib return-code translation. Compression returns `-ENOSPC` when no destination chunk exists, and `-EINVAL` if zlib does not finish cleanly. Decompression explicitly detects no-progress/no-output-space. The implementation assumes virtual scatterlist walking because `cra_flags` includes `CRYPTO_ALG_REQ_VIRT`.

## Test Signals
`testmgr.h` includes deflate compression and decompression vectors, and `testmgr.c` maps `deflate` to those vectors. Useful additional signals include truncated input, too-small output buffers, fragmented source/destination scatterlists, and repeated concurrent requests to exercise stream pooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/des_generic.c -->
# sources/distributed-fs/ceph-client/crypto/des_generic.c

## Purpose
`des_generic.c` registers generic DES and Triple-DES EDE single-block cipher algorithms. It is a thin crypto API wrapper around DES key schedule and block routines from `<crypto/internal/des.h>`.

## Important APIs, Types, And Functions
- `des_setkey()` calls `des_expand_key()` and maps weak-key handling to crypto flags.
- `des3_ede_setkey()` calls `des3_ede_expand_key()` with the same weak-key flag behavior.
- `crypto_des_encrypt()` / `crypto_des_decrypt()` and `crypto_des3_ede_encrypt()` / `crypto_des3_ede_decrypt()` invoke internal DES routines using transform context.
- `des_algs[2]` registers `des` / `des-generic` and `des3_ede` / `des3_ede-generic` as `CRYPTO_ALG_TYPE_CIPHER`.

## Control Flow
Setkey expands the supplied key into the transform context. If the lower-level expansion reports `-ENOKEY`, the wrapper either rejects it as `-EINVAL` when `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` is set or accepts it otherwise. Other errors clear the context. Encrypt and decrypt are direct single-block calls.

## State And Persistence
The transform context stores a `struct des_ctx` or `struct des3_ede_ctx` key schedule. State lasts for the transform lifetime. No IV, request, or persistent global state is stored beyond algorithm registration.

## Dependencies And Integration Points
DES is exposed as a base cipher for templates such as ECB, CBC, CTR, and authenc combinations. Testmgr includes standalone DES/DES3 vectors and composed mode vectors.

## Risks And Edge Cases
DES is cryptographically obsolete, and weak-key handling is flag-dependent. Context wipe on key setup error is important to avoid retaining prior schedules. The file does not implement mode-level padding or IV handling; consumers must use templates correctly.

## Test Signals
`testmgr.h` includes `des_tv_template`, `des3_ede_tv_template`, DES/DES3 CBC and CTR vectors, and AEAD/authenc combinations. Tests should verify weak-key rejection when `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` is requested and normal encrypt/decrypt known-answer vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/des_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/df_sp80090a.c -->
# sources/distributed-fs/ceph-client/crypto/df_sp80090a.c

## Purpose
`df_sp80090a.c` implements the NIST SP800-90A derivation function used by CTR DRBG. It provides BCC chaining and derivation output generation over AES, exported as `crypto_drbg_ctr_df()`.

## Important APIs, Types, And Functions
- `drbg_kcapi_sym()` encrypts one AES block from a `drbg_string`.
- `drbg_ctr_bcc()` implements the block chaining construction over a linked list of input strings using a supplied key.
- `crypto_drbg_ctr_df()` builds the SP800-90A input string `L || N || input || 0x80 || zero padding`, runs BCC rounds using the fixed initial key, then generates the requested output using the derived key and X value.
- The function uses `struct drbg_string`, `drbg_string_fill()`, and `drbg_cpu_to_be32()` from DRBG internals.

## Control Flow
The exported function receives a scratch buffer `df_data` laid out by the DRBG caller. It computes total input length from `seedlist`, encodes input length and requested output length in big endian, constructs a temporary `bcc_list`, and appends the original seed list with `list_splice_tail()`. BCC is run once per output block needed for key material plus IV. The resulting `temp` buffer supplies the AES key and starting block, and final output blocks are encrypted and copied into `df_data`.

## State And Persistence
No state persists across calls. The caller provides both AES key workspace and scratch memory. Temporary IV, pad, and temp regions are zeroed before return. The function mutates list linkage by splicing `seedlist` into `bcc_list`, which is safe for the DRBG call pattern but is an important integration detail.

## Dependencies And Integration Points
This file depends on the AES internal key API (`aes_prepareenckey()`, `aes_encrypt()`), DRBG internal string helpers, and `crypto_drbg_ctr_df_datalen()` sizing conventions described in comments. It is called by CTR DRBG in `drbg.c`.

## Risks And Edge Cases
The function rejects requests greater than 512 bits. Correct scratch sizing is critical; comments explicitly describe extra block space needed when state length is not a multiple of block length. The `list_splice_tail()` behavior means callers should not expect `seedlist` to remain independently linked after the call. Any AES state length/key length mismatch would break CTR DRBG seeding.

## Test Signals
DRBG CTR known-answer tests in `testmgr.h` exercise this derivation function indirectly for `drbg_pr_ctr_aes128` and `drbg_nopr_ctr_aes{128,192,256}`. Specific useful tests cover maximum 64-byte return, multi-element seed lists, non-block-aligned input length, and scratch zeroing expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/df_sp80090a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/dh.c -->
# sources/distributed-fs/ceph-client/crypto/dh.c

## Purpose
`dh.c` implements the generic Diffie-Hellman KPP algorithm and optional RFC7919 FFDHE safe-prime templates. The generic algorithm computes public keys and shared secrets with MPI modular exponentiation. The safe-prime templates bind well-known primes, generator 2, and private-key generation policy to the generic `dh` implementation.

## Important APIs, Types, And Functions
- `struct dh_ctx` stores MPI values `p`, `g`, and private exponent `xa`.
- `dh_set_secret()` decodes a serialized DH key, validates parameter length, imports `p`, `g`, and `xa`, and clears any old context.
- `dh_compute_value()` computes either `g^xa mod p` when `req->src` is NULL or `yb^xa mod p` when peer public key input is provided.
- `dh_is_pubkey_valid()` performs FIPS-mode SP800-56A public key validation for safe-prime groups.
- `struct dh_safe_prime` describes fixed FFDHE groups; the optional block under `CONFIG_CRYPTO_DH_RFC7919_GROUPS` defines FFDHE 2048 through 8192.
- `dh_safe_prime_gen_privkey()` generates a private key using SP800-56A rev3 oversampling and modular reduction for safe-prime groups.
- `dh_safe_prime_set_secret()` accepts optional key-only input, binds fixed `p`/`g`, auto-generates a key if absent, encodes the full secret, and delegates to spawned `dh`.
- `crypto_ffdhe_templates[]` registers `ffdhe2048`, `ffdhe3072`, `ffdhe4096`, `ffdhe6144`, and `ffdhe8192` templates when configured.

## Control Flow
The base `dh` KPP stores parameters during `set_secret`. Public-key generation and shared-secret computation share `dh_compute_value()`: allocate an MPI result, choose base from request input or `ctx->g`, validate peer base in FIPS mode, exponentiate, perform FIPS shared-secret/public-key checks, and write the MPI to the output scatterlist.

The safe-prime templates are normal KPP instances that spawn `dh`. Their `set_secret` path rejects caller-supplied `p` or `g`, fills in the fixed group, generates a private key if needed, encodes a normal DH secret blob, and calls `crypto_kpp_set_secret()` on the child transform. Generate/compute requests are forwarded through an embedded child request.

## State And Persistence
The base transform owns MPI allocations for `p`, `g`, and `xa`; `dh_clear_ctx()` frees and zeroes pointers. Safe-prime transform state owns a child KPP transform. Fixed group constants are static read-only data. Generated private keys and encoded buffers are freed with sensitive zeroing.

## Dependencies And Integration Points
The file depends on MPI arithmetic, `crypto_dh_decode_key()`/`crypto_dh_encode_key()` from `dh_helper.c`, kernel RNG via `crypto_stdrng_get_bytes()`, KPP spawn/instance helpers, and `fips_enabled`. It registers `dh` and optional `ffdhe*` crypto templates.

## Risks And Edge Cases
Generic DH only enforces minimum modulus length and `p != 0` through helper validation; outside FIPS mode, peer public-key validation is not performed. FIPS mode enforces `p >= 2048` and subgroup checks. Public key generation can return `-EAGAIN` if the generated key fails validation. Safe-prime private-key generation has subtle reduction logic and must preserve uniformity. Output write failures, negative MPI output signs, and `mod 0` hazards are explicitly handled.

## Test Signals
Useful tests include base DH known-answer KPP vectors, invalid serialized secrets, too-small modulus rejection, FIPS-mode public key validation failures, generated FFDHE private-key bounds, and child request forwarding. Testmgr in this tree emphasizes KPP vectors for ECDH; DH coverage may come from broader kernel crypto self-tests or consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/dh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/dh_helper.c -->
# sources/distributed-fs/ceph-client/crypto/dh_helper.c

## Purpose
`dh_helper.c` serializes and deserializes DH key material for the KPP API. It packs a `struct kpp_secret` header plus key, modulus `p`, and generator `g` sizes and byte arrays into the buffer accepted by `dh_set_secret()`.

## Important APIs, Types, And Functions
- `crypto_dh_key_len()` returns total serialized length.
- `crypto_dh_encode_key()` writes secret header, three size fields, and key/p/g data into a caller-provided buffer.
- `__crypto_dh_decode_key()` parses the header and size fields and points `struct dh` members directly into the serialized buffer without allocation.
- `crypto_dh_decode_key()` adds generic safety checks: key and generator sizes must not exceed `p_size`, and `p` must not be all zeros.

## Control Flow
Encoding computes the expected end pointer and uses `dh_pack_data()` for each field. It fails if the buffer length is zero or if packing does not exactly fill the provided buffer. Decoding checks minimum size, secret type, expected length, then assigns internal pointers based on size offsets. The public decode wrapper performs additional driver-protection checks.

## State And Persistence
The helper does not allocate or persist state. Decoded pointers alias the caller's input buffer, so the buffer must remain valid through downstream use.

## Dependencies And Integration Points
It depends on `<crypto/dh.h>` and `<crypto/kpp.h>`. The base `dh` implementation uses `crypto_dh_decode_key()`; safe-prime template code uses `__crypto_dh_decode_key()` to permit key-only input with absent `p` and `g`.

## Risks And Edge Cases
The main edge is aliasing: decode does not copy data. The public decoder prevents common driver assumptions from being violated but does not verify primality or generator order. Size arithmetic is simple but relies on `secret.len == crypto_dh_key_len(params)` after sizes are read.

## Test Signals
Tests should cover exact-length encoding/decoding, zero-length buffers, wrong secret type, truncated buffers, key/g larger than p, all-zero p, and key-only safe-prime decode through the internal helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/dh_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/drbg.c -->
# sources/distributed-fs/ceph-client/crypto/drbg.c

## Purpose
`drbg.c` implements NIST SP800-90A deterministic random bit generators as kernel crypto RNG algorithms. Depending on configuration, it registers CTR-DRBG with AES, Hash-DRBG with SHA-2, and HMAC-DRBG with SHA-2, each with prediction-resistance and no-prediction-resistance variants under the `stdrng` algorithm name.

## Important APIs, Types, And Functions
- `drbg_cores[]` defines supported cores, security strength flags, state length, block length, public driver suffix, and backend crypto name.
- `struct drbg_state` is allocated as the RNG transform context and holds `V`, `C`, scratch buffers, backend handles, reseed counters, seed state, FIPS continuous-test state, and optional Jitter RNG handle.
- `drbg_ctr_update()` / `drbg_ctr_generate()`, `drbg_hash_update()` / `drbg_hash_generate()`, and `drbg_hmac_update()` / `drbg_hmac_generate()` implement the DRBG type-specific SP800-90A algorithms.
- `drbg_seed()`, `__drbg_seed()`, `drbg_seed_from_random()`, and `drbg_get_random_bytes()` collect entropy, mix personalization/additional input, update state, and set reseed thresholds.
- `drbg_generate()` performs API validation, reseed checks, prediction-resistance behavior, additional-input handling, generation, and reseed counter increment.
- `drbg_generate_long()` slices large requests into max-request-sized chunks.
- `drbg_alloc_state()` / `drbg_dealloc_state()` allocate aligned V/C/scratch/FIPS buffers and backend crypto handles.
- `drbg_kcapi_seed()`, `drbg_kcapi_random()`, and `drbg_kcapi_set_entropy()` adapt the implementation to `struct rng_alg`.
- `drbg_fill_array()` creates two registered RNG algorithms for each core: `drbg_pr_*` and `drbg_nopr_*`.

## Control Flow
Module initialization first runs FIPS sanity checks when required, fills the `drbg_algs` array, and registers all configured RNG variants. A transform initializes only its mutex at `cra_init`; real DRBG state is allocated during `seed`, where `drbg_convert_tfm_core()` maps the driver name to a core and PR flag. Instantiation allocates backend state, optionally prepares `jitterentropy_rng`, then seeds from test data or kernel RNG/Jitter RNG.

Generation locks the DRBG state per chunk. It validates buffer and additional-input sizes, marks the state unseeded if the reseed threshold is exceeded, reseeds for PR or unseeded state, opportunistically reseeds when the kernel RNG becomes fully initialized or the no-PR interval elapses, then calls the selected type-specific generate function. CTR uses `crypto_drbg_ctr_df()` plus a spawned `ctr(aes)` skcipher; Hash uses a hash derivation function and hashgen; HMAC updates key `C` and value `V` through HMAC.

## State And Persistence
Transform state persists for the crypto RNG handle lifetime. Critical state includes `V`, `C`, reseed counter, seed state (`UNSEEDED`, `PARTIAL`, `FULL`), last seed time, reseed threshold, backend handles, scratch buffers, and FIPS previous entropy sample. `drbg_uninstantiate()` frees backend handles and sensitive buffers but preserves test data. No state survives module unload or transform destruction.

## Dependencies And Integration Points
The file integrates with the crypto RNG API, shash API for Hash/HMAC DRBG, skcipher API for CTR DRBG, `df_sp80090a.c` for CTR derivation, `get_random_bytes()` and `rng_is_initialized()`, optional Jitter RNG, `fips_enabled`, and crypto testmgr. It exports aliases such as `drbg_nopr_hmac_sha512`, `drbg_pr_ctr_aes128`, and `stdrng`.

## Risks And Edge Cases
DRBG correctness depends on exact SP800-90A state transitions, scratch buffer sizing, and backend return-code handling. FIPS continuous RNG testing can panic on repeated entropy samples. In FIPS mode, Jitter RNG failure is fatal for initial seed and most non-transient failures, but transient reseed failures are tolerated according to comments. Test mode is indicated by an empty `test_data.list`, an unusual convention that affects entropy and reseeding behavior. Large requests are chunked, so additional input can be applied to multiple chunks if supplied to `drbg_generate_long()`.

## Test Signals
`testmgr.h` contains known-answer vectors for `drbg_pr_sha256`, `drbg_pr_hmac_sha256`, `drbg_pr_ctr_aes128`, no-PR SHA/HMAC/CTR variants, and HMAC-SHA512. `testmgr.c` maps many higher-strength variants as covered by representative vectors. Additional signals include max-additional-input rejection, max-request rejection, personalization handling through `seed`, partial-to-full reseed transition after `rng_is_initialized()`, and FIPS sanity/error-path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/drbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecb.c -->
# sources/distributed-fs/ceph-client/crypto/ecb.c

## Purpose
`ecb.c` registers the `ecb` lskcipher template. It wraps either modern lskcipher algorithms or older raw single-block cipher algorithms to provide Electronic Codebook mode with no IV.

## Important APIs, Types, And Functions
- `crypto_ecb_crypt()` runs a raw cipher block function over complete blocks and returns leftover bytes unless the final flag requires strict block alignment.
- `crypto_ecb_encrypt2()` and `crypto_ecb_decrypt2()` adapt legacy `crypto_cipher` children to lskcipher operations.
- `lskcipher_alloc_instance_simple2()` and associated init/exit/setkey/free helpers implement fallback wrapping for legacy cipher algorithms.
- `crypto_ecb_create()` first tries `lskcipher_alloc_instance_simple()` and falls back to the legacy helper. It rejects lskcipher children that already have an IV.
- `crypto_ecb_tmpl` registers the `ecb` template.

## Control Flow
For modern lskcipher children, `crypto_ecb_create()` builds a template instance that mostly forwards setkey, encrypt, decrypt, init, and exit to the child while forcing `ivsize = 0`. For raw cipher fallback, the wrapper spawns a `crypto_cipher`, sets inherited flags on setkey, and calls the child's block encrypt/decrypt function in a loop. Non-final partial input is reported as unconsumed bytes; final partial input is `-EINVAL`.

## State And Persistence
State is transform-local and consists of the child lskcipher or raw cipher pointer and child context. ECB has no IV or per-request chaining state.

## Dependencies And Integration Points
The file depends on internal cipher and lskcipher template helpers. It is a core mode used by many block ciphers and by higher-level modes that depend on raw block encryption. Testmgr includes `ecb(aes)`, `ecb(des)`, `ecb(des3_ede)`, and many other `ecb(...)` vectors.

## Risks And Edge Cases
ECB is cryptographically unsafe for structured multi-block plaintexts, but it remains a primitive/template. The code must handle two child API families consistently. A notable implementation risk is instance cleanup on the path where a modern child with nonzero IV is rejected; it returns `-EINVAL` after allocation, so cleanup behavior should be reviewed if this code is changed. Partial-block handling depends on the lskcipher final flag.

## Test Signals
Testmgr maps many ECB algorithms to cipher vectors. Useful tests cover legacy raw cipher wrapping, lskcipher child wrapping, final partial-block rejection, non-final partial return length, no-IV behavior, and inherited flag propagation during setkey.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecc.c -->
# sources/distributed-fs/ceph-client/crypto/ecc.c

## Purpose
`ecc.c` is the shared elliptic-curve arithmetic implementation used by ECDH, ECDSA, and EC-RDSA. It provides curve lookup, big-integer limb helpers, modular arithmetic, point multiplication/addition, public/private key validation, public key generation, and ECDH shared secret computation.

## Important APIs, Types, And Functions
- `ecc_get_curve()` returns NIST P-192/P-256/P-384/P-521 curves, suppressing P-192 in FIPS mode. `ecc_get_curve25519()` returns the Curve25519 parameter struct.
- Conversion helpers include `ecc_digits_from_bytes()`, `vli_from_be64()`, `vli_from_le64()`, and exported compare/arithmetic helpers such as `vli_cmp()`, `vli_sub()`, `vli_mod_inv()`, and `vli_mod_mult_slow()`.
- `ecc_alloc_point()` and `ecc_free_point()` allocate and sensitive-free point coordinate buffers.
- Internal VLI routines implement addition, subtraction, multiplication, squaring, modular reduction, and inverse. Fast reducers cover NIST P-192/P-256/P-384/P-521, pseudo-Mersenne shapes, and Barrett fallback.
- Point routines include `ecc_point_double_jacobian()`, `xycz_add()`, `xycz_add_c()`, `ecc_point_mult()`, `ecc_point_add()`, and exported `ecc_point_mult_shamir()`.
- Key functions include `ecc_is_key_valid()`, `ecc_gen_privkey()`, `ecc_make_pub_key()`, `ecc_is_pubkey_valid_partial()`, `ecc_is_pubkey_valid_full()`, and `crypto_ecdh_shared_secret()`.

## Control Flow
Private key generation obtains random bytes from `crypto_stdrng_get_bytes()` and validates the result by rejection sampling bounds `[2, n-3]`. Public key generation multiplies the curve generator by the private key, then performs a full public-key validation check. Shared-secret computation parses the peer public key into a point, performs partial public-key validation, randomizes the initial projective Z coordinate with `get_random_bytes()`, multiplies by the private key, rejects the point at infinity, and returns the x coordinate.

ECDSA and ECRDSA verification use `ecc_point_mult_shamir()` to compute double-scalar multiplications. ECDH and public key generation use `ecc_point_mult()`, which is a Montgomery-ladder-style co-Z multiplication with scalar blinding by adding curve order variants before choosing a scalar representation.

## State And Persistence
The file has no mutable global runtime state, but includes static curve definitions through `ecc_curve_defs.h`. Allocated points and temporary arrays are per call. Sensitive point storage and random Z are cleared/freed where appropriate, though many stack temporaries are ordinary arithmetic buffers.

## Dependencies And Integration Points
This file depends on curve constants from `ecc_curve_defs.h`, kernel RNG APIs, FIPS mode, and crypto internal ECC headers. It exports symbols consumed by `ecdh.c`, `ecdsa.c`, `ecdsa-p1363.c`, `ecdsa-x962.c`, and `ecrdsa.c`.

## Risks And Edge Cases
This is high-risk arithmetic code. Correctness depends on limb order, curve-specific reduction, point-at-infinity handling, and scalar bounds. Public key validation has partial and full variants; ECDH uses partial validation for ephemeral keys, while ECDSA uses full validation on public keys. `ecc_get_curve()` can return NULL for P-192 in FIPS mode, so callers must handle unavailable curves. Timing side-channel behavior is mitigated in multiplication style but should not be assumed constant-time for every helper path.

## Test Signals
Testmgr contains ECDH vectors for P-192/P-256/P-384, ECDSA vectors for P-192/P-256/P-384/P-521, x962 and p1363 wrapper vectors, and ECRDSA vectors. Additional signals include invalid public points, point-at-infinity rejection, private key boundary rejection, FIPS P-192 unavailability, and cross-checking shared secrets/public keys against independent implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecc_curve_defs.h -->
# sources/distributed-fs/ceph-client/crypto/ecc_curve_defs.h

## Purpose
`ecc_curve_defs.h` provides static curve parameter definitions consumed by `ecc.c`. It defines NIST P-192, P-256, P-384, P-521, and Curve25519 constants in the internal `struct ecc_curve` format.

## Important APIs, Types, And Functions
- The file defines arrays for generator x/y coordinates, prime `p`, order `n`, coefficient `a`, and coefficient `b` for NIST curves.
- `static struct ecc_curve nist_p192`, `nist_p256`, `nist_p384`, and `nist_p521` are used by `ecc_get_curve()`.
- `static const struct ecc_curve ecc_25519` contains Curve25519 name, bit size, generator x coordinate, prime, and Montgomery coefficient.

## Control Flow
There is no executable control flow. Inclusion by `ecc.c` makes these static definitions available to curve lookup and arithmetic functions.

## State And Persistence
All data is static in-kernel constant-style curve metadata. The arrays are not declared `const` for every NIST object because the `ecc_curve` fields are non-const pointers, but callers treat them as immutable domain parameters.

## Dependencies And Integration Points
The file depends on `struct ecc_curve` from `<crypto/ecc_curve.h>` included by `ecc.c`. NIST definitions support ECDH and ECDSA. Curve25519 is exposed through `ecc_get_curve25519()` for users outside this subset.

## Risks And Edge Cases
Any constant error breaks all cryptographic operations on that curve. Limb ordering is little-endian 64-bit internal order, not byte-string order. P-521 uses 9 digits with only 521 significant bits, which drives special reduction and bounds behavior. Curve25519 lacks `n`, `b`, and `y` fields here because it is used differently than short-Weierstrass NIST curves.

## Test Signals
Known-answer ECDH/ECDSA tests indirectly verify NIST constants. Additional validation includes public-key equation checks for each generator, verifying `nG` is infinity, and cross-checking constants against FIPS/RFC sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecc_curve_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdh.c -->
# sources/distributed-fs/ceph-client/crypto/ecdh.c

## Purpose
`ecdh.c` registers generic ECDH KPP algorithms for NIST P-192, P-256, and P-384. It adapts serialized ECDH secrets and scatterlist KPP requests to the shared ECC arithmetic layer.

## Important APIs, Types, And Functions
- `struct ecdh_ctx` stores selected curve id, digit count, and private key limbs.
- `ecdh_set_secret()` decodes a serialized ECDH key. Empty key material triggers private-key generation; supplied key material is converted and range-validated.
- `ecdh_compute_value()` generates a public key when `req->src` is NULL or computes a shared secret when peer public key input is supplied.
- `ecdh_max_size()` reports two-coordinate public key size.
- `ecdh_nist_p192_init_tfm()`, `ecdh_nist_p256_init_tfm()`, and `ecdh_nist_p384_init_tfm()` bind curve parameters to registered KPP algorithms.

## Control Flow
`set_secret` clears the private key array, decodes the buffer via `crypto_ecdh_decode_key()`, and either calls `ecc_gen_privkey()` or imports caller bytes with `ecc_digits_from_bytes()` followed by `ecc_is_key_valid()`. Compute allocates a public key buffer and, for shared secrets, a secret buffer. Peer public keys must be exactly two coordinates. Data is copied from request scatterlist, passed to `crypto_ecdh_shared_secret()` or `ecc_make_pub_key()`, then copied back to the destination scatterlist.

## State And Persistence
The transform context persists the private key in a fixed `u64[ECC_MAX_DIGITS]` array. Temporary public/secret buffers are heap allocated per request and secret output buffers are freed with `kfree_sensitive()`.

## Dependencies And Integration Points
The file depends on `ecdh_helper.c` for key decode, `ecc.c` for key generation/public/shared-secret operations, KPP crypto registration, and scatterlist helpers. It registers `ecdh-nist-p192`, `ecdh-nist-p256`, and `ecdh-nist-p384`; P-192 registration may fail in FIPS mode.

## Risks And Edge Cases
The code must handle FIPS-mode P-192 unavailability and curve lookup failures from the ECC layer. Destination output is truncated to `req->dst_len`, so callers can request less than full public key/secret. Invalid peer public key length or scatterlist copy failure returns `-EINVAL`. Private key clearing on invalid supplied key uses `params.key_size`, which is byte length, against a limb array; current keys fit the array but changes should preserve safe clearing.

## Test Signals
`testmgr.h` includes `ecdh_p192_tv_template`, `ecdh_p256_tv_template`, and `ecdh_p384_tv_template`; `testmgr.c` maps the three registered algorithms. Useful tests include generated key path, explicit private key path, invalid peer length, truncated destination length, and FIPS P-192 registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdh_helper.c -->
# sources/distributed-fs/ceph-client/crypto/ecdh_helper.c

## Purpose
`ecdh_helper.c` serializes and deserializes ECDH private-key material for the KPP API. The serialized form is a `struct kpp_secret`, a key-size field, and optional key bytes.

## Important APIs, Types, And Functions
- `crypto_ecdh_key_len()` returns serialized length.
- `crypto_ecdh_encode_key()` writes header, key size, and key bytes.
- `crypto_ecdh_decode_key()` parses the header, validates type and length, and points `params->key` into the original buffer.

## Control Flow
Encoding rejects a NULL buffer and requires the provided length to match `crypto_ecdh_key_len(params)`. Decoding rejects NULL/truncated buffers, wrong secret type, and inconsistent lengths. It does not allocate; it assigns the key pointer to the payload after the key-size field.

## State And Persistence
No state is retained. Decoded keys alias caller memory, so buffer lifetime must cover consumer parsing.

## Dependencies And Integration Points
The helper uses `<crypto/ecdh.h>` and `<crypto/kpp.h>` and is consumed by `ecdh_set_secret()` in `ecdh.c`.

## Risks And Edge Cases
The helper validates serialization but not curve-specific key size or scalar range; `ecdh.c` and `ecc.c` perform those checks. Empty key payload is valid and means "generate a private key" to `ecdh_set_secret()`.

## Test Signals
Tests should cover valid explicit keys, empty key generation requests, NULL buffer rejection, truncated secret headers, wrong secret type, and mismatched encoded length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdh_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdsa-p1363.c -->
# sources/distributed-fs/ceph-client/crypto/ecdsa-p1363.c

## Purpose
`ecdsa-p1363.c` registers the `p1363` signature template for ECDSA algorithms. It converts fixed-width IEEE P1363 signatures (`r || s`) into the internal `struct ecdsa_raw_sig` format and delegates verification to a child ECDSA signature algorithm.

## Important APIs, Types, And Functions
- `struct ecdsa_p1363_ctx` stores the spawned child `crypto_sig`.
- `ecdsa_p1363_verify()` checks signature length, converts `r` and `s` from big-endian byte strings to internal limbs, and calls `crypto_sig_verify()` on the child.
- `ecdsa_p1363_key_size()`, `ecdsa_p1363_max_size()`, and `ecdsa_p1363_digest_size()` proxy child metadata.
- `ecdsa_p1363_set_pub_key()` forwards public-key setup to the child.
- `ecdsa_p1363_create()` validates that the child algorithm name starts with `ecdsa`, names the instance, and registers it.

## Control Flow
The template is instantiated as `p1363(ecdsa-...)`. At transform init it spawns the child signature algorithm. Verification computes `keylen` from the child key size, requires exactly `2 * keylen` input bytes, imports both halves with `ecc_digits_from_bytes()`, then delegates to the underlying ECDSA verifier.

## State And Persistence
The transform context holds only the child `crypto_sig` pointer. Public key state is stored inside the child transform. Request state is stack-local.

## Dependencies And Integration Points
The file depends on the crypto sig template framework, `ecc_digits_from_bytes()`, and `ecdsa.c` raw signature verification. The template object `ecdsa_p1363_tmpl` is registered by `ecdsa.c`.

## Risks And Edge Cases
Length handling must match fixed-width P1363 encoding exactly. The template only checks the first five characters of the child name (`ecdsa`), so algorithm naming conventions matter. It does not parse ASN.1 or accept variable-width integers; that is the x962 template's role.

## Test Signals
`testmgr.h` includes P1363 ECDSA P-256 vectors and `testmgr.c` maps `p1363(ecdsa-nist-p*)` algorithms, with most larger/smaller curves covered by child tests. Useful tests include wrong-length signatures, leading-zero fixed-width values, public-key forwarding, and unsupported child algorithm rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdsa-p1363.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdsa-x962.c -->
# sources/distributed-fs/ceph-client/crypto/ecdsa-x962.c

## Purpose
`ecdsa-x962.c` registers the `x962` signature template for ECDSA algorithms. It parses ASN.1 DER/BER `ECDSA-Sig-Value` signatures into raw `r` and `s` limbs before delegating verification to a child ECDSA algorithm.

## Important APIs, Types, And Functions
- `struct ecdsa_x962_ctx` stores the child `crypto_sig`.
- `struct ecdsa_x962_signature_ctx` holds a raw signature and digit count for ASN.1 callbacks.
- `ecdsa_get_signature_rs()` validates one ASN.1 INTEGER, strips a permitted leading zero, and imports it with `ecc_digits_from_bytes()`.
- `ecdsa_get_signature_r()` and `ecdsa_get_signature_s()` are ASN.1 decoder callbacks.
- `ecdsa_x962_verify()` runs `asn1_ber_decoder()` with `ecdsasignature_decoder`, then delegates to the child.
- `ecdsa_x962_max_size()` computes maximum DER encoding size including integer and sequence overhead.
- `ecdsa_x962_create()` validates an ECDSA child, configures proxy methods, and registers the instance.

## Control Flow
An `x962(ecdsa-...)` transform spawns its child on init. Verification computes digit count from child key size, decodes the ASN.1 signature into `sig_ctx.sig`, and calls `crypto_sig_verify()` on the child. Public key, key size, and digest size operations are forwarded to the child transform.

## State And Persistence
The wrapper transform persists only the child signature transform. Parsed signature state is request-local. Public key material is owned by the child.

## Dependencies And Integration Points
The file depends on generated ASN.1 decoder `ecdsasignature.asn1.h`, crypto sig templates, and ECC conversion helpers. The template object `ecdsa_x962_tmpl` is registered by `ecdsa.c`.

## Risks And Edge Cases
ASN.1 integer handling must reject negative encodings and oversized components while accepting one leading zero when needed to keep the integer positive. The decoder must populate both r and s; raw ECDSA verification performs range checks afterward. Maximum-size reporting differs for P-521 because coordinates do not need the extra positive-integer byte.

## Test Signals
`testmgr.h` includes x962 vectors for P-192, P-256, P-384, and P-521. Useful tests include malformed ASN.1 sequences, missing r or s, oversized INTEGERs, unnecessary/required leading zero cases, and invalid child algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdsa-x962.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdsa.c -->
# sources/distributed-fs/ceph-client/crypto/ecdsa.c

## Purpose
`ecdsa.c` implements generic ECDSA signature verification for NIST P-192, P-256, P-384, and P-521 and registers the raw ECDSA signature algorithms plus x962 and p1363 encoding templates.

## Important APIs, Types, And Functions
- `struct ecc_ctx` stores curve id, curve pointer, public-key-set flag, coordinate buffers, and `struct ecc_point pub_key`.
- `_ecdsa_verify()` performs the ECDSA verification equation over already-parsed hash, r, and s limbs.
- `ecdsa_verify()` adapts the crypto sig API: checks public key presence, raw signature size, truncates digest to curve digit length, imports the digest, and calls `_ecdsa_verify()`.
- `ecdsa_set_pub_key()` parses RFC5480 uncompressed public keys (`0x04 || X || Y`) and fully validates the point.
- `ecdsa_key_size()` and `ecdsa_digest_size()` report curve bits and maximum supported digest size (`SHA512_DIGEST_SIZE`).
- Four `sig_alg` objects register `ecdsa-nist-p192`, P-256, P-384, and P-521.
- `ecdsa_init()` also registers `ecdsa_x962_tmpl` and `ecdsa_p1363_tmpl`.

## Control Flow
Setting a public key resets the context, validates uncompressed encoding and coordinate size, imports X and Y, then calls `ecc_is_pubkey_valid_full()`. Verification rejects missing public keys or wrong raw signature size, imports at most one curve-width of digest bytes, verifies `0 < r,s < n`, computes `s^-1`, derives `u1 = hash*s^-1 mod n` and `u2 = r*s^-1 mod n`, computes `u1G + u2Q` with Shamir's trick, reduces x modulo n, and compares it to r.

## State And Persistence
Per-transform state stores the selected curve and public key. There is no private key or signing state. Module-level state tracks whether P-192 registration succeeded because FIPS mode may suppress that curve.

## Dependencies And Integration Points
The file depends on `ecc.c` for arithmetic, `crypto/internal/sig.h` for signature registration, SHA-2 digest size constants, and external template objects declared in internal sig headers. It is the child algorithm used by `ecdsa-x962.c` and `ecdsa-p1363.c`.

## Risks And Edge Cases
This code verifies only; it does not sign. Digest truncation to curve length follows ECDSA practice but must be consistent with test vectors. P-192 can be unavailable in FIPS mode. Public key validation is full, including `nQ == infinity`, which is stronger but more expensive. Raw signature input must already be in internal limb struct format; external encodings need wrappers.

## Test Signals
`testmgr.h` includes raw ECDSA vectors for all four NIST curves and wrapper vectors for x962/p1363. Tests should cover invalid r/s zero or >= n, wrong public key format, invalid curve point, digest longer than curve size, and FIPS P-192 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecdsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/echainiv.c -->
# sources/distributed-fs/ceph-client/crypto/echainiv.c

## Purpose
`echainiv.c` implements the `echainiv` AEAD geniv template, an encrypted chained IV generator. It derives an IV from a sequence number and salt and places the encrypted IV into the ciphertext/AAD layout used by authenc-style AEADs.

## Important APIs, Types, And Functions
- `echainiv_encrypt()` generates the IV from request IV sequence number and `aead_geniv_ctx` salt, copies source to destination for out-of-place requests, embeds the IV in output, and delegates encryption.
- `echainiv_decrypt()` extracts the IV from input AAD/ciphertext layout and delegates decryption.
- `echainiv_aead_create()` allocates a geniv AEAD instance, requires nonzero IV size aligned to 64-bit words, wires encrypt/decrypt/init/exit, and registers the instance.

## Control Flow
Encryption requires `cryptlen >= ivsize`. It forwards the request to the child AEAD over `req->dst`, with associated data unchanged. It reads a big-endian 64-bit sequence number from the tail of `req->iv`, zeroes the IV buffer, copies the existing IV-sized block into the output after AAD, and then fills each 64-bit IV word by multiplying the salt tail value, forced odd, by the sequence number. Decryption reverses the layout by mapping the IV from source at `assoclen`, then decrypting with `assoclen + ivsize`.

## State And Persistence
Persistent transform state comes from generic AEAD geniv context: child AEAD and salt stored after `struct aead_geniv_ctx`. Per-request state is the embedded child request.

## Dependencies And Integration Points
The file depends on `<crypto/internal/geniv.h>`, AEAD request helpers, scatterwalk, and authenc-like usage where authentication is performed after encryption. It registers the `echainiv` template.

## Risks And Edge Cases
The algorithm assumes block size equals IV size and IV size is a nonzero multiple of 8. It is only suitable for constructions where authentication occurs after encryption; misuse with other AEAD layouts could authenticate the wrong bytes. Sequence-number uniqueness is essential. Scatterlist copying on out-of-place encrypt must preserve AAD and plaintext/ciphertext layout exactly.

## Test Signals
Useful tests include IV-size rejection, cryptlen shorter than IV, in-place and out-of-place encrypt, decrypt IV extraction from AAD extension, and authenc integration tests that verify authentication covers the generated IV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/echainiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecrdsa.c -->
# sources/distributed-fs/ceph-client/crypto/ecrdsa.c

## Purpose
`ecrdsa.c` implements EC-RDSA (GOST R 34.10 family) signature verification as a crypto sig algorithm. It parses GOST public-key ASN.1 metadata, selects a GOST curve and Streebog digest size, validates the public key, and verifies raw EC-RDSA signatures.

## Important APIs, Types, And Functions
- `struct ecrdsa_ctx` stores algorithm, curve, and digest OIDs; selected `ecc_curve`; digest metadata; raw public key pointer/length; and public point storage.
- `get_curve_by_oid()` maps supported GOST curve OIDs to constants from `ecrdsa_defs.h`.
- `ecrdsa_verify()` performs the EC-RDSA verification equation using little-endian digest import and big-endian signature import.
- ASN.1 callbacks `ecrdsa_param_curve()`, `ecrdsa_param_digest()`, and `ecrdsa_parse_pub_key()` fill context fields during public-key parsing.
- `ecrdsa_set_pub_key()` decodes `SubjectPublicKeyInfo`, reads appended algorithm parameters, determines Streebog-256 or Streebog-512, parses curve parameters, imports public coordinates, and validates the point.
- `ecrdsa_alg` registers `ecrdsa` / `ecrdsa-generic`.

## Control Flow
Public-key setup first decodes the public-key wrapper, then reads two appended `u32` values for algorithm OID and parameter length. It selects digest metadata from algorithm OID, decodes parameters to identify curve and optional digest OID, enforces curve/digest/key length consistency, imports the two public coordinates from little-endian order, and performs partial point validation.

Verification checks that curve, digest, signature, and public key sizes are consistent. It imports signature `s` and `r`, validates `0 < r,s < q`, imports digest as little-endian `e = h mod q` with zero mapped to one, computes `v = e^-1`, `z1 = s*v mod q`, and `z2 = -r*v mod q`, then computes `z1*G + z2*Q` and compares x modulo q to r.

## State And Persistence
The transform context persists parsed public-key metadata and point storage. It stores `ctx->key` as a pointer into decoded key input during setup, then imports coordinates into owned `_pubp` storage. No signing or private state is held.

## Dependencies And Integration Points
The file depends on generated ASN.1 decoders `ecrdsa_params.asn1.h` and `ecrdsa_pub_key.asn1.h`, OID registry constants, Streebog digest sizes, shared ECC arithmetic, and curve constants from `ecrdsa_defs.h`.

## Risks And Edge Cases
The code supports selected GOST curve OIDs only and returns `-ENOPKG` for unsupported algorithms or mismatched sizes. It uses partial public-key validation, not full order validation, because these are GOST signature curves. The appended-parameter parsing after `key + keylen` is unusual and relies on the caller/key parser contract. Endianness differs between signature, digest, and public-key fields, making conversion tests important.

## Test Signals
`testmgr.h` includes `ecrdsa_tv_template` and `testmgr.c` maps `ecrdsa` to signature tests. Useful tests include unsupported OIDs, digest OID mismatch, invalid point coordinates, wrong signature length, zero or out-of-range r/s, and both 256-bit and 512-bit curve families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecrdsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecrdsa_defs.h -->
# sources/distributed-fs/ceph-client/crypto/ecrdsa_defs.h

## Purpose
`ecrdsa_defs.h` defines the EC-RDSA/GOST curve parameters used by `ecrdsa.c`. It covers 256-bit CryptoPro and TC26 parameter sets and 512-bit TC26 parameter sets.

## Important APIs, Types, And Functions
- Constants define generator x/y, prime `p`, order `n`, coefficient `a`, and coefficient `b` arrays for `gost_cp256a`, `gost_cp256b`, `gost_cp256c`, `gost_tc512a`, and `gost_tc512b`.
- Some primes include comments indicating special forms such as `2^256 - 617`, `2^255 + 3225`, `2^512 - 569`, and `2^511 + 111`.
- `cp256c_p` includes precomputed Barrett reduction data appended after the normal modulus limbs.

## Control Flow
There is no executable control flow. `ecrdsa.c` includes this header and maps OIDs to these static `struct ecc_curve` definitions.

## State And Persistence
All data is static curve metadata. Like `ecc_curve_defs.h`, arrays are mutable by type but treated as immutable constants.

## Dependencies And Integration Points
The file depends on `struct ecc_curve` from `<crypto/internal/ecc.h>`. The shared ECC reducer detects non-NIST special-prime shapes and Barrett parameters, so these constants interact directly with `vli_mmod_fast()` behavior in `ecc.c`.

## Risks And Edge Cases
Correct limb order and appended Barrett data are critical. Unsupported GOST OIDs in `ecrdsa.c` deliberately have no curve here. Any accidental mutation of non-const arrays would compromise signature verification. The 512-bit curves use 8 limbs and must stay within `ECRDSA_MAX_DIGITS`.

## Test Signals
EC-RDSA known-answer vectors validate these constants indirectly. Additional checks include verifying each generator lies on the curve, `nG` is infinity, and OID-to-curve mappings in `ecrdsa.c` select the expected parameter set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ecrdsa_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/essiv.c -->
# sources/distributed-fs/ceph-client/crypto/essiv.c

## Purpose
`essiv.c` implements the `essiv(cipher,hash)` template for skcipher and dm-crypt-specific authenc AEAD uses. ESSIV derives an IV encryption key by hashing the data-encryption key and uses a block cipher to encrypt each request IV before passing it to the wrapped cipher.

## Important APIs, Types, And Functions
- `struct essiv_instance_ctx` stores either a skcipher or AEAD spawn plus selected ESSIV cipher and hash driver names.
- `struct essiv_tfm_ctx` stores the spawned child skcipher/AEAD, ESSIV block cipher, hash transform, and AEAD IV buffer offset.
- `essiv_skcipher_setkey()` sets the child key, hashes the key, and sets the ESSIV cipher key to the hash digest.
- `essiv_aead_setkey()` handles authenc key format, sets child AEAD key, hashes encryption key then authentication key into the ESSIV salt, and sets the ESSIV cipher key.
- `essiv_skcipher_crypt()` encrypts `req->iv` in place with the ESSIV cipher and forwards encrypt/decrypt to the child skcipher.
- `essiv_aead_crypt()` encrypts the IV and patches the dm-crypt AAD layout before forwarding to the child AEAD.
- `parse_cipher_name()` extracts the inner block cipher name from the child algorithm name.
- `essiv_supported_algorithms()` checks hash digest size fits the cipher key size, IV size equals cipher block size, and hash is unkeyed.
- `essiv_create()` supports both lskcipher/skcipher and authenc AEAD instantiation, validates children, fills instance metadata, and registers the instance.

## Control Flow
Template creation parses `essiv(inner,hash)` attributes, determines whether an lskcipher or AEAD instance is requested, spawns the inner algorithm, derives the underlying block cipher name from the inner algorithm's `cra_name`, looks up the hash, validates compatibility, records the hash driver name, and registers either a skcipher or AEAD instance.

At runtime, setkey configures both the child transform and ESSIV cipher. A skcipher request simply encrypts the IV and delegates. An AEAD request computes `ssize = assoclen - ivsize`, encrypts the IV, and either writes the IV into the destination AAD area for in-place/decrypt or constructs a temporary scatterlist that inserts the encrypted IV between the sector-number AAD and payload for out-of-place encryption. Temporary assoc copies are freed in completion or immediate-error paths.

## State And Persistence
Transform state persists child transform, ESSIV cipher, hash transform, and AEAD request layout offset. Per-request AEAD state may allocate a temporary `assoc` buffer for fragmented AAD; it is freed after completion. The encrypted IV mutates `req->iv` in place.

## Dependencies And Integration Points
The file depends on crypto authenc key extraction, skcipher/AEAD/hash/cipher internal APIs, scatterwalk, and dm-crypt/fscrypt ESSIV conventions. It imports `CRYPTO_INTERNAL` namespace and registers the `essiv` template. Testmgr includes `essiv(cbc(aes),sha256)` and `essiv(authenc(hmac(sha256),cbc(aes)),sha256)` vectors.

## Risks And Edge Cases
ESSIV is tightly coupled to child naming and dm-crypt AEAD AAD layout. `parse_cipher_name()` uses parenthesis parsing, so unusual algorithm names can fail. AEAD support is intentionally limited to `authenc(...)`. Hash digest size must exactly be a valid key size for the IV cipher, and IV size must equal block size. Out-of-place AEAD encryption must handle multi-entry AAD scatterlists; allocation uses `GFP_ATOMIC`, so memory pressure can fail requests.

## Test Signals
`testmgr.h` contains skcipher and AEAD ESSIV vectors, and `testmgr.c` maps both algorithm forms. Additional tests should cover unsupported hash/cipher combinations, keyed hash rejection, non-authenc AEAD rejection, fragmented AAD scatterlists, in-place versus out-of-place encryption, decrypt IV handling, and setkey failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/essiv.c -->
