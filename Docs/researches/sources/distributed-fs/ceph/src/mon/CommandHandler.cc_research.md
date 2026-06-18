<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.cc -->
# sources/distributed-fs/ceph/src/mon/CommandHandler.cc

## Purpose
`CommandHandler.cc` implements a small monitor command parsing helper. Its only behavior is canonical parsing of boolean command arguments accepted by monitor command handlers.

## Important APIs, types, and functions
`CommandHandler::parse_bool(std::string_view str, bool* result, std::ostream& ss)` accepts textual false values `false`, `no`, and numeric `0`, and true values `true`, `yes`, and numeric `1`. It uses `strict_strtoll()` to reject non-canonical numeric input and writes a human-readable error string on failure.

## Control flow
The function asserts `result` is non-null, tries to parse the string as base-10 integer, checks explicit false spellings or parsed zero, checks explicit true spellings or parsed one, and otherwise returns `-EINVAL` after writing the accepted value set into `ss`.

## State and persistence behavior
There is no retained state or persistence. The function mutates only `*result` and the supplied error stream.

## Dependencies and integration points
The file depends on `common/strtol.h` for strict numeric parsing and `ceph_assert` for contract enforcement. It is compiled into the `mon` library and can be inherited by monitor command handlers that need uniform boolean parsing.

## Risks and edge cases
The parser is deliberately case-sensitive and accepts only exact text. Numeric strings other than exactly valid `0` or `1` are rejected, including values like `2`. Passing a null result pointer aborts in debug/assert-enabled builds.

## Test signals
Unit coverage should verify all accepted spellings, invalid strings, invalid numbers, empty input, and non-null result enforcement. Command-level tests should confirm error text is surfaced to users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.cc -->
