# Research Group subset-b-009467

This grouped report covers RISC-V Vector and Zaamo instruction YAML descriptors under `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents. The files are declarative inputs to `pkg/ifuzz/riscv64/gen/gen.go`; the generator consumes decode metadata and leaves embedded operation/Sail semantics as reference material for architecture validation.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vx.yaml

## Purpose

`vssrl.vx.yaml` describes `vssrl.vx`, a vector fixed-point rounding logical right shift, vector-scalar form, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssrl.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=101010-----------100-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa8004057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `get_scalar`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`, `max`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssrl.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssrl.vx` appears with match `101010-----------100-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xa8004057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e16.v.yaml

## Purpose

`vssseg2e16.v.yaml` describes `vssseg2e16.v`, a vector strided segment store descriptor with 2 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg2e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=001010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x28005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg2e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg2e16.v` appears with match `001010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x28005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e32.v.yaml

## Purpose

`vssseg2e32.v.yaml` describes `vssseg2e32.v`, a vector strided segment store descriptor with 2 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg2e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=001010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x28006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg2e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg2e32.v` appears with match `001010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x28006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e64.v.yaml

## Purpose

`vssseg2e64.v.yaml` describes `vssseg2e64.v`, a vector strided segment store descriptor with 2 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg2e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=001010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x28007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg2e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg2e64.v` appears with match `001010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x28007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e8.v.yaml

## Purpose

`vssseg2e8.v.yaml` describes `vssseg2e8.v`, a vector strided segment store descriptor with 2 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg2e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=001010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x28000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg2e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg2e8.v` appears with match `001010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x28000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg2e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e16.v.yaml

## Purpose

`vssseg3e16.v.yaml` describes `vssseg3e16.v`, a vector strided segment store descriptor with 3 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg3e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=010010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg3e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg3e16.v` appears with match `010010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x48005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e32.v.yaml

## Purpose

`vssseg3e32.v.yaml` describes `vssseg3e32.v`, a vector strided segment store descriptor with 3 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg3e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=010010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg3e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg3e32.v` appears with match `010010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x48006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e64.v.yaml

## Purpose

`vssseg3e64.v.yaml` describes `vssseg3e64.v`, a vector strided segment store descriptor with 3 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg3e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=010010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg3e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg3e64.v` appears with match `010010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x48007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e8.v.yaml

## Purpose

`vssseg3e8.v.yaml` describes `vssseg3e8.v`, a vector strided segment store descriptor with 3 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg3e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=010010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg3e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg3e8.v` appears with match `010010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x48000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg3e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e16.v.yaml

## Purpose

`vssseg4e16.v.yaml` describes `vssseg4e16.v`, a vector strided segment store descriptor with 4 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg4e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=011010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x68005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg4e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg4e16.v` appears with match `011010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x68005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e32.v.yaml

## Purpose

`vssseg4e32.v.yaml` describes `vssseg4e32.v`, a vector strided segment store descriptor with 4 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg4e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=011010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x68006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg4e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg4e32.v` appears with match `011010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x68006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e64.v.yaml

## Purpose

`vssseg4e64.v.yaml` describes `vssseg4e64.v`, a vector strided segment store descriptor with 4 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg4e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=011010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x68007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg4e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg4e64.v` appears with match `011010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x68007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e8.v.yaml

## Purpose

`vssseg4e8.v.yaml` describes `vssseg4e8.v`, a vector strided segment store descriptor with 4 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg4e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=011010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x68000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg4e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg4e8.v` appears with match `011010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x68000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg4e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e16.v.yaml

## Purpose

`vssseg5e16.v.yaml` describes `vssseg5e16.v`, a vector strided segment store descriptor with 5 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg5e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=100010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x88005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg5e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg5e16.v` appears with match `100010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x88005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e32.v.yaml

## Purpose

`vssseg5e32.v.yaml` describes `vssseg5e32.v`, a vector strided segment store descriptor with 5 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg5e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=100010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x88006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg5e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg5e32.v` appears with match `100010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x88006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e64.v.yaml

## Purpose

`vssseg5e64.v.yaml` describes `vssseg5e64.v`, a vector strided segment store descriptor with 5 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg5e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=100010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x88007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg5e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg5e64.v` appears with match `100010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x88007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e8.v.yaml

## Purpose

`vssseg5e8.v.yaml` describes `vssseg5e8.v`, a vector strided segment store descriptor with 5 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg5e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=100010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x88000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg5e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg5e8.v` appears with match `100010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x88000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg5e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e16.v.yaml

## Purpose

`vssseg6e16.v.yaml` describes `vssseg6e16.v`, a vector strided segment store descriptor with 6 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg6e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=101010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa8005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg6e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg6e16.v` appears with match `101010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa8005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e32.v.yaml

## Purpose

`vssseg6e32.v.yaml` describes `vssseg6e32.v`, a vector strided segment store descriptor with 6 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg6e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=101010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa8006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg6e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg6e32.v` appears with match `101010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa8006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e64.v.yaml

## Purpose

