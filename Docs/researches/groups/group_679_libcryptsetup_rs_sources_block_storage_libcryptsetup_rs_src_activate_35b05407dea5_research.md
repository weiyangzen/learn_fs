# Group Research: group_679_libcryptsetup_rs_sources_block_storage_libcryptsetup_rs_src_activate_35b05407dea5

Scope confirmed against `Docs/research_subset_a.md`: `sources/block-storage/libcryptsetup-rs` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/activate.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/activate.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/backup.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/backup.rs

Implements `CryptBackupHandle<'a>` for header backup and restore.

Key API:
- `header_backup`
- `header_restore`

Behavior:
- Accepts optional `EncryptionFormat`; `None` becomes a null requested type pointer.
- Converts backup file `Path` to `CString`.
- Calls `crypt_header_backup` and `crypt_header_restore`.

Important dependencies:
- `EncryptionFormat::as_ptr`
- `CryptDevice`
- `LibcryptErr`
- `path_to_cstring!`, `errno!`, `mutex!`

Research notes:
- File is a direct FFI wrapper with minimal policy.
- Restore/backup safety and overwrite semantics are delegated to libcryptsetup.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/backup.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/consts/flags.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/consts/flags.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/consts/mod.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/consts/mod.rs

Small module declaration file.

Exports:
- `pub mod flags;`
- `pub mod vals;`

Research notes:
- Establishes the constants namespace split between bitflags and enum/value conversions.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/consts/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/consts/vals.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/consts/vals.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/context.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/context.rs

Implements `CryptContextHandle<'a>`, covering high-level crypt device context operations.

Key API:
- `format`
- `convert`
- `set_uuid`
- `set_label`
- `volume_key_keyring`
- `load`
- `repair`
- `resize`
- `suspend`
- `resume_by_passphrase`
- `resume_by_keyfile_device_offset`

Behavior:
- `format` accepts `EncryptionFormat`, cipher/mode strings, optional UUID, either provided volume key bytes or generated key length, and optional format params.
- `load`, `convert`, and `repair` use generic `CryptParams`.
- `resume_by_passphrase` passes the passphrase as a C string pointer plus explicit length.
- `resume_by_keyfile_device_offset` passes keyfile path, size, and offset.

Important dependencies:
- `either::Either`
- `uuid::Uuid`
- `CryptParams`
- `EncryptionFormat`
- FFI macros

Research notes:
- Volume key length is byte-based; docs explicitly warn about bit-to-byte conversion.
- Passphrase resume uses `CString`, so embedded NUL bytes are rejected there, unlike byte-slice passphrase activation methods.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/context.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/debug.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/debug.rs

Defines one public debug helper.

Key API:
- `set_debug_level(level: CryptDebugLevel)`

Behavior:
- Converts `CryptDebugLevel` into the C integer value and calls `crypt_set_debug_level`.

Research notes:
- This is global libcryptsetup state.
- No result is returned because the underlying API does not expose one here.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/debug.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/device.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/device.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/err.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/err.rs

Defines crate-wide error type `LibcryptErr`.

Variants:
- `IOError`
- `UuidError`
- `NullError`
- `Utf8Error`
- `JsonError`
- `InvalidConversion`
- `NullPtr`
- `NoNull`
- `Other`

Behavior:
- Implements `Display` and `std::error::Error`.
- Negative libcryptsetup return codes are generally mapped to `IOError` with raw OS errno.
- Conversion failures use explicit variants.

Research notes:
- `Other(String)` is used by tests and wrappers for ad hoc errors.
- The error type preserves the major boundary categories: OS/libcryptsetup errno, string/JSON/UUID conversion, null pointers, and invalid enum/flag conversions.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/err.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/format.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/format.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/key.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/key.rs

Implements `CryptVolumeKeyHandle<'a>`.

Key API:
- `get`
- `verify`

Behavior:
- `get` retrieves a volume key into a caller-provided mutable byte buffer and returns `(keyslot, actual_size)`.
- Optional keyslot maps to `CRYPT_ANY_SLOT`.
- Optional passphrase is passed as nullable pointer plus length.
- `verify` checks a supplied volume key against the crypt device.

Research notes:
- The caller controls output buffer capacity; libcryptsetup updates the size value.
- Passphrase is byte-slice based, so embedded NUL is allowed.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/key.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/keyfile.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/keyfile.rs

Implements keyfile reading support.

Key types:
- `CryptKeyfileContents`
- `CryptKeyfileHandle<'a>`

Key API:
- `CryptKeyfileHandle::device_read`

