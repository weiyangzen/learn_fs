# subset-b-007776 Research

Grouped research for Heimdal hcrypto EVP, digest, HMAC, KDF, random, legacy cipher, AES, UI, and validation files imported under OpenAFS. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.h

Purpose: declares the hcrypto provider-specific EVP factories. It gives the generic EVP layer a stable set of `EVP_hcrypto_*` digest and cipher descriptors while symbol-renaming them into the `hc_` namespace to avoid OpenSSL collisions.

Important APIs/types/functions: the header exports digest factories for MD2, MD4, MD5, SHA1, SHA256, SHA384, and SHA512, plus cipher factories for RC4, RC4-40, RC2 CBC variants, DES CBC, 3DES CBC, AES CBC/CFB8 variants, and Camellia CBC variants. It relies on `EVP_MD`, `EVP_CIPHER`, and `HC_CPP_BEGIN/END` from `evp.h`.

Control flow: callers include `evp.h` first, then call a factory such as `EVP_hcrypto_aes_256_cbc()` to obtain a static descriptor consumed by `EVP_CipherInit_ex()` or `EVP_DigestInit_ex()`. This file has no executable flow of its own.

State and persistence: no runtime state is defined here. All returned descriptor storage lives in provider implementation files such as `evp-hcrypto.c`.

Dependencies and integration points: integrates generic `evp.c` selection through `EVP_DEF_OP(HCRYPTO_DEF_PROVIDER, op)` and test/validation code that explicitly calls provider factories. The symbol renames are important when this bundled Heimdal copy is built beside OpenSSL-like APIs.

Risks and test signals: declaration drift against `evp-hcrypto.c` is the main risk. Build coverage should prove every declared factory exists for the configured provider set; cipher self-tests in `test_cipher.c` and `validate.c` exercise many of these descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.c

Purpose: implements an OpenSSL-compatible EVP facade over Heimdal hcrypto provider descriptors. It manages digest and cipher contexts, dispatches digest/cipher calls through function pointers, exposes algorithm factory aliases, implements legacy key derivation, and provides no-op algorithm registration hooks.

Important APIs/types/functions: digest APIs include `EVP_MD_CTX_create/init/destroy/cleanup`, `EVP_MD_size`, `EVP_MD_block_size`, `EVP_DigestInit_ex`, `EVP_DigestUpdate`, `EVP_DigestFinal_ex`, `EVP_Digest`, and factories for SHA/MD/null digests. Cipher APIs include `EVP_CIPHER_*` metadata calls, `EVP_CIPHER_CTX_init/cleanup/set_key_length/get_app_data/set_app_data`, `EVP_CipherInit_ex`, `EVP_CipherUpdate`, `EVP_CipherFinal_ex`, `EVP_Cipher`, `EVP_get_cipherbyname`, `EVP_CIPHER_CTX_rand_key`, and `EVP_CIPHER_CTX_ctrl`. `EVP_BytesToKey` implements the legacy PEM-style MD chaining derivation.

Control flow: digest initialization cleans/reallocates context storage when the selected digest or engine changes, then calls the descriptor init function. Updates/finalization dispatch directly to descriptor callbacks. Cipher initialization resets buffered bytes, sets encryption direction, allocates provider private data when the cipher changes, initializes IV state based on CBC/stream/CFB8 mode, and calls the cipher init callback when a key is present or `EVP_CIPH_ALWAYS_CALL_INIT` is set. `EVP_CipherUpdate` either fast-paths block-aligned input directly to `do_cipher` or buffers partial blocks. `EVP_CipherFinal_ex` zero-pads any leftover partial block and encrypts/decrypts it; this is not PKCS#7 padding. Algorithm factory functions call `hcrypto_validate()` and then dispatch to the configured provider.

State and persistence: digest contexts hold `md`, `engine`, and provider-private `ptr`; cipher contexts hold descriptor, engine, IVs, partial block buffer, key length, flags, app data, and provider-private `cipher_data`. Cleanup zeroes private digest/cipher data before freeing. Static state is limited to name lookup tables and immutable null digest/cipher descriptors.

Dependencies and integration points: depends on `evp.h`, `evp-hcrypto.h`, optional `evp-cc.h`, `rand.h`, `roken`, and provider implementations. It is the central API used by HMAC, PBKDF2, validation, DES random key helpers, and higher Heimdal/OpenAFS crypto callers expecting OpenSSL-like EVP names.

Risks and test signals: important risks include no NULL checks for several descriptor callbacks, no allocation failure checks for HMAC-style callers, zero padding in finalization surprising users expecting OpenSSL default padding, partial-block behavior for decryption, `EVP_get_cipherbyname()` covering only a subset of descriptors, and validation recursion if factory calls happen during validation failures. Tests should cover digest one-shot and streaming equivalence, context reuse, CBC partial updates/finals, stream/CFB8 modes, variable key lengths, `EVP_BytesToKey` vectors, random key generation, and name lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.h

Purpose: defines the public hcrypto EVP compatibility API and the in-memory descriptor/context layouts used by `evp.c` and provider implementations.

Important APIs/types/functions: typedefs cover `EVP_MD_CTX`, `EVP_PKEY`, `EVP_MD`, `EVP_CIPHER`, and `EVP_CIPHER_CTX`. `struct hc_CIPHER` defines metadata, mode/flag bits, init/do_cipher/cleanup/ctrl callbacks, context size, and app data. `struct hc_CIPHER_CTX` stores selected cipher, engine, direction, IVs, buffers, app data, key length, flags, provider data, and block mask. `struct hc_evp_md` defines digest sizes and init/update/final/cleanup callbacks. The header declares all digest, cipher, KDF, random-key, ctrl, and registration APIs implemented in `evp.c`.

