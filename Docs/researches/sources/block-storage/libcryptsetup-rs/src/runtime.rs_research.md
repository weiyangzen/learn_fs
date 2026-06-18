# File Research: sources/block-storage/libcryptsetup-rs/src/runtime.rs

Implements runtime active-device inspection.

Key types:
- `ActiveDevice`
- `CryptRuntimeHandle<'a>`

Key API:
- `get_active_device`
- `get_active_integrity_failures`

Behavior:
- Converts `crypt_active_device` into Rust fields: offset, IV offset, size, activation flags.
- `get_active_device` calls by mapper name.
- `get_active_integrity_failures` returns libcryptsetup’s reported failure count.

Research notes:
- `CryptActivate::from_bits` validates active-device flags.
- Runtime handle stores the device name borrowed for the same lifetime as the handle.
