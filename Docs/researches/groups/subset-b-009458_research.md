# subset-b-009458 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa30_to_syz -->
# sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa30_to_syz

## Purpose

`powerisa30_to_syz` is a Python 3 code generator for syzkaller's PowerPC instruction fuzzer metadata. It consumes a Power ISA 3.0 PDF and emits Go source for package `generated`, registering a sorted `[]*powerpc.Insn` table with opcode, mask, privilege, and operand field metadata. The generated Go is intended for `github.com/google/syzkaller/pkg/ifuzz/powerpc` and is excluded when the `codeanalysis` build tag is active.

The generator is tailored to the formatting of a specific Power ISA 3.0 PDF. It extracts the "Instruction Set Sorted by Opcode" table, resolves each variable instruction to its detailed instruction-format page, reconstructs fixed opcode bits and operand bit ranges, and prints Go struct literals.

## Important APIs, types, and functions

This file is an executable script rather than an importable module, but its major internal APIs are:

- `add_stat(m, s)` and `add_fmt_ins(m, fmt, ins)`: small aggregation helpers for stderr summary statistics by format, privilege, mode, and mnemonic.
- `read_pdf_page(pnum, store=False)`: page extraction and normalization layer. It calls an external `pdftotext`, caches page text in `pagecache`, optionally splits two-column instruction pages into logical rows, removes empty and `[Phased-Out]` lines, writes debug extraction data to `outp`, and returns normalized text lines.
- `find_pdf_pagenumber_offset()`: scans physical PDF pages 15 through 99 to discover the logical-to-physical page offset and the logical page range containing the sorted opcode table.
- `add_mode_priv(mode, priv)`: converts Power ISA privilege/mode text into a Go `Priv: true` field when privilege contains `P` or `H`.
- `ppcmask(val, s, l)`: maps Power ISA bit numbering, where bit 0 is the most significant bit, to a 32-bit integer mask/value position.
- `do_sorted_opcodes(fmt_map, ins_stat)`: the core generator. It parses opcode summary rows, resolves detailed instruction layouts, applies manual fixups, builds `Opcode`, `Mask`, and `[]powerpc.InsnField` literals, prints sorted instruction records, and returns the emitted instruction count.

Global constants and state are also important. `pdf2txt` is hard-coded to `/home/aik/xpdf-4.03/build/xpdf/pdftotext`; `isa_pdf` is `sys.argv[1]`; `isa_pagenum_correction` contains mnemonic-specific page corrections for known PDF index drift; `pagecache` memoizes normalized pages; and the global file handle `f = open("outp", "w+")` receives extraction traces.

## Control flow

The script starts by reading the ISA PDF path from `sys.argv[1]`. If `sys.argv[2:5]` are present, it treats them as explicit `pageoffset`, `opcodes_first_page`, and `opcodes_last_page`; otherwise it derives those values with `find_pdf_pagenumber_offset()`.

Generation then prints the Go header, build tags, package declaration, import, `init` registration hook, and the start of `var insns = []*powerpc.Insn{`. `do_sorted_opcodes()` drives the body:

1. Read each sorted-opcode logical page translated through `pageoffset`.
2. Locate the table header offsets for `Privilege3` and `Mode Dep4`.
3. Match opcode rows with a large regular expression that captures six opcode bit groups, instruction format, book, page number, mnemonic, and ISA version.
4. Convert bit pattern strings into a base opcode mask and opcode value. Dots become variable bits, slashes become zero-like separators, and fixed `0`/`1` bits become mask/value bits.
5. For fully fixed 32-bit rows, emit an instruction immediately with `Mask: 0xFFFFFFFF`.
6. For variable layouts, apply mnemonic page corrections, read the detailed page with `store=True`, locate the mnemonic syntax and following bit-grid rows, and infer field names plus bit positions.
7. Apply special-case corrections for malformed PDF layouts, including `addpcis`, `darn`, `copy`, `paste.`, vector compare missing offsets, concatenated field labels such as `AXBXTX`, and MD-form split fields.
8. Iterate over each instruction variant line, including forms with fixed default bits like `(OE=1 Rc=0)`, then build opcode/mask bits and operand field ranges.
9. Validate overlapping bit coverage with `check_bitmap`, merge the opcode-summary mask into the detailed mask, warn when calculated opcode bits fall outside the mask, and add `Priv: true` when needed.
10. Sort and print all generated Go instruction literals.