Control flow: callers allocate or stack-initialize contexts using the declared APIs, never by directly calling provider callbacks. Provider files populate descriptor structs whose callbacks are invoked by the generic EVP code.

State and persistence: the header itself has no state, but it fixes ABI-sensitive state layout for contexts and descriptors. `EVP_MAX_IV_LENGTH`, `EVP_MAX_BLOCK_LENGTH`, and `EVP_MAX_MD_SIZE` bound internal buffers and caller expectations.

Dependencies and integration points: includes `hcrypto/engine.h`, exposes C++ linkage guards, and renames public symbols to `hc_*`. It must stay consistent with `evp.c`, `evp-hcrypto.c`, HMAC/PBKDF2 callers, and external code compiled against Heimdal hcrypto.

Risks and test signals: risks are ABI drift, mode flag misuse, and buffer constant mismatches with provider block sizes. Compile coverage across all provider files and runtime EVP validation are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hash.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hash.h

Purpose: provides small shared helpers for MD4, MD5, SHA1, SHA256, and SHA512 implementations.

Important APIs/types/functions: defines `min(a,b)`, `CRAYFIX()` for platforms where 32-bit arithmetic needs masking, `cshift(uint32_t,unsigned int)` for 32-bit rotates, and `cshift64(uint64_t,unsigned int)` for 64-bit rotates.

Control flow: digest compression functions call these inline rotate helpers inside round macros. There is no standalone runtime flow.

State and persistence: no state is stored. All helpers operate on values passed by caller.

Dependencies and integration points: includes `krb5-types.h` under `KRB5` and `roken.h` for portable integer and platform support. It is shared by the hash implementation files and centralizes portability behavior.

Risks and test signals: rotate helpers assume nonzero rotation counts less than word width as used by the digest algorithms. Tests are indirect: known-answer vectors for MD4/MD5/SHA1/SHA2 on little-endian, big-endian, and unusual integer platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.c

Purpose: implements HMAC over the hcrypto EVP digest API, including reusable `HMAC_CTX` state and a one-shot convenience wrapper.

Important APIs/types/functions: `HMAC_CTX_init`, `HMAC_CTX_cleanup`, `HMAC_size`, `HMAC_Init_ex`, `HMAC_Update`, `HMAC_Final`, and `HMAC`. Context fields include selected digest, optional engine, inner digest context, digest-sized buffer, and allocated inner/outer pads.

Control flow: initialization clears the context. `HMAC_Init_ex` updates the digest selection, allocates a digest-sized work buffer, hashes overlong keys down to digest size, allocates block-sized ipad/opad buffers, XORs the key into 0x36/0x5c pads, creates the nested EVP context if needed, and starts the inner digest with ipad. `HMAC_Update` feeds message data. `HMAC_Final` finalizes the inner digest into `buf`, starts a new digest over opad plus inner digest, and returns the outer digest. The one-shot wrapper performs init, update, final, and cleanup on a stack context.

State and persistence: reusable contexts persist allocated pads, a digest work buffer, and an EVP digest context until cleanup. Cleanup zeroes buffers before free and destroys the EVP context.

Dependencies and integration points: depends on `hmac.h`, `evp.h`, and provider digest descriptors. Used by `pkcs5.c` and `validate.c`, and by callers needing OpenSSL-compatible `HMAC()`.

Risks and test signals: `HMAC_Init_ex` does not check malloc or `EVP_MD_CTX_create` failures before use, cleanup zero lengths use `key_length` for pads even though pads are block-sized in two spots, and engine storage is disabled under `#if 0`. Tests should cover RFC-style HMAC vectors, overlong keys, repeated reuse with different digests/keys, cleanup under partially initialized contexts, and allocation-failure hardening if relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.h

Purpose: declares the hcrypto HMAC API and `HMAC_CTX` layout.

Important APIs/types/functions: renames HMAC symbols to `hc_*`, defines `HMAC_MAX_MD_CBLOCK`, declares opaque typedef `HMAC_CTX` while exposing `struct hc_HMAC_CTX`, and prototypes context lifecycle, size, init/update/final, and one-shot `HMAC`.

Control flow: consumers allocate `HMAC_CTX`, call init/init_ex/update/final/cleanup, or use one-shot `HMAC`. The actual data flow is in `hmac.c`.

State and persistence: defines persistent per-HMAC fields: digest pointer, engine pointer, nested EVP context, key/digest buffer length, opad, ipad, and digest buffer.

Dependencies and integration points: includes `hcrypto/evp.h`; therefore digest descriptors and engine types are shared with the EVP layer. It is used by PBKDF2 and validation code.

Risks and test signals: layout exposure makes ABI compatibility important. Compile-time signature checks plus HMAC known-answer tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.c

Purpose: implements the legacy MD2 message digest primitive.

Important APIs/types/functions: `MD2_Init` zeroes context state; private `calc` processes one 16-byte block using the MD2 substitution table, checksum, and 48-byte working state; `MD2_Update` buffers unaligned input and processes full blocks; `MD2_Final` applies MD2 padding, appends the checksum block, emits 16 bytes, and clears the context.

Control flow: updates accumulate `len`, process pending plus incoming bytes whenever 16-byte blocks are available, and keep any tail in `data`. Finalization computes padding length from total length, feeds padding and checksum through the same update path, then copies `state`.

State and persistence: `struct md2` persists total byte length, a 16-byte partial block, a 16-byte checksum, and a 16-byte state. Finalization zeroes the full context.

Dependencies and integration points: includes `hash.h` and `md2.h`; the digest is exposed through provider EVP descriptors and deprecated EVP MD2 APIs.

Risks and test signals: MD2 is cryptographically obsolete and should be compatibility-only. Test with RFC 1319 known-answer vectors, segmented update inputs, exact block boundaries, and finalization context clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.h

