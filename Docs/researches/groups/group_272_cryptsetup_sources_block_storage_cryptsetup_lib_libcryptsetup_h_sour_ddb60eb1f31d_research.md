# Group Research: group_272_cryptsetup_sources_block_storage_cryptsetup_lib_libcryptsetup_h_sour_ddb60eb1f31d

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/cryptsetup`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup.h -->
# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup.h

This is the public libcryptsetup API header. It defines the opaque `struct crypt_device` handle, keyslot context handle, public constants, public parameter structs, enums, callbacks, and exported function prototypes for cryptsetup users.

Major API areas:
- Context lifecycle: `crypt_init`, `crypt_init_data_device`, `crypt_init_by_name(_and_header)`, `crypt_free`.
- Logging and confirmation callbacks: `crypt_set_log_callback`, `crypt_log`, `crypt_logf`, `crypt_set_confirm_callback`.
- Global/device settings: RNG selection, PBKDF configuration, metadata locking, LUKS2 metadata/keyslot area sizing, compatibility flags.
- Format types: `CRYPT_PLAIN`, `CRYPT_LUKS1`, `CRYPT_LUKS2`, `CRYPT_LOOPAES`, `CRYPT_VERITY`, `CRYPT_TCRYPT`, `CRYPT_INTEGRITY`, `CRYPT_BITLK`, `CRYPT_FVAULT2`.
- Format parameter structs for plain, LUKS1, LUKS2, loop-AES, dm-verity, TCRYPT, dm-integrity, OPAL hardware encryption, and reencryption.
- Device actions: format, load, repair, resize, suspend/resume, conversion, UUID/label changes, header backup/restore, wipe, OPAL wipe.
- Keyslot management: add/change/destroy keyslots via passphrase, keyfile, volume key, keyslot context, signed key, keyring, token, and volume-key keyring paths.
- Activation/deactivation: passphrase, keyfile, volume key, signed key, kernel keyring, LUKS2 tokens, and keyslot-context activation.
- Runtime status/query: active device info, integrity failure count, crypt status, hardware encryption status, cipher/mode/UUID/device offsets, verity/integrity info, keyslot status/priority/encryption/PBKDF.
- LUKS2 tokens: JSON token access, keyring-token helpers, assignment APIs, internal/external token handler ABI, token handler function pointer types, external-token path controls.
- LUKS2 reencryption: initialization by passphrase/keyring/keyslot context, run/resume/recovery semantics, reencryption status and resilience parameters.
- Safe memory helpers: `crypt_safe_alloc`, `crypt_safe_free`, `crypt_safe_realloc`, `crypt_safe_memzero`, `crypt_safe_memcpy`.
- Kernel keyring linking for volume keys, including old/new keys during reencryption.

Filesystem/block-storage relevance:
- This header is the library contract for constructing and managing dm-crypt, dm-verity, dm-integrity, loop-AES-compatible, LUKS, BitLocker, FileVault2, and OPAL-backed block mappings.
- Activation flags encode block-device behavior: read-only mappings, shared access, discard/TRIM, dm-crypt workqueue/performance options, dm-verity corruption policy, dm-integrity journal/bitmap/recalculate/inline modes, large-sector IV handling, keyring-backed keys, private udev behavior, and suspended-state reporting.
- Struct fields expose storage geometry and layout decisions: offsets, sector sizes, metadata areas, keyslot areas, hash/FEC offsets, integrity tag sizes, OPAL segments, reencryption data shifts/hot zones.

Important notes:
- This file contains declarations and API documentation only; implementation lives elsewhere.
- Several legacy compatibility APIs remain exposed, including deprecated memory locking, iteration-time PBKDF setting, old keyfile offset wrappers, and deprecated `crypt_reencrypt`.
- Many APIs return negative errno values; several token and activation APIs document precise `-ENOENT`, `-EPERM`, `-ENOANO`, `-EAGAIN`, and `-ESRCH` semantics.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup.pc.in -->
# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup.pc.in

This is the pkg-config template for libcryptsetup.

It defines:
- `prefix`, `exec_prefix`, `libdir`, and `includedir` substitution variables.
- Package metadata: `Name: cryptsetup`, `Description: cryptsetup library`, `Version: @LIBCRYPTSETUP_VERSION@`.
- Compiler and linker flags: `Cflags: -I${includedir}`, `Libs: -L${libdir} -lcryptsetup`.
- Private dependencies through `Requires.private: @PKGMODULES@`.

Filesystem/block-storage relevance:
- This file controls how downstream consumers discover and link against libcryptsetup.
- It does not implement storage behavior, but it is part of the public integration surface for applications using cryptsetup’s block encryption/verity/integrity APIs.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup_macros.h -->
# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup_macros.h

This header defines common internal constants and generic macros for libcryptsetup.

Key macros:
- Casting/helper macros: `CONST_CAST`, `VOIDP_CAST`, `UNUSED`, `ARRAY_SIZE`, `BITFIELD_SIZE`.
- Ownership helpers: `MOVE_REF` transfers a pointer-like reference and nulls the source; `FREE_AND_NULL` frees and nulls.
- Utility expression: `AT_LEAST`.
- Sector/alignment constants: `SECTOR_SHIFT`, `SECTOR_SIZE`, `SHIFT_4K`, `MAX_SECTOR_SIZE`, `ROUND_SECTOR`.
- Alignment checks: `MISALIGNED`, `MISALIGNED_4K`, `MISALIGNED_512`, `NOTPOW2`.
- Default alignment constants: `DEFAULT_DISK_ALIGNMENT` and `DEFAULT_MEM_ALIGNMENT`.
- Device-mapper naming constants: `DM_UUID_LEN`, `DM_NAME_LEN`, `DM_BY_ID_PREFIX`, `DM_UUID_PREFIX`, and matching prefix lengths.
- OPAL constant: `OPAL_PSID_LEN`.
- LUKS constants: `LUKS_STRIPES` defaults to 4000; `LUKS2_OBJECTS_MAX` defaults to 32.

Filesystem/block-storage relevance:
- Sector and alignment macros are used across cryptsetup when validating block offsets, keyslot storage sizes, and device-mapper table geometry.
- DM UUID/name constants define the naming limits and prefixes used by active mapped block devices.
- `LUKS_STRIPES` is the fixed anti-forensic stripe count used by LUKS1 key material splitting.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup_macros.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup_symver.h -->
# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup_symver.h

This header provides helper macros for exporting multiple ABI versions of the same libcryptsetup public symbol.

Core behavior:
- If compiler attribute support exists, `_CRYPT_SYMVER` uses `__attribute__((__symver__(...)))`.
- Otherwise, for GCC/Clang, it falls back to inline assembler `.symver`.
- `_CRYPT_FUNC` creates local versioned implementation names like `__symbol_v2_5` and binds them to public `CRYPTSETUP_<major>.<minor>` symbol versions.
- `CRYPT_SYMBOL_EXPORT_OLD` exports an old compatible symbol version with single `@`.
- `CRYPT_SYMBOL_EXPORT_NEW` exports the default/latest symbol version with `@@`.
- If symbol versioning is unavailable, old versions become unused static inline definitions and the new version exports as the plain public symbol.

Filesystem/block-storage relevance:
- No direct storage logic is implemented here.
- It protects ABI compatibility for applications linked against older libcryptsetup versions, which is important because cryptsetup is used by system boot, initramfs, storage-management, and filesystem-stack tooling.

Important notes:
- The header explicitly warns not to use these macros for ordinary one-version public symbols.
- It is intended only for functions exported in multiple incompatible ABI versions simultaneously.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/libcryptsetup_symver.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/libdevmapper.c -->
# File Research: sources/block-storage/cryptsetup/lib/libdevmapper.c

This file is the libcryptsetup device-mapper backend. It translates cryptsetup’s internal target descriptions into Linux device-mapper tasks and parses active kernel dm tables back into cryptsetup structures.

Major responsibilities:
- Initializes and tears down libdevmapper logging/state via `dm_backend_init` and `dm_backend_exit`.
- Probes device-mapper ioctl and target versions with `_dm_check_versions`, then records feature flags for dm-crypt, dm-verity, dm-integrity, dm-zero, deferred remove, secure data, target-version probing, kernel keyring keys, sector-size support, discard support, FEC, verity signatures, workqueue options, high-priority dm-crypt, and integrity inline mode.
- Builds target parameter strings for:
  - dm-crypt: cipher/CAPI conversion, key or keyring-key string, IV offset, data device, data offset, discards, sector size, integrity tags, workqueue/performance options.
  - dm-verity: data/hash/FEC devices, block sizes, hash algorithm, root hash, salt, corruption policy, FEC options, root-hash signature key description.
  - dm-integrity: data/meta devices, tag size, journal/direct/recovery/bitmap/inline modes, journal sizing, sector size, integrity/MAC/encryption keys, discard/recalculate/fixup flags.
  - dm-linear and dm-zero.
- Creates, reloads, resumes, suspends, clears, removes, and force-removes DM devices.
- Handles udev synchronization cookies and private-device udev rule suppression.
- Uses forced deactivation by replacing busy mappings with read-only `error` targets when requested.
- Queries active mappings through `DM_DEVICE_TABLE` and `DM_DEVICE_STATUS`, parsing dm-crypt, dm-verity, dm-integrity, dm-linear, dm-error, and dm-zero target lines.
- Reports status for active/busy/suspended devices, verity validity and repaired block count, integrity failure count, dependency chains, active integrity helper mappings, and DM UUID/type comparisons.
- Provides target setter helpers: `dm_crypt_target_set`, `dm_verity_target_set`, `dm_integrity_target_set`, `dm_linear_target_set`, `dm_zero_target_set`.

Security-sensitive behavior:
- Uses `dm_task_secure_data` when available so libdevmapper treats table data as sensitive.
- Allocates DM target parameter strings and key material with `crypt_safe_alloc` and wipes/free them with `crypt_safe_free`.
- Wipes parsed dm-crypt key strings after query.
- Supports keyring-backed dm-crypt keys and converts key descriptions into dm-crypt table syntax.
- Refuses to return crypt keys from suspended devices.
- On suspend with key wipe, sends the `key wipe` dm-crypt target message, and can reinstate keys through `key set ...` target messages.

Filesystem/block-storage relevance:
- This is the operational bridge from libcryptsetup policy/metadata to live Linux block devices under `/dev/mapper`.
- It controls mapped-device geometry, read-only state, discard/TRIM behavior, dm-verity corruption handling, dm-integrity journaling/recovery, and stacked crypt+integrity relationships.
- Query paths reconstruct block mapping state so higher-level cryptsetup APIs can report or refresh active devices.

Important implementation details:
- libdevmapper is treated as not context-friendly; a global `_context` is switched around each DM call for logging.
- Version probing is cached globally with `_dm_*_checked` booleans and `_dm_flags`.
- `_dm_create_device` distinguishes existing devices, missing referenced devices, kernel key errors, and busy devices using both dm-task errno and follow-up status checks.
- `check_retry` silently drops unsupported optional dm-crypt flags for retry in some cases, but hard-errors for explicitly requested unsupported verity/integrity features.
- Active table parsers are strict: unknown target options generally return `-EINVAL`, which prevents silently accepting unrecognized kernel table state.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/libdevmapper.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/loopaes/loopaes.c -->
# File Research: sources/block-storage/cryptsetup/lib/loopaes/loopaes.c

This file implements loop-AES-compatible keyfile parsing and activation.

Key behavior:
- Selects default hash by output key size: 16 bytes -> `sha256`, 24 bytes -> `sha384`, 32 bytes -> `sha512`.
- Applies loop-AES tweak bytes based on key count: 64 keys uses `0x55`, 65 keys uses `0xF4`, otherwise `0x00`.
- Hashes each input key line into a fixed-size output key component, XORs the first byte with the tweak, concatenates all components, and wraps the result as a `volume_key`.
- Detects ASCII-armored GPG keyfiles by scanning the start of the buffer for `BEGIN PGP MESSAGE`; encrypted GPG keyfiles are rejected with a user hint to decrypt externally.
- Normalizes `\n` and `\r` to NUL, then parses one, 64, or 65 NUL-separated key entries. All parsed keys must have the same nonzero length and be terminated.
- Activates a loop-AES-compatible dm-crypt mapping:
  - One key uses `<base_cipher>-cbc-plain64` and requires plain64 support.
  - Multi-key mode uses `<base_cipher>:64-cbc-lmk` and requires LMK support.
  - Device size and flags are adjusted through `device_block_adjust`.
  - The DM target is created through `dm_crypt_target_set` and `dm_create_device`.

Filesystem/block-storage relevance:
- Provides compatibility for legacy loop-AES encrypted block devices.
- Activation produces a live dm-crypt block mapping using cryptsetup’s regular device-mapper backend.

Important notes:
- `LOOPAES_KEYS_MAX` is 65, matching accepted keyfile layouts.
- Unsupported kernel capabilities are reported as inability to support loop-AES-compatible mapping.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/loopaes/loopaes.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/loopaes/loopaes.h -->
# File Research: sources/block-storage/cryptsetup/lib/loopaes/loopaes.h

This header declares the loop-AES compatibility interface.

It defines:
- Forward declarations for `struct crypt_device` and `struct volume_key`.
- `LOOPAES_KEYS_MAX` as 65.
- `LOOPAES_parse_keyfile`, which parses keyfile data into a `volume_key`, optional hash override, and key count.
- `LOOPAES_activate`, which activates a loop-AES-compatible mapping from a base cipher, key count, volume key, and activation flags.

Filesystem/block-storage relevance:
- This is the private interface used by cryptsetup’s loop-AES format support to turn keyfile material into a dm-crypt block mapping.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/loopaes/loopaes.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/af.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks1/af.c

This file implements the LUKS1 anti-forensic splitter.

Core functions:
- `XORblock` XORs two byte buffers into a destination buffer.
- `hash_buf` hashes a big-endian block index IV followed by source data, producing a digest-sized or padding-sized output.
- `diffuse` spreads information across a block by hashing digest-sized chunks and a final partial chunk.
- `AF_split` expands one block of key material into `blocknumbers` stripes:
  - Generates random stripes for all but the last stripe.
  - XORs each random stripe into an accumulator.
  - Diffuses the accumulator after each random stripe.
  - Computes the final stripe as `src XOR accumulator`.
- `AF_merge` reverses the process:
  - Replays XOR+diffuse across all but the last stripe.
  - XORs the final stripe with the accumulator to recover the original block.
- `AF_split_sectors` computes the sector-rounded size of split data.

Filesystem/block-storage relevance:
- LUKS1 stores encrypted key material in anti-forensic stripes, so securely destroying enough stripe data destroys recoverability of the keyslot.
- The sector-rounded size is used for keyslot area layout on the metadata device.

Important notes:
- Temporary accumulator buffers use `crypt_safe_alloc` and `crypt_safe_free`.
- Hash failures propagate as negative errors.
- The code assumes caller supplies matching `blocksize`, `blocknumbers`, and hash for split and merge.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/af.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/af.h -->
# File Research: sources/block-storage/cryptsetup/lib/luks1/af.h

This header declares LUKS1 anti-forensic splitter and keyslot storage encryption helpers.

Declared APIs:
- `AF_split`: split one block of key material into anti-forensic stripes.
- `AF_merge`: recover original key material from stripes.
- `AF_split_sectors`: compute sector-rounded storage size for split data.
- `LUKS_encrypt_to_storage`: encrypt keyslot data to the metadata device.
- `LUKS_decrypt_from_storage`: decrypt keyslot data from the metadata device.

Filesystem/block-storage relevance:
- These functions are central to LUKS1 keyslot storage: anti-forensic striping plus encrypted reads/writes to sectors on the metadata device.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/af.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/keyencryption.c -->
# File Research: sources/block-storage/cryptsetup/lib/luks1/keyencryption.c

This file implements encrypted access to LUKS1 keyslot storage.

Core behavior:
- `_error_hint` logs actionable errors when dm-crypt or userspace crypto cannot use the requested cipher/mode/key size, including XTS key-size and cipher-spec format hints.
- `LUKS_endec_template` is the fallback path that creates a private temporary dm-crypt mapping named `temporary-cryptsetup-<pid>` over the metadata device:
  - Computes keyslot-aligned size from block size and `LUKS_ALIGN_KEYSLOTS`.
  - Uses `CRYPT_ACTIVATE_PRIVATE`, and read-only flag for decrypt.
  - Builds cipher spec from cipher and mode.
  - Adjusts block-device access and verifies write permissions.
  - Creates a dm-crypt target over the metadata device at the requested sector.
  - Opens the temporary mapper path with `O_DIRECT | O_SYNC`.
  - Invokes either blockwise read or write callback.
  - Removes the temporary mapping with forced deactivation.
- `LUKS_encrypt_to_storage`:
  - Requires sector-aligned input length.
  - First tries the userspace crypto wrapper through `crypt_storage_init` and `crypt_storage_encrypt`.
  - Falls back to temporary dm-crypt if the wrapper reports unsupported or missing cipher support.
  - Writes encrypted data to the metadata device with blockwise aligned IO and syncs the device.
- `LUKS_decrypt_from_storage`:
  - Requires sector-aligned destination length.
  - First tries userspace crypto.
  - Falls back to temporary dm-crypt on unsupported/missing cipher support.
  - Reads encrypted keyslot data from the metadata device, reports too-small devices where detectable, then decrypts in memory.

Filesystem/block-storage relevance:
- This code is the LUKS1 keyslot IO path for reading and writing encrypted key material on disk.
- It bridges filesystem-style aligned IO constraints, raw block-device sector offsets, and dm-crypt/userspace crypto mechanisms.

Important notes:
- Only whole 512-byte sector reads/writes are accepted.
- The temporary dm-crypt mapping is private and forcibly removed on cleanup.
- Device locking is respected through `device_is_locked` and `device_open_locked`.
- IO failures during keyslot encryption/decryption are normalized to `-EIO` with user-facing log messages.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/lib/luks1/keyencryption.c -->