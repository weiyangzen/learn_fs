# Group Research: group_271_cryptsetup_sources_block_storage_cryptsetup_lib_crypto_backend_crypt_5faea384ec6c

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_gcrypt.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_gcrypt.c

Implements the libgcrypt backend for cryptsetup’s common crypto backend interface: hashes, HMACs, RNG, PBKDF, block ciphers, BitLocker AES-CCM key decrypt, constant-time compare, and FIPS detection.

Key points:
- `crypt_backend_init()` initializes libgcrypt, secure memory, backend version text, and runs a Whirlpool split-update compatibility test.
- Hash name compatibility maps BLAKE2 names and special `whirlpool_gcryptbug` handling through `crypt_hash_compat_name()`.
- Hash/HMAC contexts wrap `gcry_md_hd_t`; `*_final()` copies requested digest bytes and resets the context for reuse.
- RNG maps normal randomness to `GCRY_STRONG_RANDOM` and salt/key/default to `GCRY_VERY_STRONG_RANDOM`.
- PBKDF2 uses either internal `pkcs5_pbkdf2()` or `gcry_kdf_derive()`.
- Argon2 can use libgcrypt KDF support when available and not using internal Argon2; parallel mode supplies custom pthread dispatch/wait callbacks.
- Cipher initialization first tries libgcrypt ECB/CBC/XTS, then falls back to the kernel cipher backend.
- `crypt_bitlk_decrypt_key()` uses AES-CCM when `GCRY_CCM_BLOCK_LEN` exists, otherwise returns `-ENOTSUP`.
- `crypt_fips_mode()` is compiled out unless `ENABLE_FIPS`; enabled builds query `gcry_fips_mode_active()` after backend init.

Storage relevance:
- This is one selectable cryptsetup crypto provider used by LUKS, FileVault2, BitLocker, PBKDF calibration, and storage encryption helpers.
- Kernel fallback means algorithms unsupported by libgcrypt can still work through Linux crypto API where available.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_gcrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_kernel.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_kernel.c

Implements a Linux AF_ALG kernel crypto backend.

Key points:
- `crypt_backend_init()` requires Linux via `uname()`, builds a version string, and probes `AF_ALG` hash support with `sha256`.
- Supported hashes are table-driven with cryptsetup names, kernel names, digest lengths, and HMAC block lengths.
- Hash/HMAC contexts hold transform and operation sockets. `_get_alg()` maps cryptsetup names to kernel algorithm names.
- `crypt_kernel_socket_init()` creates/binds AF_ALG sockets, optionally sets the key, and accepts an operation fd.
- Hash and HMAC update with `send(..., MSG_MORE)` and finalize with `read()`.
- RNG is explicitly unavailable and returns `-EINVAL`.
- PBKDF2 delegates to generic `pkcs5_pbkdf2()` using each hash’s block size; Argon2 delegates to `argon2()`.
- Ciphers and BitLocker AES-CCM are kernel-only through `crypt_cipher_*_kernel()` and `crypt_bitlk_decrypt_key_kernel()`.
- Backend flags return `CRYPT_BACKEND_KERNEL`; FIPS status delegates to `crypt_fips_mode_kernel()`.

Storage relevance:
- Provides cryptsetup with a no-userspace-crypto path where hash/HMAC/cipher operations come from the Linux kernel.
- Timing code in `pbkdf_check.c` accounts for this backend by adding system CPU time.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_kernel.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_mbedtls.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_mbedtls.c

Implements the mbedTLS backend.

Key points:
- Global state includes mbedTLS entropy and CTR-DRBG contexts initialized in `crypt_backend_init()` and freed in `crypt_backend_destroy()`.
- Hash support is limited to SHA-1, SHA-224/256/384/512, and RIPEMD-160 through `crypt_get_hash()`.
- Hash and HMAC wrap `mbedtls_md_context_t`; finalization copies through `crypt_backend_memcpy()`, zeroes temporary digest buffers, and resets contexts.
- RNG rejects FIPS mode with `-ENOTSUP`; otherwise uses CTR-DRBG and toggles prediction resistance based on randomness quality.
- Cipher support is table-driven for AES, ARIA, Camellia and modes ECB/CBC/CFB/OFB/CTR/XTS.
- CBC padding is disabled. ECB is processed in block-sized chunks because mbedTLS ECB expects exact block-size input.
- PBKDF2 uses `mbedtls_pkcs5_pbkdf2_hmac_ext()` when available, otherwise a manually initialized HMAC context.
- Argon2 always delegates to cryptsetup’s `argon2()` wrapper.
- BitLocker key decrypt uses AES-CCM authenticated decrypt through `mbedtls_ccm_auth_decrypt()`.
- `crypt_backend_memeq()` delegates to `mbedtls_ct_memcmp()`; FIPS mode always returns false.

