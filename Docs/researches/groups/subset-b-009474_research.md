# Research Group subset-b-009474

Grouped research for syzkaller x86 ifuzz generator sources. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/gen/gen.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/x86/gen/gen.go

## Purpose

`gen.go` is the x86 instruction-table generator for syzkaller's instruction fuzzer. It reads Intel XED-derived instruction records from `gen/all-enc-instructions.txt` and emits `generated/insns.go`, a Go source file containing serialized `[]*x86.Insn` templates plus an `init` hook that registers those templates with `pkg/ifuzz/x86`.

The generator is wired through `sources/test-tools/syzkaller/pkg/ifuzz/x86/x86.go` via `//go:generate go run gen/gen.go gen/all-enc-instructions.txt generated/insns.go`. Normal builds then include the generated table under the `!codeanalysis` build tag, while analysis builds rely on the sibling `generated/empty.go` stub.

## Important APIs, Types, And Functions

The executable entry point is `main()`. It validates the two-argument CLI contract, opens the XED table input, scans records, builds `*x86.Insn` values, deduplicates them, serializes the final slice with `serializer.Write`, and writes the generated file atomically with `osutil.WriteFileAtomically`.

`parsePattern(insn *x86.Insn, vals []string) error` is the primary parser. It converts XED `PATTERN` tokens into x86 instruction template fields: opcode bytes, suffix bytes after ModRM, ModRM presence and fixed or wildcard `Mod`/`Reg`/`Rm` values, embedded register selection (`Srm`), lock/rep/operand-size prefixes, immediates, VEX/XOP encoding fields, REX.W policy, supported CPU modes, and prefix exclusion flags.

`parseOperands(insn *x86.Insn, vals []string) error` handles the subset of `OPERANDS` metadata that affects encoding. It marks segment-register ModRM operands with `Reg = -6`, control-register operands with `Reg = -8` and `NoSibDisp`, debug-register operands with `NoSibDisp`, and fixed 16-bit or 32-bit memory operands with `Mem16` or `Mem32`.

`parseModrm(v string) (int8, error)` parses XED-style bit selectors such as `[0b11]`, `[mm]`, `[rrr]`, and `[nnn]` into fixed small integers or `-1` for wildcard fields. `addImm(insn *x86.Insn, imm int8)` records the first and second immediate sizes in `Insn.Imm` and `Insn.Imm2`, panicking if a third immediate is encountered.

`errSkip` is a sentinel error type for intentionally skipped instruction forms. `main` treats it differently from malformed input: non-empty skip reasons are logged to stderr and counted, while true parser errors abort through `tool.Failf`.

The generated output imports `. "github.com/google/syzkaller/pkg/ifuzz/x86"` and calls `Register(insns)` from `init()`. The target data model is `x86.Insn`, whose fields include `Name`, `Extension`, `Mode`, `Priv`, opcode/prefix/suffix byte slices, ModRM selectors, immediate sizes, VEX metadata, and special memory/addressing flags.

## Control Flow

