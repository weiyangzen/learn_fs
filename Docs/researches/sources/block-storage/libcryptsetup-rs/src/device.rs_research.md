# File Research: sources/block-storage/libcryptsetup-rs/src/device.rs

Defines initialization and owning device handle types.

Key types:
- `CryptInit`
- `CryptDevice`

Key API:
- `CryptInit::init`
- `CryptInit::init_with_data_device`
- `CryptInit::init_by_name_and_header`
- `CryptDevice::from_ptr`
- Handle factory methods for settings, format, context, keyslot, runtime, LUKS2 flags, activation, volume key, status, backup, keyfile, wipe, token, and reencryption
- `set_confirm_callback`
- `set_data_device`
- `set_data_offset`

Behavior:
- Owns raw `*mut crypt_device`.
- Frees the C device in `Drop` via `crypt_free`.
- Converts device/header/data paths to C strings before initialization.
- Stores only the raw pointer; operation-specific APIs borrow it through short-lived handle structs.

Research notes:
- `from_ptr` creates an owning `CryptDevice` from a raw pointer and will free it on drop. Callback wrappers using this must avoid double-free if the pointer remains owned elsewhere.
- Handle methods enforce mutable borrowing at the Rust API level for most operations.
