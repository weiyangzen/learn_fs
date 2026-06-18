# Group Research: group_270_cryptsetup_sources_block_storage_cryptsetup_lib_Makemodule_am_source_9b8d1e656454

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/Makemodule.am -->
# File Research: sources/block-storage/cryptsetup/lib/Makemodule.am

## Purpose
Autotools module defining the main `libcryptsetup.la` build, installed `libcryptsetup.h`, pkg-config metadata, symbol version script, and the small `libutils_io.la` helper archive.

## Key Content
Builds `libcryptsetup.la` from the core setup/device utilities, volume-key handling, dm integration, plain mode, integrity, loop-AES, TCRYPT, LUKS1, LUKS2, verity, OPAL, BITLK, and FileVault2 sources. It links UUID, devmapper, selected crypto backend libraries, optional libargon2, json-c, blkid, dl, gettext, `libcrypto_backend.la`, and `libutils_io.la`.

## Dependencies and Coupling
This file is the central source inventory for the C library under Autotools. The BITLK files in this batch are explicitly included here. `libcrypto_backend.la` is a required dependency and `lib/libcryptsetup.sym` controls exported ABI.

## Invariants and Risks
Source additions to libcryptsetup must be reflected here for Autotools builds. Meson and Autotools source lists must stay synchronized, especially for optional subsystems and vendored crypto code.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/bitlk/bitlk.c -->
# File Research: sources/block-storage/cryptsetup/lib/bitlk/bitlk.c

## Purpose
Implements BitLocker-compatible (`BITLK`) metadata parsing, keyslot extraction, passphrase/startup/recovery/clearkey unlock, FVEK decryption, metadata dumping, and dm-crypt/dm-zero activation.

## Key Content
Defines on-disk packed structures for BITLK signatures, superblocks, FVE metadata, validation metadata, VMK entries, BEK startup keys, and KDF state. `BITLK_read_sb()` reads the boot signature, rejects v1 boot code, detects normal vs BitLocker To Go layout, reads all three FVE metadata copies, validates CRC32, hashes the validated FVE block with SHA-256, parses VMKs, FVEK, volume header metadata, GUIDs, creation time, description, and cipher mode. Supported encryption maps include CBC Elephant, CBC EBOIV, and XTS.

Unlock flow is in `BITLK_get_volume_key()`: passphrases use the BitLocker SHA-256 KDF loop, recovery keys are parsed from the eight-part decimal format, startup keys are parsed from BEK metadata, and clear-key VMKs decrypt nested VMK material. VMK validation decrypts the validation datum and compares its SHA-256 hash against the validated FVE metadata before decrypting the FVEK.

Activation builds a multi-segment device-mapper table: metadata areas and relocated volume header become `dm-zero` targets, while data gaps become `dm-crypt` targets with correct IV offsets and optional large-sector IV flag.

## Dependencies and Coupling
Depends on `bitlk.h`, `internal.h`, crypto backend hash/CRC/AES-CCM helpers, UTF conversion, volume-key helpers, device I/O wrappers, and device-mapper target construction. Kernel support for BITLK IVs, Elephant diffuser, dm-zero, and large sectors is checked after activation failure.

## Invariants and Risks
The parser is defensive about entry sizes, metadata bounds, CRC, and double-fetch avoidance by copying entries from the validated buffer. Supported VMK protection types are passphrase, recovery passphrase, startup key, and clear key; TPM and smart-card paths are intentionally skipped. The `sha256_fve` field is treated as a 32-byte buffer even though the header declares it as an array of pointers, which is a type-safety hazard for future maintenance. Segment calculation assumes a maximum of ten dm targets.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/bitlk/bitlk.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/bitlk/bitlk.h -->
# File Research: sources/block-storage/cryptsetup/lib/bitlk/bitlk.h

## Purpose
Public internal header for BitLocker-compatible metadata structures and operations used by cryptsetup’s BITLK format support.

## Key Content
Defines nonce, salt, MAC tag, validation datum sizes, normal state constant, encryption type enum, VMK protection enum, FVE entry type/value enums, and in-memory structures for VMKs, FVEK, validation metadata, and parsed BITLK volume metadata. Declares read, dump, unlock, activation, and cleanup functions.

## Dependencies and Coupling
Forward-declares `crypt_device`, `device`, and `volume_key` so BITLK code can integrate with libcryptsetup internals without exposing full definitions. Constants must match parser assumptions in `bitlk.c`.