Storage relevance:
- A self-contained userspace crypto backend with narrower algorithm coverage than OpenSSL/gcrypt, but direct cipher support without kernel fallback for listed ciphers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_mbedtls.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nettle.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nettle.c

Implements the Nettle backend.

Key points:
- Version string is compile-time if `nettle/version.h` is available.
- Hash table stores function pointers for init/update/digest plus HMAC set-key/update/digest.
- Supports SHA-1, SHA-224/256/384/512, RIPEMD-160, and SHA3 variants when `NETTLE_SHA3_FIPS202` is true.
- Adds local HMAC wrappers for SHA3 because Nettle lacks direct HMAC helper wrappers for them.
- Hash contexts store a union of concrete Nettle hash contexts and reset by re-running the init function.
- HMAC contexts copy the key, retain key length, and reset by reapplying the key.
- RNG is unavailable and returns `-EINVAL`.
- PBKDF2 uses `nettle_pbkdf2()` after creating a cryptsetup HMAC context; Argon2 delegates to `argon2()`.
- Ciphers and BitLocker AES-CCM are kernel-only.
- Constant-time comparison returns inverted `memeql_sec()` semantics to match cryptsetup’s memcmp-like return convention.
- FIPS mode always returns false.

Storage relevance:
- A hash/HMAC/PBKDF provider paired with kernel cipher handling.
- Important for builds preferring Nettle while still relying on kernel crypto for storage encryption modes.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nettle.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nss.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nss.c

Implements the NSS backend.

Key points:
- `crypt_backend_init()` uses `NSS_NoDB_Init(".")` and records an NSS version string when `NSS_GetVersion()` is available.
- Supported hash/HMAC algorithms are SHA-1, SHA-256, SHA-384, and SHA-512.
- Hash contexts use `PK11_CreateDigestContext()`, `PK11_DigestBegin/Op/Final()`, and reset after final.
- HMAC imports a symmetric key into an internal NSS slot and creates a context by mechanism.
- RNG uses `PK11_GenerateRandom()` and rejects FIPS requests with `-EINVAL`.
- PBKDF2 delegates to generic `pkcs5_pbkdf2()` with table-provided HMAC block length; Argon2 delegates to `argon2()`.
- Ciphers and BitLocker AES-CCM are kernel-only.
- Constant-time comparison uses `NSS_SecureMemcmp()`.
- FIPS mode always returns false in this backend.

Storage relevance:
- Provides NSS hash/HMAC/RNG/PBKDF integration while leaving storage ciphers to the Linux kernel backend.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_nss.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_openssl.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_openssl.c

Implements the OpenSSL/LibreSSL backend.

Key points:
- Handles legacy OpenSSL, LibreSSL, and OpenSSL 3 provider APIs behind `OPENSSL3_API`.
- OpenSSL 3 path creates a private `OSSL_LIB_CTX` outside FIPS mode, loads default provider, optionally loads legacy provider, and records provider/thread/Argon2 flags in the backend version.
- Compatibility wrappers support older OpenSSL/LibreSSL allocation APIs.
- Hash names normalize selected BLAKE2 spellings before lookup/fetch.
- OpenSSL 3 uses fetched `EVP_MD`/`EVP_CIPHER`; non-3 uses classic `EVP_get_*`.
- Hash contexts use `EVP_MD_CTX`; HMAC uses `EVP_MAC` for OpenSSL 3 and `HMAC_CTX` for older APIs.
- RNG uses `RAND_bytes()` and rejects lengths above `INT_MAX`.
- PBKDF2 uses OpenSSL 3 `EVP_KDF` or old `PKCS5_PBKDF2_HMAC()` with integer overflow guards.
- Argon2 uses OpenSSL 3 KDF when available, including threads/lanes/memory parameters; otherwise delegates to cryptsetup `argon2()`.
- Cipher init constructs names like `aes-256-xts` or `sm4-ctr`, validates key length, disables padding, and falls back to kernel cipher if OpenSSL lacks the algorithm.
- BitLocker key decrypt uses AES-256-CCM via EVP when CCM controls are available.
- FIPS detection uses OpenSSL 3 default property status or legacy `FIPS_mode()` when compiled with `ENABLE_FIPS`.

