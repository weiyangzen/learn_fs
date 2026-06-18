<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env_test.go

## Purpose

Tests non-printable and backslash escaping used before displaying potentially unsafe strings.

## Important APIs, Types, and Functions

`TestEscNonPrint` exercises `needEscape`, `EscNonPrint`, and helper `hasNonPrintable`.

## Control Flow

The test injects byte `0x7f` into a string, asserts it needs escaping, checks the escaped result has no non-printable runes, verifies backslashes are escaped, and confirms plain strings and quotes are left alone except embedded escaped backslashes.

## State and Persistence Behavior

Pure string tests; no persistent state.

## Dependencies and Integration Points

Uses `strconv.IsPrint` in the test helper, matching production expectations for printable characters.

## Risks and Edge Cases

The test does not cover all Unicode categories, terminal escape sequences, or invalid UTF-8 replacement behavior. It focuses on the `strconv.Quote` based escaping path.

## Test Signals

Good signal for the common display sanitization path. Additional coverage could include control ranges, multi-byte Unicode, and strings with both quotes and backslashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env_test.go -->
