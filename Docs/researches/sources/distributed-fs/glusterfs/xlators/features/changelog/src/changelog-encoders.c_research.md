# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.c

## Purpose
Serializes changelog records into ASCII or binary on-disk formats, including optional records for fop number, entry path material, UID/GID/mode, and delete path capture.

## APIs, Types, and Functions
Conversion helpers are `entry_fn()`, `del_entry_fn()`, `fop_fn()`, `number_fn()`, `entry_free_fn()`, and `del_entry_free_fn()`. `changelog_encode_ascii()` and `changelog_encode_binary()` construct complete records and call `changelog_write_change()`. `changelog_encode_write_xtra()` serializes `changelog_opt_t` arrays. `changelog_encode_change()` selects `cb_encoder[priv->encode_mode]`.

## Control Flow, State, and Persistence
Encoding writes a one-byte type map from `priv->maps`, the target GFID as UUID text or raw `uuid_t`, optional NUL-separated extra records, and a final NUL. ASCII mode uses `uuid_utoa()` and converter callbacks; binary mode stores fixed binary fields where possible. The resulting buffer is written to the active `CHANGELOG` fd and later rolled over by helper code.

## Dependencies and Integration
Depends on `changelog-helpers.h` for `changelog_log_data_t`, optional record layouts, buffer macros, and write helpers. It is selected during rollover/open through `changelog_encode_change()` and invoked by `changelog_handle_change()`.

## Risks and Test Signals
Risks include `alloca()` sizing based on caller-maintained `cld_ptr_len`, converter/free callback mismatches, binary/ASCII decoder compatibility, and path strings containing separators. Test signals include byte-for-byte expected records for data/metadata/entry records, create/mkdir extra records, delete-path capture records, binary round-trip through the journal decoder, and write failure propagation.
