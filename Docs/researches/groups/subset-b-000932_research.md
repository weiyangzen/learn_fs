# subset-b-000932 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_xor.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/async_xor.c

## Purpose

`async_xor.c` implements the async_tx XOR and XOR-validation API used by RAID/parity code. It tries to offload page XOR work to a DMA engine and falls back to synchronous CPU XOR when no suitable channel, descriptor, alignment, or conversion storage is available.

## Important APIs, Types, and Flow

The exported APIs are `async_xor_offs()`, `async_xor()`, and `async_xor_val_offs()`. `async_xor_offs()` finds a `DMA_XOR` channel, allocates `dmaengine_unmap_data`, maps source pages as `DMA_TO_DEVICE`, maps the destination as bidirectional, and calls `do_async_xor()`. `do_async_xor()` splits operations by `device->max_xor`, chains partial descriptors through `submit->depend_tx`, clears callbacks for intermediate descriptors, and uses `DMA_PREP_INTERRUPT`/`DMA_PREP_FENCE` from submit flags. If descriptor allocation stalls, it quiesces dependencies and spins while issuing pending DMA.

The synchronous path uses `do_sync_xor_offs()`, converts source pages to virtual addresses with optional per-source offsets, optionally zeroes the destination for `ASYNC_TX_XOR_ZERO_DST`, then calls `xor_gen()`. `async_xor_val_offs()` similarly prefers `DMA_XOR_VAL`, otherwise performs an XOR into the destination and checks whether the destination page range is zero.

## State, Dependencies, and Integration

State is entirely per-call: mapped DMA addresses, submit control, dependency descriptors, and the caller-provided result flag. It depends on the DMA engine API, async_tx helpers, Linux pages, and RAID XOR helpers. The integration contract is subtle: in the synchronous path the destination is an implied XOR source unless `ASYNC_TX_XOR_DROP_DST` is set, while DMA only uses explicitly supplied source addresses.

## Risks and Test Signals

Risks center on source-list mutation, destination-as-source semantics, DMA alignment, descriptor starvation, and correct restoration of submit flags. Tests should cover DMA and synchronous fallback paths, differing source offsets, dropped destination source, zero-destination parity generation, multi-pass `max_xor` splitting, and validation result bits for zero and nonzero sums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/raid6test.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/raid6test.c

## Purpose

`raid6test.c` is a kernel self-test module for asynchronous RAID-6 recovery. It allocates pages, generates random data and syndromes, simulates all two-disk failure combinations for selected disk counts, invokes async recovery helpers, and validates recovered data and syndrome consistency.

## Important APIs, Types, and Flow

Global arrays `data`, `dataptrs`, `dataoffs`, and `addr_conv` hold test pages and async address conversion scratch. `raid6_dual_recov()` selects the recovery path by failed disk class: P+Q rebuilds syndrome, data+Q reconstructs data with `async_xor()` then rebuilds syndrome, data+P calls `async_raid6_datap_recov()`, and data+data calls `async_raid6_2data_recov()`. It then chains `async_syndrome_val()` with a completion callback and checks `sum_check_flags`.

`test()` creates baseline random data, overwrites P and Q pages, calls `async_gen_syndrome()`, then loops over failure pairs through `test_disks()`. `raid6_test()` allocates `NDISKS + 3` pages and runs special cases for 4, 5, 11, 12, 24, and 64 disks before freeing pages.

## State, Dependencies, and Integration

State is module-global test memory and temporary replacement pages `recovi`, `recovj`, and `spare`. The file depends on async_tx RAID6 APIs, random bytes, page allocation, completions, and late init ordering so built-in DMA providers can register first.

## Risks and Test Signals

The test itself is a signal: timeout logs point to async completion/pending issues, validation failures point to syndrome or recovery bugs, and `memcmp()` failures identify wrong recovered disks. Risks include PAGE_SIZE-only coverage, fixed maximum disk count, reliance on low-level pages being virtually addressable, and returning `0` even when test failures are logged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/raid6test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authenc.c -->
# sources/distributed-fs/ceph-client/crypto/authenc.c

## Purpose

`authenc.c` implements the `authenc(auth,enc)` AEAD template used by IPsec-style encrypt-then-authenticate constructions. It composes an ahash authentication algorithm with a skcipher encryption algorithm and exposes them as one AEAD transform.

## Important APIs, Types, and Flow

`crypto_authenc_extractkeys()` parses the `rtattr`-encoded combined key, validates the parameter payload, extracts the encryption-key length, and splits authentication and encryption keys. The template context stores ahash and skcipher spawns plus `reqoff`; each tfm stores allocated child transforms in `crypto_authenc_ctx`.

Encryption copies associated data when source and destination differ, encrypts the payload using the child skcipher over scatterlists advanced past `assoclen`, then computes a hash over `assoclen + cryptlen` bytes in the destination and appends the truncated auth tag. Decryption hashes `assoclen + cryptlen - authsize`, copies the supplied tag from the input, verifies with `crypto_memneq()`, and only then decrypts the ciphertext. Async callbacks preserve original request completion and suppress intermediate `-EINPROGRESS`/`-EBUSY` notifications where needed.