Purpose: declares the MD2 context, digest length, and init/update/final functions.

Important APIs/types/functions: defines `MD2_DIGEST_LENGTH` as 16, `struct md2` with length, partial data, checksum, and state arrays, typedefs `MD2_CTX`, and symbol-renames `MD2_Init`, `MD2_Update`, and `MD2_Final`.

Control flow: consumers use the standard streaming digest sequence init, one or more updates, then final.

State and persistence: the context carries partial block and checksum state across updates; finalization in `md2.c` clears it.

Dependencies and integration points: included by `md2.c` and EVP provider descriptors.

Risks and test signals: ABI/layout drift and accidental use for modern security are the main risks. Compile coverage and MD2 known-answer vectors validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.c

Purpose: implements the legacy MD4 digest primitive.

Important APIs/types/functions: `MD4_Init`, private `calc` for the three MD4 rounds, endian `swap_uint32_t` on big-endian builds, `MD4_Update`, and `MD4_Final`. Round macros implement F/G/H functions and left rotations via `cshift`.

Control flow: update maintains a 64-bit bit count split across `sz[0]`/`sz[1]`, fills the 64-byte save buffer, transforms complete blocks, and handles endian conversion when needed. Final writes MD4 padding and little-endian length, feeds it through update, and serializes the four 32-bit state words little-endian.

State and persistence: context state consists of bit count, four counters, and one partial block. Unlike MD2, finalization does not explicitly zero the context after emitting output.

Dependencies and integration points: depends on `hash.h` and `md4.h`; exposed through deprecated EVP MD4 provider descriptors and used for compatibility protocols.

Risks and test signals: MD4 is broken cryptographically and should be compatibility-only. Alignment-sensitive casts to `uint32_t *` and bitfield helper structs need platform coverage. Test with standard MD4 vectors, segmented updates, big-endian behavior, and exact 55/56/64-byte padding boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.h

Purpose: declares the MD4 digest API and context shape.

Important APIs/types/functions: defines `MD4_DIGEST_LENGTH` as 16, `struct md4` with split size, four-word counter, and 64-byte save buffer, typedefs `MD4_CTX`, and renames `MD4_Init`, `MD4_Update`, and `MD4_Final` to hcrypto symbols.

Control flow: callers use init/update/final streaming semantics.

State and persistence: the context preserves bit count, compression state, and partial block across updates.

Dependencies and integration points: consumed by `md4.c` and provider EVP descriptors.

Risks and test signals: context layout and deprecated algorithm exposure are the key risks. Build coverage and MD4 known-answer vectors validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.c

Purpose: implements the legacy MD5 digest primitive for compatibility.

Important APIs/types/functions: `MD5_Init`, private `calc` with four MD5 rounds, endian swap helper for big-endian builds, `MD5_Update`, and `MD5_Final`. Round macros implement F/G/H/I functions and constants.

Control flow: update tracks total bit length in `sz`, accumulates data in `save`, transforms 64-byte blocks, and performs endian conversion as needed. Final adds `0x80` padding, zero fill, little-endian bit length, updates the state, and serializes four little-endian 32-bit words.

State and persistence: context stores split bit count, four digest words, and a partial block. Finalization does not zero the context, so callers should treat it as containing prior message state after use.

Dependencies and integration points: depends on `hash.h` and `md5.h`; exposed via deprecated EVP MD5 descriptors and useful for older Kerberos/OpenSSL-compatible formats.

Risks and test signals: MD5 is collision-broken and should not be used for new security decisions. Alignment-sensitive casts and overflow accounting need coverage. Test with RFC 1321 vectors, streaming splits, large inputs crossing `sz[0]`, and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.h

Purpose: declares the MD5 digest API and context structure.

Important APIs/types/functions: defines `MD5_DIGEST_LENGTH` as 16, `struct md5` with split size, four counters, and 64-byte save buffer, typedefs `MD5_CTX`, and declares renamed `MD5_Init`, `MD5_Update`, and `MD5_Final`.

Control flow: consumers use standard init/update/final sequencing.

State and persistence: context persists partial input, bit counters, and compression state between updates.

Dependencies and integration points: included by `md5.c` and EVP provider descriptors.

Risks and test signals: layout drift and unsafe modern use are primary risks. MD5 known-answer and segmented-update tests validate implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/pkcs5.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/pkcs5.c

Purpose: implements PBKDF2-HMAC-SHA1 for PKCS#5 v2 style password-to-key derivation.

Important APIs/types/functions: `PKCS5_PBKDF2_HMAC_SHA1(password, password_len, salt, salt_len, iter, keylen, key)` derives arbitrary-length output using `EVP_sha1()` and `HMAC()`.

Control flow: allocates one buffer holding the current checksum plus `salt || block_index`, loops over derived key blocks, computes U1 as HMAC(password, salt || INT(block)), copies the requested prefix into output, then iteratively computes U2..Uiter and XORs each into the output block. The block counter is encoded big-endian and increments for each output chunk.

State and persistence: only temporary heap storage is used; derived key bytes are written to caller memory. The temporary buffer is freed but not explicitly zeroed before free.

Dependencies and integration points: depends on `evp.h`, `hmac.h`, and `roken`. The API is declared from `evp.h` and used by callers needing OpenSSL-compatible PBKDF2-SHA1.

Risks and test signals: `iter == 0` is not rejected, temporary key material is not scrubbed, and malloc failure is the only explicit error path. Tests should cover RFC 6070 PBKDF2-HMAC-SHA1 vectors, multi-block output, short output, empty salt/password, high iteration counts, and invalid zero-iteration policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/pkcs5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-egd.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-egd.c

