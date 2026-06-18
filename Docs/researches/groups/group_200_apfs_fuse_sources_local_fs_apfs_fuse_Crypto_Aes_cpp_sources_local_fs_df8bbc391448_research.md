# Group Research: group_200_apfs_fuse_sources_local_fs_apfs_fuse_Crypto_Aes_cpp_sources_local_fs_df8bbc391448

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Aes.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Aes.cpp

## Role

`Aes.cpp` implements the `AES` class declared in `Aes.h`. It is a standalone, table-driven software AES implementation used by APFS encryption and wrapper crypto code in this source tree.

## Core Behavior

- Defines AES encryption tables `Te0` through `Te4`, decryption tables `Td0` through `Td4`, round constants `rcon`, and a zero IV buffer.
- Initializes AES state to AES-128 defaults in the constructor: `Nb = 4`, `Nk = 4`, `Nr = 10`, zero round keys, zero IV, and `_tp = 0`.
- `CleanUp()` zeros the IV, encryption round keys, decryption round keys, and CFB/OFB byte counter.
- `SetKey()` supports AES-128, AES-192, and AES-256 by selecting `Nk` and `Nr`, expanding `_erk`, deriving reversed/inverse `_drk`, and resetting the IV to zero.
- `Encrypt()` and `Decrypt()` operate on exactly one 16-byte block using the precomputed round keys and T tables.
- `EncryptCBC()` and `DecryptCBC()` process 16-byte blocks and mutate `_iv` to the last ciphertext block.
- `EncryptCFB()`, `DecryptCFB()`, and `CryptOFB()` are byte-stream modes that mutate both `_iv` and `_tp`.

## Important Dependencies

- Implements the interface in `Crypto/Aes.h`.
- Used by `Crypto/AesXts.cpp` and `Crypto/Crypto.cpp`.
- Indirectly supports APFS volume encryption through `ApfsLib/ApfsVolume` and key-management code.

## Notable Limitations And Risk Areas

- This is table-based AES with key-dependent memory accesses, so it is not constant-time.
- Public methods do not validate null pointers or buffer sizes.
- CBC callers must provide a byte count that is a multiple of 16; the implementation does not enforce that and will read/write past the requested logical end otherwise.
- `SetKey()` resets the IV, and all chaining modes mutate object state; callers must reset IVs explicitly when reusing an instance.
- `CleanUp()` uses ordinary `std::fill_n`; compilers may optimize sensitive-memory clearing in some contexts.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Aes.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Aes.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Aes.h

## Role

`Aes.h` declares the repository's standalone AES class. It exposes block AES plus ECB-style single-block calls and CBC, CFB, and OFB stateful modes.

## Public Interface

- `Mode` selects key size: `AES_128`, `AES_192`, or `AES_256`.
- `CleanUp()` clears stored key material and IV state.
- `SetKey()` installs a key and resets the IV to zero.
- `SetIV()` installs an IV or a zero vector.
- `Encrypt()` and `Decrypt()` process a single 16-byte block.
- `EncryptCBC()` and `DecryptCBC()` process block-aligned buffers.
- `EncryptCFB()`, `DecryptCFB()`, and `CryptOFB()` process arbitrary byte counts with internal stream position state.

## Internal State

- `_erk[60]` and `_drk[60]` hold expanded round keys for AES-256 maximum schedule size.
- `_iv[16]` stores current chaining-mode state.
- `_tp` stores CFB/OFB byte position.
- `Nk`, `Nr`, and `Nb` store AES mode parameters.
- Static table declarations back the T-table implementation in `Aes.cpp`.

## Notable Limitations And Risk Areas

- The header documents block-size constraints but the class does not encode them in types.
- The class is mutable and not thread-safe if one instance is shared across operations.
- The API does not distinguish one-shot from streaming use, so callers must manage IV lifecycle carefully.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Aes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/AesXts.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/AesXts.cpp

## Role

`AesXts.cpp` implements AES-XTS-style sector/unit encryption using two AES-128 keys. It is the data-encryption primitive used by APFS volume handling.

## Core Behavior

