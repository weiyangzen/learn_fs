# File Research: sources/block-storage/libcryptsetup-rs/src/consts/flags.rs

Defines Rust `bitflags` wrappers for libcryptsetup flag constants.

Types:
- `CryptActivate`
- `CryptDeactivate`
- `CryptVerity`
- `CryptTcrypt`
- `CryptKeyfile`
- `CryptVolumeKey`
- `CryptRequirement`
- `CryptReencrypt`
- `CryptPbkdf`
- `CryptWipe`

Behavior:
- Mirrors constants from `libcryptsetup_rs_sys`.
- Version-gates newer activation flags with `cryptsetup23supported` and `cryptsetup24supported`.

Research notes:
- This is the central flags translation layer for activation, verity, tcrypt, keyfiles, volume keys, requirements, reencryption, PBKDF, and wipe operations.
- `from_bits` checks elsewhere can fail if libcryptsetup returns bits not represented by this wrapper, producing `InvalidConversion`.