Purpose: implements a `RAND_METHOD` that talks to an Entropy Gathering Daemon over a Unix-domain socket, plus OpenSSL-compatible `RAND_egd*` helpers.

Important APIs/types/functions: private helpers `connect_egd`, `get_entropy`, `put_entropy`, `get_bytes`; method callbacks `egd_seed`, `egd_bytes`, `egd_cleanup`, `egd_add`, `egd_pseudorand`, `egd_status`; exported `RAND_egd_method`, `RAND_egd`, and `RAND_egd_bytes`.

Control flow: connections default to `/var/run/egd-pool`. Reads send EGD command `0x02` with a maximum 255-byte request and read the exact number of bytes. Writes send command `0x03` with entropy metadata and payload chunks. `RAND_egd_bytes` allocates a buffer, reads bytes from a requested path, seeds the selected global RAND method with them, scrubs the buffer, and frees it.

State and persistence: no persistent local state except the default path string. Entropy is external in the EGD service and, for `RAND_egd_bytes`, transferred into the global RAND subsystem.

Dependencies and integration points: depends on Unix socket APIs when available, `rand.h`, `randi.h`, and `roken` network read/write wrappers. Fortuna uses this as a fallback entropy source when stronger platform sources are unavailable.

Risks and test signals: EGD is legacy and can block or fail; `strlen(path) > sizeof(sun_path)` should arguably be `>=`; `put_entropy` sends zero entropy bits regardless of input quality; exact read/write behavior depends on `net_read/write`. Tests should cover missing socket, custom socket path, chunking over 255 bytes, short reads/writes, and seeding integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-egd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-fortuna.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-fortuna.c

Purpose: implements a Fortuna-like PRNG `RAND_METHOD` using SHA-256 entropy pools and AES-256 counter-mode output.

Important APIs/types/functions: `FState` stores counter, result block, key, 32 SHA-256 pools, AES key schedule, reseed metadata, pool0 byte count, random pool cursor, startup flag, and pid. Core helpers include `init_state`, `add_entropy`, `reseed`, `extract_data`, `rekey`, `startup_tricks`, `fortuna_reseed`, `fortuna_init`, and method callbacks `fortuna_seed`, `fortuna_bytes`, `fortuna_cleanup`, `fortuna_add`, `fortuna_pseudorand`, `fortuna_status`. Exported `RAND_fortuna_method` returns `hc_rand_fortuna_method`.

Control flow: initialization creates empty pools and attempts an initial seed. Entropy is hashed before being added to pool 0 before first reseed or a key-selected pool afterward. Reseed is gated by pool0 fill/time rules, mixes selected pool digests, old key, and pid into a new key, then resets pool0 byte accounting. Extraction reseeds when needed, performs one-time startup randomization, detects forks by pid, emits AES(counter) blocks, periodically rekeys for large requests, and rekeys at the end of every request. The public bytes path locks a global mutex, initializes if needed, triggers extra reseeds after `FORTUNA_RESEED_BYTE`, extracts, and unlocks.

State and persistence: global `main_state`, `init_done`, `have_entropy`, `resend_bytes`, and `fortuna_mutex` persist process-local PRNG state. Cleanup zeros `main_state` and resets flags. No state is saved to disk by this file.

Dependencies and integration points: depends on Heimdal thread mutexes, `randi.h`, AES, SHA-256, Unix/EGD/timer random methods, `arc4random` when available, `/etc/shadow` fallback reads, pid/time/uid entropy, and `rand.c` default method selection on non-Apple Unix.

Risks and test signals: fallback entropy marks success even for weak timer/metadata inputs, `/etc/shadow` read size handling hashes full buffer size instead of bytes read, global mutex serialization can bottleneck callers, and fork/reseed behavior is security-critical. Tests should cover initial seeding success/failure, deterministic hooks for add/extract, fork pid change, cleanup/reinit, concurrent `RAND_bytes`, large request rekeying, and operation when Unix/EGD sources are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-fortuna.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-timer.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-timer.c

Purpose: provides a last-resort timing-jitter `RAND_METHOD` for non-Windows platforms.

Important APIs/types/functions: signal handler `sigALRM`, optional forked `pacemaker` when `setitimer` is unavailable, and callbacks `timer_seed`, `timer_bytes`, `timer_cleanup`, `timer_add`, `timer_pseudorand`, `timer_status`, plus `RAND_timer_method`.

Control flow: `timer_bytes` points global volatile state at the caller buffer, installs a SIGALRM handler, starts a 10 ms interval timer or child pacemaker, and repeatedly increments a counter while the signal handler XORs low counter bits into output bytes. It rotates each output byte and repeats four passes, then restores timer and signal state.

State and persistence: uses file-static volatile `counter`, `gdata`, `igdata`, and `gsize` during generation. No long-term state is retained and seed/add are no-ops.

Dependencies and integration points: depends on signals, timers/select/fork/wait depending on platform, `rand.h`, `roken`, and `randi.h`. Fortuna calls it only as a weak fallback entropy source.

Risks and test signals: signal handler global state is process-wide and not thread-safe, entropy quality is weak and environment-dependent, Windows reports unsupported, and the non-`setitimer` path contains old code paths that are hard to exercise. Tests should limit this to availability, nonzero output variation, signal restoration, and Fortuna fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-unix.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-unix.c

Purpose: implements a Unix device-backed `RAND_METHOD` using `/dev/urandom` or similar devices.

Important APIs/types/functions: `_hc_unix_device_fd(flags, fn)` probes `/dev/urandom`, `/dev/random`, `/dev/srandom`, and `/dev/arandom`; method callbacks are `unix_seed`, `unix_bytes`, `unix_cleanup`, `unix_add`, `unix_pseudorand`, `unix_status`; `RAND_unix_method` returns the descriptor.

