# File Research: sources/cow-pools/openzfs/module/zfs/u8_textprep.c

This file implements OpenZFS kernel UTF-8 text preparation utilities: validation, comparison, simple case mapping, Unicode decomposition/composition, and prepared-string output. It is part of subset A through `sources/cow-pools/openzfs`.

Primary public APIs:
- `u8_validate()`: validates UTF-8 input and reports byte length or an error.
- `u8_strcmp()`: compares UTF-8 strings with optional case and normalization equivalence.
- `u8_textprep_str()`: transforms a buffer using case conversion and/or Unicode normalization.
- The three APIs are exported with `EXPORT_SYMBOL()`.

Key dependencies:
- `sys/u8_textprep.h` supplies flags and public interface contracts.
- `sys/u8_textprep_data.h` supplies Unicode versioned lookup tables for case mapping, combining classes, decomposition, and composition.
- Kernel utilities provide `errno`, string helpers, integer types, and module export support.

Core constants and model:
- `U8_MB_CUR_MAX` is fixed at 4, matching modern UTF-8.
- UTF-8 validation uses `u8_number_of_bytes`, `u8_valid_min_2nd_byte`, and `u8_valid_max_2nd_byte`.
- The validation tables reject continuation-byte starts, overlong forms, surrogate encodings, and values beyond the Unicode range.
- `U8_MAX_BYTES_UCS2` supports optional UCS-2 range validation.
- Normalization uses a bounded stream-safe sequence model: max 32 characters per combining/conjoining sequence, with CGJ insertion at the 31-character practical upper limit.
- Hangul syllable and Jamo constants implement algorithmic decomposition and composition for modern Hangul.

Important internal routines:
- `do_case_conv()` performs simple Unicode case conversion through multi-level generated tables. ASCII is handled cheaply by callers; non-ASCII mappings may change byte length.
- `do_case_compare()` compares strings character by character after simple case conversion, setting `errnum` for malformed or incomplete sequences but still producing deterministic comparison results.
- `combining_class()` returns canonical combining class from generated tables, treating unknown or invalid data as starter class `0`.
- `do_decomp()` performs canonical or compatibility decomposition. It special-cases Hangul syllables algorithmically and otherwise uses flattened decomposition tables.
- `find_composition_start()` locates possible canonical composition mappings for a starter.
- `blocked()` implements the canonical composition blocking rule over collected combining classes.
- `do_composition()` recomposes normalized sequences, including Hangul Jamo composition and table-driven canonical composition.
- `collect_a_seq()` is the central normalization worker. It collects one starter plus related combining/conjoining marks, applies case conversion, decomposition, canonical ordering, stream-safe truncation with U+034F, and optional composition.
- `do_norm_compare()` compares two strings by repeatedly collecting normalized sequences from each side.

`u8_validate()` behavior:
- Returns `0` for `NULL` input.
- Honors `U8_VALIDATE_ENTIRE`; otherwise validation stops after the first character.
- Honors `U8_VALIDATE_UCS2_RANGE` by rejecting 4-byte UTF-8 characters with `ERANGE`.
- Honors `U8_VALIDATE_CHECK_ADDITIONAL` by rejecting exact matches against a caller-provided disallowed sequence list with `EBADF`.
- Reports malformed starts or continuations as `EILSEQ`, incomplete characters as `EINVAL`, and out-of-range encodings as `ERANGE`.
- The return value counts validated bytes, not Unicode scalar values.

`u8_strcmp()` behavior:
- Validates Unicode version, clamping too-new versions to `U8_UNICODE_LATEST` while setting `ERANGE`.
- Defaults to case-sensitive byte comparison when no flags are provided.
- Rejects incompatible case-mode or normalization-mode flag combinations with `EBADF` and falls back to case-sensitive behavior.
- Fast-paths plain `strcmp()`/`strncmp()` for `U8_STRCMP_CS`.
- Uses `do_case_compare()` for pure case-insensitive uppercase mode, and lower mode only when compiled with `U8_STRCMP_CI_LOWER`.
- Uses `do_norm_compare()` for normalization-aware comparisons such as NFD, NFC, NFKD, and NFKC.

`u8_textprep_str()` behavior:
- Rejects too-new Unicode versions with `ERANGE`.
- Rejects simultaneous upper/lower conversion when lower support is compiled in.
- Rejects invalid normalization flag combinations with `EBADF`.
- Returns `0` for `NULL` input or zero input length.
- Requires a non-NULL output buffer; otherwise returns `E2BIG`.
- Updates `*inlen` to remaining input bytes and `*outlen` to remaining output capacity.
- Without normalization flags, it performs a simpler pass for copying and optional simple case conversion.
- With normalization flags, it routes non-trivial sequences through `collect_a_seq()`.
- Honors `U8_TEXTPREP_IGNORE_NULL` and `U8_TEXTPREP_IGNORE_INVALID`; otherwise null or invalid sequences stop or fail processing.
- Reports output exhaustion as `E2BIG`.

Filesystem relevance:
- ZFS uses Unicode-aware text handling for dataset/filesystem name semantics and normalization-sensitive comparisons. This file provides the reusable kernel implementation rather than embedding Unicode logic in higher-level ZFS modules.
- The code is careful about bounded stack buffers and explicit output-capacity checks, important because normalization can expand byte sequences.
- The generated tables keep Unicode behavior data-driven while preserving kernel-safe fixed-size operations.

Notable implementation details:
- Hangul is handled algorithmically rather than entirely by tables, reducing table size and matching Unicode normalization rules.
- Composition only occurs after decomposition, consistent with NFC/NFKC construction.
- Long combining sequences are made stream-safe by injecting U+034F COMBINING GRAPHEME JOINER.
- Invalid input handling differs by API: validation fails immediately, comparison records errors but can continue, and textprep can either fail or copy through invalid bytes depending on flags.
- The lower-case path is guarded by compile-time macros; in this build path, unsupported lower conversion code is intentionally unreachable.