## Invariants and Risks
`struct bitlk_metadata` owns allocated strings, VMK list, FVEK, and validation allocation; callers must use `BITLK_bitlk_metadata_free()`. The `sha256_fve` member is declared as `const char *sha256_fve[32]` but used as raw 32-byte digest storage in `bitlk.c`; this should be treated carefully because the type does not express the actual data shape.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/bitlk/bitlk.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/bitops.h -->
# File Research: sources/block-storage/cryptsetup/lib/bitops.h

## Purpose
Portable byte-order and bitmap helper header used across libcryptsetup code.

## Key Content
Includes platform endian headers where available, handles OpenBSD endian macro names, defines fallback `bswap_16/32/64`, host-to/from little/big endian conversion macros, `swab16/32/64`, and classic bitmap macros `setbit`, `clrbit`, `isset`, and `isclr`.

## Dependencies and Coupling
Used by parsers handling on-disk little-endian or big-endian metadata, including BITLK. Depends on build-time feature macros such as `HAVE_BYTESWAP_H`, `HAVE_ENDIAN_H`, `HAVE_SYS_ENDIAN_H`, and `WORDS_BIGENDIAN`.

## Invariants and Risks
The conversion macros are preprocessor-only and assume integer-like arguments. Fallback bitmap macros depend on `NBBY`/`CHAR_BIT` semantics and do not guard index bounds.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypt_plain.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypt_plain.c

## Purpose
Implements key derivation for plain dm-crypt mode.

## Key Content
`crypt_plain_hash()` accepts `hash` or `hash:hash_length` syntax, derives only the requested prefix length, zero-pads the remaining key if a shorter hash length is requested, and supports `"plain"` by directly copying passphrase bytes into the key. Other hash names use the local `hash()` helper, which repeatedly hashes optional leading `"A"` bytes plus the passphrase to fill arbitrarily sized keys, following the historical hashalot-compatible scheme.

## Dependencies and Coupling
Uses libcryptsetup logging, crypto backend hash APIs, and safe memory copy helpers. This is consumed by plain-mode setup paths rather than LUKS metadata paths.

## Invariants and Risks
Plain mode has no salt or metadata authentication. `"plain"` requires passphrase length at least as large as the requested key prefix. Hash name parsing caps names at 255 bytes.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypt_plain.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/Makemodule.am -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/Makemodule.am

## Purpose
Autotools build module for the internal crypto backend archive.

## Key Content
Builds `libcrypto_backend.la` from common backend interfaces, kernel cipher support, crypto storage wrappers, PBKDF checks, CRC32, base64, UTF-8 conversion, Argon2 generic wrapper, cipher generic/check helpers, and memory utilities. Conditionally adds provider implementations for gcrypt, OpenSSL, NSS, kernel, nettle, and mbedTLS. Optionally adds internal PBKDF2 and links bundled `libargon2.la`.

## Dependencies and Coupling
Selected by configure-time conditionals. The main `libcryptsetup.la` links this archive directly.

## Invariants and Risks
All backend provider source lists must match configure feature tests. When `CRYPTO_INTERNAL_ARGON2` is enabled, the internal Argon2 archive must be built before this archive.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/Makemodule.am -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/Makemodule.am

## Purpose
Autotools build module for cryptsetup’s bundled Argon2 static library.

## Key Content
Defines `libargon2.la` with C89, pthread, and `-O3` flags. Includes BLAKE2b, Argon2 API/core/encoding/thread sources and headers. Selects either optimized SIMD Argon2 (`blamka-round-opt.h`, `opt.c`) or portable reference Argon2 (`blamka-round-ref.h`, `ref.c`) based on `CRYPTO_INTERNAL_SSE_ARGON2`.

## Dependencies and Coupling
Used only when cryptsetup builds internal Argon2. Include paths point to `argon2` and `argon2/blake2`.

## Invariants and Risks
Autotools and Meson Argon2 source lists must remain aligned. SIMD selection is compile-time, not runtime.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.c

## Purpose
Vendored Argon2 public API implementation: hashing, encoded hash generation, verification, error messages, and encoded-length calculation.

## Key Content
`argon2_ctx()` validates inputs, normalizes requested memory into lane/slice-aligned blocks, initializes an `argon2_instance_t`, fills memory, and finalizes the tag. `argon2_hash()` builds a context from simple arguments and can return raw hash, encoded hash, or both. Type-specific wrappers cover Argon2d, Argon2i, and Argon2id. Verification decodes encoded strings into a context, recomputes the hash, and compares using `argon2_compare()`.