Storage relevance:
- Broadest userspace backend in this group, with both native cipher support and kernel fallback.
- Provider context behavior is important for algorithms that live in OpenSSL 3 legacy provider.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_openssl.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_storage.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_storage.c

Implements generic userspace storage encryption wrappers and dm-crypt-compatible IV generation.

Key points:
- `crypt_sector_iv` models IV modes: none, null, plain, plain64, ESSIV, BENBI, plain64be, and EBOIV.
- `crypt_storage` stores sector size, IV shift, main cipher, and IV helper state.
- Sector size must be a power of two from 512 through 4096 bytes.
- `crypt_storage_init()` accepts standard cipher/mode strings and `capi:` strings, splits cipher mode from IV suffix, initializes the main cipher, and initializes IV state.
- ESSIV derives an IV encryption key by hashing the data key and initializing an ECB cipher.
- EBOIV initializes an ECB cipher with the data key and shifts by sector-size log2.
- `crypt_sector_iv_generate()` writes endian-specific sector IVs and encrypts ESSIV/EBOIV IV blocks.
- Encrypt/decrypt functions require aligned lengths and IV offsets, then process sector-by-sector in place.
- `crypt_storage_kernel_only()` reports whether the underlying cipher is kernel-only.

Storage relevance:
- This is the userspace mirror of dm-crypt sector-IV handling, useful for metadata parsing, tests, and non-device-mapper transformations.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_storage.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/memutils.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/memutils.c

Provides sensitive-memory helper primitives for the crypto backend.

Key points:
- Functions are marked noinline and optionally `zero_call_used_regs("used")` to reduce secret remnants in registers.
- `crypt_backend_memzero()` uses `explicit_bzero()` when available, except under MemorySanitizer workaround, otherwise volatile byte stores.
- `crypt_backend_memcpy()` uses volatile byte loads/stores to avoid extra register spilling of sensitive data.
- `crypt_internal_memeq()` performs constant-time XOR accumulation and returns zero on equality, nonzero on mismatch.

Storage relevance:
- Used throughout crypto code to copy and clear derived keys, hashes, HMAC outputs, PBKDF temporaries, and passphrase-derived buffers.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/memutils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/meson.build -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/meson.build

Defines Meson build composition for the crypto backend static library.

Key points:
- Includes the internal Argon2 subdirectory when `use_internal_argon2` is true.
- Base dependencies include the selected crypto backend library and `clock_gettime`.
- Always includes common sources: Argon2 wrapper, base64, memutils, cipher checks/generic code, CRC32, kernel cipher bridge, storage wrapper, PBKDF benchmark, and UTF helpers.
- Adds the selected backend source dynamically via `crypto_@0@.c`.
- Adds `pbkdf2_generic.c` only when `use_internal_pbkdf2` is true.
- Links internal or external libargon2 depending on Meson options.
- Produces static library `crypto_backend`.

Storage relevance:
- Controls which backend implementation is compiled into cryptsetup while keeping common storage and PBKDF helpers always present.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf2_generic.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf2_generic.c

Implements generic PKCS#5 PBKDF2 using cryptsetup’s HMAC interface.

Key points:
- `hash_buf()` hashes a buffer with a named cryptsetup hash.
- `pkcs5_pbkdf2()` implements PBKDF2 block derivation: compute `U_1...U_c`, XOR into `T`, and copy blocks into the derived key.
- Validates HMAC size, nonzero iteration count, nonzero output length, and bounded digest length by `MAX_PRF_BLOCK_LEN`.
- Optional `hash_block_size` pre-hashes long passwords before HMAC setup to avoid backend limitations or repeated long-key processing.
- Uses `alloca()` for salt-plus-block-index temporary and clears sensitive buffers before returning.
- Returns negative errno-style values.

