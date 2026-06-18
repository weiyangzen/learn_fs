## sources/distributed-fs/ceph-client/lib/tests/scanf_kunit.c

### Purpose
This KUnit suite validates kernel `vsscanf()` numeric parsing and legacy `simple_strto*()` conversion helpers across integer widths, signedness, bases, delimiters, field widths, prefixes, and deterministic pseudo-random value lists.

### Important APIs, types, and functions
`_test()` wraps `vsscanf()`, checks the conversion count, then invokes a typed checker. `check_ull`, `check_ll`, `check_ulong`, `check_long`, `check_uint`, `check_int`, `check_ushort`, `check_short`, `check_uchar`, and `check_char` consume varargs and compare parsed values to expected arrays. `numbers[]` supplies boundary values copied from kstrtox tests. Macros generate single-number tests, eight-number delimited list tests, fixed-width tests, exact-value-width tests, digit-slicing tests, prefix overflow tests, and `simple_strtoull`, `simple_strtoll`, `simple_strtoul`, `simple_strtol` checks.

### Control flow
`scanf_suite_init()` allocates `test_buffer` and `fmt_buffer`, then seeds `rnd_state` deterministically. `numbers_simple()` loops through representable values for all target types and scan formats. Parameterized cases run list parsing over delimiters `" "`, `":"`, `","`, `"-"`, and `"/"`. Field-width cases either use maximum width for the type/base or the exact rendered value length. `numbers_slice()` temporarily sets an empty delimiter to parse adjacent values by field width. `numbers_prefix_overflow()` documents userland-derived behavior for `-` and `0x` prefixes that are as wide as the field. Conversion helper tests assert both value and end pointer.

### State and persistence
The suite owns two heap buffers for its lifetime and a deterministic `struct rnd_state`. Individual result arrays are stack-local. There is no persistent kernel state outside the suite.

### Dependencies and integration points
The file depends on KUnit, `vsscanf`, snprintf formatting for test generation, overflow/type helpers, bit operations (`hweight32`, `GENMASK`), prandom, and slab allocation. It registers as suite `scanf`.

### Risks and edge cases
Expected behavior for prefix overflow is derived from userland `sscanf`, so divergence may be a deliberate kernel behavior change or a bug depending on policy. Randomized list values are deterministic by seed but generated through helper logic that favors varied bit lengths rather than statistical rigor. Tests focus on numeric conversions, not string, char-class, or pointer scanning.

### Test signals
Signals include exhaustive boundary-value loops for representable values, deterministic random list parsing across delimiters, field-width slicing without delimiters, explicit conversion-count checks, and end-pointer verification for simple conversion APIs.
