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
