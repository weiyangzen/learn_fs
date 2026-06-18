# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 23306-27672

## Scope

This chunk is a generated segment of `testCasesDoubleEdge`, the large table consumed by `TestEncodeDoubleMaskEdge` in `lib/encoder/encoder_test.go`. The exact slice starts at the tail of case 1141, contains complete generated cases 1142 through 2232, and ends with the delimiter that opens case 2233. The substantive cases in this span exercise `MultiEncoder.Encode` and `MultiEncoder.Decode` round-trips for combinations of one ordinary character-mapping flag plus two edge-only flags.

## Purpose

The table verifies that edge encoders only affect the configured leading or trailing position while ordinary encoders continue to map or quote their characters across the non-edge body of the filename. In this chunk, the dominant edge focus shifts from leading period to leading tilde:

- `EncodeLeftPeriod` maps a leading `.` to `．` and quotes an already encoded leading `．` as `‛．`.
- `EncodeLeftTilde` maps a leading `~` to `～` and quotes an already encoded leading `～` as `‛～`.
- `EncodeLeftCrLfHtVt` maps only leading tab, line feed, vertical tab, and carriage return to the matching Unicode control-symbol runes.
- `EncodeRightSpace`, `EncodeRightPeriod`, and `EncodeRightCrLfHtVt` are paired with `EncodeLeftPeriod` in the middle of the chunk to prove independent prefix/suffix handling.

The generated strings deliberately include random fullwidth characters, Greek letters, ASCII punctuation, NUL bytes, DEL bytes, control characters, and pre-encoded Unicode forms. That mix makes each case a regression signal for both collision avoidance and reversibility.

## Important APIs, Types, and Functions

- `type MultiEncoder uint` is the bitmask under test. Each `mask:` expression in this chunk combines flags such as `EncodeSquareBracket | EncodeLeftPeriod | EncodeLeftCrLfHtVt`.
- `type testCase struct { mask MultiEncoder; in string; out string }` defines each generated fixture.
- `MultiEncoder.Encode(string) string` is expected to transform `in` into `out`.
- `MultiEncoder.Decode(string) string` is expected to invert `out` back to `in`.
- `TestEncodeDoubleMaskEdge` iterates over `testCasesDoubleEdge`, calling both `Encode` and `Decode` for every case.
- `internal/gen/main.go` owns generation. Its `allEdges` table defines the edge mappings, and the `buildEdgeTestString` path creates both edge-position and non-edge-position variants.

## Case Coverage in This Chunk

The complete cases in this slice cover 1091 mask entries. The first covered group finishes the `EncodeSquareBracket | EncodeLeftPeriod | EncodeLeftCrLfHtVt` block, checking square bracket quoting/mapping while a leading period and leading CR/LF/HT/VT compete for prefix ownership.

The next major groups pair `EncodeLeftPeriod | EncodeLeftCrLfHtVt` with ordinary mapping flags:

- `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, and `EncodeDel`.
- These groups show that if `.` is the first character, `EncodeLeftPeriod` wins and the subsequent tab/newline/vertical-tab/carriage-return remains body content. If the first rune is already `．`, the output is quoted as `‛．`.
- Body characters still follow their ordinary flag rules, for example `]` to `］`, `%` to `％`, `*` to `＊`, `|` to `｜`, DEL to `␡`, and pre-encoded counterparts quoted with `‛`.

The middle section pairs `EncodeLeftPeriod` with right-edge encoders:

- With `EncodeRightSpace`, trailing ASCII space becomes `␠` and trailing `␠` is quoted, while an interior or non-leading period is unchanged.
- With `EncodeRightPeriod`, only the final `.` becomes `．`; final `．` is quoted. The leading-period mapping remains independent.
- With `EncodeRightCrLfHtVt`, trailing tab, line feed, vertical tab, and carriage return become their control-symbol forms, while pre-encoded trailing symbols are quoted.

The latter section switches to `EncodeLeftTilde`:

- `EncodeLeftTilde | EncodeLeftSpace` and `EncodeLeftTilde | EncodeLeftPeriod` verify edge precedence. The encoder implementation processes left-space first, then left-period, then left-tilde only if no earlier prefix was taken. The cases confirm that a leading space or period can consume the prefix slot and leave a following `~` unchanged.
- `EncodeLeftTilde | EncodeLeftCrLfHtVt` exercises the same precedence with leading tab/newline/vertical-tab/carriage-return. Cases beginning with `~` map to `～`; cases beginning with `～` quote to `‛～`; cases where the tilde appears after a control character leave the tilde as non-edge content.
- Ordinary flags paired with `EncodeLeftTilde` include `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, and `EncodeCtl` depending on the edge-pair family.