`vssseg6e64.v.yaml` describes `vssseg6e64.v`, a vector strided segment store descriptor with 6 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg6e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=101010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa8007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg6e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg6e64.v` appears with match `101010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa8007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e8.v.yaml

## Purpose

`vssseg6e8.v.yaml` describes `vssseg6e8.v`, a vector strided segment store descriptor with 6 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg6e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=101010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa8000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg6e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg6e8.v` appears with match `101010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa8000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg6e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e16.v.yaml

## Purpose

`vssseg7e16.v.yaml` describes `vssseg7e16.v`, a vector strided segment store descriptor with 7 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg7e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=110010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc8005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg7e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg7e16.v` appears with match `110010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc8005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e32.v.yaml

## Purpose

`vssseg7e32.v.yaml` describes `vssseg7e32.v`, a vector strided segment store descriptor with 7 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg7e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=110010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc8006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg7e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg7e32.v` appears with match `110010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc8006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e64.v.yaml

## Purpose

`vssseg7e64.v.yaml` describes `vssseg7e64.v`, a vector strided segment store descriptor with 7 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg7e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=110010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc8007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg7e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg7e64.v` appears with match `110010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc8007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e8.v.yaml

## Purpose

`vssseg7e8.v.yaml` describes `vssseg7e8.v`, a vector strided segment store descriptor with 7 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg7e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=110010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc8000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg7e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg7e8.v` appears with match `110010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc8000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg7e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e16.v.yaml

## Purpose

`vssseg8e16.v.yaml` describes `vssseg8e16.v`, a vector strided segment store descriptor with 8 fields and 16-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg8e16.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=111010-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe8005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg8e16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg8e16.v` appears with match `111010-----------101-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe8005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e32.v.yaml

## Purpose

`vssseg8e32.v.yaml` describes `vssseg8e32.v`, a vector strided segment store descriptor with 8 fields and 32-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg8e32.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=111010-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe8006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg8e32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg8e32.v` appears with match `111010-----------110-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe8006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e64.v.yaml

## Purpose

`vssseg8e64.v.yaml` describes `vssseg8e64.v`, a vector strided segment store descriptor with 8 fields and 64-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg8e64.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=111010-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe8007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg8e64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg8e64.v` appears with match `111010-----------111-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe8007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e8.v.yaml

## Purpose

`vssseg8e8.v.yaml` describes `vssseg8e8.v`, a vector strided segment store descriptor with 8 fields and 8-bit elements, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), xs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssseg8e8.v`, `assembly=vs3, (xs1), xs2, vm`, `encoding.match=111010-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe8000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the strided segment-store family: compute element addresses from base `xs1` plus stride `xs2`, apply mask `vm`, store `nf` consecutive fields starting at `vs3`, and obey vector illegal-instruction checks for segment register groups.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssseg8e8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), xs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssseg8e8.v` appears with match `111010-----------000-----0100111`, variable fields [`vm` bits 25-25, `xs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe8000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssseg8e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssub.vv.yaml

## Purpose

`vssub.vv.yaml` describes `vssub.vv`, a signed saturating vector subtraction, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssub.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=100011-----------000-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x8c000057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew_pow`, `get_sew`, `get_lmul_pow`, `get_vlen_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssub.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssub.vv` appears with match `100011-----------000-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0x8c000057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssub.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssub.vx.yaml

## Purpose

`vssub.vx.yaml` describes `vssub.vx`, a signed saturating vector subtraction, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssub.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=100011-----------100-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x8c004057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `get_scalar`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`, `max`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssub.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssub.vx` appears with match `100011-----------100-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0x8c004057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssub.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssubu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssubu.vv.yaml

## Purpose

`vssubu.vv.yaml` describes `vssubu.vv`, a unsigned saturating vector subtraction, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssubu.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=100010-----------000-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x88000057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew_pow`, `get_sew`, `get_lmul_pow`, `get_vlen_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssubu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssubu.vv` appears with match `100010-----------000-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0x88000057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssubu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssubu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssubu.vx.yaml

## Purpose

`vssubu.vx.yaml` describes `vssubu.vx`, a unsigned saturating vector subtraction, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vssubu.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=100010-----------100-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x88004057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `get_scalar`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`, `max`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vssubu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vssubu.vx` appears with match `100010-----------100-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0x88004057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssubu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsub.vv.yaml

## Purpose

`vsub.vv.yaml` describes `vsub.vv`, a ordinary vector subtraction, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsub.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=000010-----------000-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x08000057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew_pow`, `get_sew`, `get_lmul_pow`, `get_vlen_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsub.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsub.vv` appears with match `000010-----------000-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0x08000057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsub.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsub.vx.yaml

## Purpose