Behavior:
- Reads a keyfile into libcryptsetup-allocated safe memory.
- Wraps returned pointer and length in `SafeMemHandle`.
- `CryptKeyfileContents` exposes bytes via `AsRef<[u8]>`.
- If key size is omitted, uses filesystem metadata length.

Research notes:
- This file depends on the crate’s special memory cleanup path described in `lib.rs`.
- The returned key material is automatically freed and safe-zeroed through `SafeMemHandle`.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/keyfile.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/keyslot.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/keyslot.rs

Implements `CryptKeyslotHandle<'a>` for keyslot management.

Key API:
- `add_by_passphrase`
- `change_by_passphrase`
- `add_by_keyfile_device_offset`
- `add_by_key`
- `destroy`
- `status`
- `get_priority`
- `set_priority`
- `max_keyslots`
- `area`
- `get_key_size`
- `get_encryption`
- `get_pbkdf`
- `set_encryption`
- `get_dir`

Behavior:
- Supports passphrase, keyfile, and raw-volume-key based keyslot operations.
- Optional keyslots map to `CRYPT_ANY_SLOT`.
- `add_by_key` supports explicit volume key bytes, generated key length, or no volume key.
- Converts status and priority through typed enums.
- Returns keyslot area offsets and sizes.
- Retrieves PBKDF parameters into `CryptPbkdfType`.

Research notes:
- `get_encryption` returns `&str` borrowed from libcryptsetup-managed memory plus key size.
- `get_dir` returns a boxed path built from libcryptsetup’s device mapper directory string.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/keyslot.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/lib.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/lib.rs

Crate root for `libcryptsetup-rs`.

Responsibilities:
- Documents the crate as a safer Rust wrapper over libcryptsetup FFI.
- Declares all internal modules.
- Re-exports public API types and functions.
- Re-exports `libc::{c_int, c_uint, size_t}`.
- Defines `Result<T> = std::result::Result<T, LibcryptErr>`.
- Defines global synchronization state for the `mutex` feature.

Important behavior:
- With `feature = "mutex"`, uses `LazyLock<PerThreadMutex>`.
- Without `feature = "mutex"`, records the initial thread ID and panics on libcryptsetup calls from other threads.
- Contains ignored integration tests that dispatch to `tests::*`.

Research notes:
- Public API surface is intentionally centralized here.
- Comments explain a keyfile-reading workaround where bindings include copied libcryptsetup logic because corresponding free functions are not public.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/lib.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/log.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/log.rs

Provides global logging functions.

Key API:
- `log`
- `set_log_callback`

Behavior:
- `log` converts message to `CString` and calls `crypt_log` with null device pointer.
- `set_log_callback` registers a C callback and optional user data pointer globally.

Research notes:
- Callback type is an unsafe extern C function.
- User data is passed as raw `*mut c_void`; lifetime safety is the caller’s responsibility.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/log.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/flags.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/luks2/flags.rs

Implements LUKS2 persistent flag operations.

Key type:
- `CryptLuks2FlagsHandle<'a, T>`

Specialized implementations:
- `CryptLuks2FlagsHandle<'_, CryptActivate>`
- `CryptLuks2FlagsHandle<'_, CryptRequirement>`

Key API:
- `persistent_flags_set`
- `persistent_flags_get`

Behavior:
- Uses `PhantomData<T>` to distinguish activation flags from requirement flags at compile time.
- Maps to `CRYPT_FLAGS_ACTIVATION` or `CRYPT_FLAGS_REQUIREMENTS`.
- Converts returned flag bits with `from_bits`.

Research notes:
- `CryptActivate::persistent_flags_set` uses `mutex!`, but several get/set paths call the FFI inside direct `unsafe` blocks passed to `errno!` rather than through `mutex!`.
- Unknown returned bits produce `InvalidConversion`.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/flags.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/mod.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/luks2/mod.rs

Small LUKS2 module declaration file.

Exports:
- `pub mod flags;`
- `pub mod reencrypt;`
- `pub mod token;`

Research notes:
- Groups LUKS2-specific persistent flags, reencryption, and token APIs.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/reencrypt.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/reencrypt.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/token.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/luks2/token.rs

Implements LUKS2 token APIs.

Key types:
- `CryptTokenInfo`
- `TokenInput<'a>`
- `CryptLuks2TokenHandle<'a>`

Key API:
- `json_get`
- `json_set`
- `status`
- `luks2_keyring_set`
- `luks2_keyring_get`
- `assign_keyslot`
- `unassign_keyslot`
- `is_assigned`
- `activate_by_token`
- `activate_by_token_pin` behind `cryptsetup24supported`
- free function `register`

