# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_crypto.c

This file implements userland ZFS encryption support in libzfs: key material acquisition, validation, wrapping-key derivation, encryption-root creation checks, key load/unload, and key rewrap/change-key behavior.

Key model:
- User-provided keys decrypt dataset master encryption keys.
- Raw and hex keys map directly to the fixed wrapping-key length.
- Passphrases are converted to wrapping keys with PBKDF2-HMAC-SHA1 using dataset salt and iteration count.
- Salt is stored as a hidden property; PBKDF2 iteration count is stored as a property.

Constants:
- Minimum passphrase length: 8.
- Maximum passphrase length: 512.
- Interactive prompt attempts: 3.
- Wrapping key length comes from `WRAPPING_KEY_LEN`.

Keylocation parsing:
- `zfs_prop_parse_keylocation()` accepts:
  - `prompt`;
  - URI strings matching the libzfs URI regex.
- Supported URI schemes are registered in `uri_handlers`:
  - `file`
  - `https`
  - `http`

Key material input:
- `libzfs_getpassphrase()` prompts on stdin, disables terminal echo, catches SIGINT, ignores SIGTSTP while reading, restores terminal state, and rethrows interrupts.
- `get_key_interactive()` rejects raw key entry from a terminal, optionally confirms newly entered keys, and validates passphrase/hex format before confirmation.
- `get_key_material_raw()` reads non-raw keys with `getline()` and trims newline. For raw keys, it reads 33 bytes to detect keys longer than the required 32 bytes.
- `get_key_material_file()` reads from `file://` paths.
- `get_key_material_https()` fetches HTTP/HTTPS key material using either libfetch or libcurl, depending on build configuration. It can dynamically load libfetch/curl symbols. The curl path writes into an unnamed or unlinked temp file, follows redirects, applies a 30 second timeout, honors SSL env vars, and requires a 2xx response.
- `get_key_material()` dispatches prompt or URI fetching, validates the result, and reports whether interactive retry is possible.

Validation and derivation:
- `validate_key()` enforces exact raw/hex length, hex digits, and passphrase length on new-key verification.
- `hex_key_to_raw()` decodes a hex string into raw wrapping bytes.
- `derive_key()`:
  - copies raw keys;
  - decodes hex keys;
  - derives passphrase keys with `PKCS5_PBKDF2_HMAC_SHA1()`, little-endian salt, configured iterations, and `WRAPPING_KEY_LEN`.

Feature checks:
- `encryption_feature_is_enabled()` requires feature flags support and presence of the encryption feature in pool feature stats.
- `proplist_has_encryption_props()` detects encryption-related properties in a create property list.

Create-time encryption:
- `zfs_crypto_create()` validates encryption properties during dataset or pool-root creation.
- It handles parent dataset inheritance when a parent exists.
- For root dataset creation, it checks `feature@encryption` in pool properties because the feature may not be on disk yet.
- If encryption is off, any encryption-specific properties are rejected.
- If creating a new encryption root, `keyformat` is required.
- If `keyformat` is supplied without `keylocation`, keylocation defaults to `prompt`.
- It rejects `keylocation=prompt` when stdin is unavailable, such as receive streams using stdin.
- `populate_create_encryption_params_nvlists()` fetches key material, generates salt for passphrases, sets default PBKDF2 iterations if absent, rejects `pbkdf2iters` for non-passphrase keys, derives the wrapping key, and returns wrapping key bytes to the caller.
- `zfs_crypto_clone_check()` rejects encryption properties for clones because they must inherit from the origin dataset.

Encryption-root detection:
- `zfs_crypto_get_encryption_root()` returns false for unencrypted datasets, otherwise compares `ZFS_PROP_ENCRYPTION_ROOT` to the dataset name and optionally copies the encryption root name.

Loading keys:
- `zfs_crypto_load_key()` requires the encryption feature, encrypted dataset, and encryption-root target.
- It optionally accepts an alternate keylocation.
- It rejects loading an already loaded key unless `noop` is requested.
- For passphrases it reads existing salt and iterations from properties.
- It fetches and derives key material, then calls `lzc_load_key()`.
- Error mapping covers permission, invalid parameters, already loaded keys, busy datasets, incorrect keys, and unsupported suites.
- Interactive incorrect-key and other correctable failures can retry up to three attempts.
- `zfs_crypto_attempt_load_keys()` recursively attempts to load keys for all encryption roots below a filesystem/volume and prints success count. It is best effort, but returns failure if any attempted key load failed.

Unloading keys:
- `zfs_crypto_unload_key()` requires encryption feature, encrypted dataset, and encryption-root target.
- It rejects already unloaded keys.
- It calls `lzc_unload_key()` and maps permission, already unloaded, and busy errors.

Changing/rewrapping keys:
- `zfs_crypto_verify_rewrap_nvlist()` permits only `keyformat`, `keylocation`, `pbkdf2iters`, and user properties for normal change-key. With inherit-key mode, only user properties may be set.
- `zfs_crypto_rewrap()` implements both new-key and inherit-key paths:
  - requires encryption feature and encrypted dataset;
  - rejects clones because clone keys come from their origin;
  - validates raw properties through `zfs_valid_proplist()`;
  - for non-inherit mode, fills missing keyformat/keylocation from existing encryption-root props or requires them when promoting a non-root to a new encryption root;
  - fetches/derives new wrapping key data;
  - for inherit mode, requires current dataset to be an encryption root, requires encrypted parent, and requires parent key to be loaded;
  - requires current key to be loaded;
  - calls `lzc_change_key()` with `DCP_CMD_NEW_KEY` or `DCP_CMD_INHERIT`.
- It maps permission, invalid property, and unloaded-key errors to crypto failure reporting.

Other helper:
- `zfs_is_encrypted()` uses dmu stats flags when available, otherwise falls back to the encryption property.

Notable security and operational details:
- Raw keys are never accepted interactively.
- Terminal echo is restored even on read failure or signal.
- Key buffers are freed on all visible error paths, though not explicitly zeroed in this file.
- URI key retrieval supports both compile-time and dynamic-fetch backends.
- Create and rewrap paths tightly couple key material generation with property nvlist updates so kernel ioctls receive consistent wrapping-key metadata.