`vsub.vx.yaml` describes `vsub.vx`, a ordinary vector subtraction, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsub.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=000010-----------100-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x08004057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `get_scalar`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`, `max`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsub.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsub.vx` appears with match `000010-----------100-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0x08004057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsub.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei16.v.yaml

## Purpose

`vsuxei16.v.yaml` describes `vsuxei16.v`, a vector unordered indexed store descriptor using 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=000001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x04005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `vlewidth_pow`, `vlewidth_bytesnumber`, `get_sew_pow`, `get_sew_bytes`, `get_lmul_pow`, `get_num_elem`, `nfields_int`, `illegal_indexed_store`, `handle_illegal`, `process_vsxseg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block derives index EEW from the instruction width, computes data EEW from current SEW, derives index EMUL, validates indexed-store legality, and delegates the memory loop to `process_vsxseg` with one field, base register `rs1`, index vector `vs2`, source vector `vs3`, mask `vm`, and unordered-store mode.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Indexed stores are risk-prone around EMUL calculation, index EEW, unordered memory effects, masking, misalignment/fault behavior, and overlap constraints hidden inside `illegal_indexed_store` and `process_vsxseg`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxei16.v` appears with match `000001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x04005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Indexed-store tests should cover index widths 8/16/32/64, SEW/LMUL combinations, masks, faulting addresses, and unordered write observations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei32.v.yaml

## Purpose

`vsuxei32.v.yaml` describes `vsuxei32.v`, a vector unordered indexed store descriptor using 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=000001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x04006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `vlewidth_pow`, `vlewidth_bytesnumber`, `get_sew_pow`, `get_sew_bytes`, `get_lmul_pow`, `get_num_elem`, `nfields_int`, `illegal_indexed_store`, `handle_illegal`, `process_vsxseg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block derives index EEW from the instruction width, computes data EEW from current SEW, derives index EMUL, validates indexed-store legality, and delegates the memory loop to `process_vsxseg` with one field, base register `rs1`, index vector `vs2`, source vector `vs3`, mask `vm`, and unordered-store mode.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Indexed stores are risk-prone around EMUL calculation, index EEW, unordered memory effects, masking, misalignment/fault behavior, and overlap constraints hidden inside `illegal_indexed_store` and `process_vsxseg`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxei32.v` appears with match `000001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x04006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Indexed-store tests should cover index widths 8/16/32/64, SEW/LMUL combinations, masks, faulting addresses, and unordered write observations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei64.v.yaml

## Purpose

`vsuxei64.v.yaml` describes `vsuxei64.v`, a vector unordered indexed store descriptor using 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=000001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x04007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `vlewidth_pow`, `vlewidth_bytesnumber`, `get_sew_pow`, `get_sew_bytes`, `get_lmul_pow`, `get_num_elem`, `nfields_int`, `illegal_indexed_store`, `handle_illegal`, `process_vsxseg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block derives index EEW from the instruction width, computes data EEW from current SEW, derives index EMUL, validates indexed-store legality, and delegates the memory loop to `process_vsxseg` with one field, base register `rs1`, index vector `vs2`, source vector `vs3`, mask `vm`, and unordered-store mode.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Indexed stores are risk-prone around EMUL calculation, index EEW, unordered memory effects, masking, misalignment/fault behavior, and overlap constraints hidden inside `illegal_indexed_store` and `process_vsxseg`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxei64.v` appears with match `000001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x04007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Indexed-store tests should cover index widths 8/16/32/64, SEW/LMUL combinations, masks, faulting addresses, and unordered write observations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei8.v.yaml

## Purpose