## State, Dependencies, and Integration

Persistent state is the child transform pair and derived request-size layout. Per-request scratch contains two small scatterlist arrays and a tail region containing two digest buffers plus child requests. It integrates with the crypto template system, scatterwalk helpers, `crypto/internal/aead.h`, ahash, skcipher, and the exported key-splitting helper used by `authencesn.c`.

## Risks and Test Signals

Risks include malformed key attributes, insufficient `reqoff` sizing, scatterlist forwarding mistakes, in-place versus out-of-place associated-data handling, and authentication-before-decryption ordering. Test signals are AEAD known-answer tests for valid tags, `-EBADMSG` on tag mismatch, async completion behavior, and key parsing failures for bad rtattrs or inconsistent lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authenc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authencesn.c -->
# sources/distributed-fs/ceph-client/crypto/authencesn.c

## Purpose

`authencesn.c` implements `authencesn(auth,enc)`, an IPsec AEAD template for extended sequence numbers. It is derived from `authenc` but rearranges high-order ESN bits so the authentication input matches IPsec ESN layout while the packet-associated data remains in normal order.

## Important APIs, Types, and Flow

The template context stores ahash and skcipher spawns; the tfm context stores `reqoff` plus allocated child transforms. `crypto_authenc_esn_setkey()` reuses `crypto_authenc_extractkeys()`, sets both child keys, and clears the temporary key structure. `crypto_authenc_esn_setauthsize()` rejects nonzero authentication sizes below four bytes.

Encryption requires at least eight bytes of associated data. It encrypts payload scatterlists after `assoclen`, then `crypto_authenc_esn_genicv()` moves the high-order ESN bits from the start of associated data to the end of authenticated text, hashes the adjusted stream, restores the bytes, and writes the tag after ciphertext. Decryption copies the supplied tag, performs the same ESN rearrangement for hashing, verifies with `crypto_memneq()`, restores or copies associated data, then decrypts payload.

## State, Dependencies, and Integration

State is per-tfm child ahash/skcipher handles plus per-request scratch scatterlists and digest buffers. The implementation depends on scatterwalk map/copy, `memcpy_sglist()`, ahash and skcipher internals, and the `authenc` key format. It integrates with IPsec users that need ESN-aware AEAD names and request semantics.

## Risks and Test Signals

The main risks are ESN byte shuffling offsets, in-place versus out-of-place copy differences, zero-authsize bypass behavior, `assoclen < 8` rejection, and tag placement after adjusted ciphertext length. Tests should cover ESN AAD lengths, 8/12/16-byte tags, tag mismatch, no-auth mode, asynchronous hash/encrypt completion, and source/destination aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/authencesn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blake2b.c -->
# sources/distributed-fs/ceph-client/crypto/blake2b.c

## Purpose

`blake2b.c` registers keyed and unkeyed BLAKE2b shash algorithms for 160-, 256-, 384-, and 512-bit digests. It is a Crypto API wrapper around the library BLAKE2b implementation rather than a standalone compression implementation.

## Important APIs, Types, and Flow

`struct blake2b_tfm_ctx` stores an optional key and key length per transform. `crypto_blake2b_setkey()` validates the maximum key length and copies the key into the transform context. `crypto_blake2b_init()` initializes the per-request `struct blake2b_ctx` with the requested digest size and optional key. `update`, `final`, and one-shot `digest` delegate to `blake2b_update()`, `blake2b_final()`, and `blake2b()`.

The `BLAKE2B_ALG` macro defines four `shash_alg` entries with `CRYPTO_ALG_OPTIONAL_KEY`, driver names ending in `-lib`, priority 300, block size `BLAKE2B_BLOCK_SIZE`, and descriptor size `sizeof(struct blake2b_ctx)`.

## State, Dependencies, and Integration

Persistent state is only the optional key in the tfm context. Streaming hash state lives in the shash descriptor. The file depends on `<crypto/blake2b.h>` and Crypto API shash registration. Consumers select names such as `blake2b-256` or `blake2b-512`.

## Risks and Test Signals

Risks are limited but security-sensitive: key length enforcement, correct digest-size binding per algorithm name, and zeroization expectations for keyed transforms. Test signals include known-answer vectors for all digest sizes, keyed and unkeyed operation, streaming versus one-shot equivalence, and rejection of oversized keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blake2b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_common.c -->
# sources/distributed-fs/ceph-client/crypto/blowfish_common.c

## Purpose

`blowfish_common.c` provides Blowfish constants and key schedule code shared by C and assembly implementations. It exports `blowfish_setkey()` so algorithm frontends can populate `struct bf_ctx` with derived P-box and S-box material.

## Important APIs, Types, and Flow

The file defines the initial Blowfish P-box and S-box tables, an endian-neutral internal `encrypt_block()` used only during subkey generation, and `blowfish_setkey()`. The key schedule copies initial tables into the context, XORs key words through the P-box cycling across key bytes, repeatedly encrypts a zero block to replace P-box entries, then continues encrypting to fill all S-box entries.

`encrypt_block()` uses the Blowfish F function and 16 unrolled Feistel rounds over two 32-bit words, deliberately ignoring external byte order because the key schedule operates on internal words.

