# sources/cloud-native/containers-storage/pkg/stringutils/stringutils.go

Purpose: provides string generation, truncation, case-insensitive slice helpers, and shell argument quoting.

Important APIs, types, and functions: `GenerateRandomAlphaOnlyString`, `GenerateRandomASCIIString`, `Ellipsis`, `Truncate`, `InSlice`, `RemoveFromSlice`, private `quote`, and `ShellQuoteArguments`.

Control flow: random generators fill byte slices from allowed character strings using `math/rand/v2`. `Ellipsis` and `Truncate` operate on runes to preserve Unicode code points. Slice helpers use `strings.EqualFold`. Shell quoting leaves simple strings bare and single-quotes complex strings, escaping embedded single quotes with the standard close-escape-open sequence.

State and persistence: no persistence. Random output depends on package-level `math/rand/v2` source.

Dependencies and integration points: depends on `bytes`, `math/rand/v2`, and `strings`. Used by tests and callers needing display truncation or shell-safe command strings.

Risks and edge cases: random generators are not crypto-secure. Rune truncation can split grapheme clusters even though it preserves code points. Shell quoting targets POSIX shell style, not Windows cmd/PowerShell.

Test signals: `stringutils_test.go` checks lengths, rough uniqueness, ASCII-only output, Unicode-safe truncation, case-insensitive membership, and shell quoting.
