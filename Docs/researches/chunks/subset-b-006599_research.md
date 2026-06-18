# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-64.c lines 4041-4923

## Scope

This chunk covers the final generated entries in the 64-bit x86 instruction decoder test data file used by perf's `insn_x86` test. The range starts in the middle of the generated initializer for `vcvtneebf162ps (%rcx),%xmm6` and then continues through the end of `insn-x86-dat-64.c`. Because line 4041 is inside an initializer entry, the adjacent previous chunk owns that entry's byte-array opening; this chunk still documents the semantic group that follows from that point.

The covered data is not executable C logic. It is a sequence of `struct test_data` initializer records that are included directly into `test_data_64[]` by `tools/perf/arch/x86/tests/insn-x86.c`. Each record supplies instruction bytes, expected decoded length, optional Intel PT operation classification, optional branch classification, and an objdump-style assembly representation.

The range mainly exercises recently added or less common 64-bit instruction encodings:

- VEX and EVEX vector/AMX conversions and dot-product instructions.
- CET and control-flow related records such as `erets`, `eretu`, and `jmpabs`.
- APX-style encodings using high general registers `%r16` through `%r31`, `pushp`/`popp`, three-operand integer forms, `{nf}` no-flags forms, and extended addressing.
- BMI, bit-manipulation, CRC32, MOVBE, MOVDIR, ENQCMD, INVPCID/INVEPT/INVVPID, AMX tile, WRSS/WRUSS, and AVX-512 opmask movement examples.
- Conditional compare-and-add forms, conditional moves under extended encodings, rotate/shift forms, ADC/ADOX/ADCX, arithmetic/logical three-operand encodings, and legacy/control instructions near the file tail.
- Key Locker, atomic memory operation, SHA/SM3/SM4, prefetch, `serialize`, TSX suspend/load tracking, SGX enclave, `pconfig`, `wrmsrns`, `hreset`, and `wbnoinvd` entries.

## Purpose

The purpose of this generated chunk is to lock down expected decode behavior for 64-bit x86 instruction byte streams that are easy to regress when the kernel's generic x86 instruction decoder or perf's Intel PT instruction classifier changes. It provides concrete byte sequences and expected lengths for a wide spread of instruction families, with special attention to prefix-heavy encodings and register-extension behavior.

The data is consumed by the perf test harness rather than by production runtime code. The test verifies two things for every record:

- `insn_decode()` from the kernel x86 instruction decoder must report the expected instruction length.
- `intel_pt_get_insn()` must classify the instruction's high-level operation, branch kind, and relative target exactly as the record requests.

Most entries in this chunk have empty expected operation and branch strings. For those records, the harness expects `INTEL_PT_OP_OTHER`, `INTEL_PT_BR_NO_BRANCH`, and `rel == 0`; the instruction's primary test signal is successful length decoding. The exceptions in this chunk are `erets`, `eretu`, and `jmpabs`, which explicitly test Intel PT operation/branch classification.

## Important Data Shape and APIs

The included harness defines:

- `struct test_data`, with `u8 data[MAX_INSN_SIZE]`, `expected_length`, `expected_rel`, `expected_op_str`, `expected_branch_str`, and `asm_rep`.
- `test_data_64[]`, which includes this file and appends a few manual records plus the zero-length sentinel.
- `test_data_item()`, which runs both decoder checks for one record.
- `test_data_set()`, which iterates until `expected_length == 0`.
- `test__insn_x86()`, which tests both the 32-bit and 64-bit generated data arrays.

Every initializer in this chunk follows the same layout:

```c
{{bytes...}, expected_length, expected_rel, "expected_op", "expected_branch",
"objdump representation",},
```

The byte-array length and `expected_length` must agree with the instruction text and with what `insn_decode()` returns. `asm_rep` is only used for diagnostics in the test harness; it is not parsed by the test. The expected operation and branch strings are parsed by `get_op()` and `get_branch()` into Intel PT enum values.

The important instruction families in this chunk include:

