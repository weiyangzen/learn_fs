# sources/compression/lz4/tests/checkTag.c

Purpose: validates release tag compatibility with the compiled LZ4 version string.

Important APIs/functions: `validate()` checks `v` prefix, length, and prefix match with `LZ4_VERSION_STRING`; `main()` prints version/tag and returns `0`, `1`, or `2`.

Control flow/state: single-argument command with no persistent state.

Dependencies/integration: includes `lz4.h`; built as `checkTag` for automated release/version checks.

Risks: accepts arbitrary suffix after the version prefix; rejects exact-length `v<version>` tags due to length rule.

Test signals: non-zero exit flags incompatible tags or usage errors.
