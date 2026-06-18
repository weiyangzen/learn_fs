# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 4826-9466

## Scope

This chunk covers a generated section of `encoder_cases_test.go` inside `testCasesSingleEdge`. The assigned range starts in the tail of case 1183, then covers complete cases 1184 through 2342 and the opening of case 2343. All complete cases in this range combine `EncodeLeftCrLfHtVt` with one ordinary single-character encoder mask.

The visible mask groups are:

- `EncodeZero | EncodeLeftCrLfHtVt`: tail of the generated group, 39 visible complete cases in this chunk.
- `EncodeSlash | EncodeLeftCrLfHtVt`
- `EncodeSingleQuote | EncodeLeftCrLfHtVt`
- `EncodeBackQuote | EncodeLeftCrLfHtVt`
- `EncodeLtGt | EncodeLeftCrLfHtVt`
- `EncodeSquareBracket | EncodeLeftCrLfHtVt`
- `EncodeSemicolon | EncodeLeftCrLfHtVt`
- `EncodeExclamation | EncodeLeftCrLfHtVt`
- `EncodeDollar | EncodeLeftCrLfHtVt`
- `EncodeDoubleQuote | EncodeLeftCrLfHtVt`
- `EncodeColon | EncodeLeftCrLfHtVt`
- `EncodeQuestion | EncodeLeftCrLfHtVt`
- `EncodeAsterisk | EncodeLeftCrLfHtVt`
- `EncodePipe | EncodeLeftCrLfHtVt`
- `EncodeHash | EncodeLeftCrLfHtVt`
- `EncodePercent | EncodeLeftCrLfHtVt`: partial group, ending mid-case at the chunk boundary.

Most complete non-boundary groups in this range contain 76 cases each. The generator emits a dense matrix for each leading CR/LF/HT/VT edge character and for each paired punctuation mapping.

## Purpose

The file is generated regression test data for rclone's `lib/encoder` package. Its purpose is to prove that `MultiEncoder.Encode` and `MultiEncoder.Decode` remain reversible when an edge-only rule is combined with another character mapping.

This chunk specifically validates the leading CR/LF/HT/VT rule. With `EncodeLeftCrLfHtVt`, only a leading tab, newline, vertical tab, or carriage return is rewritten to the matching Unicode control-symbol form:

- tab to `␉`
- newline to `␊`
- vertical tab to `␋`
- carriage return to `␍`

If one of those symbol forms is already present at the start of the name, the encoder prefixes it with `QuoteRune` (`‛`) so decode can distinguish a literal symbol from an encoded control byte. The rest of the name is still processed by the paired mask, such as slash to fullwidth slash or percent to fullwidth percent.

## Important APIs, Types, And Data Shapes

The chunk is data rather than executable logic. Each row is a `testCase` value with:

- `mask MultiEncoder`: bitmask selecting the encoder behavior under test.
- `in string`: raw file name input.
- `out string`: expected encoded file name output.

The consuming type and tests are in `encoder_test.go`. `TestEncodeSingleMaskEdge` iterates `testCasesSingleEdge`, runs `tc.mask.Encode(tc.in)`, compares the result with `tc.out`, then decodes that encoded value and requires the original input.

The implementation being tested is in `encoder.go`:

- `MultiEncoder` is a bitmask type whose flags include `EncodeLeftCrLfHtVt` and the punctuation masks visible in this chunk.
- `QuoteRune` is `‛`, used to disambiguate literal encoded forms from forms produced by `Encode`.
- `MultiEncoder.Encode` handles prefix-only replacements before its main rune scan.
- `MultiEncoder.Decode` reverses prefix-only replacements before decoding the rest of the string.
- `FromStandardName`, `ToStandardName`, `FromStandardPath`, and `ToStandardPath` integrate the same encoder with path/name conversion, although this chunk directly exercises only `Encode` and `Decode`.

The generated cases use mixed ASCII, fullwidth punctuation, Greek letters, control-symbol runes, and escaped control bytes. That mix is intentional: it verifies that the target edge byte is special only at the left edge, while identical bytes or symbol forms in the middle or at the right edge stay literal unless the paired mask also requires conversion.

## Control Flow

Runtime control flow for these cases is simple:

1. `go test` runs `TestEncodeSingleMaskEdge`.
2. The test loops across `testCasesSingleEdge`.
3. For each case, the mask's `Encode` method is called on `in`.
4. The encoded result must exactly equal `out`.
5. The test then calls `Decode` on `out`.
6. Decode must return the original `in`.

Within `Encode`, the important branch for this chunk is the prefix-only block. When `EncodeLeftCrLfHtVt` is set and no earlier left-edge rule has already consumed a prefix, it checks `in[0]` for `\t`, `\n`, `\v`, or `\r`. If found, it moves the encoded symbol into `prefix` and removes the byte from `in`. If the first rune is already `␉`, `␊`, `␋`, or `␍`, it moves `‛` plus that rune into `prefix` and removes the rune from `in`.

