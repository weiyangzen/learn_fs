# subset-b-009456 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/json/arm64.json -->
# sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/json/arm64.json

## Purpose

`arm64.json` is the source instruction-description corpus used by syzkaller's ARM64 instruction fuzzer generator. It is a JSON array of 1,218 ARM64 instruction form records, representing 573 distinct `Name` values and many width, scalar, vector, SIMD, load/store, branch, and system variants. The sibling README states that the data is taken from Go's vendored `golang.org/x/arch/arm64/arm64asm/inst.json`, with the sibling LICENSE carrying the upstream license notice.

The file is consumed by `sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/gen.go` through the `//go:generate go run gen/gen.go gen/json/arm64.json generated/insns.go` directive in `arm64.go`. The generator converts each JSON record into an `arm64.Insn` template and writes `generated/insns.go`, whose `init` function registers those templates with the generic `ifuzz/iset` architecture registry.

## Data Model And Important Fields

Every object has exactly these keys: `Name`, `Bits`, `Arch`, `Syntax`, `Code`, and `Alias`.

`Name` is the instruction mnemonic or grouped instruction-family name, for example `ADC`, `ADD (immediate)`, `UQSHRN, UQSHRN2`, or `ZIP1`.

`Bits` is the operationally important field for syzkaller. It is a pipe-delimited 32-bit encoding pattern read left-to-right from bit 31 downward. Literal binary fragments such as `0`, `1`, `00:2`, or `011111:6` become fixed opcode and mask bits. Named fragments such as `Rm:5`, `imm12:12`, `Q`, `size:2`, or `cond:4` become generated `InsnField` entries with a field name, start bit, and length. Parenthesized patterns are accepted by the parser as non-fixed/non-field gaps because `gen.go` skips parsing when the pattern starts with `(`.

`Arch` classifies the variant in human-readable terms. The largest categories include `64-bit variant` with 147 entries, `32-bit variant` with 139, `Vector Vector variant` with 118, `Scalar Scalar variant` with 102, `Vector variant` with 46, and other floating-point, SIMD, load/store, branch, and system forms.

`Syntax`, `Code`, and `Alias` document assembly syntax, pseudocode caveats, and alias relationships from the upstream table. The current syzkaller generator parses these fields into `insnDesc` but does not use them when building the generated instruction templates. In this snapshot, 38 records have non-empty `Code` and 181 have non-empty `Alias`, so a future generator that starts enforcing semantic constraints or alias policy would need to treat these fields as part of the compatibility contract.

## Control Flow Through The Generator

`gen.go` reads this file with `os.ReadFile`, unmarshals it into `[]insnDesc`, and iterates in file order. For each record, `JSONToInsns` initializes `mask`, `opcode`, `curBit`, and an empty field list. It splits `Bits` on `|`, defaults each piece to size 1, parses optional `name:size` pairs, and then either parses a binary literal into fixed opcode/mask bits or records a named variable field.

After each piece, the generator left-shifts `opcode` and `mask` by the piece size, subtracts the size from `curBit`, and conditionally ORs in the fixed literal value and mask. The resulting template stores `Name`, `OpcodeMask`, `Opcode`, `Fields`, and `AsUInt32`. It marks only six exact instruction names as privileged through `isPrivateInsn`: `AT`, `DC`, `IC`, `SYS`, `SYSL`, and `TLBI`. Finally, `serializer.Write` serializes the slice into Go source and `osutil.WriteFileAtomically` writes `generated/insns.go`.

At runtime, the generated `insns.go` imports `arm64`, calls `Register(insns_arm64)` from `init`, and causes `ifuzz/ifuzz.go`'s blank import of `github.com/google/syzkaller/pkg/ifuzz/arm64/generated` to populate `iset.Arches[iset.ArchArm64]`. `Register` appends pseudo ARM64 instructions, indexes every instruction by mode/type through `modeInsns.Add`, and stores the non-pseudo templates for `ParseInsn`.

## State And Persistence Behavior

The JSON itself has no runtime state and no persistence side effects. Its persistent effect is generated code: changing this file and running `go generate` rewrites `sources/test-tools/syzkaller/pkg/ifuzz/arm64/generated/insns.go`. That generated file embeds the instruction templates as Go data and is what normal builds execute unless the `codeanalysis` build tag excludes it.

The order of records is also persistent behavior because `ParseInsn` scans the `templates` slice sequentially and returns the first template whose `(val & OpcodeMask) == Opcode`. Overlapping encodings, aliases, or broad masks can therefore change decode results if record order changes. This is especially relevant because alias metadata is not used to arbitrate duplicates.

## Dependencies And Integration Points

Primary local dependencies are `arm64/gen/gen.go`, `arm64/arm64.go`, `arm64/generated/insns.go`, `arm64/generated/empty.go`, `arm64/pseudo.go`, and the shared `ifuzz/iset` package.

External provenance is Go's `golang.org/x/arch/arm64/arm64asm/inst.json`, as documented by `gen/json/README.md`. License compatibility depends on the sibling `LICENSE` file staying in sync with the imported data source.

The generated data integrates with `Insn.Encode`, `InsnSet.Decode`, and `ParseInsn`. Encoded random templates use `AsUInt32`, initially the fixed opcode bits with variable fields left as zero. Decoding extracts fields using `extractBits` based on the generated `InsnField` metadata.

## Risks And Edge Cases