The scan loop strips comments after `#`, trims whitespace, joins continuation lines ending in `\`, and treats `{` and `}` as record delimiters. Attributes inside a record are split at the first colon and then space-tokenized.

`ICLASS`, `CPL`, and `EXTENSION` populate record-wide instruction metadata. `CPL: 0` marks `Priv`; selected AVX/FMA/BMI/XOP extensions restrict `Mode` to long-64 and protected-32 modes; `AVX2GATHER` also sets `Avx2Gather`.

Each `PATTERN` starts a new variant. If a prior variant is pending, it is appended before cloning the record-wide base `Insn`. `parsePattern` then walks the pattern tokens. Hex tokens become opcode bytes until a ModRM token is seen and suffix bytes afterward. Binary opcode fragments are accepted in the special `0b...._...` shape. ModRM tokens set `Modrm` and selectors, immediate tokens record fixed or mode-dependent sizes, VEX tokens fill `Vex`, `VexMap`, `VexP`, `VexL`, and `VexNoR`, and mode/prefix tokens refine compatibility and prefix behavior. Unknown pattern tokens return `errSkip`, so unsupported XED features are skipped instead of partially generated.

`OPERANDS` is parsed only when a valid pending pattern exists. Operand failures also skip that pending variant.

After scanning, `main` performs a deduplication pass. AVX512 VEX/EVEX extensions are skipped. Remaining instructions are compared with `reflect.DeepEqual` against previously accepted templates, iterating the accepted list backwards. The pass normalizes equivalent `Mod=3` and `Mod=-3` forms through `Mod=-1` when necessary, so register-only and memory-only duplicates can collapse into a single wildcard form.

The final control step writes a generated Go file containing a `!codeanalysis` build tag, `package generated`, a registration `init`, and the serialized instruction slice. Stderr receives deduplication and handled/skipped counts.

## State And Persistence Behavior

The generator has no long-lived runtime state beyond the process-local `insns`, `skipped`, continuation-line buffer, and current record/variant pointers. Its persistent effect is the generated `sources/test-tools/syzkaller/pkg/ifuzz/x86/generated/insns.go` file.

Generated `insns.go` is the runtime state source for x86 ifuzz registration. When imported through `pkg/ifuzz/ifuzz.go`'s blank import of `github.com/google/syzkaller/pkg/ifuzz/x86/generated`, its `init` function calls `x86.Register(insns)`. `Register` appends pseudo instructions, indexes templates by mode and type with `iset.ModeInsns.Add`, and stores the resulting `InsnSet` in `iset.Arches[iset.ArchX86]`.

The output is intended to be deterministic for a fixed input table, Go version, serializer behavior, and parser code. `osutil.WriteFileAtomically` avoids leaving a partially written generated file if the write fails.

## Dependencies And Integration Points

Input dependency is the checked-in XED-derived `gen/all-enc-instructions.txt` table. The parser is tightly coupled to XED token spelling for `ICLASS`, `CPL`, `EXTENSION`, `PATTERN`, and `OPERANDS`.

Important local Go dependencies are `pkg/ifuzz/x86` for the `Insn` schema and registration API, `pkg/ifuzz/iset` for mode constants, `pkg/serializer` for Go literal emission, `pkg/osutil` for atomic writes, and `pkg/tool` for fail-fast CLI diagnostics.

Runtime integration flows through `generated/insns.go`, `generated/empty.go`, `ifuzz/ifuzz.go` blank imports, and `iset.Arches`. Downstream encoder/decoder behavior depends on fields filled here, including ModRM wildcard values, immediate-size sentinel values, VEX fields, prefix suppression flags, and mode masks.

The file also has a maintenance relationship with sibling architecture generators. Like ARM64, PowerPC, and RISC-V generated packages, x86 generated output is excluded by `codeanalysis`, with a package stub left behind for buildability.

## Risks And Edge Cases

The parser is intentionally incomplete. Many XED tokens are accepted as no-ops "to unbreak build", while unknown tokens skip an instruction form. This keeps generation moving but can silently reduce instruction coverage when new XED patterns appear.

Sentinel values are dense and easy to misuse. `Mode` is a bitmask; `Mod`, `Reg`, and `Rm` use negative values for wildcard and special register classes; `Imm` uses negative values for mode-dependent sizes; `VexP` starts at `-1`. A wrong sentinel can produce invalid encodings or over-broad templates.

Mode and prefix handling is approximate in several branches. Comments note that `eosz16`, `eosznot64`, and `REP!=3` may affect REP or `0x66` handling but are currently ignored. That can matter for exact instruction validity even if fuzzing coverage remains useful.

Deduplication mutates `insn.Mod` during comparison and restores it after each comparison. The current code accounts for this, but future changes around `reflect.DeepEqual` or shared pointer fields could make equality decisions fragile.

`reportError` is meant to preserve source-line context, but in non-skip pattern and operand errors it calls `reportError(errSkip.Error())` on a zero-value sentinel instead of the actual error. That appears to be a diagnostic bug: malformed input may abort with an empty message after printing the line.

The generator does not check `s.Err()` after scanner iteration. Extremely long input lines or I/O errors could be missed unless they also lead to parse failures.

## Test Signals

Core validation is `go generate ./pkg/ifuzz/x86` from the syzkaller module root followed by a clean diff for `generated/insns.go`. The stderr counts for "deduped", "handled", and "skipped" are useful golden signals for parser drift.

Build and runtime validation should include `go test ./pkg/ifuzz/...` in normal mode, which exercises package registration and x86 encode/decode paths through the generated table. A `go test -tags codeanalysis ./pkg/ifuzz/...` build checks that the generated table can be excluded without breaking imports.

Focused generator tests would cover representative tokens: fixed and wildcard ModRM, suffix bytes after ModRM, two immediates, VEX/XOP map and prefix fields, mode narrowing, `MOD!=3` normalization, segment/control-register operands, and known skip cases such as `NOP5` through `NOP9`.

Regression tests should also assert that malformed pattern or operand input reports the actual parse error, because the current error path likely loses that message.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/gen/gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/generated/empty.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/x86/generated/empty.go

## Purpose

`empty.go` is a minimal package-preservation file for `sources/test-tools/syzkaller/pkg/ifuzz/x86/generated`. Its comment states that it exists "To unbreak build with insns.go is excluded by build tags."

The paired generated file, `generated/insns.go`, is guarded by `//go:build !codeanalysis`. When the `codeanalysis` build tag is active, `insns.go` is excluded. `empty.go` remains buildable so imports of `github.com/google/syzkaller/pkg/ifuzz/x86/generated` still resolve even though the large generated instruction table is intentionally absent.