- `CleanUp()` clears both embedded AES instances.
- `SetKey()` installs `key1` into the data AES instance and `key2` into the tweak AES instance, both as AES-128.
- `Encrypt()` builds the initial tweak from little-endian `unit_no || 0`, encrypts it with key2, then loops over 16-byte blocks:
  - XOR plaintext with tweak.
  - AES-encrypt with key1.
  - XOR with tweak to produce ciphertext.
  - Multiply tweak by `x` in GF(2^128).
- `Decrypt()` mirrors the same tweak flow but AES-decrypts the middle block.
- `MultiplyTweak()` handles little-endian and big-endian hosts separately using APFS endian helpers.

## Important Dependencies

- Depends on `Crypto/Aes.h`.
- Uses `ApfsLib/Endian.h` for host/little-endian conversions.
- Referenced by `ApfsLib/ApfsVolume` and APFS dump tooling.

## Notable Limitations And Risk Areas

- Only AES-128 XTS keys are supported by `SetKey()`.
- There is no ciphertext stealing support; `size` must be a multiple of 16.
- The function loops in 16-byte increments without validating `size`, so non-block-aligned input can overread/overwrite.
- `Xor128()` casts arbitrary pointers to `uint64_t *`, which can be unaligned and can violate strict-aliasing assumptions on some platforms.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/AesXts.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/AesXts.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/AesXts.h

## Role

`AesXts.h` declares the `AesXts` wrapper class around two `AES` instances for XTS-mode block encryption.

## Public Interface

- `CleanUp()` clears both AES contexts.
- `SetKey(key1, key2)` installs the data and tweak keys.
- `Encrypt(cipher, plain, size, unit_no)` encrypts a data unit.
- `Decrypt(plain, cipher, size, unit_no)` decrypts a data unit.

## Internal State

- `m_aes_1` performs data-block encryption/decryption.
- `m_aes_2` encrypts unit numbers into initial tweaks.
- Private helpers perform 128-bit XOR and tweak multiplication.

## Notable Limitations And Risk Areas

- The header does not document that sizes must be 16-byte aligned.
- The class is state-light after key setup, but not explicitly thread-safe because the embedded AES objects are mutable.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/AesXts.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Asn1Der.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Asn1Der.cpp

## Role

`Asn1Der.cpp` implements a small ASN.1 DER decoder and debug dumper used by APFS key-management parsing.

## Core Behavior

- `der_decode_tag()` parses short-form and high-tag-number DER tags, preserving class/constructed bits in a packed `uint64_t`.
- `der_decode_len()` parses short and long-form definite lengths.
- `der_decode_tl()` validates an expected tag, returns the body pointer, and checks body bounds.
- `der_decode_constructed_tl()` and `der_decode_sequence_tl()` return constructed body ranges.
- `der_decode_uint()` reads a fixed-width big-endian unsigned integer into `uint64_t`.
- `der_decode_uint64()` decodes a tagged integer-like value up to 8 bytes.
- `der_decode_octet_string_copy()` validates exact length and copies the payload.
- `der_dump()` recursively prints parsed TLV records and hex payloads for debugging.

## Important Dependencies

- Implements declarations from `Crypto/Asn1Der.h`.
- Used by `ApfsLib/KeyMgmt.cpp` for APFS wrapped-key and HMAC metadata parsing.

## Notable Limitations And Risk Areas

- Length parsing uses pointer arithmetic such as `der + nb` and `der + len`; malformed huge lengths can be risky in general C++ pointer arithmetic even though bounds checks follow.
- DER canonical constraints are not fully enforced: minimal length encoding, indefinite-length rejection semantics, integer sign/canonical form, and high-tag minimal form are not deeply validated.
- `der_decode_len()` rejects `(der + nb) >= der_end`, which also rejects a long-form length field ending exactly at `der_end`; that is conservative but slightly stricter than pure byte availability.
- `der_dump()` prints to stdout and should remain debug-only.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Asn1Der.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Asn1Der.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Asn1Der.h

## Role

`Asn1Der.h` declares the small DER parsing interface and tag constants used by APFS crypto/key-management code.

## Public Interface

- Defines `der_tag_t` as `uint64_t`.
- Defines high-bit tag flags for constructed and context-specific encodings.
- Enumerates universal ASN.1 tag numbers for common primitive and string types.
- Declares helpers for tag, length, tag-length, constructed body, sequence body, integer, uint64, octet-string-copy decoding, plus `der_dump()`.

