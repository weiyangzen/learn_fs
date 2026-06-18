# subset-b-000936 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/shash.c -->
# sources/distributed-fs/ceph-client/crypto/shash.c

## Purpose
`shash.c` implements the Linux Crypto API synchronous hash frontend. It owns transform allocation/registration for `struct shash_alg`, key state enforcement, default digest/finup behavior, state import/export, `/proc` and netlink reporting, cloning, and helper registration for shash instances.

## Important APIs, Types, And Functions
Key exported APIs are `crypto_alloc_shash()`, `crypto_has_shash()`, `crypto_clone_shash()`, `crypto_shash_setkey()`, `crypto_shash_init()`, `crypto_shash_finup()`, `crypto_shash_digest()`, `crypto_shash_export*()`, `crypto_shash_import*()`, `crypto_register_shash(es)()`, `crypto_unregister_shash(es)()`, `crypto_grab_shash()`, and `shash_register_instance()`. The central type is `crypto_shash_type`, which binds shash-specific allocation sizes, init/free callbacks, report/show hooks, and mask/type matching.

## Control Flow
Transform init calls `crypto_shash_init_tfm()`, marks keyed algorithms with `CRYPTO_TFM_NEED_KEY`, installs an exit wrapper if needed, then delegates to `alg->init_tfm()`. Operational calls reject `CRYPTO_TFM_NEED_KEY`. Missing algorithm hooks are filled in by `shash_prepare_alg()`: `finup` becomes update+final, `digest` becomes init+finup, unset setkey becomes `shash_no_setkey()`, and missing import/export defaults to descriptor memcpy where allowed. Block-only hashes get extra descriptor and state bytes for a partial block buffer plus one-byte length; `crypto_shash_finup()` drains full blocks, retains required final bytes for `CRYPTO_AHASH_ALG_FINAL_NONZERO`, and zeroes descriptor context after finalization.

## State And Persistence
State is per transform plus per request descriptor context. Keyed algorithms persist key material in the transform and advertise missing-key state through flags. Export/import serializes the algorithm state and, for block-only hashes, the local partial block tail. Finalization and digest paths explicitly zero descriptor context after use, limiting residue lifetime. No filesystem persistence exists.

## Dependencies And Integration Points
This file depends on `hash.h`, `crypto_tfm`, Crypto API spawn/instance infrastructure, `scatterwalk`, netlink cryptouser reports, and optional procfs output. Algorithms such as SM3 and Streebog register through the exported shash registration functions.

## Risks
Important risks are descriptor size/state size accounting, import validation of the block-only partial length, correct zeroization after errors/finalization, and avoiding export/import mismatches when an algorithm supplies only one hook. The block-only buffer layout relies on `descsize - (blocksize + 1)` conventions that must remain in sync with `shash_prepare_alg()`.

## Test Signals
Useful signals include `tcrypt` hash modes, `crypto/testmgr` import/export tests, keyed hash tests that assert `-ENOKEY` before setkey, block-only hash streaming tests around exact block boundaries, and KASAN/KMSAN runs for descriptor buffer bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/shash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sig.c -->
# sources/distributed-fs/ceph-client/crypto/sig.c

## Purpose
`sig.c` implements the Crypto API public-key signature algorithm type. It provides allocation, registration, template instance registration, spawn grabbing, transform init/exit, default unsupported operations, and user/proc reporting for `CRYPTO_ALG_TYPE_SIG`.

## Important APIs, Types, And Functions
The main exported entry points are `crypto_alloc_sig()`, `crypto_register_sig()`, `crypto_unregister_sig()`, `sig_register_instance()`, and `crypto_grab_sig()`. The core type descriptor is `crypto_sig_type`. `sig_prepare_alg()` validates and normalizes `struct sig_alg`, installing default `-ENOSYS` stubs for absent `sign`, `verify`, and private-key setting, requiring `set_pub_key` and `key_size`, and deriving `max_size`/`digest_size` from key size when omitted.