Storage relevance:
- Fallback PBKDF2 core used by kernel/NSS and optionally gcrypt/OpenSSL builds.
- Directly affects passphrase-derived keys for LUKS and FileVault2 when internal PBKDF2 is selected.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf2_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf_check.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf_check.c

Implements PBKDF parameter limits and benchmarking/calibration.

Key points:
- `crypt_pbkdf_get_limits()` defines hard limits for PBKDF2 and Argon2i/Argon2id.
- PBKDF2 minimum iterations are 1000; Argon2 has minimum time cost 4, memory 32 KiB, benchmark memory floor 64 MiB, max memory 4 GiB, and parallelism 1-4.
- CPU-time measurement uses `getrusage()` for PBKDF2, adding system time for kernel backend or broken user-time reporting.
- Argon2 benchmarking uses wall-clock `CLOCK_MONOTONIC_RAW` because parallel threads make CPU time inappropriate.
- `next_argon2_params()` adjusts time cost and memory cost toward target runtime, bounded by min/max.
- `crypt_argon2_check()` first finds parameters taking at least 250 ms, then iterates until within 95-110% of target or convergence.
- `crypt_pbkdf_check()` estimates PBKDF2 iterations for target runtime, scaling iterations up until a stable measurement over 500 ms.
- `crypt_pbkdf_perf()` selects the PBKDF2 or Argon2 calibration path and reports iterations and memory.

Storage relevance:
- Determines calibrated KDF strength for formatted volumes and passphrase operations.
- Progress callback can interrupt calibration with `-EINTR`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf_check.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/utf8.c -->
# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/utf8.c

Provides UTF-8/UTF-16LE conversion helpers adapted from systemd/GLib lineage.

Key points:
- UTF-16 helpers detect surrogate ranges and combine valid surrogate pairs into Unicode code points.
- `crypt_utf16_to_utf8()` treats input length as bytes, decodes little-endian UTF-16, ignores malformed surrogate fragments, and NUL-terminates the caller-provided output buffer.
- `utf8_encoded_expected_len()` recognizes 1- to 6-byte leading byte patterns.
- `utf8_encoded_to_unichar()` validates continuation bytes and returns decoded code point.
- `utf16_encode_unichar()` emits UTF-16LE words and rejects surrogate code points as invalid standalone values.
- `crypt_utf8_to_utf16()` converts valid multibyte UTF-8 to UTF-16LE; invalid or single-byte characters are copied bytewise as 16-bit values.
- `crypt_char16_strlen()` counts UTF-16 words until NUL.

Storage relevance:
- Supports formats requiring UTF-16/UTF-8 passphrase or metadata handling, especially Windows/Apple-adjacent encrypted volume formats.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/crypto_backend/utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/fvault2/fvault2.c -->
# File Research: sources/block-storage/cryptsetup/lib/fvault2/fvault2.c

Implements FileVault2/CoreStorage-compatible metadata reading, volume-key derivation, dumping, and activation.

Key points:
- Defines packed CoreStorage structures for the volume header, metadata block headers, XML-bearing metadata block types, volume group descriptor, passphrase-wrapped KEK, and KEK-wrapped volume key.
- `_check_crc()` validates CoreStorage CRC32C checksums with required seed `0xffffffff`.
- `_unwrap_key()` implements AES key unwrap for 128-bit KEKs and wrapped keys using AES-ECB decrypt, validating the `0xA6...A6` integrity value.
- `_search_xml()` uses regex over XML plist strings to extract keyed values.
- Metadata block `0x0019` parser extracts PBKDF2 salt/iteration count, wrapped KEK, and wrapped volume key from base64 XML data.
- Metadata block `0x001A` parser extracts logical volume size and family UUID.
- Metadata block `0x0305` parser extracts logical volume block offset.
- `_read_volume_header()` reads and validates the physical volume header, CoreStorage magic, version, AES key size, and builds the encrypted-metadata XTS key from header key data plus physical-volume UUID.
- `_read_disklabel()` finds encrypted metadata block offset/count through the disk label metadata block and volume group descriptor.
- `_read_encrypted_metadata()` decrypts encrypted metadata blocks with AES-XTS, validates CRCs, and requires all three relevant metadata types.
- `FVAULT2_read_metadata()` orchestrates header, disk label, and encrypted metadata reads, then fixes cipher parameters to `aes` and `xts-plain64`.
- `FVAULT2_get_volume_key()` derives a passphrase key with PBKDF2-HMAC-SHA256, unwraps KEK and volume key, then derives the second XTS half by SHA256(volume-key-half || family-uuid).
- Activation builds a dm-crypt target over the logical volume offset/size with the derived AES-XTS key.
- Sensitive temporary keys use safe allocation/free where relevant.