## Encoding Model

The code packs ASN.1 class and constructed bits into high bits of `der_tag_t`, with low bits carrying the tag number. This lets call sites compare expected context-specific tags as constants such as `0x8000000000000001U`.

## Notable Limitations And Risk Areas

- The API is pointer-range based and returns `nullptr` on parse failure, so callers must check every step.
- It exposes low-level DER mechanics rather than a structured ASN.1 object model.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Asn1Der.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Crypto.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Crypto.cpp

## Role

`Crypto.cpp` provides higher-level crypto primitives built from the local AES, SHA-1, and SHA-256 implementations: RFC 3394 AES key wrap/unwrap, HMAC-SHA1, HMAC-SHA256, and PBKDF2-HMAC-SHA1/SHA256.

## Core Behavior

- `Rfc3394_KeyWrap()` wraps `size / 8` 64-bit plaintext blocks with six AES rounds and writes `A || R[1..n]`.
- `Rfc3394_KeyUnwrap()` reverses that process, optionally returns the recovered IV, and reports success only when the IV equals the RFC 3394 default `0xA6...A6`.
- `HMAC_SHA1()` and `HMAC_SHA256()` implement standard HMAC block-key normalization, inner hash, outer hash, and digest output.
- `PBKDF2_HMAC_SHA1()` and `PBKDF2_HMAC_SHA256()` derive up to one or two digest-sized blocks depending on requested length, appending big-endian block indices to the salt.

## Important Dependencies

- Uses `Crypto/Aes.h`, `Crypto/Sha1.h`, `Crypto/Sha256.h`, and `ApfsLib/Endian.h`.
- Used by APFS key-management code and encrypted disk-image handling.

## Notable Limitations And Risk Areas

- RFC 3394 code stores `r[6]`, so it only supports up to six 64-bit input blocks; callers must keep `size <= 48` bytes.
- RFC 3394 functions assume 64-bit aligned buffers through `reinterpret_cast<uint64_t *>`.
- Comments explicitly say the key-wrap code is not tested on big-endian machines.
- PBKDF2 functions rely on `assert()` for salt and derived-key size limits; those checks disappear in release builds.
- `PBKDF2_HMAC_SHA1()` permits salt up to `0x20` and derived key up to `0x20`; `PBKDF2_HMAC_SHA256()` permits salt up to `0x10` and derived key up to `0x20`.
- HMAC clears the temporary digest but does not clear `kdata`.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Crypto.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Crypto.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Crypto.h

## Role

`Crypto.h` declares the repository's higher-level crypto utility functions.

## Public Interface

- `Rfc3394_KeyWrap()` wraps key material using AES and a caller-supplied IV.
- `Rfc3394_KeyUnwrap()` unwraps key material, returns plaintext, optionally returns the recovered IV, and validates the default wrap IV.
- `HMAC_SHA1()` and `HMAC_SHA256()` compute message authentication codes.
- `PBKDF2_HMAC_SHA1()` and `PBKDF2_HMAC_SHA256()` derive key bytes from password/salt/iteration inputs.

## Important Dependencies

- Includes `Crypto/Aes.h` for AES mode selection in RFC 3394 wrappers.

## Notable Limitations And Risk Areas

- The header does not express maximum supported sizes for RFC 3394 or PBKDF2 buffers.
- All functions are raw-pointer APIs and rely on callers to provide valid, sufficiently sized buffers.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Des.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Des.cpp

## Role

`Des.cpp` implements single-DES encryption/decryption and CBC mode. It is used as the base primitive for `TripleDES` and encrypted disk-image support.

## Core Behavior

- Constructor and destructor zero the key schedule and IV.
- `SetKey()` converts the 8-byte key to a 64-bit value, clears existing state, and computes 16 DES subkeys.
- `SetIV()` sets or clears the 64-bit CBC IV.
- `Encrypt()` and `Decrypt()` process 8-byte ECB blocks.
- `EncryptCBC()` XORs each plaintext block with the IV, encrypts it, and updates the IV to the ciphertext.
- `DecryptCBC()` preserves each ciphertext block as next IV, decrypts, then XORs with previous IV.
- Static helpers implement DES initial/final permutations, expansion, S-box substitution, P permutation, PC-1/PC-2 key scheduling, Feistel rounds, and big-endian byte conversion.

