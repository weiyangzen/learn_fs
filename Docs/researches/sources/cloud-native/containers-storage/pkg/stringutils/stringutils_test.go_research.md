# sources/cloud-native/containers-storage/pkg/stringutils/stringutils_test.go

Purpose: tests random string helpers, Unicode-aware truncation, case-insensitive membership, and shell quoting.

Important APIs, types, and functions: helper functions `testLengthHelper`, `testUniquenessHelper`, `isASCII`, tests for alpha/ASCII generation, `TestEllipsis`, `TestTruncate`, `TestInSlice`, `TestShellQuoteArgumentsEmpty`, and `TestShellQuoteArguments`.

Control flow: generator tests verify length and no repeats over 25 generated 64-byte strings. Truncation tests use a string containing a multi-byte rune. Shell quote tests compare exact POSIX quoting output.

State and persistence: no persistence. Tests consume randomness and in-memory strings.

Dependencies and integration points: depends on `testing`. It validates public helpers in `stringutils.go`.

Risks and edge cases: uniqueness tests are probabilistic. Test strings include Unicode, which is useful for rune behavior but does not cover combining marks. Shell quoting tests cover a representative but not exhaustive set of metacharacters.

Test signals: confirms ASCII character set, length contracts, common truncation behavior, case-insensitive lookup, and quote escaping of embedded single quotes.