## Control Flow
Registration runs through `sig_prepare_alg()`, then `crypto_register_alg()`. Transform initialization installs `crypto_sig_exit_tfm()` if the algorithm provides `exit`, calls `alg->init()` when present, and otherwise succeeds. Instance cleanup calls the template-provided `sig->free()` callback. Allocation uses `crypto_alloc_tfm()` constrained by `crypto_sig_type`.

## State And Persistence
Persistent state is limited to per-transform key and algorithm private state managed by concrete `sig_alg` implementations. This file does not serialize state, store keys, or allocate per-request buffers. Defaults intentionally make missing operations fail explicitly with `-ENOSYS`.

## Dependencies And Integration Points
It depends on `<crypto/internal/sig.h>`, common Crypto API internals, cryptouser netlink reports, procfs display, and template/spawn infrastructure. Consumers allocate by algorithm name through `crypto_alloc_sig()` and call operation wrappers defined elsewhere in the sig API.

## Risks
The main risk is accepting underspecified algorithms; `sig_prepare_alg()` mitigates this by requiring public-key loading and key-size support. Defaulting `sign`/`verify` to `-ENOSYS` allows verify-only or sign-only providers but callers must handle unsupported paths. Size defaults based on key bits may be unsuitable for algorithms with nontrivial encoding unless overridden.

## Test Signals
Tests should cover registration rejection when `set_pub_key` or `key_size` is absent, init/exit callback pairing, user/proc reporting, `-ENOSYS` behavior for missing sign/verify/private-key hooks, and successful allocation/spawn through template users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/simd.c -->
# sources/distributed-fs/ceph-client/crypto/simd.c

## Purpose
`simd.c` provides shared helpers for registering AEAD algorithms that wrap internal SIMD implementations. The wrapper presents an asynchronous public AEAD and routes requests either directly to the SIMD child when SIMD is usable or through cryptd when execution context cannot safely use SIMD.

## Important APIs, Types, And Functions
Exports are `simd_register_aeads_compat()` and `simd_unregister_aeads()`. Private types are `struct simd_aead_alg`, containing the public wrapper `aead_alg` and internal algorithm name, and `struct simd_aead_ctx`, holding a `cryptd_aead`. Core callbacks include `simd_aead_init()`, `simd_aead_exit()`, `simd_aead_setkey()`, `simd_aead_setauthsize()`, `simd_aead_encrypt()`, and `simd_aead_decrypt()`.

## Control Flow
Registration first verifies each internal AEAD name and driver name start with `"__"`, registers those internal algorithms, then creates public names by stripping the prefix. `simd_aead_init()` allocates a cryptd wrapper for the internal driver and sizes wrapper requests to fit either direct child or cryptd request state plus one copied subrequest. Encrypt/decrypt copy the original request into request context, select cryptd when `crypto_simd_usable()` is false or when atomic context would queue onto already queued cryptd work, set the selected child transform, and invoke the child AEAD operation.

## State And Persistence
State is per transform: the wrapper stores only `cryptd_tfm`; the child holds key/authsize state. Requests keep a copied `aead_request` in request context. There is no persistent storage; unregister frees wrappers and unregisters internal algorithms.

## Dependencies And Integration Points
The file integrates `crypto/cryptd.h`, `crypto/internal/aead.h`, `crypto/internal/simd.h`, `asm/simd.h`, and preemption/atomic context checks. Architecture-specific SIMD AEAD providers use this helper to expose public algorithms safely.

## Risks
Risk centers on request size calculation, preserving request flags across setkey, and selecting the correct child in atomic contexts. Internal algorithms must be named with the `"__"` convention or registration fails. Because public wrappers are async, synchronous-only allocators will intentionally not find them.

## Test Signals
Signals include registration/unregistration of prefixed AEADs, encryption/decryption in normal and atomic-like contexts, cryptd fallback coverage, setkey flag propagation, authsize propagation, and request-size KASAN checks under concurrent AEAD operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/simd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/skcipher.c -->
# sources/distributed-fs/ceph-client/crypto/skcipher.c