After generation, the script closes the Go slice, prints total instruction counts and per-stat summaries to stderr, and exits through normal process termination. Error paths call `sys.exit()` when required PDF structure cannot be found or when unsupported layouts are encountered.

## State and persistence behavior

The generator has process-local parsing state in `pagecache`, `ins_stat`, and `fmt_map`. It has two persistent side effects: generated Go is written to stdout, and verbose extraction/debug output is written to stderr plus a local file named `outp` in the current working directory. It does not update repository files directly; build systems are expected to redirect stdout into the generated Go file.

The script relies on deterministic PDF contents and a deterministic external text extractor. Because `read_pdf_page()` caches by page number string, repeated detailed-page reads reuse normalized text and avoid repeated `pdftotext` calls.

## Dependencies and integration points

Runtime dependencies are Python standard libraries `re`, `sys`, `pprint`, and `subprocess`, plus the external Xpdf `pdftotext` binary. The input dependency is a Power ISA 3.0 PDF matching the expected table layout. The output dependency is syzkaller's `pkg/ifuzz/powerpc` package, specifically the Go symbols `powerpc.Register`, `powerpc.Insn`, `powerpc.InsnField`, and `powerpc.InsnBits`.

The emitted Go integrates through an `init()` function:

- `package generated`
- `import "github.com/google/syzkaller/pkg/ifuzz/powerpc"`
- `powerpc.Register(insns)`

That means importing the generated package registers the instruction metadata into the ifuzz PowerPC backend.

## Risks and maintenance notes

The largest risk is PDF-layout fragility. Parsing depends on exact text extraction geometry, table headings, page footers, field names, and mnemonic formatting. Several manual fixups already show known breakage points, and new PDFs or `pdftotext` versions can shift offsets or concatenate labels differently.

The hard-coded absolute `pdftotext` path is non-portable and makes the script environment-specific. The local `outp` debug file can overwrite an unrelated file in the caller's working directory. Error handling is intentionally fail-fast, but many failures happen after partially writing Go to stdout, so callers should generate to a temporary file before replacing checked-in output.

Parsing risks include broad bare `except` blocks, direct integer parsing of layout fields, reliance on `priv_off` and `mode_off` being initialized by a header line, and special handling for only known duplicated or split fields. The script also treats privilege as true for any `P` or `H` in the extracted privilege cell, which is simple but depends on the source table encoding.

## Test signals

Useful validation signals are generated-code compilation, successful `go test` coverage for `pkg/ifuzz/powerpc` and packages importing `generated`, and comparison of generated instruction count/stat summaries against known-good runs. The script's own stderr output is also a test signal: missing pages, unsupported layouts, bit overlaps, wrong field lengths, and opcode/mask warnings indicate generator or input drift.

Golden-output testing would be valuable because the generator is deterministic for a fixed PDF and `pdftotext` version. A robust test should redirect stdout to a temporary Go file, verify it formats and builds, and ensure no unexpected stderr warnings appear.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa30_to_syz -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa31_tex_to_syz -->
# sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa31_tex_to_syz

## Purpose

`powerisa31_tex_to_syz` is a Python 3 code generator for syzkaller's PowerPC instruction fuzzer metadata using the Power ISA 3.1 LaTeX sources instead of PDF text extraction. It walks an ISA source directory, parses instruction syntax and layout macros, identifies privileged mnemonics from the appendix mnemonic table, and emits Go code for package `generated` that registers `[]*powerpc.Insn`.

Compared with the ISA 3.0 PDF generator, this script is structured around LaTeX macro data. That removes many page-offset and table-splitting concerns, but still requires detailed knowledge of the ISA document macro conventions.

