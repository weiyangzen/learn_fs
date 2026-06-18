# File Research: sources/block-storage/libcryptsetup-rs/src/consts/vals.rs

Defines enum and scalar wrappers for non-bitflag libcryptsetup constants.

Key types:
- `CryptDebugLevel`
- `EncryptionFormat`
- `KeyslotInfo`
- `KeyslotPriority`
- `CryptLogLevel`
- `CryptFlagsType`
- `CryptReencryptInfo`
- `CryptReencryptModeInfo`
- `CryptReencryptDirectionInfo`
- `CryptKdf`
- `CryptRng`
- `LuksType`
- `CryptStatusInfo`
- `CryptWipePattern`
- `MetadataSize`
- `KeyslotsSize`
- `LockState`

Behavior:
- Uses `consts_to_from_enum!` for many numeric enum conversions.
- Implements string pointer conversions for `EncryptionFormat`, `CryptKdf`, and `LuksType`.
- Validates metadata sizes against supported LUKS2 metadata values.
- Validates keyslots size as 4KB-aligned and no larger than 128MB.
- Includes unit tests for `MetadataSize` and `KeyslotsSize`.

Research notes:
- `EncryptionFormat::from_ptr` and `CryptKdf::from_ptr` assume non-null C strings.
- `LockState::from` treats any non-zero or unexpected value as locked.
- `KeyslotsSize::try_from(0)` is accepted as default because `0` is divisible by 4KB and below max.
