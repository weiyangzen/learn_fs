# sources/test-tools/syzkaller/pkg/ifuzz/x86/generated/insns.go lines 1831-2283

## Scope

This chunk is part of the generated x86 instruction catalog for syzkaller's `ifuzz` package. It contains `*x86.Insn` composite literals inside the package-level `insns` slice registered by `generated.init()` through `x86.Register(insns)`. The lines covered here do not define new functions or methods; they provide data consumed by the shared x86 instruction selection, encoding, and decoding paths.

The range starts in the AVX vector integer/floating-point table and continues through AVX AES/PCLMUL, F16C, FMA, AVX2 gather and packed-integer operations, BMI1/BMI2, RTM, PKU, CLWB/PREFETCHWT1/WBNOINVD/PCONFIG, GFNI, VAES, and VPCLMULQDQ entries.

## Purpose

The entries describe how `ifuzz` can generate and recognize many modern x86 encodings. Each literal maps one instruction form to fields on `x86.Insn`, including opcode bytes, extension label, compatible CPU modes, ModRM constraints, immediate sizes, legacy prefixes, VEX encoding requirements, REX.W constraints, and privileged status.

The table is generated from `pkg/ifuzz/x86/gen` input, as indicated by the file header and the `go:generate` directive in `x86.go`. Manual edits to this generated table would be overwritten by regeneration and could desynchronize the instruction metadata from upstream encoding sources.

## Important APIs, Types, and Fields

The central type is `x86.Insn` from `pkg/ifuzz/x86/x86.go`. Fields used heavily in this chunk include:

- `Name` and `Extension`: identify the instruction mnemonic and extension bucket used by callers through `Insn.Info()`.
- `Mode`: bitmask over `iset.ModeLong64`, `ModeProt32`, `ModeProt16`, and `ModeReal16`. Examples in this chunk include `Mode: 3` for long64 plus protected 32-bit, `Mode: 15` for all modes, `Mode: 1` for long64 only, `Mode: 2` for protected 32-bit only, and `Mode: 14` for non-long modes.
- `Priv`: marks privileged instructions such as `INVPCID`, `WBNOINVD`, and `PCONFIG` so `iset.Config.Priv` gates generation.
- `Opcode`, `Prefix`, and `Suffix`: define opcode bytes and fixed legacy prefix bytes. This range uses legacy `0x66`/`0xf3` prefixes for instructions such as `TZCNT`, `LZCNT`, `ADCX`, `ADOX`, and GFNI non-VEX forms.
- `Modrm`, `Mod`, `Reg`, `Rm`, and `NoSibDisp`: control ModRM/SIB generation and decoder matching. This range uses fixed `Reg` values for opcode extensions such as `BLSR/BLSMSK/BLSI`, fixed `Rm: 4` for AVX2 gather forms requiring SIB, and `Mod: -3` to force memory-only forms.
- `Imm`, `Imm2`: define trailing immediate widths. This chunk has one-byte immediates on blend, insert/extract, string compare, F16C convert, RORX, XABORT, VPALIGNR, GFNI affine, and VPCLMULQDQ forms, and `Imm: -1` for `XBEGIN` where immediate size follows operand-size rules.
- `Rexw`: constrains VEX.W or legacy REX.W. `1` requires 64-bit operand encoding, `-1` forbids W, and zero leaves it random/default.
- `Vex`, `VexMap`, `VexL`, `VexNoR`, and `VexP`: describe 3-byte VEX encodings. Most vector entries use `Vex: 196` (`0xc4`), map 1/2/3, optional or fixed vector length, and fixed prefix selectors (`VexP`) corresponding to mandatory prefix classes.
- `Avx2Gather`: marks gather instructions so `Encode` avoids illegal destination/index/mask register collisions.

## Control Flow and Data Use

At package initialization, `generated.init()` calls `Register(insns)`. `Register` appends pseudo-instructions, builds `modeInsns` indexes, and installs the x86 `InsnSet` into `iset.Arches[iset.ArchX86]`.

Instruction generation flows through `InsnSet.GetInsns(mode, typ)` and `Insn.Encode(cfg, r)`. For this chunk's VEX-heavy entries, `Encode` emits a 3-byte VEX prefix, chooses or fixes VEX R/X/B/W/L/pp fields from the `Insn` metadata, appends opcode bytes, emits ModRM/SIB/disp bytes based on `Mod`, `Reg`, and `Rm`, and appends immediates. Entries with `VexNoR` force the VEX.vvvv field to `1111`; entries with `VexP` fix the mandatory-prefix selector; entries with `VexL` fix vector length or leave it randomized depending on `-1` vs `1`.

Decoding flows through `InsnSet.Decode(mode, text)`. It detects VEX/XOP-style prefixes, extracts `VexMap`, strips legacy prefixes otherwise, then scans all registered `Insn` entries. For this chunk, matching depends on mode compatibility, VEX-vs-legacy status, `VexMap`, opcode bytes, optional ModRM presence, fixed `Reg` fields, displacement length, immediates, and suffixes. The decoder is intentionally permissive: it is designed not to reject valid generated instructions, but it may accept some invalid encodings.

## Chunk Content Notes