Control flow: reads open the first available random device with `O_NDELAY`, loop until the requested byte count is filled, retry on `EINTR`, and close. Seed/add attempts to open a writable random device and writes caller bytes, ignoring write failure. Status opens and closes a readable device.

State and persistence: no local state is retained. Writes may influence kernel RNG state depending on OS behavior and permissions.

Dependencies and integration points: depends on `rand.h`, `randi.h`, `roken`, Unix file APIs, and `rk_cloexec`. Used directly as the default method on Apple and as an entropy source for Fortuna elsewhere.

Risks and test signals: nonblocking `/dev/random` semantics vary, write-to-device seeding is often ignored or privileged, and every call reopens the device. Tests should cover device probe order, short/interrupted reads, zero/negative sizes, status failure when devices are absent, and cloexec behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-w32.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-w32.c

Purpose: implements the Windows CryptoAPI-backed `RAND_METHOD`.

Important APIs/types/functions: `_hc_CryptProvider` lazily initializes a global `HCRYPTPROV`; method callbacks are `w32crypto_seed`, `w32crypto_bytes`, `w32crypto_cleanup`, `w32crypto_add`, `w32crypto_status`; `RAND_w32crypto_method` returns the descriptor.

Control flow: provider acquisition tries `CryptAcquireContext` variants and publishes the selected provider with `InterlockedCompareExchangePointer`. `w32crypto_bytes` calls `CryptGenRandom`; pseudo-random bytes share the same callback. Seed/add are no-ops. Cleanup attempts to release the provider.

State and persistence: global volatile `g_cryptprovider` caches the CryptoAPI provider handle for the process. No random state file is used.

Dependencies and integration points: depends on Windows `wincrypt.h`, `rand.h`, Heimdal threading headers, and `randi.h`. `rand.c` selects this method by default on `_WIN32`.

Risks and test signals: provider acquisition error logic and compare-exchange cleanup deserve review because small mistakes can leak or fail to release provider handles; seed/add ignore caller entropy; CryptoAPI provider availability varies by platform. Tests should cover first-use initialization, concurrent initialization, cleanup/reinit, `CryptGenRandom` failure, and status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-w32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.c

Purpose: provides the OpenSSL-compatible global RAND API and method selection layer.

Important APIs/types/functions: global APIs include `RAND_seed`, `RAND_bytes`, `RAND_cleanup`, `RAND_add`, `RAND_pseudo_bytes`, `RAND_status`, `RAND_set_rand_method`, `RAND_get_rand_method`, `RAND_set_rand_engine`, `RAND_load_file`, `RAND_write_file`, and `RAND_file_name`. Static `selected_meth` and `selected_engine` hold the active source.

Control flow: `init_method` lazily selects Windows CryptoAPI on `_WIN32`, Unix device random on Apple, and Fortuna elsewhere. Public operations initialize if needed and dispatch to the method callbacks. Method changes clean up the previous method and release any selected engine. Engine selection uprefs the engine, fetches its RAND method, and replaces the global method. Random file loading reads chunks and seeds the method; writing emits 1024 bytes from `RAND_bytes`; filename selection uses `RANDFILE`, `HOME`, Unix random devices, or Windows local app data.

State and persistence: process-global selected method/engine persist until cleanup or replacement. `RAND_load_file` and `RAND_write_file` interact with caller-specified random state files; `RAND_file_name` only chooses a path.

Dependencies and integration points: depends on `rand.h`, `randi.h`, `engine.h`, `roken`, OS file APIs, and Windows shell APIs when built on Windows. Used by EVP random key generation and DES random key helpers.

Risks and test signals: no locking protects global method/engine changes, file load treats `size` as minimum but returns success after any bytes, state-file writes do not use atomic replacement, and default method varies by platform. Tests should cover default selection, zero-size requests, method replacement cleanup, engine failure, random file read/write permissions, filename selection under setuid restrictions, and concurrent callers if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.h

Purpose: declares the hcrypto RAND compatibility API and `RAND_METHOD` callback table.

Important APIs/types/functions: `struct RAND_METHOD` contains seed, bytes, cleanup, add, pseudorand, and status callbacks. The header declares global RAND APIs, EGD helpers, method factories for Fortuna/Unix/EGD/Windows, and symbol renames to `hc_*`.

Control flow: callers either use the global RAND functions or install a method/engine; method implementations supply the callback behavior.

State and persistence: no state is defined here, but the method table describes the stateful callback contract implemented by `rand.c` and `rand-*` files.

Dependencies and integration points: includes `hcrypto/engine.h` and is consumed by EVP, DES random key generation, provider code, and platform random implementations.

Risks and test signals: callback signatures use `int` sizes while public functions use `size_t`, so very large sizes require care in dispatching implementations. Compile coverage and RAND method smoke tests validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/randi.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/randi.h

Purpose: declares internal RAND method descriptors and helper entry points shared among random backend files.

Important APIs/types/functions: extern declarations expose `hc_rand_fortuna_method`, `hc_rand_unix_method`, `hc_rand_egd_method`, `hc_rand_timer_method`, and `hc_rand_w32crypto_method`. It also declares `RAND_timer_method` and `_hc_unix_device_fd`.

Control flow: backend implementations and `rand.c` reference these descriptors for default selection and fallback seeding.

State and persistence: no state is declared beyond extern method objects owned by implementation files.

Dependencies and integration points: included by all `rand-*` implementations. It ties Fortuna fallback logic to Unix, EGD, and timer sources.

Risks and test signals: mismatched extern names or conditional compilation can break method selection. Full build coverage across Windows, Apple, and Unix configurations is the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/randi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.c

Purpose: implements RC2 key expansion, block encrypt/decrypt, and CBC mode for legacy compatibility.