## State, Dependencies, and Integration

State is the caller-provided `bf_ctx` inside a Crypto API transform. The file exports only key setup; block encryption/decryption frontends live in `blowfish_generic.c` or architecture-specific modules. It depends on `crypto/blowfish.h`, module exports, and kernel integer types.

## Risks and Test Signals

Risks include accepting invalid key lengths if callers bypass algorithm min/max checks, byte-order mismatches between common key schedule and frontend block functions, and sensitive key material remaining in transform contexts until freed. Test signals are Blowfish known-answer vectors across minimum, maximum, and odd key lengths, plus cross-checks between generic and assembly frontends sharing this schedule.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_generic.c -->
# sources/distributed-fs/ceph-client/crypto/blowfish_generic.c

## Purpose

`blowfish_generic.c` registers the generic single-block Blowfish cipher implementation with the Crypto API. It supplies block encrypt/decrypt functions and reuses `blowfish_setkey()` from the common module.

## Important APIs, Types, and Flow

`bf_encrypt()` and `bf_decrypt()` read a 64-bit block as big-endian halves, run the unrolled Blowfish Feistel rounds using the P-box and S-box data stored in `struct bf_ctx`, then write big-endian output. Encryption applies rounds 0 through 15 and post-whitening P[16]/P[17]. Decryption applies the P-array in reverse order and finishes with P[1]/P[0].

The registered `crypto_alg` is named `blowfish` with driver `blowfish-generic`, type `CRYPTO_ALG_TYPE_CIPHER`, block size `BF_BLOCK_SIZE`, context size `sizeof(struct bf_ctx)`, and key bounds from `BF_MIN_KEY_SIZE` to `BF_MAX_KEY_SIZE`.

## State, Dependencies, and Integration

Persistent state is the Blowfish expanded key in the transform context. The file depends on unaligned big-endian accessors, `crypto/algapi.h`, and `crypto/blowfish.h`. It integrates with modes/templates such as CBC, ECB, CMAC, or other cipher users that request `blowfish` or `blowfish-generic`.

## Risks and Test Signals

Risks are byte-order correctness, round-order correctness, and module dependency on the exported common key setup. Tests should use known-answer vectors for encryption/decryption, mode-level round trips, invalid key lengths through Crypto API setkey, and generic-versus-accelerated equivalence where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blowfish_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/bpf_crypto_skcipher.c -->
# sources/distributed-fs/ceph-client/crypto/bpf_crypto_skcipher.c

## Purpose

`bpf_crypto_skcipher.c` exposes linear skcipher operations to the BPF crypto framework. It is an adapter from `struct bpf_crypto_type` callbacks to the kernel `crypto_lskcipher` API.

## Important APIs, Types, and Flow

The callback table `bpf_crypto_lskcipher_type` provides allocation, free, algorithm availability, setkey, encrypt, decrypt, IV size, state size, and flag access. Allocation calls `crypto_alloc_lskcipher(algo, 0, 0)`, and availability checks `crypto_has_skcipher()` constrained to `CRYPTO_ALG_TYPE_LSKCIPHER`. Encrypt and decrypt forward directly to `crypto_lskcipher_encrypt()` and `crypto_lskcipher_decrypt()` with source, destination, length, and state/IV pointer.

Module init registers the type as `"skcipher"` with `bpf_crypto_register_type()`, and exit unregisters it, warning if unregister fails.

## State, Dependencies, and Integration

The file has no independent cryptographic state. Transform lifetime is owned by BPF crypto callers through the callback interface. Dependencies are `linux/bpf_crypto.h`, `crypto/skcipher.h`, and the lskcipher subsystem. Integration points are BPF programs/helpers that request symmetric cipher support.

## Risks and Test Signals

Risks are type mismatch between skcipher and lskcipher names, lifetime handling across BPF object references, and surfacing child transform flags correctly. Test signals include BPF crypto selftests for allocation failure, unknown algorithms, key errors, IV/state size reporting, encrypt/decrypt round trips, and module unregister while no live references remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/bpf_crypto_skcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/camellia_generic.c -->
# sources/distributed-fs/ceph-client/crypto/camellia_generic.c

## Purpose

`camellia_generic.c` implements and registers the generic Camellia block cipher. It contains lookup tables, key schedules for 128/192/256-bit keys, block encryption/decryption routines, and a `crypto_alg` named `camellia`.

## Important APIs, Types, and Flow

`struct camellia_ctx` stores the key length and expanded key table. `camellia_set_key()` accepts only 16-, 24-, or 32-byte keys and dispatches to `camellia_setup128()`, `camellia_setup192()`, or `camellia_setup256()`. The 192-bit setup pads to 256 bits by appending the bitwise complement of the last 64 key bits.

The implementation uses precomputed SP tables, `CAMELLIA_F`, `CAMELLIA_FLS`, rotation macros, and `camellia_setup_tail()` to derive subkeys. `camellia_encrypt()` and `camellia_decrypt()` read 16-byte blocks as big-endian words, select 24 rounds for 128-bit keys or 32 rounds for 192/256-bit keys, call `camellia_do_encrypt()` or `camellia_do_decrypt()`, and write the swapped output halves.