## Purpose
`skcipher.c` implements the Crypto API symmetric-key cipher frontend. It provides scatterlist walking, key setting, encrypt/decrypt dispatch, state import/export, transform allocation, sync allocation checks, algorithm registration, template instance registration, and a helper for simple block-cipher modes.

## Important APIs, Types, And Functions
Important exports include `skcipher_walk_virt()`, `skcipher_walk_aead_encrypt()`, `skcipher_walk_aead_decrypt()`, `skcipher_walk_done()`, `crypto_skcipher_setkey()`, `crypto_skcipher_encrypt()`, `crypto_skcipher_decrypt()`, `crypto_skcipher_export()`, `crypto_skcipher_import()`, `crypto_alloc_skcipher()`, `crypto_alloc_sync_skcipher()`, `crypto_has_skcipher()`, `crypto_register_skcipher(s)()`, `crypto_unregister_skcipher(s)()`, `skcipher_register_instance()`, and `skcipher_alloc_instance_simple()`.

## Control Flow
Walk setup initializes total length, IV pointers, flags, scatterwalk positions, block size, stride, IV size, and alignmask. `skcipher_walk_next()` chooses fast mapped walking, copy mode for alignment fixes, or slow temporary-buffer mode for cross-page/block constraints. `skcipher_walk_done()` advances source/destination scatterwalks, copies temporary output when needed, propagates IV changes back, frees temporary page/buffer resources, and schedules the next segment. Transform init handles native skcipher algorithms or lskcipher-backed algorithms, sets need-key flags, and computes request size. Encrypt/decrypt reject missing keys, dispatch to lskcipher sg adapters for lskcipher-backed transforms, or call native algorithm callbacks.

## State And Persistence
State is per transform for keys and algorithm context, per request for IV/state, and per walk for temporary pages/buffers. `CRYPTO_TFM_NEED_KEY` persists until setkey succeeds. Lskcipher-backed import/export stores state after an aligned IV area in request context. No filesystem persistence exists.

## Dependencies And Integration Points
The file integrates scatterwalk, internal cipher/aead/skcipher APIs, lskcipher sg adapters from `skcipher.h`, cryptouser reporting, procfs reporting, algorithm template/spawn infrastructure, and simple block cipher modes that wrap `crypto_cipher` children.

## Risks
High-risk areas are page-boundary walking, alignment handling, IV copy-back, partial-block rejection, request size limits for sync allocations, and correct key-length validation. lskcipher compatibility paths must keep request-context layout consistent with `crypto_lskcipher_export()` and `crypto_lskcipher_import()`. Walk slow paths allocate memory with either `GFP_KERNEL` or `GFP_ATOMIC`; callers must set sleepability correctly.

## Test Signals
Coverage should include in-place and out-of-place scatterlists, unaligned source/destination/IV buffers, cross-page input, non-block-multiple lengths, no-key errors, lskcipher-backed transforms, sync request-size rejection, template instance allocation, and `tcrypt` skcipher modes 200/500/600 plus `crypto/testmgr` vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/skcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/skcipher.h -->
# sources/distributed-fs/ceph-client/crypto/skcipher.h

## Purpose
`skcipher.h` is a local internal header connecting the generic skcipher frontend with lskcipher scatterlist adapter helpers and shared algorithm-preparation logic.

## Important APIs, Types, And Functions
It declares `crypto_lskcipher_encrypt_sg()`, `crypto_lskcipher_decrypt_sg()`, `crypto_init_lskcipher_ops_sg()`, and `skcipher_prepare_alg_common()`. It includes `<crypto/internal/skcipher.h>` and local `"internal.h"`, then wraps declarations with `_LOCAL_CRYPTO_SKCIPHER_H`.

## Control Flow
There is no runtime control flow in this file. It provides compile-time declarations used by `skcipher.c` and lskcipher compatibility code elsewhere.

