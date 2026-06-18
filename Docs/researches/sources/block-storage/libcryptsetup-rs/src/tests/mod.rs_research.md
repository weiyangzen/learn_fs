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