## State, Dependencies, and Integration

Persistent state is the expanded key table in the transform context. The file depends on Crypto API cipher registration, unaligned big-endian helpers, and bit rotations. It integrates with block modes and template algorithms that request `camellia` or `camellia-generic`.

## Risks and Test Signals

Risks include key-schedule table indexing, half swapping, endian handling, and 192-bit complement padding. Tests should include official Camellia vectors for all key sizes, decrypt(encrypt()) round trips, alignment-sensitive inputs, mode-level tests, and equivalence with architecture-specific Camellia implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/camellia_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast5_generic.c -->
# sources/distributed-fs/ceph-client/crypto/cast5_generic.c

## Purpose

`cast5_generic.c` implements CAST-128/CAST5 per RFC 2144 and registers the generic `cast5` cipher. It includes CAST5-specific S-boxes, key schedule, and block encryption/decryption functions.

## Important APIs, Types, and Flow

The file uses shared `cast_s1` through `cast_s4` from `cast_common.c` plus local S-boxes `s5`, `s6`, `s7`, and `sb8`. `cast5_setkey()` pads the key to 128 bits, records reduced-round mode for keys up to 80 bits, runs `key_schedule()` twice to generate masking subkeys `Km` and rotation subkeys `Kr`, and stores them in `struct cast5_ctx`.

`__cast5_encrypt()` and `__cast5_decrypt()` are exported helpers. They parse 64-bit blocks as big-endian halves and apply the CAST F1/F2/F3 functions in the specified round order. Reduced-round mode skips the final four rounds. Wrapper functions adapt those helpers to the `crypto_alg` block cipher interface.

## State, Dependencies, and Integration

State is the expanded `cast5_ctx`, including `Km`, `Kr`, and reduced-round flag. Dependencies are unaligned accessors, `crypto/cast5.h`, and the exported shared CAST S-boxes. It integrates with Crypto API cipher consumers by registering `cast5` and `cast5-generic`.

## Risks and Test Signals

Risks include reduced-round threshold errors, key padding, byte extraction in the key schedule, and dependence on `cast_common` exports. Tests should include RFC 2144 vectors, 40- to 128-bit keys, reduced-round coverage, decryption inverse checks, and comparisons with accelerated CAST5 implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast5_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast6_generic.c -->
# sources/distributed-fs/ceph-client/crypto/cast6_generic.c

## Purpose

`cast6_generic.c` implements CAST-256/CAST6 per RFC 2612 and registers the generic `cast6` cipher. It builds on the shared CAST S-boxes and provides exported helpers for other implementations.

## Important APIs, Types, and Flow

`__cast6_setkey()` requires key lengths divisible by four, pads to 32 bytes, reads eight big-endian key words, and runs 12 key-schedule iterations. Each iteration applies two `W()` octaves using fixed `Tm` and `Tr` constants, then extracts rotation and masking subkeys into `struct cast6_ctx`. `cast6_setkey()` adapts this to the Crypto API.

`__cast6_encrypt()` reads a 128-bit block, applies six forward `Q()` quad rounds followed by six reverse `QBAR()` quad rounds, and writes big-endian output. `__cast6_decrypt()` applies the inverse order. The registered `crypto_alg` exposes key bounds from `CAST6_MIN_KEY_SIZE` to `CAST6_MAX_KEY_SIZE`.

## State, Dependencies, and Integration

State is the expanded CAST6 context. Dependencies include `crypto/cast6.h`, unaligned accessors, and `cast_common.c` exported tables. The module registers names `cast6` and `cast6-generic` for block-mode consumers.

## Risks and Test Signals

Risks include accepting only 4-byte-multiple keys, subkey extraction order, Q/QBAR inversion, and shared table linkage. Test signals are RFC vectors, all valid key lengths, invalid non-multiple key rejection, decrypt/encrypt round trips, and generic-versus-accelerated equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast6_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast_common.c -->
# sources/distributed-fs/ceph-client/crypto/cast_common.c

## Purpose

`cast_common.c` provides the shared CAST S-box tables used by CAST-128 and CAST-256 implementations. It contains no transform registration and no runtime algorithm logic beyond exporting constants.

## Important APIs, Types, and Flow

The file defines `__visible const u32 cast_s1[256]`, `cast_s2[256]`, `cast_s3[256]`, and `cast_s4[256]`, each exported with `EXPORT_SYMBOL_GPL()`. CAST5 and CAST6 generic code alias these as `s1` through `s4` in their F-function macros.

There is no control flow other than module load/unload metadata. The value of the file is code and data sharing: large constant tables live in one module rather than being duplicated by each CAST implementation.

## State, Dependencies, and Integration

State is immutable static data. Dependencies are limited to `linux/module.h` and `crypto/cast_common.h`. Integration points are any GPL module that imports the exported S-box symbols, chiefly `cast5_generic.c`, `cast6_generic.c`, and architecture-specific CAST implementations.

## Risks and Test Signals

Risks are table corruption, symbol visibility, and version/linkage issues. Test signals are indirect: CAST5 and CAST6 known-answer tests will fail if a table value or export is wrong. Build and module-load tests should also confirm dependent CAST modules resolve the exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cbc.c -->
# sources/distributed-fs/ceph-client/crypto/cbc.c