## State And Persistence
No state is stored here. The declarations imply that lskcipher-backed skcipher transforms keep request state in skcipher request context and use sg adapter functions defined elsewhere.

## Dependencies And Integration Points
`skcipher.c` includes this header for lskcipher sg dispatch and common validation. Any source implementing the declared functions must match the request layout and behavior expected by `skcipher.c`.

## Risks
Risk is mostly ABI drift inside the local crypto subtree: changing prototypes or request-layout expectations without matching `skcipher.c` and adapter implementations can break lskcipher-backed algorithms at compile time or runtime.

## Test Signals
Build coverage is the first signal. Runtime signals are successful allocation and operation of lskcipher-backed skcipher algorithms, including encrypt/decrypt, import/export, and request-size handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/skcipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sm3.c -->
# sources/distributed-fs/ceph-client/crypto/sm3.c

## Purpose
`sm3.c` registers the SM3 hash as a shash algorithm backed by the shared SM3 library implementation. It exposes `"sm3"` and `"sm3-lib"` Crypto API aliases.

## Important APIs, Types, And Functions
The module defines `crypto_sm3_init()`, `crypto_sm3_update()`, `crypto_sm3_final()`, `crypto_sm3_digest()`, `crypto_sm3_export_core()`, `crypto_sm3_import_core()`, and `sm3_alg`. The descriptor context is `struct sm3_ctx`, accessed through `SM3_CTX(desc)`.

## Control Flow
Module init registers `sm3_alg` with `crypto_register_shash()`. Init delegates to `sm3_init()`, update to `sm3_update()`, final to `sm3_final()`, and one-shot digest to `sm3()`. Core export/import simply memcpy the whole `struct sm3_ctx`.

## State And Persistence
SM3 state lives in the shash descriptor context and is exported/imported as raw `struct sm3_ctx`. No keys or persistent storage are involved.

## Dependencies And Integration Points
This file depends on `<crypto/sm3.h>` library routines and `<crypto/internal/hash.h>` registration. It integrates with the generic shash frontend in `shash.c`, `testmgr`, and `tcrypt` modes for SM3.

## Risks
The main risks are struct-layout compatibility for import/export and matching the library implementation's expected state representation. Since export/import copies the full context, any future nonportable fields in `struct sm3_ctx` would matter.

## Test Signals
Signals include SM3 known-answer tests, incremental update versus one-shot digest equivalence, export/import resume tests, module alias allocation, and `tcrypt` mode 52 or hash speed modes 326/422.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sm3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sm4.c -->
# sources/distributed-fs/ceph-client/crypto/sm4.c

## Purpose
`sm4.c` implements the shared generic SM4 block cipher library: constants, S-box, key expansion, and single-block encryption/decryption primitive. It is not the Crypto API algorithm registration layer; `sm4_generic.c` provides that.

## Important APIs, Types, And Functions
Exported symbols are `crypto_sm4_fk`, `crypto_sm4_ck`, `crypto_sm4_sbox`, `sm4_expandkey()`, and `sm4_crypt_block()`. Internal helpers implement nonlinear substitution, key linear transform, encryption linear transform, key substitution, encryption substitution, and one SM4 round.

## Control Flow
`sm4_expandkey()` validates a 16-byte key, loads it big-endian, xors fixed FK constants, then derives 32 round keys using CK constants and the SM4 key schedule. It fills encryption keys in forward order and decryption keys in reverse order. `sm4_crypt_block()` loads a 16-byte block big-endian, performs 32 rounds four at a time using the supplied key schedule, then stores the reversed output words.

## State And Persistence
Expanded round keys live in caller-provided `struct sm4_ctx`. The constant tables are static read-only data and exported aliases. No persistent storage exists.

## Dependencies And Integration Points
Consumers include `sm4_generic.c` and architecture-optimized SM4 providers. The file depends on `<crypto/sm4.h>`, unaligned big-endian accessors, and module export infrastructure.