After prefix handling, `Encode` scans the remaining body for ordinary mappings. The paired masks in this range drive conversions such as `/` to `／`, `'` to `＇`, `;` to `；`, `!` to `！`, `#` to `＃`, and `%` to `％`. Existing destination characters are quoted when that paired mask is enabled, so a literal fullwidth slash, fullwidth percent, or control-symbol character can survive a decode round trip.

`Decode` performs the inverse prefix handling. A leading `␉`, `␊`, `␋`, or `␍` becomes the corresponding control byte. A leading `‛` followed by one of those symbols becomes the literal symbol. It then decodes the rest of the body according to the same mask.

## State And Persistence Behavior

There is no runtime persistence in this chunk. The table is static generated Go source committed under the rclone source tree. The only state it affects is transient test process memory while `go test` iterates the cases.

The durable source of truth is the generator in `lib/encoder/internal/gen/main.go`. The file header marks `encoder_cases_test.go` as generated by that program. Regeneration rewrites this file from the generator's mask lists, edge definitions, random seed, and string-building helpers.

Because this range is part of a large generated table, line numbers and case numbers are not stable under generator changes. The behavioral contract is the mask combination and edge matrix, not any specific random filler string.

## Dependencies And Integration Points

Primary dependencies and integration points:

- `encoder.go`: defines `MultiEncoder`, `EncodeLeftCrLfHtVt`, all punctuation masks in this chunk, `QuoteRune`, and encode/decode behavior.
- `encoder_test.go`: defines `testCase` and `TestEncodeSingleMaskEdge`, the direct consumer of these rows.
- `lib/encoder/internal/gen/main.go`: generates this data from `allEdges`, `allMappings`, `maskBits`, and `buildEdgeTestString`.
- Go's `testing` package: subtests are named with the numeric table index, so failures point back to generated case numbers such as 1184 or 2327.
- rclone backend code indirectly depends on `lib/encoder` through filesystem name/path encoding. A regression here can surface as remote filename corruption on backends that reject leading control characters or punctuation.

The generator's `allEdges` entry for `EncodeLeftCrLfHtVt` defines the edge originals as `\t`, `\n`, `\v`, and `\r`, with replacements calculated as `␀` plus the same control value. The visible test groups are produced by pairing that edge with each eligible single-character mapping. The generator deliberately skips invalid combinations where `EncodeCtl` or `EncodeCrLf` would overlap with left/right CR/LF/HT/VT edge handling.

## Risks And Maintenance Notes

- The assigned range starts and ends inside generated cases. Chunk-local parsing as standalone Go would fail, but the full file is valid generated Go source.
- Prefix precedence matters. `EncodeLeftCrLfHtVt` only runs if earlier left-edge rules did not set `prefix`. Future changes to left-edge ordering can alter behavior for combined masks.
- Decode correctness depends on quoting. Without `‛` before literal leading `␉`, `␊`, `␋`, or `␍`, decode would turn a literal symbol into an actual control byte.
- Body handling must not apply the left-edge rule away from the first rune. This chunk contains repeated cases with the same CR/LF/HT/VT byte or symbol at interior and trailing positions to catch over-broad replacement logic.
- Ordinary punctuation encoding must still run after prefix extraction. Cases such as `EncodeSlash | EncodeLeftCrLfHtVt` and `EncodePercent | EncodeLeftCrLfHtVt` verify that leading control handling does not short-circuit body mappings.
- Generated data is hard to audit manually. The safer maintenance workflow is to modify `internal/gen/main.go`, regenerate, and inspect representative group boundaries and failing case numbers rather than editing individual rows.
- The strings include raw control bytes, Unicode symbol-for-control characters, and fullwidth characters. Tooling that normalizes Unicode or trims control characters could silently damage these fixtures.

## Test Signals

Strong validation signals for this chunk are:

- `go test ./lib/encoder` passes, especially `TestEncodeSingleMaskEdge`.
- A failure reports the generated table index and shows `Encode(%q)` or `Decode(%q)` mismatches, making the exact row traceable in `encoder_cases_test.go`.
- Representative cases from each group show these invariants:
  - leading `\t`, `\n`, `\v`, or `\r` is replaced by `␉`, `␊`, `␋`, or `␍`;
  - leading `␉`, `␊`, `␋`, or `␍` is quoted as `‛␉`, `‛␊`, `‛␋`, or `‛␍`;
  - the same control byte or symbol away from the first rune is not handled by the left-edge rule;
  - paired punctuation masks still convert and quote their own source/destination runes in the body;
  - `Decode(Encode(in)) == in` for every row.

For regression work, the most useful focused tests are a small table around each leading control byte plus one paired mask with destination quoting, then the full generated `TestEncodeSingleMaskEdge` suite to catch matrix-level interactions.