Important APIs/types/functions: `RC2_set_key` expands caller key bytes into 64 16-bit words with effective-bit control; `RC2_encryptc` and `RC2_decryptc` process one 8-byte block; `RC2_cbc_encrypt` handles CBC encryption/decryption and partial trailing blocks.

Control flow: key setup clamps key length to 128 bytes and effective bits to 1024, expands through the RC2 S-box, applies the effective-key-bit mask, and fills `RC2_KEY`. Encryption loads four little-endian words, runs 16 mixing rounds with mash steps after rounds 4 and 10, and writes little-endian output. Decryption reverses that sequence. CBC encryption XORs plaintext with IV, encrypts, and updates IV; trailing partial encryption fills missing bytes from IV. CBC decryption saves ciphertext as next IV, decrypts, XORs output with previous IV, and handles partial output.

State and persistence: `RC2_KEY` stores expanded key data. CBC calls mutate the caller-provided IV in place.

Dependencies and integration points: depends on `rc2.h` and is exposed through EVP RC2 provider descriptors.

Risks and test signals: RC2 is legacy and should be compatibility-only. `RC2_set_key` aborts on nonpositive key length, partial CBC behavior is nonstandard for many protocols, and IV mutation must be expected by callers. Tests should cover RFC 2268 vectors, 40/64/full effective bits, encrypt/decrypt inverse, CBC IV updates, and partial block handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.h

Purpose: declares RC2 constants, key structure, and encryption APIs.

Important APIs/types/functions: defines `RC2_ENCRYPT`, `RC2_DECRYPT`, `RC2_BLOCK_SIZE`, `RC2_BLOCK`, `RC2_KEY_LENGTH`, `RC2_KEY` with 64 expanded words, and prototypes for `RC2_set_key`, `RC2_encryptc`, `RC2_decryptc`, and `RC2_cbc_encrypt`.

Control flow: consumers expand a key, then call block or CBC operations with direction flag.

State and persistence: expanded key material persists in `RC2_KEY`; CBC IV state is caller-owned and mutated by implementation.

Dependencies and integration points: used by `rc2.c` and EVP RC2 providers.

Risks and test signals: declaration drift and deprecated algorithm use are the main risks. RC2 known-answer and CBC round-trip tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.c

Purpose: implements the ARCFOUR/RC4 stream cipher.

Important APIs/types/functions: `RC4_set_key` performs key scheduling over a 256-entry permutation; `RC4` generates keystream bytes and XORs input to output while updating key stream indices.

Control flow: key setup initializes the state array to identity, then walks 256 entries swapping based on key bytes modulo key length. Encryption/decryption repeatedly advances `x`, updates `y`, swaps state entries, selects a keystream byte from `state[state[x] + state[y]]`, and XORs it with input. The same operation decrypts.

State and persistence: `RC4_KEY` stores mutable `x`, `y`, and permutation state; every `RC4` call advances it, so the context is not reusable for independent messages without rekeying.

Dependencies and integration points: includes `rc4.h` and is exposed through EVP RC4 descriptors and validation tests.

Risks and test signals: RC4 is cryptographically obsolete, key length zero would divide by zero, and state reuse is dangerous. Tests should cover published ARCFOUR vectors, incremental calls matching one-shot output, in-place operation, and rejection or caller avoidance of zero-length keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.h

Purpose: declares RC4 key state and APIs.

Important APIs/types/functions: `RC4_KEY` contains stream indices `x`/`y` and 256-word state array. The header renames and declares `RC4_set_key` and `RC4`.

Control flow: callers initialize `RC4_KEY` once per stream and pass it through one or more `RC4` calls.

State and persistence: all stream state is in `RC4_KEY` and mutates for each byte processed.

Dependencies and integration points: consumed by `rc4.c` and EVP RC4 provider descriptors.

Risks and test signals: ABI layout and legacy algorithm exposure are risks. ARCFOUR vectors and segmented-stream tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.c

Purpose: provides the fast table-based Rijndael/AES block cipher core used by hcrypto AES wrappers.

Important APIs/types/functions: exported routines are `rijndaelKeySetupEnc`, `rijndaelKeySetupDec`, `rijndaelEncrypt`, and `rijndaelDecrypt`. The file contains large precomputed encryption/decryption T-tables, S-box derived tables, inverse tables, and round constants. `GETU32`/`PUTU32` map between byte arrays and 32-bit state words.

Control flow: encryption key setup reads 128/192/256-bit keys, expands round keys using S-box table lookups and `rcon`, and returns 10/12/14 rounds. Decryption setup first creates encryption keys, reverses round-key order, and applies inverse MixColumns to inner round keys. Encrypt/decrypt map a 16-byte block into four state words, add the initial round key, run table-driven full rounds either fully unrolled or looped depending on `FULL_UNROLL`, then perform a final S-box-only round and write 16 output bytes.

State and persistence: no global mutable state exists. Callers own round-key arrays sized for up to `4 * (RIJNDAEL_MAXNR + 1)` words. Tables are static const data.

Dependencies and integration points: includes `rijndael-alg-fst.h`, `krb5-types.h` under `KRB5`, and `config.h`. Higher AES APIs in the hcrypto provider wrap this core for CBC/CFB and Fortuna uses AES through the higher AES interface.

Risks and test signals: table-based AES can leak through cache timing on hostile local platforms, invalid `keyBits` returns zero and callers must handle it, and unaligned word access paths differ by compiler. Tests should cover NIST AES ECB known-answer vectors for 128/192/256-bit keys, decrypt inverse, key setup return values, endian/compiler variants, and provider CBC/CFB vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.h

Purpose: declares the fast Rijndael/AES core API and maximum key/block/round constants.

