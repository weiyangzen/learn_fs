# File Research: sources/block-storage/cryptsetup/src/utils_reencrypt.c

This is the main `cryptsetup reencrypt` implementation for LUKS2 and the top-level dispatcher that falls back to the legacy LUKS1 reencryption path. It handles encrypt, decrypt, reencrypt, initialize-only, resume-only, active online reencryption, and forced offline modes.

Key responsibilities:
- Classifies devices as clean LUKS2, LUKS2 reencryption in progress, LUKS1, legacy LUKS1 reencryption, non-LUKS, or invalid.
- Enforces LUKS version conflicts and routes `--encrypt`, `--decrypt`, or normal reencryption to `_encrypt`, `_decrypt`, or `_reencrypt`.
- Initializes LUKS2 reencryption through `crypt_reencrypt_init_by_keyslot_context`.
- Resumes LUKS2 reencryption through `crypt_reencrypt_run`.
- Detects active dm holders for online reencryption unless `--force-offline-reencrypt` is used.
- Handles detached headers, data shifts, temporary headers, sector size changes, cipher changes, and volume key changes.
- Manages keyslot and token unlock contexts for reencryption.

Important control flow:
- `reencrypt()` is the public entry point. It loads by active name if `--active-name` is set, otherwise by header/data device, validates LUKS version expectations, checks resume/init-only conflicts, then dispatches.
- `load_luks()` loads LUKS metadata and detects LUKS2 online reencryption via persistent requirements. If normal load fails, it checks for the LUKS1 legacy unusable magic.
- `luks2_reencrypt_eligible()` rejects unsupported LUKS2 configurations: legacy offline reencryption requirement, OPAL, integrity profiles, or unknown cipher format.
- `reencrypt_luks2_load()` resumes an already initialized LUKS2 operation after validating requested options against stored reencryption parameters and unlocking the needed old/new volume key contexts.
- `encrypt_luks2_init()` formats a new LUKS2 header and initializes encryption over an existing plaintext data device. It supports detached header mode and temporary header placement for in-place header creation.
- `decrypt_luks2_init()` supports LUKS2 decryption only with detached headers and data offset zero. `decrypt_luks2_datashift_init()` handles the special case where a missing header file is exported first, then reencryption is initialized with datashift.
- `reencrypt_luks2_init()` handles LUKS2-to-LUKS2 reencryption, including cipher/mode changes, sector size changes, optional volume key replacement, keyslot duplication, token reassignment, and active mapping discovery.

Key data structures:
- `enum device_status_info` models device classification for dispatch.
- `struct keyslot_contexts` tracks candidate keyslots, token contexts, old/new volume key contexts, generated new volume key state, and new/old keyslot IDs.
- `struct crypt_params_reencrypt` is filled differently for encrypt, decrypt, resume, and reencrypt modes.

Keyslot/token handling:
- Token candidates are collected from token/keyslot assignments.
- Token unlock is attempted before passphrase prompts when token options are present.
- For volume key changes with active keyslots, new keyslots are created and token assignments are copied from old keyslots to new keyslots.
- `set_keyslot_params()` preserves keyslot encryption and PBKDF parameters unless CLI options request replacement. It replaces `cipher_null` keyslot encryption with default LUKS2 keyslot encryption.

Safety and validation:
- Active-holder auto-detection prevents accidental offline reencryption of active devices.
- Non-block-device data paths in batch mode require `--force-offline-reencrypt`.
- Sector size increases are rejected for offline devices when blkid probing is needed.
- Filesystem superblock block size is checked before increasing encryption sector size.
- Broken LUKS signatures are detected before encrypting a non-LUKS device.
- LUKS2 decryption requires `--header`; encryption without detached header requires device size reduction.
- Reencryption cannot proceed if no segment parameter changes are requested.

External dependencies:
- Heavy use of libcryptsetup APIs: `crypt_init*`, `crypt_load`, `crypt_reencrypt_status`, `crypt_reencrypt_init_by_keyslot_context`, `crypt_reencrypt_run`, `crypt_activate_by_keyslot_context`, keyslot/token APIs, persistent flags, integrity info, and header backup/restore.
- Uses cryptsetup helpers from other files: argument macros, `luksFormat`, token unlock helpers, PBKDF setup, progress reporting, blkid/signature helpers, volume key helpers, and signal handling.
- Calls `reencrypt_luks1()` and `reencrypt_luks1_in_progress()` for legacy LUKS1 behavior.