## Risks
Risks are algorithmic correctness in endian handling, reverse-order decryption key layout, and table-based S-box side-channel properties on platforms without constant-time lookup protections. Bad key sizes return `-EINVAL`; callers must not use uninitialized contexts after setkey failure.

## Test Signals
Signals include SM4 known-answer vectors, encrypt-decrypt round trips, decryption using `rkey_dec`, module symbol users, and `tcrypt` SM4 modes for ecb/cbc/ctr/xts/gcm/ccm/cmac/xcbc/cbcmac.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sm4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sm4_generic.c -->
# sources/distributed-fs/ceph-client/crypto/sm4_generic.c

## Purpose
`sm4_generic.c` registers the generic SM4 single-block cipher with the Crypto API cipher interface. It wraps the shared SM4 library routines from `sm4.c`.

## Important APIs, Types, And Functions
The main functions are `sm4_setkey()`, `sm4_encrypt()`, `sm4_decrypt()`, `sm4_init()`, and `sm4_fini()`. The registered `crypto_alg` is `sm4_alg`, with name `"sm4"`, driver `"sm4-generic"`, 16-byte block size, 16-byte key size, and `struct sm4_ctx` transform context.

## Control Flow
Module init calls `crypto_register_alg(&sm4_alg)`. Setkey fetches `struct sm4_ctx` from `crypto_tfm_ctx()` and calls `sm4_expandkey()`. Encrypt/decrypt fetch the same context and call `sm4_crypt_block()` with encryption or decryption round-key arrays. Exit unregisters the algorithm.

## State And Persistence
Per-transform state is the expanded SM4 key schedule in `struct sm4_ctx`. No per-request allocations or persistent storage are used.

## Dependencies And Integration Points
This file depends on the generic SM4 library exported by `sm4.c` and the legacy Crypto API `CRYPTO_ALG_TYPE_CIPHER` interface. Block modes such as ecb/cbc/ctr/skcipher templates can wrap this cipher.

## Risks
Risks include using the legacy cipher API rather than skcipher directly, failure propagation from invalid key lengths, and table-lookup side channels inherited from the generic library. The context must be keyed before block operations.

## Test Signals
Signals include allocation by `"sm4"` and `"sm4-generic"`, setkey rejection for non-16-byte keys, known-answer vectors through ecb(sm4), and `tcrypt` modes 191/218/518 plus AEAD/mode users that depend on SM4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sm4_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/streebog_generic.c -->
# sources/distributed-fs/ceph-client/crypto/streebog_generic.c

## Purpose
`streebog_generic.c` implements and registers the generic Streebog/GOST R 34.11-2012 hash functions for 256-bit and 512-bit digests. It contains the compression function, finalization logic, state counters, and large precomputed transform tables.

## Important APIs, Types, And Functions
Important functions are `streebog_init()`, `streebog_update()`, `streebog_finup()`, `streebog_stage2()`, `streebog_stage3()`, `streebog_g()`, `streebog_round()`, `streebog_xlps()`, `streebog_xor()`, and `streebog_add512()`. It registers two `shash_alg` entries: `"streebog256"`/`"streebog256-generic"` and `"streebog512"`/`"streebog512-generic"`, both marked `CRYPTO_AHASH_ALG_BLOCK_ONLY`.

## Control Flow
Init zeroes `struct streebog_state` and seeds `h` with all `0x01` bytes for 256-bit mode. Update processes full 64-byte blocks only and returns the leftover byte count for the shash block-only frontend to buffer. `streebog_stage2()` compresses a full block, increments bit counter `N` by 512, and adds the message block to `Sigma`. Finalization pads the remaining bytes with a `1` byte, compresses the final block, adds the final bit length and final message block into counters, then compresses `N` and `Sigma` under zero. Digest output is the upper half for Streebog-256 and full state for Streebog-512.

