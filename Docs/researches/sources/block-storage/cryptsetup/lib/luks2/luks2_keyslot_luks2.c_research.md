# File Research: sources/block-storage/cryptsetup/lib/luks2/luks2_keyslot_luks2.c

Concrete handler for normal `luks2` keyslots. It derives a keyslot encryption key from the passphrase, AF-splits/merges the volume key using the LUKS1 anti-forensic splitter, encrypts/decrypts the AF material in the binary keyslot area, manages keyslot JSON allocation/update, dumps user-visible keyslot details, validates type-specific metadata, and repairs stale KDF fields.

Key responsibilities:
- Encrypts keyslot material to storage through `crypt_storage_wrapper`, using dm-crypt when possible and disabling dm-crypt for non-root callers.
- Decrypts keyslot material from storage under a metadata-device read lock.
- Parses KDF parameters from keyslot JSON for PBKDF2, Argon2i, and Argon2id, including base64 salt decoding and strict 32-byte salt length checking.
- Stores a keyslot by deriving the keyslot encryption key, AF-splitting the supplied volume key, wrapping the derived key into a `volume_key`, and encrypting the AF material to the configured area offset.
- Opens a keyslot by deriving the same keyslot key, decrypting AF material, and AF-merging it back into the volume key buffer.
- Serializes memory-hard KDF unlocks with `crypt_serialize_lock()` when the configured memory cost exceeds 32 MiB.
- Updates keyslot JSON by setting raw-area encryption/key size, benchmarking and writing current PBKDF settings, generating a fresh salt, and setting the AF hash.
- Allocates new keyslot JSON with `type = luks2`, volume key size, LUKS1 AF object, raw area object, and a free binary area found by `LUKS2_find_area_gap()`.
- Opens, stores, updates, wipes, dumps, validates, and repairs through the exported `luks2_keyslot` handler table.
- On wipe, removes references to the deleted keyslot from digests and tokens.
- Validates that `kdf`, `af`, and `area` subobjects have the expected type-specific fields and that KDF objects contain only the required fields for their type.
- Repairs historical KDF objects by deleting fields not valid for the current PBKDF2 or Argon2 type.

Important behavior:
- Salt is regenerated whenever keyslot JSON is updated, so updating PBKDF or area encryption parameters invalidates the old passphrase-derived wrapping key until key material is stored again.
- The stored `key_size` must match the supplied volume key length when writing, preventing accidental volume-key size mutation after allocation.
- Null keyslot encryption only allows an empty passphrase on open.
- `luks2_keyslot_store()` takes the LUKS2 device write lock, writes encrypted keyslot material first, then writes metadata.
- New allocation checks the JSON still fits in the metadata area after adding the keyslot object and removes the keyslot JSON if the update fails.
- AF stripes are currently fixed through `LUKS_STRIPES` in the cryptographic operations even though the JSON stores a stripes value and validation requires it.
- The dump path prints cipher, cipher key size, PBKDF settings, salt, AF stripes/hash, and binary area offset/length.

Dependencies:
- Depends on `luks2_internal.h` for header access, area finding, JSON helpers, device locking, metadata writes, digest/token assignment, and JSON size checks.
- Depends on `utils_storage_wrappers.h` and crypt storage wrappers for encrypted keyslot area I/O.
- Uses the LUKS1 AF splitter implementation from `../luks1/af.h`.
- Uses cryptsetup PBKDF, random, base64, hash-size, safe allocation, safe free, and volume-key APIs.
- Uses metadata-device read/write locks and block storage wrapper I/O.

Notable risks:
- The code has a `FIXME` around verifying key size against AF encrypted-key size, so key-size/AF-size assumptions are partly implicit.
- Keyslot JSON update benchmarks PBKDF using current crypt device settings; errors there abort allocation/update before key material is written.
- The validation function checks required shape but does not fully verify every numeric range or cryptographic algorithm availability; later open/store paths catch unavailable hash/cipher cases.
- The secure sequencing of encrypted material write and metadata write is sensitive: a failure between them can leave stale or unusable keyslot contents, so callers rely on higher-level recovery and validation.