- Floating-point and vector conversions: `vbcstnebf162ps`, `vbcstnesh2ps`, `vcvtneeph2ps`, `vcvtneobf162ps`, `vcvtneoph2ps`, `vcvtneps2bf16`, `vbroadcast*`, `vinsert*`, `vextract*`, and `vrndscale*`.
- AMX and tile records: `tcmmimfp16ps`, `tcmmrlfp16ps`, `tdpfp16ps`, `ldtilecfg`, `sttilecfg`, `tileloadd`, `tileloaddt1`, and `tilestored`.
- Extended/APX general-register encodings: records involving `%r16` through `%r31`, 32-bit address override forms, high-register SIB addressing, `jmpabs`, `pushp`, `popp`, three-operand arithmetic, and `{nf}` no-flags instructions.
- BMI and bit operations: `bextr`, `blsi`, `blsmsk`, `blsr`, `bzhi`, `pdep`, `pext`, `shlx`, `shrx`, `andn`, `tzcnt`, `lzcnt`, `popcnt`, and several shift/rotate forms.
- System and virtualization records: `enqcmd`, `enqcmds`, `invept`, `invpcid`, `invvpid`, `wrmsrns`, `hreset`, `serialize`, `xresldtrk`, `xsusldtrk`, `encls`, `enclu`, `enclv`, `pconfig`, and `wbnoinvd`.
- Opmask and memory-movement records: `kmovb`, `kmovd`, `kmovq`, `kmovw`, `movbe`, `movdir64b`, `movdiri`, `wrssd`, and `wruss*`.
- Integer arithmetic/logical coverage: `adc`, `adcx`, `adox`, `add`, `and`, `or`, `sbb`, `sub`, `xor`, `imul`, `inc`, `dec`, `neg`, `not`, `idiv`, `rcl`, `rcr`, `rol`, `ror`, `sar`, `shl`, `shr`, `shld`, and `shrd`.
- Crypto and memory-operation extensions: Key Locker `loadiwkey`, `encodekey128`, `encodekey256`, AES key-locker forms, atomic `aadd`/`aand`/`aor`/`axor`, SHA-512, SM3, and SM4 vector instructions.

## Control Flow

This chunk has no direct control flow. At compile time it is pasted into the `test_data_64[]` array by the C preprocessor.

Runtime control flow is supplied by `insn-x86.c`:

1. `test__insn_x86()` calls `test_data_set(test_data_64, 1)`.
2. `test_data_set()` walks this chunk's records as part of the larger array until the sentinel record after the include.
3. For each record, `test_data_item()` decodes `dat->data` in `INSN_MODE_64` and compares `insn.length` with `dat->expected_length`.
4. The same function maps `expected_op_str` and `expected_branch_str` to Intel PT enum values, calls `intel_pt_get_insn()`, and compares the resulting `op`, `branch`, and `rel` fields.
5. Any mismatch logs the record's `asm_rep` and causes the test suite to fail.

The `erets` and `eretu` records in this generated file overlap with manual records appended in `test_data_64[]`. That duplication deliberately reinforces Intel PT classification for these encodings. The chunk's `jmpabs` record is classified as `jmp` plus `indirect`, but its relative target remains zero because the instruction text carries an absolute immediate form rather than a relative branch offset.

## State and Persistence

There is no mutable software state in this generated data file. The only state-like information is the static, compiled-in test vector content.

The persistent contract represented by each record is:

- The instruction byte stream is a valid test input for the 64-bit decoder.
- `expected_length` is the authoritative decoded length expected from `insn_decode()`.
- `expected_rel` is the expected relative branch displacement reported by Intel PT decoding.
- `expected_op_str` and `expected_branch_str` encode expected Intel PT classification where the instruction is control-flow relevant.
- `asm_rep` preserves the objdump rendering used as a human-readable diagnostic.

Because this file is generated, source-of-truth edits should be made in `insn-x86-dat-src.c` and regenerated with `gen-insn-x86-dat.sh`, not hand-edited in the generated C include. Local hand edits would persist in the working tree but are expected to be overwritten by the generation pipeline.