## Important APIs, Types, And Functions

This file declares only `package generated`. It exports no API, defines no types, has no variables, has no imports, and has no `init` function.

Its observable contract is structural rather than functional: the `generated` package must exist in all relevant build-tag configurations. In normal builds, `insns.go` supplies the functional API through an `init` function that calls `x86.Register(insns)`. In `codeanalysis` builds, this stub supplies a no-op package.

## Control Flow

There is no control flow inside the file. Importing the package when only `empty.go` is included performs no work.

The important control-flow distinction is build-tag driven. Without `codeanalysis`, the generated table file is included and package import triggers registration of x86 instruction templates. With `codeanalysis`, `empty.go` is the only package file, so import has no side effect and no generated instruction registration occurs.

## State And Persistence Behavior

`empty.go` has no runtime state and no persistence side effects. It does not read files, write files, register instructions, or mutate global variables.

Because no `init` function runs from this stub, `iset.Arches[iset.ArchX86]` will not be populated by the generated x86 package in a `codeanalysis` build. That absence is intentional for analysis-oriented builds that exclude large generated artifacts, but it would be a functional limitation for any runtime fuzzing command accidentally built with that tag.

The file is hand-maintained and should not be overwritten by `pkg/ifuzz/x86/gen/gen.go`; the generator writes `generated/insns.go` instead.

## Dependencies And Integration Points

There are no direct imports. The integration point is the package directory itself, especially the blank import in `sources/test-tools/syzkaller/pkg/ifuzz/ifuzz.go` that pulls in `github.com/google/syzkaller/pkg/ifuzz/x86/generated` for side-effect registration in normal builds.

This file follows the same generated-package stub convention used by sibling architectures such as ARM64, PowerPC, and RISC-V. The convention pairs a `!codeanalysis` generated table with an untagged empty package file.

## Risks And Edge Cases

Removing this file can break `-tags codeanalysis` builds with an error equivalent to "build constraints exclude all Go files" for the generated x86 package.

Adding imports, variables, or initialization here would be risky because those additions would run specifically in the stripped build configuration where generated instruction data is meant to be absent. The safest invariant is that the file stays as a package declaration only.

Tests or tools that expect x86 instructions to be registered must avoid the `codeanalysis` tag or explicitly account for the no-op generated package under that tag.

## Test Signals

The targeted signal for this file is a successful build or test with the `codeanalysis` tag, such as `go test -tags codeanalysis ./pkg/ifuzz/...` from the syzkaller module root. That validates that blank imports of x86 generated metadata remain resolvable when `insns.go` is excluded.

Normal `go test ./pkg/ifuzz/...` validates the opposite path: `generated/insns.go` is included, `init` runs, and x86 instruction metadata registers with `iset.Arches`. Static checks should ensure `empty.go` has no build constraint excluding it from `codeanalysis` builds and that its package name remains `generated`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/generated/empty.go -->