## Control Flow

At test runtime, `TestEncodeDoubleMaskEdge` performs a linear table walk. For each row, the mask is assigned to `e`, `e.Encode(tc.in)` must equal `tc.out`, and then `e.Decode(got)` must equal the original input. Failures identify the table index in a subtest name.

At encoder runtime, the relevant `Encode` control flow is:

1. Return unchanged for `EncodeRaw` or empty input.
2. Handle special `EncodeDot` names, which this chunk does not directly target.
3. Build a `prefix` by testing left-edge flags in fixed order: left space, left period, left tilde, then left CR/LF/HT/VT. Only one prefix edge transform is applied because each later edge check requires `prefix == ""`.
4. Build a `suffix` by testing right-edge flags in fixed order: right space, right period, then right CR/LF/HT/VT.
5. If no prefix or suffix was applied, find the first body rune that needs encoding. If a prefix or suffix exists, skip this early no-op optimization and scan the remaining body.
6. Emit the prefix, encoded body, and suffix. Body encoding handles NUL, quote rune, fullwidth collision quoting, control-symbol collision quoting, and each enabled ordinary flag.

This chunk specifically stresses steps 3 and 4, especially the single-prefix rule and independence between prefix and suffix processing.

## State and Persistence Behavior

There is no runtime persistence, filesystem mutation, or global state modified by these cases. The source file itself is generated and deterministic from `internal/gen/main.go` using a fixed default random seed. The only state exercised by tests is local per-case string transformation state: selected prefix, selected suffix, and the body scan buffer inside `MultiEncoder.Encode`; `Decode` must reconstruct the original input without consulting external state.

## Dependencies and Integration Points

- Depends on the encoder package constants and `MultiEncoder` implementation in `lib/encoder/encoder.go`.
- Integrated into Go tests through `encoder_cases_test.go` and `encoder_test.go`; because both files are in package `encoder`, the unexported `testCase` type and generated variables are directly visible.
- Generated by `lib/encoder/internal/gen/main.go`; manual edits would be overwritten by `go generate`.
- The broader rclone integration is filename normalization for backends with restrictive file-name rules. These edge rules protect platforms that reject leading/trailing whitespace, periods, tildes, or control characters while preserving reversibility.

## Risks and Invariants

- Edge precedence is an invariant: only one left-edge transformation may occur. Reordering `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, or `EncodeLeftCrLfHtVt` would change outputs in this chunk.
- Prefix and suffix logic must not accidentally encode interior occurrences of edge-only characters. Many cases place `.`, `~`, `．`, `～`, spaces, and control-symbol runes near but not at the relevant edge.
- Collision quoting is critical. Existing encoded forms such as `．`, `～`, `␠`, control-symbol runes, and fullwidth punctuation must be prefixed with `QuoteRune` when the active flag would otherwise make encoded and raw names ambiguous.
- Ordinary mappings must still run when an edge prefix or suffix was already consumed. The body scan path after prefix/suffix selection is therefore covered by combinations like left-period plus square bracket or left-tilde plus percent.
- The generated table is large and easy to desynchronize from `encoder.go`; changes to mappings, mask names, or edge precedence require regenerating this file and reviewing the whole generated diff.
- This chunk begins and ends on generated table boundaries rather than semantic boundaries, so merge/reconciliation should account for case 1141 and case 2233 being split across adjacent chunks.

## Test Signals

Strong test signal comes from round-trip assertions over randomly mixed strings and explicit edge placements. A failure in this chunk usually points to one of these behaviors:

- `EncodeLeftPeriod` or `EncodeLeftTilde` no longer maps or quotes only the first rune.
- `EncodeLeftCrLfHtVt` or `EncodeRightCrLfHtVt` mishandles one of tab, newline, vertical tab, or carriage return.
- Right-edge encoders accidentally run before, instead of after, left-edge trimming of the working string.
- Body mappings are skipped when a prefix or suffix was present.
- `Decode` cannot distinguish raw fullwidth/control-symbol input from encoded output because quote handling changed.

The direct validation command for this source area is:

```bash
cd sources/user-network-fs/rclone
go test ./lib/encoder
```
