<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/sanitize.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/sanitize.go

## Purpose

Sanitizes untrusted remote strings before display in web UIs, terminals, or logs.

## Important APIs, Types, and Functions

`CleanAndTrim(str string) string` replaces Unicode control (`Cc`), format (`Cf`), and surrogate (`Cs`) runes with replacement characters, trims surrounding whitespace, and limits output to `maxRunes` 128 runes.

## Control Flow

The function builds a rune slice, replacing problematic categories and preserving other runes, including private-use characters. It trims whitespace after replacement, then truncates by rune count.

## State and Persistence Behavior

Pure string transformation. No persistence.

## Dependencies and Integration Points

Uses standard `strings` and `unicode`. `id.go` uses it for peer protocol IDs and agent versions returned from peerstore.

## Risks and Edge Cases

Length limiting is by runes, while pin-name validation elsewhere is by bytes. Replacement instead of deletion preserves evidence of unsafe input but may affect visual length. Whitespace introduced before invalid characters is trimmed after replacement.

## Test Signals

No direct test in this subset. Good tests would cover terminal escape controls, bidirectional format characters, long Unicode strings, private-use preservation, and whitespace trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdutils/sanitize.go -->