`vsuxei8.v.yaml` describes `vsuxei8.v`, a vector unordered indexed store descriptor using 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=000001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x04000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `vlewidth_pow`, `vlewidth_bytesnumber`, `get_sew_pow`, `get_sew_bytes`, `get_lmul_pow`, `get_num_elem`, `nfields_int`, `illegal_indexed_store`, `handle_illegal`, `process_vsxseg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block derives index EEW from the instruction width, computes data EEW from current SEW, derives index EMUL, validates indexed-store legality, and delegates the memory loop to `process_vsxseg` with one field, base register `rs1`, index vector `vs2`, source vector `vs3`, mask `vm`, and unordered-store mode.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Indexed stores are risk-prone around EMUL calculation, index EEW, unordered memory effects, masking, misalignment/fault behavior, and overlap constraints hidden inside `illegal_indexed_store` and `process_vsxseg`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxei8.v` appears with match `000001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x04000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Indexed-store tests should cover index widths 8/16/32/64, SEW/LMUL combinations, masks, faulting addresses, and unordered write observations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei16.v.yaml

## Purpose

`vsuxseg2ei16.v.yaml` describes `vsuxseg2ei16.v`, a vector unordered indexed segment store descriptor with 2 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg2ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=001001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x24005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg2ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg2ei16.v` appears with match `001001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x24005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei32.v.yaml

## Purpose

`vsuxseg2ei32.v.yaml` describes `vsuxseg2ei32.v`, a vector unordered indexed segment store descriptor with 2 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg2ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=001001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x24006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg2ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg2ei32.v` appears with match `001001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x24006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei64.v.yaml

## Purpose

`vsuxseg2ei64.v.yaml` describes `vsuxseg2ei64.v`, a vector unordered indexed segment store descriptor with 2 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg2ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=001001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x24007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg2ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg2ei64.v` appears with match `001001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x24007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei8.v.yaml

## Purpose

`vsuxseg2ei8.v.yaml` describes `vsuxseg2ei8.v`, a vector unordered indexed segment store descriptor with 2 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg2ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=001001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x24000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg2ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg2ei8.v` appears with match `001001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x24000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg2ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei16.v.yaml

## Purpose

`vsuxseg3ei16.v.yaml` describes `vsuxseg3ei16.v`, a vector unordered indexed segment store descriptor with 3 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg3ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=010001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x44005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg3ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg3ei16.v` appears with match `010001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x44005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei32.v.yaml

## Purpose

`vsuxseg3ei32.v.yaml` describes `vsuxseg3ei32.v`, a vector unordered indexed segment store descriptor with 3 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg3ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=010001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x44006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg3ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg3ei32.v` appears with match `010001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x44006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei64.v.yaml

## Purpose

`vsuxseg3ei64.v.yaml` describes `vsuxseg3ei64.v`, a vector unordered indexed segment store descriptor with 3 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg3ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=010001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x44007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg3ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg3ei64.v` appears with match `010001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x44007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei8.v.yaml

## Purpose

`vsuxseg3ei8.v.yaml` describes `vsuxseg3ei8.v`, a vector unordered indexed segment store descriptor with 3 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg3ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=010001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x44000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg3ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg3ei8.v` appears with match `010001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x44000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg3ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei16.v.yaml

## Purpose

`vsuxseg4ei16.v.yaml` describes `vsuxseg4ei16.v`, a vector unordered indexed segment store descriptor with 4 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg4ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=011001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x64005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg4ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg4ei16.v` appears with match `011001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x64005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei32.v.yaml

## Purpose

`vsuxseg4ei32.v.yaml` describes `vsuxseg4ei32.v`, a vector unordered indexed segment store descriptor with 4 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg4ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=011001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x64006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg4ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg4ei32.v` appears with match `011001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x64006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei64.v.yaml

## Purpose

`vsuxseg4ei64.v.yaml` describes `vsuxseg4ei64.v`, a vector unordered indexed segment store descriptor with 4 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg4ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=011001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x64007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg4ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg4ei64.v` appears with match `011001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x64007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei8.v.yaml

## Purpose

`vsuxseg4ei8.v.yaml` describes `vsuxseg4ei8.v`, a vector unordered indexed segment store descriptor with 4 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg4ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=011001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x64000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg4ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg4ei8.v` appears with match `011001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x64000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg4ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei16.v.yaml

## Purpose

`vsuxseg5ei16.v.yaml` describes `vsuxseg5ei16.v`, a vector unordered indexed segment store descriptor with 5 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg5ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=100001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x84005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg5ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg5ei16.v` appears with match `100001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x84005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei32.v.yaml

## Purpose

`vsuxseg5ei32.v.yaml` describes `vsuxseg5ei32.v`, a vector unordered indexed segment store descriptor with 5 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg5ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=100001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x84006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg5ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg5ei32.v` appears with match `100001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x84006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei64.v.yaml

## Purpose

`vsuxseg5ei64.v.yaml` describes `vsuxseg5ei64.v`, a vector unordered indexed segment store descriptor with 5 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg5ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=100001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x84007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg5ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg5ei64.v` appears with match `100001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x84007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei8.v.yaml

## Purpose

`vsuxseg5ei8.v.yaml` describes `vsuxseg5ei8.v`, a vector unordered indexed segment store descriptor with 5 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg5ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=100001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x84000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg5ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg5ei8.v` appears with match `100001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0x84000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg5ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei16.v.yaml

## Purpose

`vsuxseg6ei16.v.yaml` describes `vsuxseg6ei16.v`, a vector unordered indexed segment store descriptor with 6 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg6ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=101001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa4005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg6ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg6ei16.v` appears with match `101001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa4005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei32.v.yaml

## Purpose

`vsuxseg6ei32.v.yaml` describes `vsuxseg6ei32.v`, a vector unordered indexed segment store descriptor with 6 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg6ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=101001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa4006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg6ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg6ei32.v` appears with match `101001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa4006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei64.v.yaml

## Purpose

`vsuxseg6ei64.v.yaml` describes `vsuxseg6ei64.v`, a vector unordered indexed segment store descriptor with 6 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg6ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=101001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa4007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg6ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg6ei64.v` appears with match `101001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa4007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei8.v.yaml

## Purpose

`vsuxseg6ei8.v.yaml` describes `vsuxseg6ei8.v`, a vector unordered indexed segment store descriptor with 6 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg6ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=101001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xa4000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg6ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg6ei8.v` appears with match `101001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xa4000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg6ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei16.v.yaml

## Purpose

`vsuxseg7ei16.v.yaml` describes `vsuxseg7ei16.v`, a vector unordered indexed segment store descriptor with 7 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg7ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=110001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg7ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg7ei16.v` appears with match `110001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc4005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei32.v.yaml

## Purpose

`vsuxseg7ei32.v.yaml` describes `vsuxseg7ei32.v`, a vector unordered indexed segment store descriptor with 7 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg7ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=110001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg7ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg7ei32.v` appears with match `110001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc4006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei64.v.yaml

## Purpose

`vsuxseg7ei64.v.yaml` describes `vsuxseg7ei64.v`, a vector unordered indexed segment store descriptor with 7 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg7ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=110001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg7ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg7ei64.v` appears with match `110001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc4007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei8.v.yaml

## Purpose

`vsuxseg7ei8.v.yaml` describes `vsuxseg7ei8.v`, a vector unordered indexed segment store descriptor with 7 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg7ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=110001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg7ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg7ei8.v` appears with match `110001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xc4000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg7ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei16.v.yaml

## Purpose

`vsuxseg8ei16.v.yaml` describes `vsuxseg8ei16.v`, a vector unordered indexed segment store descriptor with 8 fields and 16-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg8ei16.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=111001-----------101-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe4005027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg8ei16.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg8ei16.v` appears with match `111001-----------101-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe4005027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei32.v.yaml

## Purpose

`vsuxseg8ei32.v.yaml` describes `vsuxseg8ei32.v`, a vector unordered indexed segment store descriptor with 8 fields and 32-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg8ei32.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=111001-----------110-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe4006027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg8ei32.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg8ei32.v` appears with match `111001-----------110-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe4006027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei64.v.yaml

## Purpose

`vsuxseg8ei64.v.yaml` describes `vsuxseg8ei64.v`, a vector unordered indexed segment store descriptor with 8 fields and 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg8ei64.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=111001-----------111-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe4007027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg8ei64.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg8ei64.v` appears with match `111001-----------111-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe4007027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei8.v.yaml

## Purpose

`vsuxseg8ei8.v.yaml` describes `vsuxseg8ei8.v`, a vector unordered indexed segment store descriptor with 8 fields and 8-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vs3, (xs1), vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vsuxseg8ei8.v`, `assembly=vs3, (xs1), vs2, vm`, `encoding.match=111001-----------000-----0100111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe4000027`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. No embedded `sail()` block is present, so this YAML contributes decode metadata only in this repository. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. This file has no embedded Sail block; semantic control flow is therefore represented only by the mnemonic and encoding. Architecturally it belongs to the unordered indexed segment-store family: read indices from `vs2`, compute addresses from base `xs1`, store `nf` fields starting at `vs3`, apply mask `vm`, and rely on vector indexed-store legality checks.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vsuxseg8ei8.v` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vs3, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. This segment-store file has no embedded Sail block, so illegal register-group sizing, NFIELDS, EEW/index-width legality, masked-off memory behavior, and ordered versus unordered store semantics must be verified elsewhere.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vsuxseg8ei8.v` appears with match `111001-----------000-----0100111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vs3` bits 11-7], opcode `0xe4000027`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Segment-store validation should compare against assembler/spec encodings for each field count and EEW or index width, and use architectural tests for masked stores, illegal register groups, addressing, and memory side effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsuxseg8ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.vv.yaml

