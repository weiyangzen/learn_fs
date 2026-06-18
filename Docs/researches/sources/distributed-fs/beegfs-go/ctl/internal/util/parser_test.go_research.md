# sources/distributed-fs/beegfs-go/ctl/internal/util/parser_test.go

Purpose: unit tests for parser helpers.

Important APIs/types/functions: `TestParseIntFromStr`; `TestParseUintRangeFromStr`.

Control flow: table-driven tests exercise byte-size inputs and range inputs, asserting either errors or exact parsed values. The byte tests include SI/IEC variants, decimal prefixed values, max uint64, overflow, invalid prefixes, and case-sensitive byte suffix behavior. Range tests include trimmed ranges, single values, reversed ranges, invalid separators, negative-looking values, and configured lower/upper bounds.

State and persistence: no state; pure unit tests.

Dependencies and integration points: uses `testing` and `stretchr/testify/assert`.

Risks: tests do not cover `I64FormatPrefixWithUnlimited` or pflag wrappers. `t.Run` subtests are not used for each parser case, so failing cases report through assertion messages rather than subtest names.

Test signals: strong direct coverage for parser edge cases. Additional coverage should target unlimited formatting and flag integration.
