# File Research: sources/block-storage/libcryptsetup-rs/src/luks2/reencrypt.rs

Implements LUKS2 reencryption parameter conversion and operations.

Key types:
- `CryptParamsReencrypt`
- `CryptParamsReencryptRef<'a>`
- `CryptLuks2ReencryptHandle<'a>`

Key API:
- `reencrypt_init_by_passphrase`
- `reencrypt_init_by_keyring`
- `reencrypt`
- `reencrypt2` behind `cryptsetup24supported`
- `status`

Behavior:
- Converts reencryption params into `crypt_params_reencrypt`.
- Optionally nests LUKS2 format params.
- Accepts optional mapper name, old/new keyslots, and cipher/mode.
- Uses retained `CString`s to avoid use-after-free, with comments calling this out.
- `reencrypt2` supports user data pointer for newer libcryptsetup API.

Research notes:
- `CryptParamsReencryptRef` retains nested `CryptParamsLuks2Ref` and strings for FFI pointer validity.
- Reencrypt progress callbacks are raw unsafe extern C functions.