## State And Persistence
State is per shash descriptor: chaining value `h`, processed-bit counter `N`, message sum `Sigma`, and final hash buffer. The shash frontend stores any partial block tail outside `struct streebog_state` because the algorithm is block-only. Temporary finalization union is wiped with `memzero_explicit()`. No filesystem persistence exists.

## Dependencies And Integration Points
This file depends on `<crypto/streebog.h>`, shash registration from `<crypto/internal/hash.h>`, little-endian helpers, and `shash.c` block-only buffering. `tcrypt` directly references Streebog test and speed modes.

## Risks
The largest risks are correctness of little-endian arithmetic/carry handling in `streebog_add512()`, block-only interaction with shash buffering, final padding for zero-length and boundary-length messages, and table integrity. `streebog_update()` assumes `len >= STREEBOG_BLOCK_SIZE`; the shash block-only frontend must enforce that. Table-based transforms may expose cache-timing behavior.

## Test Signals
Signals include RFC 6986 known-answer vectors for both digest sizes, empty-message and 63/64/65-byte boundary tests, incremental update versus one-shot digest equivalence, export/import through shash core where applicable, HMAC Streebog tests, and `tcrypt` modes 53, 54, 115, 116, 327, and 328.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/streebog_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/tcrypt.c -->
# sources/distributed-fs/ceph-client/crypto/tcrypt.c

## Purpose
`tcrypt.c` is a late-init benchmarking and smoke-test module for Crypto API algorithms. It allocates scratch pages, runs selected correctness tests through `alg_test()`, and runs throughput/cycle benchmarks for AEAD, ahash/shash, skcipher, async skcipher, and multibuffer request patterns.

## Important APIs, Types, And Functions
Main module parameters are `alg`, `type`, `mask`, `mode`, `sec`, `num_mb`, and `klen`. Core helpers include `testmgr_alloc_buf()`, `sg_init_aead()`, `do_one_aead_op()`, `do_mult_aead_op()`, `test_aead_speed()`, `test_mb_aead_speed()`, `test_hash_sg_init()`, `test_ahash_speed_common()`, `test_skcipher_speed()`, `test_mb_skcipher_speed()`, `tcrypt_test()`, `do_test()`, and `tcrypt_mod_init()`.

## Control Flow
Module init allocates `TVMEMSIZE` pages, clamps `num_mb` to at least one, and calls `do_test()`. Mode 0 checks a named algorithm or iterates modes 1..199. Correctness modes call `tcrypt_test()`, which delegates to `alg_test()` and treats certain non-FIPS algorithms as pass-skipped in FIPS mode. Speed modes allocate transforms and requests, set keys/auth sizes/IVs, initialize scatterlists over scratch pages, optionally pre-encrypt AEAD decrypt buffers to create valid tags, then benchmark either for `sec` seconds using jiffies or for fixed warm-up/measured loops using `get_cycles()`. Non-FIPS init intentionally returns `-EAGAIN` after work completes so the module does not remain loaded.

## State And Persistence
Global module state includes parameter values and `tvmem` scratch pages. Per-test state includes allocated transforms, requests, scatterlists, callback waits, and page buffers. Buffers are filled mostly with `0xff`; no results are persisted. All scratch pages are freed on init exit paths.

## Dependencies And Integration Points
This file exercises the broad Crypto API: `crypto_aead`, `crypto_ahash`, `crypto_skcipher`, `alg_test()`, async callback waits, scatterlists, jiffies, cycles, FIPS mode, and the speed templates from `tcrypt.h`. It is a consumer of algorithms registered by files such as SM3, SM4, Streebog, TEA, shash, and skcipher.

## Risks
Risks include benchmark side effects from shared transform state, invalid test setup for algorithms with unusual IV/key/auth constraints, memory cleanup mistakes across many goto paths, and misleading speed results from fixed all-`0xff` inputs or cycle counter behavior. Multibuffer paths stress asynchronous completion and can expose request reuse issues. Mode dispatch is large and easy to drift when algorithms are renamed.