Important APIs/types/functions: defines `RIJNDAEL_MAXKC`, `RIJNDAEL_MAXKB`, and `RIJNDAEL_MAXNR`; renames `rijndaelKeySetupEnc`, `rijndaelKeySetupDec`, `rijndaelEncrypt`, and `rijndaelDecrypt`; declares key setup and single-block encrypt/decrypt prototypes.

Control flow: callers prepare an encryption or decryption round-key array, then pass it with the returned round count to block operations.

State and persistence: no state is declared except caller-owned round-key arrays.

Dependencies and integration points: used by `rijndael-alg-fst.c` and AES provider wrappers.

Risks and test signals: callers must allocate sufficient round-key space and respect valid AES key sizes. Compile coverage and AES known-answer vectors validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rijndael-alg-fst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rnd_keys.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rnd_keys.c

Purpose: supplies deprecated DES random key compatibility wrappers on top of the hcrypto RAND API.

Important APIs/types/functions: `DES_rand_data`, `DES_generate_random_block`, `DES_rand_data_key`, `DES_set_sequence_number`, `DES_set_random_generator_seed`, `DES_new_random_key`, `DES_init_random_number_generator`, and `DES_random_key`.

Control flow: simple wrappers call `RAND_bytes` or `RAND_seed`. `DES_new_random_key` loops until `RAND_bytes` succeeds, fixes odd parity with `DES_set_odd_parity`, and rejects weak DES keys with `DES_is_weak_key`. `DES_random_key` aborts on failure because it has no return code.

State and persistence: no local state is stored. RAND state is affected by seed calls, and generated DES key bytes are written to caller buffers.

Dependencies and integration points: depends on `des.h` and `rand.h`; preserves older DES APIs expected by Kerberos/OpenSSL-compatible code.

Risks and test signals: DES and these APIs are deprecated; `DES_random_key` abort behavior is harsh; RNG failure handling differs between wrappers. Tests should cover parity fixing, weak-key rejection with deterministic RNG hooks, RAND failure propagation, and deprecated symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rnd_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.c

Purpose: implements SHA-1.

Important APIs/types/functions: `SHA1_Init`, private `calc` for the 80-round compression function, endian `swap_uint32_t` for little-endian/Cray handling, `SHA1_Update`, and `SHA1_Final`.

Control flow: initialization sets SHA-1 initial constants and clears bit count. Update tracks bit length, buffers data into 64-byte blocks, endian-swaps into 32-bit words when needed, and compresses. Final writes SHA-1 padding and big-endian length, processes it, and serializes five 32-bit words big-endian.

State and persistence: `struct sha` stores split bit count, five counters, and a 64-byte save buffer. Finalization does not explicitly zero the context.

Dependencies and integration points: depends on `hash.h` and `sha.h`; exposed through EVP SHA/SHA1 descriptors, HMAC-SHA1, PBKDF2-HMAC-SHA1, and validation.

Risks and test signals: SHA-1 is collision-broken for signatures but still appears in compatibility KDF/HMAC contexts. Alignment/endian paths require testing. Use FIPS/RFC SHA-1 vectors, segmented updates, large inputs, and HMAC/PBKDF2 integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.h

Purpose: declares SHA-1, SHA-256, SHA-384, and SHA-512 contexts, digest lengths, and streaming APIs.

Important APIs/types/functions: defines `SHA_DIGEST_LENGTH`, `SHA256_DIGEST_LENGTH`, `SHA384_DIGEST_LENGTH`, `SHA512_DIGEST_LENGTH`; declares `struct sha`, `struct hc_sha256state`, and `struct hc_sha512state`; typedefs `SHA_CTX`, `SHA256_CTX`, `SHA512_CTX`, and `SHA384_CTX`; and prototypes init/update/final functions with symbol renaming.

Control flow: consumers use init/update/final streaming calls; SHA384 reuses the SHA512 state shape.

State and persistence: contexts store bit counts, compression counters, and partial block buffers sized to the algorithm block size.

Dependencies and integration points: shared by SHA implementation files, Fortuna, EVP provider descriptors, HMAC, and PBKDF2.

Risks and test signals: layout compatibility and endian behavior are key. Known-answer vectors for all SHA variants plus segmented-update tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha256.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha256.c

Purpose: implements SHA-256.

Important APIs/types/functions: `SHA256_Init`, private `calc` with SHA-256 message schedule and 64 constants, endian `swap_uint32_t`, `SHA256_Update`, and `SHA256_Final`.

Control flow: initialization sets the eight SHA-256 initial words. Update tracks bit length, buffers and transforms 64-byte blocks, and swaps input words on little-endian/Cray builds. Compression expands 16 input words to 64, then runs 64 rounds using Ch, Maj, and sigma functions. Final adds SHA-2 padding and big-endian length and serializes eight big-endian words.

State and persistence: `SHA256_CTX` stores split bit count, eight counters, and a 64-byte save buffer. Finalization does not explicitly zero the context.

Dependencies and integration points: depends on `hash.h` and `sha.h`; used by EVP SHA256 descriptors and Fortuna entropy pools.

Risks and test signals: alignment/endian assumptions and length overflow accounting are the primary implementation risks. Test with NIST SHA-256 vectors, segmented inputs, 55/56/64-byte padding boundaries, large inputs, and Fortuna integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha512.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha512.c

Purpose: implements SHA-512 and SHA-384.

Important APIs/types/functions: `SHA512_Init`, private `calc` with 80 SHA-512 constants, endian `swap_uint64_t`, `SHA512_Update`, `SHA512_Final`, `SHA384_Init`, `SHA384_Update`, and `SHA384_Final`.

Control flow: SHA512 initialization sets eight 64-bit initial words. Update tracks 128-bit bit length in two 64-bit words, buffers 128-byte blocks, endian-swaps as needed, and compresses. Final applies SHA-512 padding with a 128-bit big-endian length field and serializes eight big-endian words. SHA384 uses different initial constants, delegates update/final compression to SHA512, then truncates the final 64-byte digest to 48 bytes.