Malformed JSON causes `json.Unmarshal` to fail, but `JSONToInsns` currently returns `nil` rather than surfacing the error. Because `Register` panics on an empty instruction slice, bad data may fail later and less precisely than the input parsing point.

Malformed `Bits` pieces can panic or silently generate incorrect data. The parser indexes `pattern[0:1]`, assumes total bit widths fit the 32-bit instruction layout, subtracts from an unsigned `curBit`, and does not validate that all pieces sum to exactly 32 bits. A too-long or zero-length pattern could underflow or produce invalid field positions.

Semantic constraints in `Code` are ignored. Examples include entries that say `if immh == '0000' then SEE "Advanced SIMD modified immediate";`; the generator still treats `immh` as an unconstrained variable field. This can create instruction templates that decode broad encodings or generate reserved/undefined combinations.

Alias text is ignored. The JSON includes aliases such as MOV, CMP, CMN, TST, UXTL, and ASR forms, but the generated templates do not distinguish canonical versus alias forms beyond record order. That is acceptable for basic decode coverage but risky if callers later need exact disassembly semantics.

Privilege classification is name-based and narrow. Only six exact names are marked private, while many system-ish instructions such as barriers, exception returns, debug instructions, and trap instructions may still be considered non-private unless represented by those exact names or filtered elsewhere.

Because `Syntax` is unused, changes to syntax-only data do not affect generated behavior. Conversely, reviewers must focus on `Bits` changes when assessing fuzzer behavior.

## Test Signals

`pkg/ifuzz/arm64_test.go` includes decode smoke tests for sample instruction byte streams and uses `iset.Arches["arm64"]`, which indirectly verifies that generated package registration ran. `pkg/ifuzz/arm64/util_test.go` verifies bit extraction used when decoded operands are initialized.

Useful validation commands for this file are `jq length sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/json/arm64.json`, `go test ./pkg/ifuzz/...` from the syzkaller module root, and `go generate ./pkg/ifuzz/arm64` followed by a diff of `generated/insns.go`. A targeted generator test should also assert that every `Bits` pattern sums to 32 and that `JSONToInsns` returns 1,218 templates for the current data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/json/arm64.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/generated/empty.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/arm64/generated/empty.go

## Purpose

`empty.go` is a tiny package-preservation file for `github.com/google/syzkaller/pkg/ifuzz/arm64/generated`. Its only compiled declaration is `package generated`; the preceding comment explains that it exists "To unbreak build with insns.go is excluded by build tags."

The paired generated file, `generated/insns.go`, has the build constraint `// go:build !codeanalysis`. When builds are run with the `codeanalysis` tag, `insns.go` is excluded. Without `empty.go`, the blank import in `pkg/ifuzz/ifuzz.go` would point at a directory with no buildable Go source files, breaking analysis builds even though those builds intentionally omit the large generated instruction table.

## APIs, Types, And Functions

This file exports no API, declares no types, and defines no functions. Its observable API is the continued existence of an importable `generated` package across build-tag configurations.

The package-level behavior differs by tags. In normal builds, `insns.go` is included and its `init` function calls `arm64.Register(insns_arm64)`. In `codeanalysis` builds, only `empty.go` remains, so no registration `init` runs from this package.

## Control Flow

There is no control flow inside this file. Its control-flow significance is negative: it lets compilation continue when `generated/insns.go` is absent. In normal runtime paths, the actual work comes from `insns.go` registering generated ARM64 instruction templates. In `codeanalysis` mode, importing this package has no side effects.

## State And Persistence Behavior

The file has no runtime state and no persistence behavior. It is hand-maintained, not regenerated by `arm64/gen/gen.go`. It should remain stable even when `generated/insns.go` is regenerated from `gen/json/arm64.json`.

The absence of registration in `codeanalysis` builds means global state in `iset.Arches` will not receive ARM64 generated instruction templates from this package under that tag. That is intentional for code-analysis-oriented builds but would be a behavioral problem if someone used `codeanalysis` for runtime fuzzing.

## Dependencies And Integration Points

The direct integration point is `sources/test-tools/syzkaller/pkg/ifuzz/ifuzz.go`, which blank-imports `github.com/google/syzkaller/pkg/ifuzz/arm64/generated` to pull in generated instruction descriptions. `empty.go` keeps that import resolvable when build tags exclude `insns.go`.

The same pattern appears in sibling architecture generated packages for x86, powerpc, and riscv64. This makes `empty.go` part of a repository-wide convention for generated instruction packages that can be compiled out under `codeanalysis`.

## Risks And Edge Cases

Removing this file can break builds using `-tags codeanalysis` with an error equivalent to "build constraints exclude all Go files" for the generated package.

Adding imports or initialization here would be risky because `empty.go` is the only file left in `codeanalysis` builds. Any side effect added here would run specifically in the stripped analysis configuration and could mask the intended absence of generated instruction data.

The copyright year differs across architecture placeholders, but this has no runtime effect. The important invariant is that the file remains buildable under all tag sets that exclude `insns.go`.

## Test Signals

Normal `go test ./pkg/ifuzz/...` exercises the generated registration path through `insns.go`, not the fallback path. The specific signal for this file is a build or test command with the `codeanalysis` tag, such as `go test -tags codeanalysis ./pkg/ifuzz/...` from the syzkaller module root. That should compile the blank import without requiring the generated ARM64 instruction table.

Static checks should verify that the package name stays `generated`, that the file has no build tag excluding it from `codeanalysis`, and that `generated/insns.go` remains guarded by `!codeanalysis`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/arm64/generated/empty.go -->
