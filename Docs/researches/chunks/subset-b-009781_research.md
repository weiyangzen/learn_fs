# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 1-4825

## Scope

This chunk covers the opening segment of rclone's generated encoder test-case table. The source begins with the generator notice and package declaration, then defines:

- all of `testCasesSingle`, cases `0` through `19`;
- the beginning of `testCasesSingleEdge`, cases `0` through `1182` complete and the opening of case `1183`.

The assigned range ends inside the `testCasesSingleEdge` literal at line 4825, after the `mask: EncodeZero | EncodeLeftCrLfHtVt` line for case `1183`. Later lines in the same source file continue that case, finish `testCasesSingleEdge`, and define `testCasesDoubleEdge`; those later tables are outside this chunk.

## Purpose

`encoder_cases_test.go` is generated test data for `lib/encoder`. It supplies deterministic `testCase` literals consumed by `encoder_test.go` to verify that `MultiEncoder.Encode` maps restricted filename characters to safe Unicode substitutes and that `MultiEncoder.Decode` reverses the transformation exactly.

This chunk focuses on two classes of coverage:

- Single-mask coverage: each individual character-class flag with a mixed string containing raw characters, already-encoded Unicode equivalents, control bytes, fullwidth characters, and ordinary filler.
- Single-edge coverage: one ordinary encodable mask combined with one left-edge flag, exercising leading-only substitutions while making sure identical characters away from the leading edge are not incorrectly transformed.

The file protects rclone backends that must translate names for storage systems with filename restrictions, especially systems that reject NUL, slash, Windows-reserved punctuation, leading spaces/periods/tildes, control characters, or ambiguous already-encoded forms.

## Important APIs, Types, And Data

The generated data uses the `testCase` type from `encoder_test.go`:

- `mask MultiEncoder`: bitmask selecting encoding behavior.
- `in string`: raw filename input.
- `out string`: expected encoded filename.

The masks referenced in this chunk are `MultiEncoder` constants from `encoder.go`:

- Core printable/control masks: `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, and `EncodeCtl`.
- Left-edge masks: `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, and `EncodeLeftCrLfHtVt`.

The expected outputs demonstrate the encoder's substitution alphabet:

- `QuoteRune` is `‛`; it disambiguates an input that already contains an encoded substitute.
- Many printable ASCII restrictions map to fullwidth equivalents, such as `/` to `／`, `:` to `：`, `?` to `？`, `*` to `＊`, `|` to `｜`, `\` to `＼`, and quotes/brackets/semicolons/exclamation marks to their fullwidth forms.
- NUL maps to `␀`; control characters can map into the Unicode control-picture block such as `␉`, `␊`, `␋`, and `␍`.
- Leading space maps to `␠`, leading period to `．`, leading tilde to `～`, and leading CR/LF/HT/VT to their control-picture forms.

Within lines 1-4825, the mask distribution is systematic: each ordinary encodable mask appears once in `testCasesSingle`, then most ordinary masks are paired with each visible left-edge mask for repeated edge-position cases. The range reaches deeper into `EncodeZero | EncodeLeftCrLfHtVt` than the earlier edge groups and is truncated before that group is complete.

## Control Flow

This file has no executable control flow of its own. It is a package-level set of Go composite literals. Runtime control flow comes from `encoder_test.go`:

1. `TestEncodeSingleMask` iterates over `testCasesSingle`.
2. For each case, it constructs `e := tc.mask`, calls `e.Encode(tc.in)`, and checks the result equals `tc.out`.
3. It then calls `e.Decode(got)` and checks that decoding returns the original `tc.in`.
4. `TestEncodeSingleMaskEdge` repeats the same Encode/Decode round-trip assertion over `testCasesSingleEdge`.

The product control path under test is `MultiEncoder.Encode` and `MultiEncoder.Decode` in `encoder.go`. For edge masks, `Encode` first peels off at most one qualifying prefix, then at most one qualifying suffix, and only then scans the remaining middle string for normal character substitutions. This ordering matters for the cases in this chunk: a leading already-encoded marker such as `␠`, `．`, `～`, or `␊` must be quoted when it sits at the protected edge, but the same rune inside the middle or at the opposite edge should usually remain unchanged unless another selected mask applies.

## State And Persistence Behavior

The chunk is static generated test data. It does not read files, write files, allocate durable state, access environment variables, or persist runtime state. Its only state is the compiled in-memory slices created when Go builds the `encoder` package tests.

The persistence risk is source-level rather than runtime-level: because the file is generated by `lib/encoder/internal/gen/main.go`, manual edits to individual cases can be overwritten by `go generate` and can also create drift between the generator and committed test data.

## Dependencies And Integration Points

Primary integration points:

- `lib/encoder/encoder_test.go`: defines `testCase` and consumes `testCasesSingle` and `testCasesSingleEdge`.
- `lib/encoder/encoder.go`: defines `MultiEncoder`, mask constants, `QuoteRune`, `Encode`, and `Decode`.
- `lib/encoder/internal/gen/main.go`: generator that writes this file. The visible generation logic writes `testCasesSingle`, then `testCasesSingleEdge`, using deterministic random strings and edge-case expansion.
- Backend encoding declarations elsewhere in rclone depend on the same `MultiEncoder` behavior to make remote filenames legal while preserving round-trip identity.

The generated strings intentionally include non-ASCII filler, fullwidth characters, control-picture characters, raw control bytes, DEL/NUL, and already-encoded variants. That gives the tests signal for Unicode handling and quote disambiguation without needing each backend to reproduce these combinations.

## Risks And Maintenance Notes

- The file is generated and very large. Hand-editing individual literals is fragile; generator changes should be preferred when behavior changes.
- Chunk boundaries are not Go-syntax boundaries. This assigned range ends inside case `1183`, so this chunk must be merged with later chunks before treating the source file as a complete table.
- The tests assert exact byte/string outputs. Any change to `QuoteRune`, fullwidth mappings, control-picture mappings, or edge-prefix/suffix priority will cause many failures.
- Edge masks are subtle because they only apply at the beginning or end of a name, while ordinary masks apply throughout the remaining string. Reordering prefix/suffix processing or middle scanning can break cases where the same rune appears at multiple positions.
- Already-encoded forms are deliberately quoted at protected positions. Removing quote behavior would make Decode ambiguous and can lose information for filenames that originally contained fullwidth/control-picture characters.
- The generated cases include raw control bytes and escape sequences in Go string literals. Tooling that normalizes text, rewrites Unicode, or changes escapes could alter test meaning.

## Test Signals

Strong validation signals for this chunk are:

- `go test ./lib/encoder` from the rclone source tree passes `TestEncodeSingleMask` and `TestEncodeSingleMaskEdge`.
- Regenerating with `go generate ./lib/encoder` produces the same case ordering and expected outputs for this range.
- Representative single-mask failures identify the exact mask name and case index, making regressions local to one mapping class.
- Representative edge failures show whether the bug is in leading-space, leading-period, leading-tilde, or leading-CR/LF/HT/VT handling.
- Decode round-trip assertions pass for both raw restricted characters and inputs that already contain their encoded Unicode counterparts.

This chunk's main research signal is that it is not independent business logic; it is a generated oracle for the encoder's reversible filename mapping contract.