## Purpose

`cbc.c` implements the CBC block cipher mode template for the linear skcipher API. It wraps a block cipher-like lskcipher child and provides encrypt/decrypt operations with IV chaining.

## Important APIs, Types, and Flow

Encryption has separate segment and in-place paths. Out-of-place encryption XORs each plaintext block into the IV buffer, encrypts the IV into destination, then updates IV from ciphertext. In-place encryption XORs each source block with the current IV, encrypts in place, and updates the original IV from the final ciphertext block.

Decryption also has segment and in-place paths. Out-of-place decryption decrypts each block then XORs with the previous IV/ciphertext, finally storing the last input ciphertext block as the new IV. In-place decryption walks backward from the last complete block so previous ciphertext is still available for XOR, saving the last ciphertext as the updated IV.

`crypto_cbc_create()` allocates a simple lskcipher instance, requires power-of-two block size and zero child state size, installs CBC encrypt/decrypt callbacks, and registers the template instance.

## State, Dependencies, and Integration

State is the mutable IV passed by callers; the transform context stores the child lskcipher pointer allocated by template helpers. Dependencies are internal skcipher APIs, `crypto_xor()`, and lskcipher template allocation. It integrates as the `cbc(...)` template.

## Risks and Test Signals

Risks include partial-block handling, `FINAL` returning `-EINVAL` on remainders, in-place backward decrypt correctness, IV update semantics, and rejection of stateful children. Test signals are CBC known-answer vectors, multi-call partial updates, in-place and out-of-place equivalence, invalid final lengths, and IV chaining after calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ccm.c -->
# sources/distributed-fs/ceph-client/crypto/ccm.c

## Purpose

`ccm.c` implements Counter with CBC-MAC AEAD templates: `ccm`, `ccm_base`, the IPsec `rfc4309` wrapper, and the `cbcmac` shash template used by CCM. It composes CTR-mode encryption with CBC-MAC authentication.

## Important APIs, Types, and Flow

`crypto_ccm_setkey()` sets the same key on child CTR skcipher and CBC-MAC ahash. `crypto_ccm_setauthsize()` accepts even tag sizes from 4 through 16. `crypto_ccm_auth()` formats the B0 block and associated-data length encoding, hashes AAD and plaintext with block padding, and returns a 16-byte MAC. `crypto_ccm_init_crypt()` validates `L'` in `iv[0]`, zeros the counter field, and constructs scatterlists that prepend the tag block before data for CTR processing.

Encryption computes CBC-MAC over plaintext, CTR-encrypts tag plus payload, then copies the requested tag length to the end of the destination. Decryption saves the incoming tag, CTR-decrypts tag plus ciphertext, recomputes CBC-MAC over plaintext, and compares tags. `crypto_ccm_create_common()` validates that the MAC is `cbcmac(...)`, the cipher is `ctr(...)`, both use the same underlying cipher, and CTR has 16-byte IV/block conventions.

`rfc4309` stores a three-byte nonce suffix in the key, builds a CCM child IV from nonce plus eight-byte packet IV, and moves the leading AAD bytes into child AAD. The `cbcmac` template wraps a single-block cipher as a block-only shash.

## State, Dependencies, and Integration

Tfm state stores child ahash/skcipher or child AEAD plus RFC4309 nonce. Request state stores formatted blocks, auth tag buffers, scatterlists, and embedded child requests. Dependencies include scatterwalk, internal AEAD/hash/skcipher/cipher APIs, and Crypto API templates.

## Risks and Test Signals

Risks include CCM length encoding overflow, AAD formatting, partial tag handling, IV mutation, RFC4309 AAD length restrictions, and async callback correctness. Test signals are NIST/RFC CCM vectors, RFC4309 vectors, invalid auth sizes, invalid IV `L'`, tag mismatch returning `-EBADMSG`, in-place/out-of-place operation, and template creation rejection for mismatched children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ccm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha.c -->
# sources/distributed-fs/ceph-client/crypto/chacha.c

## Purpose

`chacha.c` registers Crypto API skcipher wrappers for ChaCha20, XChaCha20, and XChaCha12 using the shared ChaCha library implementation.

## Important APIs, Types, and Flow

`struct chacha_ctx` stores eight 32-bit key words and the number of rounds. `chacha_setkey()` requires a 32-byte key, loads little-endian words, and records 20 or 12 rounds. `chacha_stream_xor()` initializes a `chacha_state` from the key and IV, walks the skcipher request with `skcipher_walk_virt()`, rounds non-final chunks down to `CHACHA_BLOCK_SIZE`, and calls `chacha_crypt()` to XOR keystream with input.

`crypto_chacha_crypt()` uses the request IV directly. `crypto_xchacha_crypt()` derives a subkey with HChaCha over the first 128 nonce bits, then builds a standard 16-byte ChaCha IV from stream position and remaining nonce bits before calling the shared stream XOR routine.

## State, Dependencies, and Integration