Behavior:
- Converts token JSON between `serde_json::Value` and C strings.
- Represents token status as typed enum with optional token type string.
- Allows add/replace/remove token via `TokenInput`.
- Supports keyring token parameter set/get.
- Token assignment maps `None` keyslot to all slots.
- `is_assigned` maps `0` to true and `-ENOENT` to false.
- Registers token handlers after checking handler name is NUL-terminated.

Research notes:
- Token activation accepts optional user data pointer.
- `register` requires callers to pass a static string ending with `\0`, typically via `c_str!`.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/luks2/token.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/macros.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/macros.rs

Defines core crate macros for synchronization, error mapping, pointer conversion, string conversion, enum conversion, C strings, and callback shims.

Key macros:
- `mutex!`
- `errno!`
- `errno_int_success!`
- `int_to_return!`
- `try_int_to_return!`
- `ptr_to_option!`
- `ptr_to_option_with_reference!`
- `ptr_to_result!`
- `ptr_to_result_with_reference!`
- `path_to_cstring!`
- `to_cstring!`
- `to_byte_ptr!`
- `to_mut_byte_ptr!`
- `from_str_ptr!`
- `from_str_ptr_to_owned!`
- `consts_to_from_enum!`
- `c_str!`
- `c_confirm_callback!`
- `c_logging_callback!`
- `c_progress_callback!`
- token handler callback macros

Behavior:
- `mutex!` wraps unsafe libcryptsetup calls and enforces either feature-gated locking or single-thread use.
- `errno!` treats negative values as errno, zero as success, and positive values as panic.
- `errno_int_success!` treats negative values as errno and non-negative as returned success value.
- Pointer macros centralize null-to-option/result behavior.
- Callback macros convert raw C callback inputs into Rust values and optional user data references.

Research notes:
- `path_to_cstring!` uses `Path::to_str`, so non-UTF-8 paths are rejected.
- Callback macros can panic on invalid strings or log levels in some cases.
- The token handler open macro appears internally inconsistent in the read source: it declares `Result<Box<[u8]>, LibcryptErr>` but matches `Ok(())`, and references `$crate::SizeT` while the crate re-exports `size_t`.
- Unit tests cover callback wrappers, enum conversion macro, and no-mutex multi-thread panic.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/mem.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/mem.rs

Implements safe-zeroing and safe-free memory handles.

Key types:
- `SafeMemzero` trait behind `cryptsetup23supported`
- `SafeOwnedMemZero` behind `cryptsetup23supported`
- `SafeBorrowedMemZero` behind `cryptsetup23supported`
- `SafeMemHandle`

Behavior:
- Uses macros to define pointer-plus-size memory handles.
- Drop for safe-zero handles calls `safe_memzero`, and owned variants can additionally call `libc::free`.
- `SafeMemHandle` drops with `crypt_safe_free`.
- `SafeMemHandle::alloc` uses `crypt_safe_alloc` behind `cryptsetup23supported`.
- Implements `AsRef<[u8]>` and `AsMut<[u8]>` for memory views.
- Marks `SafeMemHandle` as `Send`.

Research notes:
- Safety depends on pointer provenance and exact size correctness; docs warn about memory corruption if wrong.
- `SafeMemHandle` is used by keyfile contents to ensure key material is cleaned up.
- Tests cover explicit zeroing and borrowed-memory zeroing.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/mem.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/runtime.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/runtime.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/settings.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/settings.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/status.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/status.rs

Implements crypt device status and metadata inspection.

Key API:
- `CryptDeviceStatusHandle::dump`
- `dump_json` behind `cryptsetup24supported`
- `get_cipher`
- `get_cipher_mode`
- `get_uuid`
- `get_device_path`
- `get_metadata_device_path`
- `get_data_offset`
- `get_iv_offset`
- `get_volume_key_size`
- `get_verity_info`
- `get_integrity_info`
- free function `status`
- free function `get_sector_size`

Behavior:
- Reads textual, JSON, cipher, UUID, path, offset, key size, verity, and integrity information from libcryptsetup.
- `dump_json` parses returned C string into `serde_json::Value` and intentionally does not free the buffer, with a comment explaining double-free/valgrind observations.
- `status` accepts optional `CryptDevice`; `None` passes null device pointer.
- `get_sector_size` returns raw `c_int`.

Research notes:
- `get_cipher`, `get_cipher_mode`, and `get_uuid` call FFI without `mutex!` around the direct pointer access in the visible code for some getters.
- Path getters return borrowed `&Path` tied to libcryptsetup-managed strings.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/status.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/encrypt.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/tests/encrypt.rs