## Purpose

`vwadd.vv.yaml` describes `vwadd.vv`, a signed widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwadd.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110001-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwadd.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwadd.vv` appears with match `110001-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xc4002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.vx.yaml

## Purpose

`vwadd.vx.yaml` describes `vwadd.vx`, a signed widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwadd.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110001-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwadd.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwadd.vx` appears with match `110001-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xc4006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.wv.yaml

## Purpose

`vwadd.wv.yaml` describes `vwadd.wv`, a signed widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwadd.wv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110101-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xd4002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwadd.wv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwadd.wv` appears with match `110101-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xd4002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.wx.yaml

## Purpose

`vwadd.wx.yaml` describes `vwadd.wx`, a signed widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwadd.wx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110101-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xd4006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwadd.wx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwadd.wx` appears with match `110101-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xd4006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwadd.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vv.yaml

## Purpose

`vwaddu.vv.yaml` describes `vwaddu.vv`, a unsigned widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwaddu.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110000-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc0002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwaddu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwaddu.vv` appears with match `110000-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xc0002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vx.yaml

## Purpose

`vwaddu.vx.yaml` describes `vwaddu.vx`, a unsigned widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwaddu.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110000-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc0006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwaddu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwaddu.vx` appears with match `110000-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xc0006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.wv.yaml

## Purpose

`vwaddu.wv.yaml` describes `vwaddu.wv`, a unsigned widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwaddu.wv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110100-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xd0002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwaddu.wv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwaddu.wv` appears with match `110100-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xd0002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.wx.yaml

## Purpose

`vwaddu.wx.yaml` describes `vwaddu.wx`, a unsigned widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwaddu.wx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110100-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xd0006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwaddu.wx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwaddu.wx` appears with match `110100-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xd0006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmacc.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmacc.vv.yaml

## Purpose

`vwmacc.vv.yaml` describes `vwmacc.vv`, a signed widening multiply-accumulate, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmacc.vv`, `assembly=vd, vs1, vs2, vm`, `encoding.match=111101-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xf4002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmacc.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmacc.vv` appears with match `111101-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xf4002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmacc.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmacc.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmacc.vx.yaml