## Important Dependencies

- Implements `Crypto/Des.h`.
- `TripleDes.cpp` accesses private internals through friendship.
- Used by `ApfsLib/DiskImageFile.cpp` for legacy encrypted image handling.

## Notable Limitations And Risk Areas

- DES is cryptographically obsolete; this is compatibility code.
- ECB/CBC loops require `size` to be a multiple of 8 and do not validate it.
- No input/output pointer validation is performed.
- CBC methods mutate IV state, so repeated calls continue a stream unless callers reset the IV.
- Destructor clears key schedule with ordinary `memset`, which may not be guaranteed secure wiping.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Des.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Des.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Des.h

## Role

`Des.h` declares the single-DES class and private DES primitive helpers.

## Public Interface

- `Encrypt()` and `Decrypt()` process block buffers.
- `EncryptCBC()` and `DecryptCBC()` process CBC buffers.
- `SetKey()` installs an 8-byte DES key.
- `SetIV()` installs or clears an 8-byte IV.

## Internal State

- `m_keySchedule[16]` stores the 16 DES subkeys.
- `m_initVector` stores CBC state.
- Static permutation, expansion, S-box, key-schedule, and byte-conversion helpers implement the algorithm.
- `TripleDES` is a friend so it can reuse the DES internals directly.

## Notable Limitations And Risk Areas

- The public API does not document block-alignment requirements.
- Raw-pointer calls make buffer-size correctness entirely a caller responsibility.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Des.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha1.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Sha1.cpp

## Role

`Sha1.cpp` implements SHA-1 hashing for local HMAC/PBKDF2 and disk-image compatibility code.

## Core Behavior

- `Init()` sets the SHA-1 initial hash constants, clears the bit count and buffer index, and zeros the 64-byte buffer.
- `Update()` appends bytes to the block buffer, processes full 64-byte blocks with `Round()`, and increments the bit count.
- `Final()` appends SHA-1 padding, writes the 64-bit big-endian message length, processes the last block, and writes a 20-byte digest.
- `Round()` expands 16 message words to 80 and runs the four SHA-1 round families using `Ch`, `Parity`, and `Maj`.

## Important Dependencies

- Implements `Crypto/Sha1.h`.
- Used by `Crypto/Crypto.cpp` for HMAC-SHA1 and PBKDF2-HMAC-SHA1.
- Used by disk-image code for older encrypted image formats.

## Notable Limitations And Risk Areas

- SHA-1 is collision-broken and should only be used where compatibility requires it.
- `Final()` does not call `Init()` afterward, so object reuse requires an explicit `Init()`.
- No secure clearing is performed for internal buffers after finalization.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha1.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha1.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Sha1.h

## Role

`Sha1.h` declares the local SHA-1 streaming hash class.

## Public Interface

- `Init()` resets hash state.
- `Update(data, size)` absorbs bytes.
- `Final(hash)` writes a 20-byte digest.

## Internal State

- `m_buffer[64]` stores partial blocks.
- `m_hash[5]` stores the current SHA-1 chaining state.
- `m_bit_cnt` stores total input bits.
- `m_buf_idx` stores partial-buffer position.
- `m_K[4]` stores SHA-1 round constants.

## Notable Limitations And Risk Areas

- Digest output length is implicit; callers must provide at least 20 bytes.
- The class is mutable and not thread-safe if shared.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha1.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha256.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Sha256.cpp

## Role

`Sha256.cpp` implements SHA-256 hashing for APFS key management, HMAC, PBKDF2, and related crypto workflows.

## Core Behavior

- Defines SHA-256 round constants `m_k[64]`.
- Provides bitwise helpers for choice, majority, big sigma, and small sigma functions.
- `Init()` sets SHA-256 initial constants, clears the buffer pointer and byte count, and zeros the buffer.
- `Update()` buffers bytes and processes complete 64-byte blocks.
- `Round()` expands the 64-word schedule and runs the 64 compression rounds.
- `Final()` pads the message, writes a 64-bit big-endian length via high/low 32-bit parts, processes the final block, writes a 32-byte digest, and resets the object with `Init()`.

## Important Dependencies