State is per-transform key words and round count. Dependencies are `crypto/chacha.h`, internal skcipher APIs, unaligned little-endian helpers, and skcipher walking. Registered algorithms are `chacha20`, `xchacha20`, and `xchacha12` with driver names ending in `-lib`.

## Risks and Test Signals

Risks include IV layout, XChaCha subkey derivation, block-boundary walking, and round-count selection. Test signals are ChaCha20/XChaCha known-answer vectors, split scatterlist requests, unaligned data, zero-length input, and encrypt/decrypt identity because stream cipher encryption and decryption are identical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha20poly1305.c -->
# sources/distributed-fs/ceph-client/crypto/chacha20poly1305.c

## Purpose

`chacha20poly1305.c` implements RFC7539 ChaCha20-Poly1305 AEAD templates, including `rfc7539` with 12-byte IVs and `rfc7539esp` with 8-byte packet IVs plus a salt stored in the key.

## Important APIs, Types, and Flow

The template instance stores a skcipher spawn and salt length. Each tfm stores the child ChaCha skcipher and flexible salt. `chachapoly_setkey()` requires `CHACHA_KEY_SIZE + saltlen`, stores the salt suffix, and sets the child ChaCha key. `chacha_iv()` builds the 16-byte ChaCha IV as little-endian initial block counter, salt, and request IV bytes.

Encryption sets `rctx->cryptlen` to plaintext length, encrypts payload with counter 1, derives the Poly1305 key by ChaCha block counter 0, hashes AAD and ciphertext with Poly1305 padding plus 64-bit length trailer, and writes the tag to the destination scatterwalk. Decryption derives the Poly1305 key first, hashes AAD and ciphertext, verifies the tag from the input, then decrypts with counter 1. Async continuations clear MAY_SLEEP after callback entry and complete only terminal statuses.

## State, Dependencies, and Integration

State is per-tfm child skcipher and optional ESP salt; per-request state stores scratch scatterlists, Poly1305 one-time key, calculated tag, lengths, flags, and embedded skcipher request. Dependencies include internal AEAD/skcipher/hash headers, `crypto/chacha.h`, `crypto/poly1305.h`, scatterwalk, and ZERO_PAGE padding.

## Risks and Test Signals

Risks include salt/key length mismatch, ESP AAD adjustment, tag verification ordering, scatterwalk tag placement, zero-length plaintext, and async continuation status. Test signals are RFC7539 and ESP vectors, invalid authsize, bad tag `-EBADMSG`, associated-data-only messages, in-place/out-of-place operation, and child ChaCha algorithm validation during template creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/chacha20poly1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cipher.c -->
# sources/distributed-fs/ceph-client/crypto/cipher.c

## Purpose

`cipher.c` implements internal single-block cipher helper APIs: setkey with alignment handling, one-block encrypt/decrypt wrappers, and cloning of simple cipher transforms.

## Important APIs, Types, and Flow

`crypto_cipher_setkey()` validates key length against the algorithm's `cia_min_keysize` and `cia_max_keysize`. If the key pointer violates the transform alignmask, `setkey_unaligned()` allocates an aligned temporary buffer with `GFP_ATOMIC`, copies the key, invokes the algorithm setkey, and frees the temporary with `kfree_sensitive()`.

`cipher_crypt_one()` selects the algorithm encrypt or decrypt function. If source or destination is unaligned, it copies one block to an aligned stack buffer, runs the primitive in place, then copies to destination. Otherwise it calls the primitive directly. `crypto_cipher_encrypt_one()` and `crypto_cipher_decrypt_one()` export this behavior in the `CRYPTO_INTERNAL` namespace. `crypto_clone_cipher()` clones transforms for algorithms without `cra_init`, preserving flags and module references.

## State, Dependencies, and Integration

State is the underlying `crypto_tfm` and algorithm context. The file depends on internal cipher headers, allocation APIs, and `internal.h`. It is consumed by templates such as CMAC and CBC-MAC that need one-block cipher operations.

## Risks and Test Signals