## Purpose

`vwmacc.vx.yaml` describes `vwmacc.vx`, a signed widening multiply-accumulate, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, xs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmacc.vx`, `assembly=vd, xs1, vs2, vm`, `encoding.match=111101-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xf4006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmacc.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, xs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmacc.vx` appears with match `111101-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xf4006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmacc.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccsu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccsu.vv.yaml

## Purpose

`vwmaccsu.vv.yaml` describes `vwmaccsu.vv`, a widening multiply-accumulate with signed/unsigned mixed operands, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmaccsu.vv`, `assembly=vd, vs1, vs2, vm`, `encoding.match=111111-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xfc002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmaccsu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmaccsu.vv` appears with match `111111-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xfc002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccsu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccsu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccsu.vx.yaml

## Purpose

`vwmaccsu.vx.yaml` describes `vwmaccsu.vx`, a widening multiply-accumulate with signed/unsigned mixed operands, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, xs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmaccsu.vx`, `assembly=vd, xs1, vs2, vm`, `encoding.match=111111-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xfc006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmaccsu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, xs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmaccsu.vx` appears with match `111111-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xfc006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccsu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccu.vv.yaml

## Purpose

`vwmaccu.vv.yaml` describes `vwmaccu.vv`, a unsigned widening multiply-accumulate, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmaccu.vv`, `assembly=vd, vs1, vs2, vm`, `encoding.match=111100-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xf0002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmaccu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmaccu.vv` appears with match `111100-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xf0002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccu.vx.yaml

## Purpose

`vwmaccu.vx.yaml` describes `vwmaccu.vx`, a unsigned widening multiply-accumulate, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, xs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmaccu.vx`, `assembly=vd, xs1, vs2, vm`, `encoding.match=111100-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xf0006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmaccu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, xs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmaccu.vx` appears with match `111100-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xf0006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccus.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccus.vx.yaml

## Purpose