Storage relevance:
- Adds read/activate support for FileVault2 volumes within cryptsetup’s block-storage toolchain.
- Relies on crypto backend PBKDF2, hash, and AES ECB/XTS support.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/fvault2/fvault2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/fvault2/fvault2.h -->
# File Research: sources/block-storage/cryptsetup/lib/fvault2/fvault2.h

Declares the FileVault2 public-internal interface.

Key points:
- Defines fixed sizes for wrapped keys, PBKDF2 salt, and UUID strings.
- `struct fvault2_params` stores cipher/mode, key size, PBKDF2 parameters, wrapped KEK/VK material, UUIDs, logical volume offset, and logical volume size.
- Declares metadata read, volume-key derivation, dump, activation by volume key, and volume-key-size helper functions.

Storage relevance:
- This header is the contract between FileVault2 format handling and generic cryptsetup activation/keyslot code.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/fvault2/fvault2.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/integrity/integrity.c -->
# File Research: sources/block-storage/cryptsetup/lib/integrity/integrity.c

Implements dm-integrity metadata handling, activation, tag/key sizing, and formatting helper flows.

Key points:
- LUKS2 integrity metadata is read from the data device even for detached headers; other types use metadata device.
- `INTEGRITY_read_superblock()` reads dm-integrity superblock, checks magic/version, converts endian fields, and validates sector-size shift.
- `INTEGRITY_read_sb()`, `INTEGRITY_dump()`, and `INTEGRITY_data_sectors()` expose parsed superblock fields.
- `INTEGRITY_key_size()` maps supported integrity algorithms to required key sizes, with required-size validation.
- `INTEGRITY_hash_tag_size()` infers tag size from CRC/xxhash constants or crypt backend hash size for hash/HMAC/phmac names.
- `INTEGRITY_tag_size()` combines random-IV tag overhead and authentication tag overhead for AEAD/HMAC/PHMAC/Poly1305/CMAC cases.
- `INTEGRITY_create_dmd_device()` constructs a `crypt_dm_active_device` with flags adjusted from superblock flags and calls `dm_integrity_target_set()`.
- `INTEGRITY_activate_dmd_device()` validates target shape, creates/reloads the device, and reports unsupported kernel features such as dm-integrity, fixed padding, secure recalc, or inline mode.
- `INTEGRITY_activate()` supports refresh mode by querying existing keys/params and reusing them when new ones are omitted.
- `_create_reduced_device()` builds a temporary dm-linear reduced mapping for formatting a bounded backing size.
- `INTEGRITY_format()` creates a temporary private dm-integrity device to format metadata, handles inline mode, optional reduced device, exclusive device checks, and reloads superblock flags afterward.

Storage relevance:
- Bridges cryptsetup format/activation flows to the kernel dm-integrity target.
- Critical for authenticated encryption, standalone integrity devices, LUKS2 integrity segments, and inline integrity support.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/integrity/integrity.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/integrity/integrity.h -->
# File Research: sources/block-storage/cryptsetup/lib/integrity/integrity.h

Defines dm-integrity superblock layout, flags, and helper prototypes.

Key points:
- Superblock magic is `"integrt"` and supported versions are 1 through 6.
- Flags describe journal MAC, recalculation, dirty bitmap, fixed padding, fixed HMAC, and inline mode.
- Packed `struct superblock` matches kernel dm-integrity on-disk metadata, including tag size, journal sections, data sectors, flags, sector/block log fields, recalc sector, and salt.
- Declares superblock read/dump/data-sector helpers, key/tag-size helpers, format, activation, dmd creation, and dmd activation.

Storage relevance:
- Internal ABI between cryptsetup integrity code and the on-disk/kernel dm-integrity metadata format.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/integrity/integrity.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/internal.h -->
# File Research: sources/block-storage/cryptsetup/lib/internal.h

