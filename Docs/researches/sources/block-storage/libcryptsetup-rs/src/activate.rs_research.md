# File Research: sources/block-storage/libcryptsetup-rs/src/activate.rs

Implements `CryptActivationHandle<'a>`, the device activation/deactivation facade over libcryptsetup.

Key API:
- `activate_by_passphrase`
- `activate_by_keyfile_device_offset`
- `activate_by_volume_key`
- `activate_by_keyring`
- `activate_by_signed_key` behind `cryptsetup23supported`
- `deactivate`
- `set_keyring_to_link` behind `cryptsetup27supported`

Behavior:
- Converts optional mapper names into nullable C strings.
- Maps `Option<c_uint>` keyslots to `CRYPT_ANY_SLOT`.
- Accepts passphrases and volume keys as byte slices, preserving embedded non-NUL data.
- Keyfile activation derives `keyfile_size` from filesystem metadata when omitted.
- Uses `CryptActivate` and `CryptDeactivate` bitflags.

Important dependencies:
- `CryptDevice::as_ptr`
- `LibcryptErr`
- `to_cstring!`, `path_to_cstring!`, `to_byte_ptr!`, `errno!`, `errno_int_success!`, `mutex!`

Research notes:
- The wrapper is thin and mostly preserves libcryptsetup semantics.
- `activate_by_keyfile_device_offset` performs host filesystem metadata lookup before FFI when size is absent, so failure can be Rust `IOError` before libcryptsetup is called.
- Typo in doc comment: “Activeate”.
