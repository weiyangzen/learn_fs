# sources/compression/xz/src/xz/suffix.c

Purpose: derives output filenames for compression and decompression in the full `xz` command, including built-in suffix rules, custom `--suffix`, format-specific defaults, and DOS 8.3 short-filename behavior.

Important functions: `suffix_get_dest_name()` is the exported entry point and dispatches to `compressed_name()` or `uncompressed_name()` based on global `opt_mode`. `suffix_set()` validates and stores `custom_suffix`; `suffix_is_set()` reports whether it exists. Internal helpers include `test_suffix()`, `msg_suffix()`, `is_dir_sep()`, `has_dir_sep()`, and DJGPP-only `has_sfn_suffix()`.

Control flow: decompression tests known compressed suffixes such as `.xz`, `.txz`, `.lzma`, `.tlz`, optional `.lz`, and DJGPP `.lzm`/short suffixes, then falls back to the custom suffix. Compression selects the suffix table from `opt_format`, rejects already-compressed names, handles `.tar` abbreviations, and appends or replaces suffixes. DJGPP adds short-filename truncation and special dash suffix policy.

State and persistence: owns one process-global heap string, `custom_suffix`, replacing it on each `suffix_set()`. Destination names are heap-allocated and returned to the caller. It does not write files.

Dependencies and integration: depends on global command options from `private.h`/coder state (`opt_mode`, `opt_format`), `xmalloc()`, `xstrdup()`, message warning/fatal APIs, gettext, and nonprint masking. It integrates with file-opening code that needs a destination path before creating output.

Risks: path separator handling differs on DOS-like systems and VMS; custom suffixes with separators are rejected to avoid path injection. Incorrect suffix-table order would change user-visible naming, especially `.txz`/`.tlz`. The raw format requires a custom suffix or stdout, so callers must enforce that higher-level rule.

Test signals: the tests list includes `test_suffix.sh` in `Makefile.am`, although it is outside this work item. Compression shell tests indirectly exercise default suffix-free stdout behavior; filename edge cases need dedicated CLI coverage.