## Important APIs, types, and functions

The key helper functions are:

- `read_file(fname)`: returns a file as a list of lines without trailing newline records, or `[]` if the path is not readable according to `os.access`.
- `get_layouts(layout_file)`: parses `ilayouts.tex` layout macro definitions. It carries the preceding `%` comment as the bit layout description and returns a mapping from layout macro name to `(positions, names)`, where positions are bit widths and names are fixed field labels or `None` placeholders.
- `complete_layout(layout, insn_layout)`: expands unnamed placeholders in a layout using the arguments from a concrete instruction layout macro invocation. It normalizes special text such as `any value\textsuperscript{*}` and repeated slashes.
- `find_insns(tex_file, layouts)`: extracts instruction mnemonics and layouts from a single `.tex` file. It tracks `\instrsyntax{...}` lines, then associated `\layout...{...}` macro calls, and returns a map from instruction name to one or two layout tuples.
- `collect_priv(tex_file, insns)`: parses `Appendices/inst-mnem.tex`, merges rows between `\hline`, splits LaTeX table columns, and returns instruction names marked privileged by relevant privilege cells.
- `generate_go(insns, priv)`: emits Go struct literals for all parsed instructions. It contains nested helpers `ppcmask()` and `generate_opcode()` to convert parsed field layouts into opcode, mask, and field metadata.

The script also creates pretty-printers `pp` and `pe`, although only `pe` is materially used for stderr diagnostics.

## Control flow

The script expects `sys.argv[1]` to be the root of an ISA LaTeX source tree. It parses `isa_dir + "/ilayouts.tex"` first, then runs `find` for every `*.tex` file under the ISA directory. Each file is passed to `find_insns()`, and all instruction maps are merged with `insns.update(...)`.

`find_insns()` maintains current instruction syntax and layout state. When it sees `\instrsyntax{...}`, it flushes any previous instruction-plus-layout group. Layout macro calls are resolved through `layouts[...]`, expanded with `complete_layout()`, and accumulated. `add_insns()` then converts each syntax line into a map entry. It supports one or two layouts per instruction and records default one-bit field values from syntax suffixes like `(OE=0 Rc=1)`.

After parsing all instruction sources, the script prints a generated Go file:

1. `// Code generated ...`
2. `//go:build !codeanalysis` and legacy `// +build !codeanalysis`
3. `package generated`
4. import of `github.com/google/syzkaller/pkg/ifuzz/powerpc`
5. `init()` calling `powerpc.Register(insns)`
6. `var insns = []*powerpc.Insn{ ... }`

`generate_go()` sorts instruction names, calculates opcode and mask for the primary layout, optionally calculates `OpcodeSuffix`, `MaskSuffix`, and `FieldsSuffix` for a second layout, appends `Priv: true` for privileged instructions, and prints each record. It writes the processed instruction count to stderr at the end.

## State and persistence behavior

The generator does not persist state itself. It reads the ISA source tree and writes generated Go to stdout plus diagnostics to stderr. Callers are responsible for redirecting stdout to the checked-in generated file.

In-memory state includes the layout map, the instruction map, temporary parser state inside `find_insns()`, and the privileged instruction list. Merging instruction maps with `insns.update()` means later `.tex` files can overwrite an instruction with the same name if duplicates exist in `find` traversal order.

## Dependencies and integration points

Runtime dependencies are Python standard libraries `re`, `os`, `sys`, `pprint`, and `subprocess`, plus the external `find` command. Input dependencies are the Power ISA 3.1 LaTeX tree, especially `ilayouts.tex`, instruction `.tex` files containing `\instrsyntax` and `\layout...` macros, and `Appendices/inst-mnem.tex`.

The generated output integrates with syzkaller's PowerPC ifuzz layer through these Go API expectations:

- `powerpc.Register(insns)` accepts generated instruction metadata.
- `powerpc.Insn` has fields `Name`, `Opcode`, `Mask`, `Fields`, optional suffix opcode/mask/fields, and `Priv`.
- `powerpc.InsnField` and `powerpc.InsnBits` encode operand bit ranges with Power ISA bit numbering.

