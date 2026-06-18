# sources/cloud-native/composefs-rs/crates/composefs/src/dumpfile_parse.rs

Purpose: Parses and displays individual composefs dumpfile entries and wraps `composefs-info dump` execution.

Important APIs and types: `Xattr`, `Xattrs`, `Mtime`, `Entry`, and `Item` model dumpfile records. Core parsing helpers are `unescape_limited`, `unescape_to_osstr`, `unescape_to_path`, `unescape_to_path_canonical`, `Xattr::parse`, `Mtime::from_str`, and `Entry::parse`. `Entry::filter_special`, `Item` accessors, `Display` impls, `DumpConfig`, and `dump` are the integration surface.

Control flow: `Entry::parse` splits space-delimited fields, canonicalizes absolute paths, parses octal mode and hardlink prefix, and dispatches by `rustix::fs::FileType`. Hardlinks ignore all metadata except payload target. Regular entries become inline content or external object references depending on payload. Symlink targets are not canonicalized, but path length is bounded. Xattrs are parsed from `key=value`, size-limited, and sorted for deterministic output. `dump` spawns `composefs-info dump`, streams stdout lines through `Entry::parse`, filters overlay special xattrs, and reports stderr if the command fails.

State and persistence: Parser state is per-line. `dump` launches an external process and consumes a supplied image `File`; it does not persist changes itself.

Dependencies and integration: Depends on `anyhow`, `rustix::fs::FileType`, `MAX_INLINE_CONTENT`, `SYMLINK_MAX`, and external `composefs-info`. `dumpfile.rs` consumes `Entry` and `Item` for filesystem construction.

Risks: The parser uses simple space splitting, making escaping correctness critical. Display for xattr values still uses standard escaping, noted as slightly divergent from C, while the higher-level writer avoids that path. External command integration depends on `composefs-info` availability. A diagnostic uses `found={keylen}` for an oversized value, likely a minor message bug.

Test signals: Tests cover unescaping limits, canonical path rejection, xattr parsing and length limits, parse/display idempotence, directory size canonicalization, hardlink metadata canonicalization, xattr ordering, expected failures, and executable-gated `mkcomposefs` round trips including filters.