## Test Signals
Useful signals are successful module load/run for targeted modes, expected `-EAGAIN` in non-FIPS after pass, absence of allocation leaks under fault injection, correct AEAD decrypt pre-auth setup, and mode-specific logs for SM3, SM4, Streebog, TEA/XTEA/XETA, hash speed ranges 300/400, skcipher speed ranges 200/500/600, and AEAD multibuffer ranges 215..225.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/tcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/tcrypt.h -->
# sources/distributed-fs/ceph-client/crypto/tcrypt.h

## Purpose
`tcrypt.h` defines data structures and static speed-template data used by `tcrypt.c`. It centralizes key-size lists, a DES3 benchmark key, AEAD key-size lists, and generic hash block/update sizes.

## Important APIs, Types, And Functions
The file defines `struct cipher_speed_template`, `struct aead_speed_template`, and `struct hash_speed`. It provides `DES3_SPEED_VECTORS`, `des3_speed_template[]`, multiple `speed_template_*` arrays, AEAD templates, and `generic_hash_speed_template[]`.

## Control Flow
There is no runtime control flow. `tcrypt.c` iterates zero-terminated key-size arrays and hash speed arrays until `.blen == 0`.

## State And Persistence
The file contributes static read-only test data to the tcrypt module. It does not store runtime state or persistent artifacts.

## Dependencies And Integration Points
It is included directly by `tcrypt.c`. The block/key sizes here determine the coverage matrix for cipher, AEAD, and hash benchmark modes.

## Risks
Template mistakes can silently skip key sizes, use invalid key lengths for a mode, or bias benchmark coverage. The DES3 vector is a fixed key used only for speed tests, not secret material.

## Test Signals
Signals include successful compilation, benchmark modes iterating the expected key-size counts, no buffer-size overflows in `tcrypt.c` for the largest templates, and visible log coverage for each `generic_hash_speed_template` entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/tcrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/tea.c -->
# sources/distributed-fs/ceph-client/crypto/tea.c

## Purpose
`tea.c` registers generic TEA, XTEA, and XETA block ciphers with the Crypto API legacy cipher interface. XETA preserves compatibility with historically incorrect XTEA operation ordering.

## Important APIs, Types, And Functions
The module defines `struct tea_ctx`, `struct xtea_ctx`, `tea_setkey()`, `tea_encrypt()`, `tea_decrypt()`, `xtea_setkey()`, `xtea_encrypt()`, `xtea_decrypt()`, `xeta_encrypt()`, `xeta_decrypt()`, and `tea_algs[3]`. Algorithms are named `"tea"`, `"xtea"`, and `"xeta"` with corresponding `*-generic` driver names, 16-byte keys, and 8-byte blocks.

## Control Flow
Setkey reads four little-endian 32-bit key words into the transform context. TEA encrypt/decrypt run 32 rounds with delta accumulation or reverse subtraction. XTEA encrypt/decrypt use XTEA key index formulas based on `sum`, while XETA uses the compatibility formula with altered grouping/order. Module init registers all three algorithms with `crypto_register_algs()`; exit unregisters them.

## State And Persistence
Per-transform state is the four-word key schedule. There are no per-request allocations and no persistent storage. The algorithms operate on one 8-byte block per cipher callback.

## Dependencies And Integration Points
The file depends on `<crypto/algapi.h>` and unaligned little-endian helpers. Mode templates such as ECB can wrap these ciphers, and `tcrypt` includes correctness modes for TEA, XTEA, and XETA.

## Risks
TEA-family ciphers are legacy and cryptographically weak for modern use. The implementation assumes the Crypto API enforces 16-byte key lengths before setkey, since setkey itself does not validate `key_len`. Endian behavior is little-endian and must match test vectors. XETA exists specifically for compatibility and should not be mistaken for correct XTEA.

## Test Signals
Signals include known-answer vectors for all three ciphers, encrypt/decrypt round trips, key-length rejection through the Crypto API, module alias allocation, and `tcrypt` modes 19, 20, and 30.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/tea.c -->