## Dependencies and Coupling
Uses `argon2.h`, `encoding.h`, and `core.h`. Calls core functions for validation, initialization, memory filling, and finalization.

## Invariants and Risks
Memory is wiped before freeing temporary outputs. Verification allocates buffers sized to the encoded string as an upper bound. The API supports Argon2 version 1.0 decoding and current version 1.3 encoding.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.h

## Purpose
Vendored Argon2 public header defining parameter limits, error codes, context structure, algorithm types, versions, and API declarations.

## Key Content
Defines min/max bounds for lanes, threads, output, memory, passes, password, salt, secret, and associated data. Declares `argon2_context`, external allocator callback types, `argon2_type`, version constants, flags for clearing password/secret, and all raw/encoded/verify/context APIs.

## Dependencies and Coupling
Included by cryptsetup’s internal Argon2 wrapper and all bundled Argon2 implementation files. Visibility macros adapt for GCC/Clang, MSVC, and default builds.

## Invariants and Risks
Callers must satisfy context pointer/length consistency rules. Different parallelism values intentionally produce different Argon2 outputs. The global `FLAG_clear_internal_memory` is declared here and defined in `core.c`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/argon2.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2-impl.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2-impl.h

## Purpose
Portable low-level helpers for BLAKE2 and Argon2 encoding of little-endian words and rotates.

## Key Content
Detects native little-endian targets, defines inline `load32`, `load64`, `store32`, `store64`, `load48`, `store48`, `rotr32`, and `rotr64`. Uses memcpy-based loads/stores on little-endian systems to avoid alignment violations and bytewise fallback otherwise.

## Dependencies and Coupling
Included by BLAKE2b and Argon2 block-fill code. Its endian helpers are foundational for stable cross-platform hash output.

## Invariants and Risks
Correctness depends on exact little-endian serialization. Rotate helpers assume valid nonzero rotation constants as used by BLAKE2/BlaMka code.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2-impl.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2.h

## Purpose
Vendored BLAKE2b interface and state definitions used by Argon2.

## Key Content
Defines BLAKE2b constants, packed parameter block, streaming state, compile-time size checks, streaming API declarations, simple one-shot API, and Argon2-specific `blake2b_long()`.

## Dependencies and Coupling
Includes `argon2.h` for visibility macros. Implemented by `blake2b.c` and used by `core.c`, `ref.c`, and `opt.c`.

## Invariants and Risks
The packed parameter block must remain exactly 64 bytes. `blake2b_long()` is required by Argon2 for variable-length block expansion and final output generation.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2b.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2b.c

## Purpose
Portable BLAKE2b implementation for bundled Argon2.

## Key Content
Implements parameterized initialization, keyed initialization, update, finalization, one-shot hashing, compression with 12 rounds, state invalidation, counter/final-block management, and Argon2’s `blake2b_long()` variable-output construction.

## Dependencies and Coupling
Uses `blake2.h`, `blake2-impl.h`, and `clear_internal_memory()` from Argon2 core. Argon2 core uses BLAKE2b for initial hashing, first block expansion, and final tag generation.

## Invariants and Risks
State reuse after finalization is rejected. Temporary buffers and state fields are wiped. `blake2b_long()` prefixes output length in little-endian form as required by Argon2.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blake2b.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-opt.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-opt.h

## Purpose
SIMD-optimized BlaMka/BLAKE2 round macros for Argon2 block filling.

## Key Content
Provides SSE2/SSSE3, AVX2, and AVX512F implementations of the BlaMka multiply-add round, rotation helpers, diagonalization/undiagonalization, and `BLAKE2_ROUND*` macros. AVX2 and AVX512 paths use vector shuffles/permutations and packed 64-bit arithmetic to process Argon2 block columns/rows efficiently.

## Dependencies and Coupling
Included by `opt.c`. Requires x86 intrinsic headers and compiler feature macros matching the selected build flags.

## Invariants and Risks
This is compile-time CPU-targeted code. Binaries built with unsupported instruction sets will not run on older CPUs unless the build system constrains deployment appropriately.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-opt.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-ref.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-ref.h

## Purpose
Portable scalar BlaMka round macros for Argon2 reference block filling.

## Key Content
Defines `fBlaMka()` and the no-message BLAKE2-style `G` and `BLAKE2_ROUND_NOMSG` macros over 64-bit words. The multiply-add variant is from the Lyra PHC team and is the core compression primitive used in Argon2 memory block mixing.