Integration-style encryption tests using loopback devices.

Key helpers:
- `init`
- `init_null_cipher`
- `init_by_keyfile`
- `activate_without_explicit_format`
- `activate_by_passphrase`
- `create_keyfile`
- `activate_by_keyfile`
- `activate_null_cipher`
- `write_random`
- `test_existence`
- `run_plaintext_test`

Test entry points:
- `test_encrypt_by_password`
- `test_encrypt_by_keyfile`
- `test_encrypt_by_password_without_explicit_format`
- `test_unencrypted`

Behavior:
- Creates LUKS2 AES-XTS devices, adds keyslots, activates mapper devices, writes random plaintext through mapper, then scans backing storage for plaintext.
- Negative encryption tests expect plaintext not to appear in backing file.
- Null cipher test expects plaintext to be visible.
- Uses mmap scanning with 1 MiB sliding window.
- Cleans up mapper device when `DO_CLEANUP` allows.

Research notes:
- Tests require root and loopback support through shared loopback harness.
- The keyfile path is derived from the loopback backing file path with `-key`.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/encrypt.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/keyfile.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/tests/keyfile.rs

Tests keyfile memory cleanup behavior.

Key entry point:
- `test_keyfile_cleanup`

Behavior:
- Creates a temporary keyfile with known contents.
- Reads it through `CryptKeyfileHandle::device_read`.
- Checks returned bytes match expected password.
- Drops `CryptKeyfileContents`, then inspects the old pointer range to verify the cleartext is no longer present.

Research notes:
- This test directly targets `SafeMemHandle` cleanup semantics for keyfile material.
- It intentionally reads from a dangling pointer after drop for cleanup verification, which is unsafe test logic.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/keyfile.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/loopback.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/tests/loopback.rs

Provides loopback-backed test fixture utilities.

Key helpers:
- `setup_backing_file`
- `use_loopback`

Behavior:
- Creates a random-named backing file in `TEST_DIR` or `/tmp`.
- Fills it with zeroes or random bytes.
- Requires effective UID root.
- Uses `loopdev::LoopControl` to attach the file to a free loop device.
- Runs a caller-provided closure with loop device path and backing file path.
- Detaches and deletes backing file when cleanup is enabled.
- Captures panics around test closure so cleanup can run before re-raising.

Research notes:
- `FORMAT_WITH_ZEROS` and `DO_CLEANUP` are controlled in `tests/mod.rs`.
- Backing file names use URL-safe base64 of random bytes.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/loopback.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/mod.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/tests/mod.rs

Test module root and environment helpers.

Exports:
- `encrypt`
- `keyfile`
- `loopback`
- `reencrypt` behind `cryptsetup24supported`

Helpers:
- `format_with_zeros`
- `do_cleanup`

Behavior:
- Reads `FORMAT_WITH_ZEROS` and `DO_CLEANUP` environment variables.
- Defaults both to `true`.
- Unit tests verify default and explicit `false` behavior.

Research notes:
- Integration tests in `lib.rs` are ignored and call into these modules.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/reencrypt.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/tests/reencrypt.rs

Integration-style LUKS2 reencryption test.

Key entry point:
- `test_reencrypt_by_password`

Behavior:
- Creates a LUKS2 AES-XTS loopback device.
- Adds an initial key.
- Adds a new unbound/no-segment key using `CryptVolumeKey::NO_SEGMENT`.
- Activates the device.
- Reads current sector size, cipher, and cipher mode.
- Initializes reencryption with checksum resilience and SHA-256 hash.
- Runs `reencrypt2`.
- Deactivates mapper device.

Research notes:
- Requires `cryptsetup24supported`.
- Exercises `CryptParamsReencrypt`, nested `CryptParamsLuks2`, activation, keyslot, status, sector size, and reencryption APIs together.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/tests/reencrypt.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/wipe.rs -->
# File Research: sources/block-storage/libcryptsetup-rs/src/wipe.rs

Implements wipe operations.

Key type:
- `CryptWipeHandle<'a>`

Key API:
- `wipe`

Behavior:
- Wraps `crypt_wipe`.
- Accepts device path, wipe pattern, offset, length, block size, flags, optional progress callback, and optional user data.
- Converts device path to C string and user data to `*mut c_void`.

Research notes:
- Progress callback is an unsafe extern C function.
- User data lifetime and callback safety are caller-managed.
<!-- END FILE RESEARCH: sources/block-storage/libcryptsetup-rs/src/wipe.rs -->