## Dependencies and Integration Points

This chunk depends on the perf x86 instruction test harness and the generated-data workflow:

- `tools/perf/arch/x86/tests/insn-x86.c` defines `struct test_data`, includes `insn-x86-dat-64.c`, and executes the decode checks.
- `tools/perf/arch/x86/tests/gen-insn-x86-dat.sh` and `gen-insn-x86-dat.awk` generate this file from `insn-x86-dat-src.c` and objdump output.
- `tools/perf/arch/x86/include/asm/insn.h` provides the kernel instruction decoder interface used by `insn_decode()`.
- `tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.h` provides `intel_pt_get_insn()` and the Intel PT operation/branch enums checked by the harness.
- The build's assembler and objdump must recognize the instruction mnemonics and encodings used in the source data. Newer APX, AMX, Key Locker, and vector-extension records can depend on a sufficiently recent binutils toolchain when regenerating.

The integration point is the perf test suite entry registered by `arch-tests.c` as `"x86 instruction decoder - new instructions"`. A failure in any entry here reports as a perf test regression, even though the underlying bug may be in generated data, x86 decode tables, Intel PT classification logic, assembler/objdump generation, or expectations for a newly updated instruction encoding.

## Risks

- Generated-file drift is the main maintenance risk. Editing this file directly can fix or introduce a visible test result but leave `insn-x86-dat-src.c` inconsistent, so the change may disappear on regeneration.
- Prefix-heavy and extended-register encodings are fragile. The chunk heavily exercises EVEX/APX-style prefix bytes, address-size overrides, SIB forms, high registers, and immediate widths; a one-byte error can still produce a decodable instruction with the wrong length or operand interpretation.
- Boundary handling matters. The chunk starts inside one record, so a final merged report must reconcile it with the previous chunk before making whole-entry claims for the first `vcvtneebf162ps` item.
- Most entries only assert decode length, not full semantic classification. A decoder can pass these records while still rendering the wrong mnemonic or operands outside the length and Intel PT operation fields.
- The diagnostic assembly strings are not checked mechanically. They help humans identify failing records, but stale text would not fail the test unless the bytes or expected decoder fields are wrong.
- Toolchain version changes can alter generated output. If objdump changes mnemonic spelling, spacing, aliases, or support for APX/AMX/Key Locker forms, regeneration can create noisy diffs or expectation changes.
- Duplicate encodings and aliases appear intentionally in this file, such as repeated `shl` forms and related `erets`/`eretu` coverage. Deduplicating generated data by byte sequence alone could accidentally remove alias or regression coverage.
- Intel PT classification strings are sparse but high impact. A wrong non-empty `expected_op_str` or `expected_branch_str` causes explicit classification failures; a missing non-empty string can silently reduce branch/call/return coverage to length-only testing.

## Test and Validation Signals

Useful validation signals are the existing perf test and targeted regeneration checks:

- Build perf and run the x86 instruction decoder test, especially `perf test "x86 instruction decoder - new instructions"` or the equivalent test selector in this tree.
- Run the test with verbose output to see each `asm_rep` decoded successfully or the exact record that failed.
- Regenerate `insn-x86-dat-64.c` from `insn-x86-dat-src.c` with `gen-insn-x86-dat.sh` after source-data changes and confirm this chunk remains aligned with generated objdump output.
- For APX/AMX/Key Locker and other new instruction-family records, validate on a toolchain new enough to assemble and disassemble the source mnemonics consistently.
- If failures occur only on the records with non-empty classification strings, inspect `intel_pt_get_insn()` and the `get_op()`/`get_branch()` mapping before assuming `insn_decode()` length logic is wrong.
- If failures occur on records with empty classification strings, focus first on instruction length decoding, prefix handling, address-size handling, immediate-width parsing, and ModRM/SIB displacement length handling.
- The manual tail records appended by `insn-x86.c` after this include provide an additional signal for `rdpkru`, `wrpkru`, `erets`, and `eretu`; failures duplicated between generated and manual records point to decoder/classifier behavior rather than this chunk alone.