Central internal header for libcryptsetup shared types, helper declarations, logging macros, device APIs, volume-key APIs, and internal utility contracts.

Key points:
- Pulls in core utility headers, crypto backend API, public libcryptsetup API, macros, and symbol versioning.
- Declares volume-key lifecycle, key descriptions, kernel keyring upload/drop, linked volume-key lists, and key state helpers.
- Declares PBKDF setup, verification, benchmarking, cipher spec retrieval, and memory adjustment helpers.
- Declares device allocation/open/check/size/topology/block-adjust/locking functions and metadata/data device accessors.
- Declares dm-device creation/reload helpers and integrity-aware creation.
- Defines logging macros around `crypt_logf()`.
- Declares random source initialization/use/cleanup.
- Declares plain-mode activation/hash helpers, LUKS2 reencryption accessors, wipe helpers, keyring helpers, and serialization locks.
- Provides `uint64_mult_overflow()` used by FileVault2 offset calculations.
- Defines key verification constants and exposes `crypt_check_cipher()`.

Storage relevance:
- This is the common dependency surface for FileVault2, integrity, keyslot context, and crypto-adjacent code.
- The file does not implement behavior, but it defines the internal coupling points for block devices, dm targets, key material, and crypto.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/keyslot_context.c -->
# File Research: sources/block-storage/cryptsetup/lib/keyslot_context.c

Implements keyslot context creation, dispatch, lazy secret loading, and exported ABI wrappers.

Key points:
- Context types include passphrase, keyfile, token, raw volume key, signed key, passphrase keyring, and volume-key keyring.
- Per-context function pointers dispatch to LUKS2 segment key open, LUKS1 volume key open, plain/integrity direct keys, BitLocker, FileVault2, verity signed keys, and passphrase retrieval.
- Passphrase context directly supplies passphrase bytes and can unlock LUKS1/LUKS2/BitLocker/FileVault2.
- Keyfile context lazily reads the keyfile into `i_passphrase` through `crypt_keyfile_device_read()` and then uses passphrase unlock paths.
- Token context calls LUKS2 token unlock for volume keys or passphrases, caches returned passphrase, and updates token id.
- Keyring passphrase context lazily retrieves passphrase bytes from the user keyring by description.
- Raw key context returns allocated `volume_key` objects and supports LUKS, plain, BitLocker, FileVault2, verity-without-signature, and integrity paths.
- Signed-key context returns separate volume key and signature keys for verity.
- Volume-key keyring context fetches a safe-allocated volume key by key description and can cache key size.
- `crypt_keyslot_context_init_common()` initializes version, error, and cached passphrase state.
- New exported constructors create self-contained contexts that copy secret/path/description inputs; old symbol versions preserve v1 pointer-lifetime behavior.
- `crypt_keyslot_context_set_pin()` replaces token PIN, safe-copying when context is self-contained.
- `crypt_keyslot_context_destroy_internal()` invokes type-specific cleanup and securely frees cached passphrases.
- `keyslot_context_type_string()` maps context type constants to readable names.

Storage relevance:
- This is the central unlock abstraction connecting user-provided credentials to LUKS, BitLocker, FileVault2, verity, plain, and integrity volume-key acquisition.
- Its ABI-versioned self-contained behavior matters for safe lifetime management of passphrases, PINs, and volume keys.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/keyslot_context.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/keyslot_context.h -->
# File Research: sources/block-storage/cryptsetup/lib/keyslot_context.h

Declares the internal keyslot context dispatch structure and initializer functions.

Key points:
- Defines function-pointer types for LUKS2 key retrieval, LUKS1/LUKS2 volume-key retrieval, generic volume keys, BitLocker, FileVault2, signed verity keys, passphrase retrieval, context cleanup, and key-size queries.
- Defines context version constants: basic pointer-lifetime v1 and self-contained v2.
- `struct crypt_keyslot_context` stores type, version, per-type union payload, last error, cached passphrase, and dispatch function table.
- Union payloads cover passphrase, keyfile, token, raw volume key, signed key, passphrase keyring, and volume-key keyring state.
- Declares internal initializers for key, signed key, passphrase, keyfile, token, and keyring contexts plus destroy and type-string helpers.

Storage relevance:
- Header-level contract for the credential abstraction used by setup, activation, and format-specific unlock paths.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/keyslot_context.h -->