`vwmaccus.vx.yaml` describes `vwmaccus.vx`, a widening multiply-accumulate with unsigned scalar and signed vector operand, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, xs1, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmaccus.vx`, `assembly=vd, xs1, vs2, vm`, `encoding.match=111110-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xf8006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes widened destination geometry, validates illegal width and source/destination overlap, reads the existing widened accumulator from `vd`, reads vector or scalar multiplicands, initializes masked results, adds the widened product to the old accumulator for active elements, writes back `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmaccus.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, xs1, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmaccus.vx` appears with match `111110-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xf8006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmaccus.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmul.vv.yaml

## Purpose

`vwmul.vv.yaml` describes `vwmul.vv`, a signed widening multiply, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmul.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=111011-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xec002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmul.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmul.vv` appears with match `111011-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xec002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmul.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmul.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmul.vx.yaml

## Purpose

`vwmul.vx.yaml` describes `vwmul.vx`, a signed widening multiply, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmul.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=111011-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xec006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmul.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmul.vx` appears with match `111011-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xec006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmul.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulsu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulsu.vv.yaml

## Purpose

`vwmulsu.vv.yaml` describes `vwmulsu.vv`, a signed-by-unsigned widening multiply, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmulsu.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=111010-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe8002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmulsu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmulsu.vv` appears with match `111010-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xe8002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulsu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulsu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulsu.vx.yaml

## Purpose

`vwmulsu.vx.yaml` describes `vwmulsu.vx`, a signed-by-unsigned widening multiply, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmulsu.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=111010-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe8006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmulsu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmulsu.vx` appears with match `111010-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xe8006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulsu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulu.vv.yaml

## Purpose

`vwmulu.vv.yaml` describes `vwmulu.vv`, a unsigned widening multiply, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmulu.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=111000-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe0002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmulu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmulu.vv` appears with match `111000-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xe0002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulu.vx.yaml

## Purpose

`vwmulu.vx.yaml` describes `vwmulu.vx`, a unsigned widening multiply, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwmulu.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=111000-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xe0006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwmulu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwmulu.vx` appears with match `111000-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xe0006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwmulu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwredsum.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwredsum.vs.yaml

## Purpose

`vwredsum.vs.yaml` describes `vwredsum.vs`, a signed widening reduction sum descriptor, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwredsum.vs`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110001-----------000-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc4000057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_reduction_widen`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_source`, `read_single_element`, `to`, `write_single_element`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block validates widening reduction legality, returns early for `vl=0`, reads the initial scalar accumulator from `vs1`, masks source elements from `vs2`, widens and accumulates active elements into a single widened sum, writes element zero of `vd`, leaves other destination elements as tail state, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwredsum.vs` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwredsum.vs` appears with match `110001-----------000-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xc4000057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Reduction tests should include `vl=0`, masked lanes, signed and unsigned widening, accumulator initialization from `vs1[0]`, and tail-element preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwredsum.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwredsumu.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwredsumu.vs.yaml

## Purpose

`vwredsumu.vs.yaml` describes `vwredsumu.vs`, a unsigned widening reduction sum descriptor, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwredsumu.vs`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110000-----------000-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc0000057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_reduction_widen`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_source`, `read_single_element`, `to`, `write_single_element`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block validates widening reduction legality, returns early for `vl=0`, reads the initial scalar accumulator from `vs1`, masks source elements from `vs2`, widens and accumulates active elements into a single widened sum, writes element zero of `vd`, leaves other destination elements as tail state, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwredsumu.vs` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwredsumu.vs` appears with match `110000-----------000-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xc0000057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Reduction tests should include `vl=0`, masked lanes, signed and unsigned widening, accumulator initialization from `vs1[0]`, and tail-element preservation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwredsumu.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.vv.yaml

## Purpose

`vwsub.vv.yaml` describes `vwsub.vv`, a signed widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsub.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110011-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xcc002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsub.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsub.vv` appears with match `110011-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xcc002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.vx.yaml

## Purpose

`vwsub.vx.yaml` describes `vwsub.vx`, a signed widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsub.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110011-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xcc006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsub.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsub.vx` appears with match `110011-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xcc006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.wv.yaml

## Purpose

`vwsub.wv.yaml` describes `vwsub.wv`, a signed widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsub.wv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110111-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xdc002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsub.wv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsub.wv` appears with match `110111-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xdc002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.wx.yaml

## Purpose

`vwsub.wx.yaml` describes `vwsub.wx`, a signed widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsub.wx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110111-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xdc006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsub.wx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsub.wx` appears with match `110111-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xdc006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsub.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.vv.yaml

## Purpose

`vwsubu.vv.yaml` describes `vwsubu.vv`, a unsigned widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsubu.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110010-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc8002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsubu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsubu.vv` appears with match `110010-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xc8002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.vx.yaml

## Purpose

`vwsubu.vx.yaml` describes `vwsubu.vx`, a unsigned widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsubu.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110010-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc8006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsubu.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsubu.vx` appears with match `110010-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xc8006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.wv.yaml

## Purpose

`vwsubu.wv.yaml` describes `vwsubu.wv`, a unsigned widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsubu.wv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110110-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xd8002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsubu.wv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsubu.wv` appears with match `110110-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xd8002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.wx.yaml

## Purpose

`vwsubu.wx.yaml` describes `vwsubu.wx`, a unsigned widening subtract, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwsubu.wx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=110110-----------110-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xd8006057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `get_scalar`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and the narrow source overlap, reads a wide accumulator/source vector from `vs2`, reads the narrow vector or scalar operand, initializes masked wide results, performs signed or unsigned add/subtract per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwsubu.wx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwsubu.wx` appears with match `110110-----------110-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0xd8006057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwsubu.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vi.yaml

## Purpose

`vxor.vi.yaml` describes `vxor.vi`, a vector bitwise XOR, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, imm, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vxor.vi`, `assembly=vd, vs2, imm, vm`, `encoding.match=001011-----------011-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `imm` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x2c003057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_shift_amount`, `get_fixed_rounding_incr`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vxor.vi` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, imm, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `imm` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vxor.vi` appears with match `001011-----------011-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `imm` bits 19-15, `vd` bits 11-7], opcode `0x2c003057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vv.yaml

## Purpose

`vxor.vv.yaml` describes `vxor.vv`, a vector bitwise XOR, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vxor.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=001011-----------000-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x2c000057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew_pow`, `get_sew`, `get_lmul_pow`, `get_vlen_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vxor.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vxor.vv` appears with match `001011-----------000-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0x2c000057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vx.yaml

## Purpose

`vxor.vx.yaml` describes `vxor.vx`, a vector bitwise XOR, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, xs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vxor.vx`, `assembly=vd, vs2, xs1, vm`, `encoding.match=001011-----------100-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x2c004057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_normal`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `get_scalar`, `read_vreg`, `init_masked_result`, `to`, `unsigned_saturation`, `signed_saturation`, `get_fixed_rounding_incr`, `get_shift_amount`, `min`, `max`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block reads SEW/LMUL, validates the normal vector destination and mask form with `illegal_normal`, reads the mask plus vector/scalar/immediate operands, initializes masked destination elements, iterates over every active element, dispatches by `funct6` to the arithmetic or logical operation, writes the vector destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vxor.vx` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, xs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Integer vector ALU entries depend on exact funct6/funct3 selection, mask handling, signed versus unsigned saturation, rounding mode for fixed-point shifts, scalar/immediate sign extension, and overlap checks represented only in Sail.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vxor.vx` appears with match `001011-----------100-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7], opcode `0x2c004057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. ALU tests should cover masked lanes, scalar or immediate operand forms, signed/unsigned saturation, fixed-point rounding where applicable, and `vstart` reset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vxor.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf2.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf2.yaml

## Purpose

`vzext.vf2.yaml` describes `vzext.vf2`, a vector zero-extension, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vzext.vf2`, `assembly=vd, vs2, vm`, `encoding.match=010010------00110010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48032057`, the opcode mask is `0xfc0ff07f`, and the match string has 21 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `assert`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block treats the source as a fractional-width vector, validates width and overlap, reads masked destination state and source elements, zero-extends each active source element into the full destination SEW, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vzext.vf2` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vzext.vf2` appears with match `010010------00110010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7], opcode `0x48032057`, and mask `0xfc0ff07f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf4.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf4.yaml

