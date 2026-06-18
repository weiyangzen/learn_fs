# File Research: sources/block-storage/libcryptsetup-rs/src/format.rs

Defines format parameter structs and `CryptFormatHandle`.

Key abstractions:
- `CryptParams` trait
- `CryptParamsLuks1` / `CryptParamsLuks1Ref`
- `CryptParamsLuks2` / `CryptParamsLuks2Ref`
- `CryptParamsVerity` / `CryptParamsVerityRef`
- `CryptParamsLoopaes` / `CryptParamsLoopaesRef`
- `CryptParamsIntegrity` / `CryptParamsIntegrityRef`
- `CryptParamsPlain` / `CryptParamsPlainRef`
- `CryptParamsTcrypt` / `CryptParamsTcryptRef`
- `CryptFormatHandle`

Behavior:
- Separates owned Rust parameter structs from lifetime-bound FFI reference structs.
- Reference structs retain `CString`, path `CString`, boxed nested params, and byte buffers so C pointers remain valid during calls.
- Implements `TryFrom<&crypt_params_*>` for reading C structs into Rust.
- Implements `TryInto<*Ref>` for passing Rust params into C.
- `CryptFormatHandle::get_type` and `get_default_type` convert C type strings into `EncryptionFormat`.

Research notes:
- This is the main pointer-lifetime safety layer for format parameters.
- Verity, integrity, and tcrypt conversions copy C buffers into Rust vectors when reading.
- Tcrypt keyfile pointers are built from a retained vector of C strings and a retained vector of raw pointers.
- Tests cover `EncryptionFormat` equality and pointer round-trip conversion.