Risks include alignment buffer sizing, stack buffer bounds for maximum block size, clone behavior for algorithms with initialization, and namespace-only consumers. Test signals include unaligned key/input/output cases, invalid key lengths, clone lifecycle tests, and template tests that exercise `crypto_cipher_encrypt_one()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cmac.c -->
# sources/distributed-fs/ceph-client/crypto/cmac.c

## Purpose

`cmac.c` implements the CMAC keyed hash template over block ciphers with 8- or 16-byte block sizes. It registers `cmac(cipher)` shash instances.

## Important APIs, Types, and Flow

`struct cmac_tfm_ctx` stores a child `crypto_cipher` and two derived subkeys immediately after the context. `crypto_cmac_digest_setkey()` sets the child cipher key, encrypts a zero block, then derives K1 and K2 by finite-field doubling with reduction constants `0x87` for 128-bit blocks and `0x1B` for 64-bit blocks. `crypto_cmac_digest_init()` zeros the chaining block. `update()` XORs and encrypts complete blocks, returning leftover length. `finup()` handles the final block: complete blocks use K1, incomplete blocks apply `0x80` padding and use K2, then one final cipher encryption produces the tag.

`cmac_create()` validates child block size, sets block-only/final-nonzero flags, installs shash callbacks, supports tfm clone by cloning the child cipher, and registers the instance.

## State, Dependencies, and Integration

Tfm state is child cipher plus CMAC subkeys; descriptor state is the current chaining block. Dependencies include internal cipher/hash APIs, `crypto_xor()`, and `crypto_cipher_encrypt_one()`. It integrates with any caller requesting `cmac(<cipher>)`.

## Risks and Test Signals

Risks include subkey endian/doubling logic, partial-final semantics, block-only update behavior, clone lifetime, and child cipher key propagation. Test signals are CMAC known-answer vectors for AES and 64-bit ciphers, exact-block versus partial-block finalization, invalid child block size rejection, clone consistency, and setkey error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/compress.h -->
# sources/distributed-fs/ceph-client/crypto/compress.h

## Purpose

`compress.h` is a local internal header for Crypto API compression support. It declares shared helpers used by compression implementation files without exposing them as public API.

## Important APIs, Types, and Flow

The header forward-declares `struct acomp_req` and `struct comp_alg_common`, includes local `internal.h`, and declares `crypto_init_scomp_ops_async(struct crypto_tfm *tfm)` plus `comp_prepare_alg(struct comp_alg_common *alg)`. There is no executable control flow in this file.

`crypto_init_scomp_ops_async()` is intended to initialize asynchronous operations for synchronous compression transforms, while `comp_prepare_alg()` prepares common compression algorithm metadata before registration.

## State, Dependencies, and Integration

There is no persistent state in the header. It depends on local crypto internals and is included by compression source files in this directory. Its integration role is to keep compression helper declarations source-local rather than part of installed public headers.

## Risks and Test Signals

Risks are declaration drift from implementation signatures, accidental public/private API confusion, and include-order dependency through `internal.h`. Test signals are compile coverage of compression modules and registration tests for sync and async compression algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/compress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32.c -->
# sources/distributed-fs/ceph-client/crypto/crc32.c

## Purpose

`crc32.c` registers a Crypto API shash wrapper around `crc32_le()`. It exposes `crc32` with optional seed keying and no final XOR, matching the behavior of the library helper.

## Important APIs, Types, and Flow

The transform context is a `u32` seed initialized to zero by `crc32_cra_init()`. `crc32_setkey()` accepts exactly four little-endian key bytes and stores the seed. `crc32_init()` copies the seed to descriptor state. `crc32_update()` advances descriptor CRC with `crc32_le()`. `crc32_final()` writes the current CRC little-endian. `crc32_finup()` and `crc32_digest()` perform update plus output in one step, with digest using the transform seed directly.

The registered `shash_alg` has block size 1, digest size 4, optional key flag, driver `crc32-lib`, and descriptor size `sizeof(u32)`.

## State, Dependencies, and Integration

State is the per-transform seed and per-request accumulator. Dependencies are `linux/crc32.h`, unaligned little-endian accessors, and shash registration. It integrates with kernel consumers that need CRC32 through the Crypto API rather than direct library calls.

## Risks and Test Signals

Risks include confusion with CRC variants that use initial/final XOR, seed endianness, and one-shot digest mutating expectations. Test signals are vectors matching `crc32_le()`, custom seed tests, update-versus-finup equivalence, and rejection of non-four-byte keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32c.c -->
# sources/distributed-fs/ceph-client/crypto/crc32c.c

## Purpose

`crc32c.c` registers a Crypto API shash wrapper for CRC-32C/Castagnoli using the kernel `crc32c()` helper. Unlike `crc32.c`, it initializes to `~0` and applies a final bitwise complement.

## Important APIs, Types, and Flow

`struct chksum_ctx` stores the transform seed; `struct chksum_desc_ctx` stores the streaming accumulator. `crc32c_cra_init()` initializes the seed to `~0`. `chksum_setkey()` accepts exactly four little-endian bytes to override the seed. `chksum_init()` copies seed into descriptor state, `chksum_update()` advances with `crc32c()`, and `chksum_final()` writes `~crc` little-endian. `finup()` and `digest()` share `__chksum_finup()`.

The registered algorithm name is `crc32c`, driver `crc32c-lib`, block size 1, digest size 4, optional key, and descriptor size `sizeof(struct chksum_desc_ctx)`.

## State, Dependencies, and Integration

State is transform seed plus per-request CRC accumulator. Dependencies are `linux/crc32.h`, shash internals, and unaligned helpers. It integrates with protocols and filesystems that select CRC32C through the Crypto API.

## Risks and Test Signals

Risks are variant confusion around initial and final complement, seed byte order, and hardware/software CRC32C equivalence. Tests should compare against known Castagnoli vectors, custom seed cases, split update equivalence, and invalid key length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crc32c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cryptd.c -->
# sources/distributed-fs/ceph-client/crypto/cryptd.c

## Purpose

`cryptd.c` implements the software async crypto daemon template `cryptd(...)`. It wraps synchronous skcipher, shash, and AEAD algorithms so callers can use async request semantics backed by per-CPU workqueues.

## Important APIs, Types, and Flow

The module creates a per-CPU `cryptd_queue` of `crypto_queue` objects protected by local BH locks and serviced by a per-CPU workqueue. `cryptd_enqueue_request()` enqueues on the current CPU, schedules work, and increments a transform refcount when applicable. `cryptd_queue_worker()` dequeues one request, completes backlog with `-EINPROGRESS`, completes the active request with status 0 to invoke the wrapper continuation, and reschedules if more requests remain.

Template creation dispatches by requested type to `cryptd_create_skcipher()`, `cryptd_create_hash()`, or `cryptd_create_aead()`. Each creates an instance named like the child but with driver `cryptd(child-driver)`, priority child + 50, async flag, child spawn, and wrapper callbacks. Runtime callbacks save the original completion, enqueue the parent request, prepare an embedded child request in worker context, run the synchronous child operation with MAY_SLEEP, then complete the original request. Hash wrappers adapt shash operations to ahash requests and support export/import.

Public helpers `cryptd_alloc_aead()`, `cryptd_aead_child()`, `cryptd_aead_queued()`, and `cryptd_free_aead()` manage refcounted AEAD wrappers.

## State, Dependencies, and Integration

Persistent module state is `cryptd_wq` and the global per-CPU queue. Instance state stores child spawns and queue pointer. Tfm state stores child transforms and refcounts. Dependencies include crypto template internals, workqueues, local locks, refcounts, and softirq-safe completion behavior.

## Risks and Test Signals

Risks include queue-depth `-ENOSPC`, CPU-local locking, transform free while queued work remains, callback restoration, handling `-EINPROGRESS`, and hash descriptor export/import state. Test signals are async crypto selftests under load, backlog notifications, module unload with empty queues, refcounted AEAD allocation/free, and equivalence with direct synchronous child algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cryptd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_engine.c -->
# sources/distributed-fs/ceph-client/crypto/crypto_engine.c

## Purpose

`crypto_engine.c` provides the framework for hardware crypto drivers that process async Crypto API requests through a software queue and a kthread request pump. It abstracts queueing, start/stop, request transfer, finalization, and engine algorithm registration helpers.

## Important APIs, Types, and Flow

`crypto_transfer_*_request_to_engine()` helpers enqueue AEAD, akcipher, ahash, KPP, and skcipher requests into the engine queue. `crypto_pump_requests()` is the core scheduler: under `queue_lock` it checks running/busy state, dequeues a request and backlog, marks `cur_req` when retry is unsupported, calls the algorithm `op.do_one_request()`, handles errors, requeues `-ENOSPC` when retry is supported, notifies backlog with `-EINPROGRESS`, and loops when retry support allows multiple outstanding hardware requests.

`crypto_finalize_*_request()` completes hardware requests, clears `cur_req` when needed, calls `crypto_request_complete()` in softirq context, and requeues pump work. `crypto_engine_start()` marks the engine running and schedules the pump. `crypto_engine_stop()` waits up to about ten seconds for queue/busy drain before returning `-EBUSY` or stopping. Allocation creates a device-managed engine, initializes queue and lock, starts a kthread worker, and optionally sets realtime scheduling.

Registration helpers validate `op.do_one_request` and register/unregister engine-backed AEAD, ahash, akcipher, KPP, and skcipher algorithms, including array rollback helpers.

## State, Dependencies, and Integration

Engine state includes queue, spinlock, kworker, pump work, running/busy flags, retry support, current request, device pointer, and private data. Dependencies are internal crypto algorithm types, kthread workers, device-managed allocation, scheduler policy, and softirq completion assumptions.

## Risks and Test Signals

Risks include request ordering on retry, stop races, lock context, callbacks outside softirq expectations, drivers failing to finalize current requests, and queue overflow. Test signals are hardware-driver selftests for enqueue/drain, `-ENOSPC` retry, stop while busy, registration rollback, realtime worker creation, and request completion ordering with backlog notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_null.c -->
# sources/distributed-fs/ceph-client/crypto/crypto_null.c

## Purpose

`crypto_null.c` registers no-op cryptographic algorithms used for IPsec, testing, and debugging: `cipher_null`, `digest_null`, and `ecb(cipher_null)` skcipher.

## Important APIs, Types, and Flow

Hash callbacks `null_init()`, `null_update()`, `null_final()`, and `null_digest()` all return success without producing data. Hash setkey also succeeds. `null_crypt()` copies one null cipher block for the legacy cipher API. `null_skcipher_crypt()` copies the request source scatterlist to destination when they differ and otherwise leaves data untouched.

Module init registers the legacy cipher, shash, and skcipher in order, rolling back earlier registrations on failure. Module exit unregisters all three. Registered sizes and key/IV constants come from `crypto/null.h`.

## State, Dependencies, and Integration

There is no transform context state. Dependencies are Crypto API hash and skcipher internals, scatterlist copy helpers, and null algorithm constants. Integration points are IPsec null encryption/authentication modes and tests that need a transform with predictable no-op behavior.

## Risks and Test Signals

Risks are mostly semantic: callers must understand that null digest produces zero-length/empty authentication behavior and null cipher provides no confidentiality. Implementation risks include registration rollback order and out-of-place scatterlist copying. Test signals are successful registration, no-op round trips, setkey accepting the configured null key size, and IPsec/null transform interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_null.c -->