The AVX section covers packed min/max, multiply/add, shifts, compare/string operations, move/mask/non-temporal moves, AES-assisted forms, PCLMUL, and mixed scalar/vector instructions. Many entries are duplicated for source/destination direction, memory vs register forms (`Mod: -3` vs `Mod: 3`), 128-bit vs 256-bit length (`VexL: -1` or `1`), and 32-bit vs 64-bit operand width (`Rexw`).

The FMA block enumerates the large family of `VFMADD*`, `VFMSUB*`, `VFNMADD*`, and `VFNMSUB*` forms. It records the opcode family split by operand order (`132`, `213`, `231`), scalar vs packed element type, and `Rexw` distinction between double/quad-oriented and single/dword-oriented forms.

The AVX2 gather block uses `Avx2Gather: true`, `Rm: 4`, and memory-only `Mod: -3`. This is significant because gather encodings have stricter register aliasing rules than normal ModRM/SIB vector operations; the encoder has dedicated logic to adjust conflicting `reg` and SIB index values.

The later AVX2 packed-integer block adds 256-bit versions of many AVX/SSE-like operations, plus permutation, broadcast, mask-move, variable-shift, and insert/extract forms. These entries are almost all VEX-encoded with fixed `VexL: 1` or paired `VexL: -1`/`VexL: 1` variants.

The BMI1/BMI2 and related scalar entries are VEX-encoded but not vector instructions. They use `VexMap`, `VexP`, `Rexw`, and mode splits to model 32-bit and 64-bit operand forms for `PDEP`, `PEXT`, `ANDN`, `BLSR`, `BLSMSK`, `BLSI`, `BZHI`, `BEXTR`, `SHLX`, `SARX`, `SHRX`, `MULX`, and `RORX`.

The tail mixes newer legacy and VEX forms: `TZCNT`/`LZCNT` are paired with base `BSF`/`BSR` opcode aliases; RTM includes `XBEGIN`, `XEND`, `XABORT`, and `XTEST`; PKU contains `RDPKRU` and `WRPKRU`; GFNI appears in both legacy and VEX forms; VAES and VPCLMULQDQ add newer vector AES/carryless multiply encodings.

## State and Persistence Behavior

This chunk has no runtime persistence, file I/O, heap-owned state beyond the static `insns` slice, or mutation of individual entries after registration. Persistent behavior is effectively compile-time: the generated Go source embeds the instruction metadata in the binary. Runtime state is limited to `Register` constructing indexes in `InsnSet.modeInsns` and assigning the resulting set into the process-local `iset.Arches` map during package initialization.

## Dependencies and Integration Points

The generated package imports `github.com/google/syzkaller/pkg/ifuzz/x86` with a dot import, so the literals instantiate `x86.Insn` directly and call `Register` directly. The table integrates with:

- `pkg/ifuzz/iset`: mode/type classification, instruction compatibility checks, and integer/immediate generation.
- `pkg/ifuzz/x86/encode.go`: byte-level instruction generation from the metadata.
- `pkg/ifuzz/x86/decode.go`: instruction length decoding and validation of generated bytes.
- `pkg/ifuzz/x86/gen`: source generator for `generated/insns.go`; changes should normally happen in generator inputs or parser logic.
- Optional XED integration via `DecodeExt`, used as an external decode oracle when available.

## Risks and Edge Cases

The main risk is metadata accuracy. A wrong `VexMap`, `VexP`, `VexL`, `Rexw`, `Mod`, `Reg`, `Rm`, or `Imm` value can cause `ifuzz` to emit invalid instructions, miss valid encodings, or miscompute instruction length.

Aliased opcodes require care. `TZCNT`/`BSF` and `LZCNT`/`BSR` share opcode bytes with prefix-sensitive behavior; the table uses `Prefix` and `NoRepPrefix` to constrain extra random prefixes. Similar prefix sensitivity appears in `ADCX`, `ADOX`, GFNI legacy forms, and privileged/system instructions.

Mode bitmasks are easy to misread because they are bitmasks, not enum values. For example, `Mode: 3` means long64 plus protected 32-bit, while `Mode: 14` means all modes except long64. Incorrect mode masks can expose unsupported instructions in real/protected/long mode fuzzing.

The decoder only checks a subset of VEX fields. It filters on VEX presence and `VexMap`, but the exact W/L/pp/vvvv constraints are primarily used by the encoder. This is consistent with the decoder's permissive design but means table changes should be validated with generation plus external decoder signals where possible.

Privileged entries such as `INVPCID`, `WBNOINVD`, and `PCONFIG` rely on `Priv: true` for selection gating. If this flag is missing, normal user-mode fuzzing could emit privileged instructions unexpectedly.

## Test Signals

Useful validation signals for this chunk are encoder/decoder round trips over all modes and instruction types, especially with XED enabled through `DecodeExt`. High-value cases include AVX2 gather encodings, FMA scalar vs packed variants, BMI1/BMI2 32-bit and 64-bit mode splits, aliasing opcodes (`TZCNT`/`BSF`, `LZCNT`/`BSR`), and privileged/system instructions under both `Priv` settings.

Regression tests should verify that generated byte streams for this table decode to a nonzero length in the internal decoder and, when XED is available, are accepted or rejected consistently with the intended instruction form. Generator-level tests should also ensure this file remains generated, sorted/grouped consistently with source instruction metadata, and reproducible from `pkg/ifuzz/x86/gen`.