## Dependencies and Coupling
Included by `ref.c`. Uses rotate helpers from `blake2-impl.h`.

## Invariants and Risks
This path is slower than SIMD but portable. Macro arguments are evaluated as mutable lvalues and must be real block word variables.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/blake2/blamka-round-ref.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.c

## Purpose
Argon2 core engine: memory allocation/wiping, input validation, initial hashing, first-block generation, memory-fill scheduling, reference-index calculation, and final tag generation.

## Key Content
Implements block copy/xor/load/store helpers, allocator hooks, secure wipe fallbacks, global internal-memory clearing, `finalize()`, `index_alpha()`, single-threaded and multithreaded memory filling, full input validation, `initial_hash()`, `fill_first_blocks()`, and `initialize()`. Multithreaded fill launches lane workers per slice and enforces a thread limit.

## Dependencies and Coupling
Uses `core.h`, `thread.h`, BLAKE2b, and BLAKE2 endian helpers. The actual segment compression function is supplied by either `ref.c` or `opt.c`.

## Invariants and Risks
Memory cost is rounded down to equal lane/slice segments after enforcing the minimum. Custom allocators must be provided as a matching allocate/free pair. Sensitive memory is wiped when `FLAG_clear_internal_memory` is enabled, which defaults to true.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.h

## Purpose
Internal Argon2 core definitions and function declarations.

## Key Content
Defines block sizes, prehash sizes, the 1 KiB `block` structure, `argon2_instance_t`, `argon2_position_t`, thread data structure, and declarations for allocator, wiping, validation, initialization, segment filling, memory filling, indexing, and finalization functions.

## Dependencies and Coupling
Included by all Argon2 implementation units. The `fill_segment()` declaration is implemented by exactly one of `ref.c` or `opt.c`.

## Invariants and Risks
The block layout and constants must match the Argon2 specification. `argon2_instance_t` stores derived lane and segment lengths; callers must initialize them consistently before filling memory.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/core.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.c

## Purpose
Argon2 encoded-string parser and formatter, including internal unpadded Base64 helpers.

## Key Content
Implements constant-time-ish Base64 character mapping, unpadded Base64 encode/decode, strict minimal decimal parsing, `decode_string()` for `$argon2<T>[$v=...]$m=...,t=...,p=...$salt$hash`, `encode_string()`, and helper length calculators `b64len()` and `numlen()`.

## Dependencies and Coupling
Uses `encoding.h`, `core.h`, `argon2_type2string()`, and `validate_inputs()`. Called by `argon2_hash()` and `argon2_verify()`.

## Invariants and Risks
Decoded strings must match the requested Argon2 type and may not contain trailing data. Decimal fields reject leading-zero nonminimal forms and overflow. Salt and output buffers must be preallocated by the caller with maximum accepted sizes.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.h

## Purpose
Internal declarations for Argon2 encoded hash string handling.

## Key Content
Declares decoded length constants, `encode_string()`, `decode_string()`, `b64len()`, and `numlen()`. Documents caller responsibilities for preinitializing buffers in `argon2_context`.

## Dependencies and Coupling
Includes `argon2.h`. Implemented by `encoding.c` and consumed by `argon2.c`.

## Invariants and Risks
The header exposes minimum decoded salt/output constants, but validation ultimately uses the broader Argon2 limits in `validate_inputs()`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/encoding.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/meson.build -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/meson.build

## Purpose
Meson build definition for bundled Argon2.

## Key Content
Defines `libargon2_sources` with BLAKE2b, Argon2 API, core, encoding, and thread sources. Adds `opt.c` when `use_internal_sse_argon2` is enabled, otherwise `ref.c`. Builds a static `argon2` library with C89 and optimization level 3, includes `blake2`, and links thread dependency.

## Dependencies and Coupling
Meson counterpart to `argon2/Makemodule.am`.

## Invariants and Risks
Only C source files are listed; headers are included transitively. Meson and Autotools source selection must stay equivalent.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/opt.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/opt.c

## Purpose
SIMD implementation of Argon2 `fill_segment()`.

## Key Content
Defines vectorized `fill_block()` variants for AVX512F, AVX2, and SSE-class targets, plus address-block generation and the same segment traversal logic as the reference implementation. It maintains a vector `state` initialized from the previous block, selects reference blocks based on data-independent or data-dependent addressing, and writes mixed blocks with overwrite or XOR behavior depending on Argon2 version/pass.

