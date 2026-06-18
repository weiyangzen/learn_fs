# File Research: sources/block-storage/libcryptsetup-rs/src/settings.rs

Implements PBKDF and crypt device settings.

Key types:
- `CryptPbkdfType`
- `CryptPbkdfTypeRef<'a>`
- `CryptSettingsHandle<'a>`

Key API:
- `set_rng_type`
- `get_rng_type`
- `set_pbkdf_type`
- `get_pbkdf_type_params`
- `get_pbkdf_default`
- `get_pbkdf_type`
- `set_iteration_time`
- `memory_lock`
- `metadata_locking`
- `set_metadata_size`
- `get_metadata_size`

Behavior:
- Converts `crypt_pbkdf_type` into Rust and back with retained hash `CString`.
- Supports RNG selection, PBKDF defaults, PBKDF per-device configuration, iteration time, memory lock, metadata locking, and metadata/keyslot sizes.
- `get_metadata_size` validates returned sizes through `MetadataSize` and `KeyslotsSize`.

Research notes:
- `CryptPbkdfType::try_from` requires the PBKDF type pointer to match a known `CryptKdf`.
- Hash is optional and null-aware.
