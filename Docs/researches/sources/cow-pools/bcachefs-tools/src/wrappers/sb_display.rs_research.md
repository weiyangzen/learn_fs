# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/sb_display.rs

Rust replacement for C `bch2_sb_to_text_with_names`, designed to avoid allocator mismatches when scanning devices for display.

Core behavior:
- Builds `UUID=<uuid>` from the superblock user UUID.
- Uses `device_scan::scan_sbs` to find matching device superblocks.
- Prints normal superblock fields via C `bch2_sb_to_text`, excluding member fields so Rust can print members with names.
- For each alive member in members_v1 and/or members_v2, prints device index, path, model, optional serial number, and C member detail text.
- Supports `field_only` by delegating to `__bch2_sb_field_to_text`.

Important implementation detail:
- Scanned superblock handles remain in a Rust `Vec` and are dropped by Rust, avoiding the previous pattern where Rust-allocated memory was freed by C `kvfree`.

Potential concerns:
- `field_only` transmutes a `u32` to `bch_sb_field_type`; invalid values rely on C lookup behavior.
- Missing devices are displayed as `(not found)`, but the rest of the member still prints.