## Dependencies and Coupling
Includes `argon2.h`, `core.h`, BLAKE2 headers, and `blamka-round-opt.h`. Selected only when the build enables internal SSE Argon2.

## Invariants and Risks
Compile flags must match the intrinsic path. The optimized path must remain bit-for-bit compatible with `ref.c`; changes to indexing or XOR rules must be mirrored.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/opt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/ref.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/ref.c

## Purpose
Portable reference implementation of Argon2 `fill_segment()`.

## Key Content
Implements scalar `fill_block()` using copy/xor, BlaMka no-message rounds over columns then rows, address-block generation for data-independent modes, and segment filling for Argon2d/i/id. It handles first-slice startup offsets, reference lane/index calculation, and version-specific overwrite vs XOR behavior.

## Dependencies and Coupling
Includes `argon2.h`, `core.h`, `blamka-round-ref.h`, `blake2-impl.h`, and `blake2.h`. Selected when optimized internal Argon2 is disabled.

## Invariants and Risks
This is the correctness reference for the SIMD path. `fill_segment()` returns silently if the instance pointer is null, matching upstream style rather than reporting an error.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/ref.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.c

## Purpose
Minimal cross-platform thread wrapper for Argon2 memory filling.

## Key Content
When threading is enabled, implements `argon2_thread_create()` and `argon2_thread_join()` using `_beginthreadex`/`WaitForSingleObject`/`CloseHandle` on Windows and `pthread_create`/`pthread_join` elsewhere.

## Dependencies and Coupling
Included by `core.c` multithreaded fill path via `thread.h`.

## Invariants and Risks
No abstraction beyond create/join is provided. Threading can be compiled out with `ARGON2_NO_THREADS`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.h

## Purpose
Thread abstraction header for Argon2.

## Key Content
Defines platform-specific thread function and handle types, and declares `argon2_thread_create()` and `argon2_thread_join()` when `ARGON2_NO_THREADS` is not set. Uses Win32 process/thread APIs on Windows and pthreads otherwise.

## Dependencies and Coupling
Consumed by `core.c` and implemented by `thread.c`.

## Invariants and Risks
The API intentionally only supports creation and joining. Callers own scheduling and error handling.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/thread.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2_generic.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2_generic.c

## Purpose
cryptsetup wrapper around either external libargon2 or bundled Argon2.

## Key Content
When Argon2 headers/internal code are available, `argon2()` maps string type names `argon2i` and `argon2id` to libargon2 context execution and translates failures to errno-style values. It asserts the active crypto backend does not already provide native Argon2. If Argon2 is unavailable, the function returns `-EINVAL`. `crypt_argon2_version()` reports whether external libargon2 or cryptsetup’s bundled libargon2 is used.

## Dependencies and Coupling
Includes `crypto_backend_internal.h` and either system `<argon2.h>` or bundled `argon2/argon2.h`.

## Invariants and Risks
Argon2d is not exposed through this wrapper. Backend-native Argon2 takes precedence over external/internal wrapper code.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/argon2_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/base64.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/base64.c

## Purpose
Base64 encode/decode helpers for the crypto backend.

## Key Content
Implements RFC4648 alphabet encoding with `=` padding and a decoder that tolerates whitespace around input characters. Decode validates padding positions, unused low bits in padded sextets, and rejects trailing non-whitespace data after padding. Errors other than allocation failure are normalized to `-EINVAL`.

## Dependencies and Coupling
Includes `crypto_backend.h`. Used by higher-level metadata/token code needing binary-to-text conversion.

## Invariants and Risks
`crypt_base64_decode()` requires `out_length`. If input length is `(size_t)-1`, it treats input as NUL-terminated. Output buffers are heap allocated and caller-owned.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_check.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_check.c

## Purpose
Measures Linux kernel crypto cipher throughput.

## Key Content
Uses the kernel AF_ALG cipher wrapper to encrypt and decrypt a caller-supplied buffer in 64 KiB chunks. `cipher_measure()` times one full buffer pass with `CLOCK_MONOTONIC_RAW`, rejects too-small timings, and `crypt_cipher_perf_kernel()` repeats encryption and decryption until each exceeds roughly one second, then reports MiB/s.

## Dependencies and Coupling
Depends on `crypto_backend_internal.h` kernel cipher APIs. Intended for benchmarking kernel implementations used by dm-crypt.

## Invariants and Risks
This is a CPU/kernel crypto benchmark, not a storage benchmark. It mutates the supplied buffer in place during measurement.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_check.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_generic.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_generic.c