The generator has PowerPC-specific fixups for MD-form rotate fields and SPR numbering. For rotate/shift instructions such as `rldcl`, `rldic`, `rldicl`, `rldimi`, `rldcr`, and `rldicr`, six-bit `me` and `mb` fields are split into `(21,5)` and `(26,1)`. For `mfspr` and `mtspr`, the ten-bit `spr` field is reordered into `(16,5)` and `(11,5)`.

## Risks and maintenance notes

The parser depends on ISA LaTeX conventions rather than a formal AST. It assumes layout bit comments immediately precede `\newcommand{\layout...}` definitions and that those comments can be converted into bit widths and optional field names by splitting on spaces. It also assumes instruction syntax and layout macros appear close enough for the simple state machine in `find_insns()`.

`read_file()` checks readability with `os.access(fname, os.O_RDONLY)`, using a file-open flag as the mode argument rather than the more conventional `os.R_OK`. On typical systems this still evaluates as a permission bit value, but it is subtle and can obscure intent.

The external `find` traversal order is not explicitly sorted. Final Go output is sorted by instruction name, but duplicate mnemonic resolution depends on traversal order before sorting. Missing layout macros, more than two layouts, malformed default-value suffixes, and unexpected appendix table shapes are fatal or silently incomplete depending on where they occur.

Field handling is intentionally specialized. Fixed slash fields are forced to zero, numeric fields become opcode bits, empty names are ignored, default field values are only extracted for one-character numeric assignments, and only known split-field encodings receive custom handling. New ISA macro forms may require generator updates.

## Test signals

Primary validation is that generated Go compiles and that `go test` succeeds for the PowerPC ifuzz packages that consume `generated`. The stderr "Processed N instructions" count should be stable for a fixed ISA source revision and can be compared with a golden count.

Additional useful tests include checking that generated output is gofmt-stable, contains expected privileged instructions, includes suffix metadata for two-layout instructions, and has no zero-length field ranges. Fixture tests around `get_layouts()`, `complete_layout()`, and `generate_opcode()` would catch the most likely parser drift without requiring the full ISA tree.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/gen/powerisa31_tex_to_syz -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/generated/empty.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/powerpc/generated/empty.go

## Purpose

`empty.go` is a minimal package stub for `sources/test-tools/syzkaller/pkg/ifuzz/powerpc/generated`. Its comment states that it exists to keep the build working when `insns.go` is excluded by build tags. The file declares package `generated` and contains no functions, variables, types, or imports.

## Important APIs, types, and functions

There are no exported or unexported APIs in this file. The only code element is:

- `package generated`: preserves the package so imports of the generated instruction package can still resolve in build configurations where generated instruction data is unavailable.

## Control flow

There is no runtime control flow. Importing this package from a build that only includes `empty.go` has no side effects and performs no registration with the PowerPC ifuzz package.

## State and persistence behavior

The file has no state and no persistence behavior. It does not initialize package variables, write files, read environment variables, or register instructions.

## Dependencies and integration points

`empty.go` has no imports. Its integration role is structural: it keeps the `generated` package present when the real generated `insns.go` file is excluded. This matters because the generator scripts emit generated Go guarded by `//go:build !codeanalysis`; under code-analysis builds or other tag combinations, a package with no remaining Go files would break imports.

## Risks and maintenance notes

The main risk is behavioral absence. Any build configuration that includes only this stub will not register PowerPC instruction metadata, so ifuzz functionality depending on generated instructions may be empty or unavailable. That appears intentional for analysis-oriented builds, but tests should not assume instruction registration happens when `insns.go` is excluded.

Because the file is deliberately tiny, accidental addition of imports or init-time behavior would defeat its role as a low-risk fallback stub.

## Test signals

The useful test signal is successful compilation under the build tags that exclude generated instruction data. Package-level tests should also distinguish between normal builds, where generated instructions are expected to register, and code-analysis builds, where this stub may be the only file in package `generated`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/generated/empty.go -->
