## sources/distributed-fs/ceph-client/lib/tests/string_helpers_kunit.c

### Purpose
This KUnit suite validates helper routines from `lib/string_helpers.c`: unescaping, escaping, human-readable size formatting, and ASCII case conversion. It is heavily table-driven and checks both returned lengths and output bytes.

### Important APIs, types, and functions
`test_string_check_buf()` compares expected lengths and bytes. `strings[]` drives `string_unescape()`, `string_unescape_any()`, and in-place variants for space, octal, hex, and special escapes. `escape0[]` and `escape1[]` encode expected `string_escape_mem()` output without and with a dictionary. `test_string_find_match()` applies flag normalization, including NULL-aware cases and octal-over-hex priority. Size helpers use `string_get_size()` with `STRING_UNITS_10`, `STRING_UNITS_2`, `STRING_UNITS_NO_SPACE`, and `STRING_UNITS_NO_BYTES`. `test_upper_lower()` covers `string_upper()` and `string_lower()`.

### Control flow
`test_unescape()` iterates all unescape flag combinations, runs one random in-place unescape combination, then iterates all escape flag combinations for both dictionaries. `test_string_escape()` optionally injects NULL bytes, builds a concatenated input and expected output, calls `string_escape_mem()`, and separately checks overflow/length-only behavior by passing a NULL output buffer of size 0. `test_get_size()` runs representative small, normal, odd block-size, and huge values through decimal and binary unit modes. `test_upper_lower()` allocates a destination per case, converts, compares, and frees.

### State and persistence
All buffers are KUnit-managed or manually freed within a test. There is no persistent state. One in-place unescape test uses `get_random_u32_below()` to choose flags, but all non-in-place and escape combinations are exhaustive over masks.

### Dependencies and integration points
The suite depends on KUnit, random helpers, string helpers, allocation, and array-size utilities. It integrates as suite `string_helpers`.

### Risks and edge cases
The escape tables are dense, and missing combinations are represented by absent outputs that get skipped for a particular flag set. The one random in-place flag combination does not exhaustively cover every in-place mode in a single run. Expected strings include embedded control and high-bit bytes, so source readability and escaping correctness matter.

### Test signals
Signals include exhaustive flag-mask iteration for non-in-place unescape and escape modes, length-only overflow checks for `string_escape_mem()`, byte-for-byte expected output comparisons, unit-format variations with and without spaces/bytes suffixes, and upper/lower conversion checks.