## Purpose
Generic cipher metadata helpers independent of a concrete crypto provider.

## Key Content
Maintains a static cipher table with block sizes and wrapped-key support, including common dm-crypt algorithms and Adiantum compound names. `crypt_cipher_ivsize()` returns IV size, with special handling for `hctr2` and `ecb`. `crypt_cipher_wrapped_key()` reports whether an algorithm uses a wrapped key. `crypt_fips_mode_kernel()` reads `/proc/sys/crypto/fips_enabled`.

## Dependencies and Coupling
Includes `crypto_backend.h` and POSIX file APIs. Used by setup/validation paths that need cipher properties before initializing a full cipher context.

## Invariants and Risks
Algorithm matching is case-insensitive and allows mode-prefix matches for table entries with a mode. Unknown algorithms return `-EINVAL` for IV size and false for wrapped-key status.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crc32.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crc32.c

## Purpose
Table-driven CRC32 and CRC32C helpers.

## Key Content
Contains static lookup tables for standard CRC32 polynomial and CRC32C, a shared `compute_crc32()` loop, and exported `crypt_crc32()` / `crypt_crc32c()` wrappers. The seed is supplied by the caller and no final XOR is applied internally.

## Dependencies and Coupling
Includes `crypto_backend.h`. BITLK uses `crypt_crc32()` to validate FVE metadata copies.

## Invariants and Risks
Callers must apply any format-specific initial/final XOR policy themselves. The function is byte-oriented and not hardware accelerated.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend.h

## Purpose
Main internal crypto backend API for libcryptsetup.

## Key Content
Declares backend lifecycle/version/flags, hash, HMAC, RNG, PBKDF limits and execution, PBKDF benchmarking, CRC32/CRC32C, Base64, UTF-8/UTF-16 conversion, block cipher operations, kernel cipher benchmark/checks, storage encryption wrappers, temporary BITLK AES-CCM key decrypt helper, secure memzero/memcpy/memeq helpers, and FIPS status queries.

## Dependencies and Coupling
Included widely by libcryptsetup and backend implementation files. Provides an abstraction over concrete providers such as OpenSSL, gcrypt, NSS, nettle, mbedTLS, kernel crypto, and internal PBKDF code.

## Invariants and Risks
Callers receive errno-style negative failures. Backend flags advertise special behavior such as kernel support, PBKDF2 signed-iteration limits, and native Argon2 availability.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend_internal.h -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend_internal.h

## Purpose
Private crypto backend declarations shared among backend implementation units.

## Key Content
Declares internal PBKDF2, internal/external Argon2 wrapper, kernel cipher context structure, kernel cipher init/encrypt/decrypt/destroy/check functions, BITLK kernel AES-CCM decrypt helper, and internal constant-time memory comparison.

## Dependencies and Coupling
Includes `crypto_backend.h`. Used by backend source files that need implementation-only helpers not exposed to the rest of libcryptsetup.

## Invariants and Risks
`struct crypt_cipher_kernel` owns two file descriptors and must be destroyed to avoid descriptor leaks. Kernel helper availability depends on `ENABLE_AF_ALG`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_backend_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_cipher_kernel.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_cipher_kernel.c

## Purpose
Linux AF_ALG userspace crypto backend for skcipher and selected AEAD operations.

## Key Content
When `ENABLE_AF_ALG` is enabled, initializes AF_ALG transform sockets, binds algorithm names, sets keys and optional AEAD auth size, accepts operation sockets, and performs encrypt/decrypt through `sendmsg()` control messages plus `read()`. `crypt_cipher_check_kernel()` constructs skcipher or AEAD algorithm names and tests key setup. `crypt_bitlk_decrypt_key_kernel()` uses kernel `ccm(aes)` to decrypt BITLK key material with appended tag and RFC3610-style CCM IV construction.

When AF_ALG is disabled, all kernel operations return `-ENOTSUP` or `-EINVAL` stubs.

## Dependencies and Coupling
Uses Linux `<linux/if_alg.h>`, sockets, control messages, and crypto backend memory helpers. Called by cipher checks, benchmarks, generic fallback cipher paths, and BITLK key decryption.

## Invariants and Risks
Input/output lengths must match exact AF_ALG send/read expectations. Algorithm names must fit fixed kernel sockaddr fields. Context file descriptors are reset in `crypt_cipher_destroy_kernel()`. AEAD and BITLK support are tightly coupled to kernel AF_ALG semantics.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_cipher_kernel.c -->