## Purpose

`vzext.vf4.yaml` describes `vzext.vf4`, a vector zero-extension, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vzext.vf4`, `assembly=vd, vs2, vm`, `encoding.match=010010------00100010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48022057`, the opcode mask is `0xfc0ff07f`, and the match string has 21 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `assert`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block treats the source as a fractional-width vector, validates width and overlap, reads masked destination state and source elements, zero-extends each active source element into the full destination SEW, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vzext.vf4` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vzext.vf4` appears with match `010010------00100010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7], opcode `0x48022057`, and mask `0xfc0ff07f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf8.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf8.yaml

## Purpose

`vzext.vf8.yaml` describes `vzext.vf8`, a vector zero-extension, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vzext.vf8`, `assembly=vd, vs2, vm`, `encoding.match=010010------00010010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=false`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x48012057`, the opcode mask is `0xfc0ff07f`, and the match string has 21 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `assert`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block treats the source as a fractional-width vector, validates width and overlap, reads masked destination state and source elements, zero-extends each active source element into the full destination SEW, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vzext.vf8` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vzext.vf8` appears with match `010010------00010010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7], opcode `0x48012057`, and mask `0xfc0ff07f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vzext.vf8.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.aq.yaml

## Purpose

`amoadd.d.aq.yaml` describes `amoadd.d.aq`, a Zaamo atomic fetch-and-add doubleword descriptor with acquire memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.d.aq`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000010----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0400302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.d.aq` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.d.aq` appears with match `0000010----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0400302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.aqrl.yaml

## Purpose

`amoadd.d.aqrl.yaml` describes `amoadd.d.aqrl`, a Zaamo atomic fetch-and-add doubleword descriptor with acquire-release memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.d.aqrl`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000011----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0600302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.d.aqrl` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.d.aqrl` appears with match `0000011----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0600302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.rl.yaml

## Purpose

`amoadd.d.rl.yaml` describes `amoadd.d.rl`, a Zaamo atomic fetch-and-add doubleword descriptor with release memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.d.rl`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000001----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0200302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.d.rl` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.d.rl` appears with match `0000001----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0200302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.yaml

## Purpose

`amoadd.d.yaml` describes `amoadd.d`, a Zaamo atomic fetch-and-add doubleword descriptor with unordered memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.d`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000000----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0000302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.d` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.d` appears with match `0000000----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0000302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.aq.yaml

## Purpose

`amoadd.w.aq.yaml` describes `amoadd.w.aq`, a Zaamo atomic fetch-and-add word descriptor with acquire memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.w.aq`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000010----------010-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0400202f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.w.aq` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.w.aq` appears with match `0000010----------010-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0400202f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.aqrl.yaml

## Purpose

`amoadd.w.aqrl.yaml` describes `amoadd.w.aqrl`, a Zaamo atomic fetch-and-add word descriptor with acquire-release memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.w.aqrl`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000011----------010-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0600202f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.w.aqrl` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.w.aqrl` appears with match `0000011----------010-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0600202f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.rl.yaml

## Purpose

`amoadd.w.rl.yaml` describes `amoadd.w.rl`, a Zaamo atomic fetch-and-add word descriptor with release memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.w.rl`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000001----------010-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0200202f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.w.rl` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.w.rl` appears with match `0000001----------010-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0200202f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.yaml

## Purpose

`amoadd.w.yaml` describes `amoadd.w`, a Zaamo atomic fetch-and-add word descriptor with unordered memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.w`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000000----------010-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0000202f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.w` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.w` appears with match `0000000----------010-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0000202f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.aq.yaml

## Purpose

`amoand.d.aq.yaml` describes `amoand.d.aq`, a Zaamo atomic fetch-and-and doubleword descriptor with acquire memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoand.d.aq`, `assembly=xd, xs2, (xs1)`, `encoding.match=0110010----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x6400302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoand.d.aq` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoand.d.aq` appears with match `0110010----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x6400302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.aqrl.yaml

## Purpose

`amoand.d.aqrl.yaml` describes `amoand.d.aqrl`, a Zaamo atomic fetch-and-and doubleword descriptor with acquire-release memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoand.d.aqrl`, `assembly=xd, xs2, (xs1)`, `encoding.match=0110011----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x6600302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoand.d.aqrl` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoand.d.aqrl` appears with match `0110011----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x6600302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.rl.yaml

## Purpose

`amoand.d.rl.yaml` describes `amoand.d.rl`, a Zaamo atomic fetch-and-and doubleword descriptor with release memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoand.d.rl`, `assembly=xd, xs2, (xs1)`, `encoding.match=0110001----------011-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x6200302f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoand.d.rl` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoand.d.rl` appears with match `0110001----------011-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x6200302f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.rl.yaml -->