- Implements `Crypto/Sha256.h`.
- Used by `Crypto/Crypto.cpp` and `ApfsLib/KeyMgmt.cpp`.

## Notable Limitations And Risk Areas

- Digest output length is implicit; callers must provide at least 32 bytes.
- The byte count is `size_t`; extremely large streams rely on host width and the manual high/low length split.
- Internal state is reset after `Final()`, unlike `Sha1`, so the two hash classes have different reuse semantics.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha256.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha256.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/Sha256.h

## Role

`Sha256.h` declares the local SHA-256 streaming hash class.

## Public Interface

- `Init()` resets the hash.
- `Update(data, size)` absorbs bytes.
- `Final(hash)` writes a 32-byte digest.

## Internal State

- `m_buffer[64]` stores partial input blocks.
- `m_hash[8]` stores the chaining state.
- `m_bufferPtr` stores partial-buffer position.
- `m_byteCnt` stores total input bytes.
- `m_k[64]` stores round constants.

## Notable Limitations And Risk Areas

- Output buffer size is not represented in the type.
- The class is mutable and should not be shared concurrently without external synchronization.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/Sha256.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/TripleDes.cpp -->
# File Research: sources/local-fs/apfs-fuse/Crypto/TripleDes.cpp

## Role

`TripleDes.cpp` implements 3-key EDE Triple-DES and CBC mode by reusing the private DES primitive helpers.

## Core Behavior

- Constructor and destructor zero the three DES key schedules and IV.
- `SetKey()` reads three 8-byte DES keys from a 24-byte buffer and builds one schedule per key.
- `Encrypt()` performs DES encrypt with key 1, DES decrypt with key 2, and DES encrypt with key 3 for each block.
- `Decrypt()` performs the inverse D-E-D flow.
- `EncryptCBC()` XORs with `m_iv`, applies EDE encryption, and updates `m_iv`.
- `DecryptCBC()` stores ciphertext as next IV, applies inverse EDE, XORs with prior IV, and updates state.
- `SetIV()` sets or clears the 64-bit IV.

## Important Dependencies

- Depends on `Crypto/Des.h` and `Crypto/TripleDes.h`.
- Used by `ApfsLib/DiskImageFile.cpp` for encrypted disk-image compatibility.

## Notable Limitations And Risk Areas

- 3DES is legacy crypto and should only be used for compatibility.
- All encryption/decryption sizes must be multiples of 8; this is not checked.
- `SetKey()` assumes a valid 24-byte key buffer.
- CBC mode mutates IV state across calls.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/TripleDes.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/TripleDes.h -->
# File Research: sources/local-fs/apfs-fuse/Crypto/TripleDes.h

## Role

`TripleDes.h` declares the 3-key Triple-DES class.

## Public Interface

- `Encrypt()` and `Decrypt()` process ECB-style block buffers.
- `EncryptCBC()` and `DecryptCBC()` process CBC buffers.
- `SetKey()` installs a 24-byte key.
- `SetIV()` installs or clears an 8-byte IV.

## Internal State

- `m_keySchedule[3][16]` stores three DES subkey schedules.
- `m_iv` stores CBC state.

## Notable Limitations And Risk Areas

- The API does not state required key length or 8-byte block alignment.
- Like DES, this is compatibility-oriented legacy crypto.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/Crypto/TripleDes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/apfs-fuse/apfsfuse/ApfsFuse.cpp -->
# File Research: sources/local-fs/apfs-fuse/apfsfuse/ApfsFuse.cpp

## Role

`ApfsFuse.cpp` is the main read-only FUSE frontend for `apfs-fuse`. It wires low-level FUSE callbacks to `ApfsLib` container, volume, directory, file, xattr, decompression, partition-map, and device abstractions.

## Global State And Configuration

- `ops` stores the low-level FUSE operation table.
- `g_disk_main` and `g_disk_tier2` hold primary and optional fusion-drive devices.
- `g_container` and `g_volume` hold the mounted APFS container and selected volume.
- `g_vol_id`, `g_xid`, and `g_snap_xid` select volume, checkpoint transaction, and snapshot.
- `g_uid`, `g_gid`, `g_set_uid`, and `g_set_gid` implement mount-time UID/GID override.
- `g_physblksize` controls sector size for partition parsing.
- `g_password` supplies an encrypted-volume passphrase.
- `FUSE_TIMEOUT` is set to one day for attribute and entry caching.