State and persistence: `SHA512_CTX`/`SHA384_CTX` store two length words, eight counters, and a 128-byte save buffer. Finalization does not scrub context; SHA384 final uses a stack 64-byte temporary that is not explicitly scrubbed.

Dependencies and integration points: depends on `hash.h` and `sha.h`; exposed through EVP SHA384/SHA512 descriptors and validation.

Risks and test signals: 64-bit endian/alignment behavior and bit-length overflow are the main risks. Test with NIST SHA-384/SHA-512 vectors, segmented inputs, exact padding boundaries, and big-endian/little-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/test_cipher.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/test_cipher.c

Purpose: standalone cipher known-answer test program for hcrypto provider descriptors, with optional Apple CommonCrypto provider comparisons.

Important APIs/types/functions: `struct tests` holds cipher name, key, key size, IV, data size, input, expected output, and optional expected IV. Static vectors cover AES-256-CBC, AES-128-CFB8, RC2-40-CBC, 3DES-CBC, Camellia-128-CBC, and RC4. `test_cipher` initializes encrypt/decrypt EVP contexts, sets key length, encrypts, compares hex-encoded failures, decrypts, and compares plaintext. `main` parses `--help`/`--version` and runs provider tests.

Control flow: each vector is tested by creating separate encrypt/decrypt contexts, initializing with descriptor then key/IV, invoking single-shot `EVP_Cipher`, checking ciphertext, decrypting in place, and cleaning contexts. Apple-only tests compile under `__APPLE__`.

State and persistence: no persistent state beyond static test vectors. Failures terminate with `errx`; success returns accumulated zero count.

Dependencies and integration points: depends on `evp.h`, `evp-hcrypto.h`, optional `evp-cc.h`, `getarg`, `hex`, `err`, and `roken`. It exercises provider descriptors rather than low-level primitives directly.

Risks and test signals: coverage is useful but narrow: most tests are one-block or stream single-shot, IV output checks are TODO, and padding/update APIs are not covered. Test improvements should add segmented `EVP_CipherUpdate/Final`, IV mutation expectations, AES-128/192 CBC, SHA/HMAC vectors, and failure-path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/test_cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.c

Purpose: implements a small OpenSSL-compatible password prompt helper.

Important APIs/types/functions: private `intr` signal handler, platform-specific `read_string`, and exported `UI_UTIL_read_pw_string(buf, length, prompt, verify)`.

Control flow: Unix `read_string` installs interrupt handlers for most signals, opens `/dev/tty` or falls back to stdin, prints prompt to stderr, disables terminal echo when requested, reads until newline/EOF/interrupt/overflow, restores echo and signal handlers, and returns `0`, `-1` overflow, `-2` interrupt, or `-3` input error. Windows `_getch/_getche` path uses console I/O and SIGINT handling. `UI_UTIL_read_pw_string` reads the password without echo and optionally reads a verification prompt and compares strings.

State and persistence: file-static `intr_flag` tracks signal interruption. Password buffers are caller-owned; verify buffer is heap allocated and freed but not scrubbed.

Dependencies and integration points: depends on `ui.h`, `roken`, terminal APIs, signals, and optional `conio.h`. Used by code expecting OpenSSL `UI_UTIL_read_pw_string` behavior.

Risks and test signals: signal handling across `NSIG` can be invasive, terminal state restoration on unusual errors is critical, overflow handling leaves truncated data, and verification buffer is not zeroed before free. Tests should cover echo restoration, `/dev/tty` fallback, overflow, interrupt, verify mismatch, EOF, and Windows console behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.h -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.h

Purpose: declares the password prompt utility compatibility API.

Important APIs/types/functions: renames `UI_UTIL_read_pw_string` to `hc_UI_UTIL_read_pw_string` and declares `int UI_UTIL_read_pw_string(char *, int, const char *, int)`.

Control flow: callers pass a destination buffer, maximum length, prompt, and verify flag; behavior lives in `ui.c`.

State and persistence: no state is defined in the header.

Dependencies and integration points: included by `ui.c` and any OpenSSL-compatible password prompt callers in Heimdal/OpenAFS.

Risks and test signals: signature compatibility is the main concern. Compile coverage and prompt behavior tests validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/ui.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/validate.c -->
# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/validate.c

Purpose: performs built-in hcrypto self-validation before public EVP factory use.

Important APIs/types/functions: static `hc_tests` contains known-answer vectors for AES-256-CBC, 3DES-CBC, and RC4, with some AES-CFB8 and Camellia vectors disabled. `test_cipher` runs one vector through EVP encrypt/decrypt. `check_hmac` validates HMAC-SHA1 over four zero bytes with key `hello-world`. `hcrypto_validate` runs tests once.

Control flow: public EVP factories call `hcrypto_validate`. The function uses a static `validated` flag, increments it before running tests to avoid recursion, then tests each configured cipher vector and HMAC. Failures call `errx`, terminating the process. The comment states races are acceptable and duplicate runs are tolerated.

State and persistence: only the static `validated` flag persists. Test vectors are immutable static data. No output artifacts are written.

Dependencies and integration points: depends on `evp.h`, `hmac.h`, `roken`, and `err.h`. It is tightly coupled to EVP provider descriptors and guards broad hcrypto use inside the process.

Risks and test signals: self-validation can terminate production processes on mismatch, is not thread-synchronized, covers only a subset of algorithms, and sets `validated` before tests complete. Useful signals are successful process startup using EVP factories, deliberate failure injection proving abort behavior, expanded known-answer vectors, and multi-thread first-use tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/hcrypto/validate.c -->