## FUSE Callback Behavior

- `apfs_getattr()` calls `apfs_stat_internal()` and replies with file attributes or `ENOENT`.
- `apfs_lookup()` resolves child names through `ApfsDir::LookupName()`, fills `fuse_entry_param`, and replies with entry metadata.
- `apfs_open()` rejects non-read-only opens, loads inode metadata, decompresses compressed files up front when needed, and stores a `File *` in `fi->fh`.
- `apfs_read()` reads uncompressed files through `ApfsDir::ReadFile()` using the inode private ID, or serves bytes from preloaded decompressed data.
- `apfs_opendir()` allocates a `Directory` handle.
- `apfs_readdir()` lazily builds a FUSE direntry buffer from `ApfsDir::ListDirectory()`.
- `apfs_readlink()` reads `com.apple.fs.symlink`.
- `apfs_getxattr()`/`apfs_getxattr_mac()` read named extended attributes; macOS also accepts a `position`.
- `apfs_listxattr()` lists attributes as NUL-separated names.
- `apfs_release()` and `apfs_releasedir()` delete per-handle state.
- `apfs_statfs()` reports block counts and free blocks from the APFS container.

## Metadata Mapping

`apfs_stat_internal()` maps APFS inode records into `struct stat`:

- Synthetic root parent inode `ROOT_DIR_PARENT` becomes inode 1, mode `0755`, directory, two links.
- APFS mode, owner, group, rdev, timestamps, and inode number are copied into platform-specific stat fields.
- UID/GID can be overridden globally from mount options.
- Regular file size is derived from uncompressed-size metadata, `com.apple.decmpfs`, resource fork size, data-stream size, or zero.
- Directory size is set from child/link count.

## Startup And Mount Flow

1. Initializes the FUSE operations table.
2. Sets default UID/GID from effective process credentials.
3. Parses command-line options: debug level, secondary fusion device, mount options, partition ID, volume ID, passphrase, container offset, and lax mode.
4. Requires exactly `<device> <dir>`.
5. Forces `ro` and sets `fsname` in FUSE mount options.
6. Parses `-o` options for `uid`, `gid`, `vol`, `blksize`, `pass`, `xid`, and `snap`.
7. Opens primary and optional secondary devices.
8. Applies physical block size override.
9. If no explicit offset is supplied, attempts GPT parsing to locate an APFS partition.
10. Constructs and initializes `ApfsContainer`.
11. Opens the selected APFS volume with passphrase and snapshot options.
12. Creates a FUSE 2 or FUSE 3 low-level session, daemonizes when debug is disabled, runs the session loop, unmounts, destroys the session, frees FUSE args, closes devices, and deletes APFS objects.

## Important Dependencies

- FUSE 2 or FUSE 3 low-level APIs.
- `ApfsLib/ApfsContainer`, `ApfsVolume`, `ApfsDir`, `Decmpfs`, `DeviceLinux`, `DeviceMac`, and `GptPartitionMap`.
- Platform stat timestamp fields differ for Linux and macOS.

## Notable Limitations And Risk Areas

- The filesystem is intentionally read-only; write opens return `EACCES` and no mutation callbacks are registered.
- Most state is process-global, which is simple for one mount but makes multi-mount-in-process use impractical.
- `apfs_lookup()` calls `fuse_reply_entry()` even if `apfs_stat_internal()` fails after name lookup; that can return partially initialized attributes.
- `apfs_read()` ignores the success/failure result of `ReadFile()` for uncompressed files and replies with a zero-filled buffer on failed or short reads.
- Compressed files are decompressed at open time into memory, which can be expensive for large files.
- `apfs_getxattr_mac()` replies with `min(data.size(), size)` from `data + position` without bounding `position` against `data.size()`.
- GPT partition selection reuses `partition_id` for the secondary device, so explicit primary partition state can affect secondary probing flow.
- Cleanup paths after some early errors do not always close/delete every object already opened, especially secondary-device paths.
<!-- END FILE RESEARCH: sources/local-fs/apfs-fuse/apfsfuse/ApfsFuse.cpp -->