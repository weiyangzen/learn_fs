# Research Group subset-b-009465

This grouped report covers RISC-V Vector instruction YAML descriptors under `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vf.yaml` is a riscv-unified-db YAML
descriptor for `vmfle.vf`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, fs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point less-
than-or-equal comparison producing a mask bit per active element. This is the vector-scalar
floating-point form; `fs1` occupies the rs1 field and is read by Sail through `get_scalar_fp`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2314 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmfle.vf`,
`definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011001-----------101-----1010111`, which computes to opcode `0x64005057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `fs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, fs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `fs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmfle.vf` is emitted.
- Check the generated entry has opcode `0x64005057`, mask `0xfc00707f`, and fields `vm, vs2, fs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmfle.vv`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point less-
than-or-equal comparison producing a mask bit per active element. This is the vector-vector form;
both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2239 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmfle.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011001-----------001-----1010111`, which computes to opcode `0x64001057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmfle.vv` is emitted.
- Check the generated entry has opcode `0x64001057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfle.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vf.yaml` is a riscv-unified-db YAML
descriptor for `vmflt.vf`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, fs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point less-
than comparison producing a mask bit per active element. This is the vector-scalar floating-point
form; `fs1` occupies the rs1 field and is read by Sail through `get_scalar_fp`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2314 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmflt.vf`,
`definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011011-----------101-----1010111`, which computes to opcode `0x6c005057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `fs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, fs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `fs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmflt.vf` is emitted.
- Check the generated entry has opcode `0x6c005057`, mask `0xfc00707f`, and fields `vm, vs2, fs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmflt.vv`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point less-
than comparison producing a mask bit per active element. This is the vector-vector form; both
element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2239 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmflt.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011011-----------001-----1010111`, which computes to opcode `0x6c001057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmflt.vv` is emitted.
- Check the generated entry has opcode `0x6c001057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmflt.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vf.yaml` is a riscv-unified-db YAML
descriptor for `vmfne.vf`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, fs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point not-
equal comparison producing a mask bit per active element. This is the vector-scalar floating-point
form; `fs1` occupies the rs1 field and is read by Sail through `get_scalar_fp`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2314 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmfne.vf`,
`definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011100-----------101-----1010111`, which computes to opcode `0x70005057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `fs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, fs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `fs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmfne.vf` is emitted.
- Check the generated entry has opcode `0x70005057`, mask `0xfc00707f`, and fields `vm, vs2, fs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmfne.vv`, a floating-point compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents floating-point not-
equal comparison producing a mask bit per active element. This is the vector-vector form; both
element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2239 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmfne.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011100-----------001-----1010111`, which computes to opcode `0x70001057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes SEW/LMUL/VLMAX, checks FP compare legality, reads mask and
operands, initializes a mask destination preserving inactive lanes, evaluates the selected FP
predicate per active element, writes `vd` as a mask register, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Floating-point exceptions, NaN behavior, FRM legality, and illegal SEW=8 behavior are architectural semantics in Sail but not constraints in the generated instruction table.

The Sail body reads `fcsr.FRM()`, rejects illegal FP compare destinations with
`illegal_fp_vd_unmasked`, asserts `SEW != 8`, preserves inactive destination mask bits via
`init_masked_result_cmp`, and writes mask bits with `write_vmask`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmfne.vv` is emitted.
- Check the generated entry has opcode `0x70001057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include legal FP element widths, illegal SEW=8, NaNs, FP exception flags, masked inactive lanes, and destination mask alias cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmfne.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmin.vv`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
signed integer minimum, selecting the smaller signed element value. This is the vector-vector form;
both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 134
lines / 6447 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmin.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000101-----------000-----1010111`, which computes to opcode `0x14000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmin.vv` is emitted.
- Check the generated entry has opcode `0x14000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmin.vx`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
signed integer minimum, selecting the smaller signed element value. This is the vector-scalar
integer form; `xs1` occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 117
lines / 4888 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmin.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000101-----------100-----1010111`, which computes to opcode `0x14004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmin.vx` is emitted.
- Check the generated entry has opcode `0x14004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmin.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vv.yaml` is a riscv-unified-db YAML
descriptor for `vminu.vv`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
unsigned integer minimum, selecting the smaller unsigned element value. This is the vector-vector
form; both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 134
lines / 6448 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vminu.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000100-----------000-----1010111`, which computes to opcode `0x10000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vminu.vv` is emitted.
- Check the generated entry has opcode `0x10000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vx.yaml` is a riscv-unified-db YAML
descriptor for `vminu.vx`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
unsigned integer minimum, selecting the smaller unsigned element value. This is the vector-scalar
integer form; `xs1` occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 117
lines / 4889 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vminu.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000100-----------100-----1010111`, which computes to opcode `0x10004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vminu.vx` is emitted.
- Check the generated entry has opcode `0x10004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vminu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnand.mm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnand.mm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnand.mm.yaml` is a riscv-unified-db
YAML descriptor for `vmnand.mm`, a mask logical operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask NAND, writing the
inverse of the bitwise AND of two mask sources. This is a mask-register logical form; operands and
destination are mask registers and there is no separate `vm` masking operand.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 75
lines / 2158 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmnand.mm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0111011----------010-----1010111`, which computes to opcode `0x76002057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the mask logical flow reads source masks, applies the Boolean operation bit by bit,
writes the destination mask, and resets `vstart` where a Sail body is provided.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Mask logical descriptors operate over mask-register bit vectors. Sail bodies, when present, read
mask sources with mask semantics, compute the Boolean operation per bit, write a mask destination,
and reset `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmnand.mm` is emitted.
- Check the generated entry has opcode `0x76002057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnand.mm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnor.mm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnor.mm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnor.mm.yaml` is a riscv-unified-db YAML
descriptor for `vmnor.mm`, a mask logical operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask NOR, writing the
inverse of the bitwise OR of two mask sources. This is a mask-register logical form; operands and
destination are mask registers and there is no separate `vm` masking operand.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 75
lines / 2157 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmnor.mm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0111101----------010-----1010111`, which computes to opcode `0x7a002057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the mask logical flow reads source masks, applies the Boolean operation bit by bit,
writes the destination mask, and resets `vstart` where a Sail body is provided.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Mask logical descriptors operate over mask-register bit vectors. Sail bodies, when present, read
mask sources with mask semantics, compute the Boolean operation per bit, write a mask destination,
and reset `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmnor.mm` is emitted.
- Check the generated entry has opcode `0x7a002057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmnor.mm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmor.mm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmor.mm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmor.mm.yaml` is a riscv-unified-db YAML
descriptor for `vmor.mm`, a mask logical operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and an
optional Sail reference body. Semantically, this descriptor represents mask OR over two mask
sources. This is a mask-register logical form; operands and destination are mask registers and there
is no separate `vm` masking operand.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 75
lines / 2156 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmor.mm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0110101----------010-----1010111`, which computes to opcode `0x6a002057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the mask logical flow reads source masks, applies the Boolean operation bit by bit,
writes the destination mask, and resets `vstart` where a Sail body is provided.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Mask logical descriptors operate over mask-register bit vectors. Sail bodies, when present, read
mask sources with mask semantics, compute the Boolean operation per bit, write a mask destination,
and reset `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmor.mm` is emitted.
- Check the generated entry has opcode `0x6a002057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmor.mm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmorn.mm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmorn.mm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmorn.mm.yaml` is a riscv-unified-db YAML
descriptor for `vmorn.mm`, a mask logical operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask OR-not form,
combining one mask source with the inverted other source. This is a mask-register logical form;
operands and destination are mask registers and there is no separate `vm` masking operand.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 31
lines / 664 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmorn.mm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0111001----------010-----1010111`, which computes to opcode `0x72002057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
There is no Sail execution flow in this file beyond the empty `operation()` field.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- The missing Sail block reduces semantic auditability; tests should rely on external RISC-V Vector references for this mnemonic.

This descriptor has an empty `operation()` block and no embedded Sail body, so local semantic
traceability comes from the mnemonic, assembly form, and encoding metadata rather than executable
pseudocode. Mask logical descriptors operate over mask-register bit vectors. Sail bodies, when
present, read mask sources with mask semantics, compute the Boolean operation per bit, write a mask
destination, and reset `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmorn.mm` is emitted.
- Check the generated entry has opcode `0x72002057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmorn.mm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmsbc.vv`, a borrow-out mask arithmetic in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents subtract-with-borrow mask
generation, writing whether each subtraction borrows. This is the vector-vector form; both element
operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 70
lines / 1972 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsbc.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0100111----------000-----1010111`, which computes to opcode `0x4e000057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks unmasked mask-destination legality, reads operands and carry/borrow
mask state, computes borrow-out for each active element, writes the mask result, clears `vstart`,
and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

The borrow template reads the carry/borrow input mask with `read_vmask_carry`, computes unsigned
subtraction underflow per active element, writes the borrow result to a mask destination, and uses
`illegal_vd_unmasked` legality rather than normal vector destination rules.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsbc.vv` is emitted.
- Check the generated entry has opcode `0x4e000057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include borrow-in from v0, zero operands, all-ones operands, masked variants, and destination mask preservation rules.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vvm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vvm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vvm.yaml` is a riscv-unified-db
YAML descriptor for `vmsbc.vvm`, a borrow-out mask arithmetic in the RISC-V Vector (`V`) extension.
It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, v0`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents subtract-with-borrow
mask generation, writing whether each subtraction borrows. This is the vector-vector carry/borrow-
mask form; the input carry mask is fixed to `v0` rather than exposed as `vm`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 71
lines / 2135 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsbc.vvm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, v0`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0100110----------000-----1010111`, which computes to opcode `0x4c000057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks unmasked mask-destination legality, reads operands and carry/borrow
mask state, computes borrow-out for each active element, writes the mask result, clears `vstart`,
and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, v0` must describe
the same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

The borrow template reads the carry/borrow input mask with `read_vmask_carry`, computes unsigned
subtraction underflow per active element, writes the borrow result to a mask destination, and uses
`illegal_vd_unmasked` legality rather than normal vector destination rules.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsbc.vvm` is emitted.
- Check the generated entry has opcode `0x4c000057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include borrow-in from v0, zero operands, all-ones operands, masked variants, and destination mask preservation rules.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vvm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmsbc.vx`, a borrow-out mask arithmetic in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents subtract-with-borrow mask
generation, writing whether each subtraction borrows. This is the vector-scalar integer form; `xs1`
occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 70
lines / 1947 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsbc.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0100111----------100-----1010111`, which computes to opcode `0x4e004057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks unmasked mask-destination legality, reads operands and carry/borrow
mask state, computes borrow-out for each active element, writes the mask result, clears `vstart`,
and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1` must describe the
same architectural operands that ``vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

The borrow template reads the carry/borrow input mask with `read_vmask_carry`, computes unsigned
subtraction underflow per active element, writes the borrow result to a mask destination, and uses
`illegal_vd_unmasked` legality rather than normal vector destination rules.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsbc.vx` is emitted.
- Check the generated entry has opcode `0x4e004057`, mask `0xfe00707f`, and fields `vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include borrow-in from v0, zero operands, all-ones operands, masked variants, and destination mask preservation rules.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vxm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vxm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vxm.yaml` is a riscv-unified-db
YAML descriptor for `vmsbc.vxm`, a borrow-out mask arithmetic in the RISC-V Vector (`V`) extension.
It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, v0`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents subtract-with-borrow
mask generation, writing whether each subtraction borrows. This is the vector-scalar carry/borrow-
mask form; the input carry mask is fixed to `v0` rather than exposed as `vm`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 71
lines / 2110 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsbc.vxm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, v0`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0100110----------100-----1010111`, which computes to opcode `0x4c004057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks unmasked mask-destination legality, reads operands and carry/borrow
mask state, computes borrow-out for each active element, writes the mask result, clears `vstart`,
and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, v0` must describe
the same architectural operands that ``vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

The borrow template reads the carry/borrow input mask with `read_vmask_carry`, computes unsigned
subtraction underflow per active element, writes the borrow result to a mask destination, and uses
`illegal_vd_unmasked` legality rather than normal vector destination rules.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsbc.vxm` is emitted.
- Check the generated entry has opcode `0x4c004057`, mask `0xfe00707f`, and fields `vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include borrow-in from v0, zero operands, all-ones operands, masked variants, and destination mask preservation rules.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbc.vxm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbf.m.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbf.m.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbf.m.yaml` is a riscv-unified-db YAML
descriptor for `vmsbf.m`, a first-set mask prefix operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vm`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask-set-before-first,
setting output bits before the first selected set source bit. This is a mask-producing mask-source
form; the destination and source are mask registers and bit 25 controls masking.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 69
lines / 1862 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsbf.m`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010100------00001010-----1010111`, which computes to opcode `0x5000a057` and opcode mask
`0xfc0ff07f` with 21 fixed bits and 11 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow scans mask bits from low to high with a `found_elem` flag to build the
before/inclusive/only-first result, then writes the destination mask and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vm` must describe the
same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The first-set mask template scans all mask bits (`vlenb * 8`), requires `vstart == 0` and `vd !=
vs2`, tracks whether a selected source bit has been found, and produces before/inclusive/only-first
masks.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsbf.m` is emitted.
- Check the generated entry has opcode `0x5000a057`, mask `0xfc0ff07f`, and fields `vm, vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include no set source bits, first bit set, later set bits, masked-off first bits, `vstart != 0`, and `vd == vs2` illegal cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsbf.m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vi.yaml` is a riscv-unified-db YAML
descriptor for `vmseq.vi`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents integer equality
comparison producing mask results. This is the vector-immediate form; the five-bit immediate
occupies bits 19-15 and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2292 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmseq.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011000-----------011-----1010111`, which computes to opcode `0x60003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmseq.vi` is emitted.
- Check the generated entry has opcode `0x60003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmseq.vv`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents integer equality
comparison producing mask results. This is the vector-vector form; both element operands are read
from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2332 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmseq.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011000-----------000-----1010111`, which computes to opcode `0x60000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmseq.vv` is emitted.
- Check the generated entry has opcode `0x60000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmseq.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents integer equality
comparison producing mask results. This is the vector-scalar integer form; `xs1` occupies the rs1
field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2431 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmseq.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011000-----------100-----1010111`, which computes to opcode `0x60004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmseq.vx` is emitted.
- Check the generated entry has opcode `0x60004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmseq.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vi.yaml` is a riscv-unified-db YAML
descriptor for `vmsgt.vi`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer
greater-than comparison producing mask results. This is the vector-immediate form; the five-bit
immediate occupies bits 19-15 and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2292 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsgt.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011111-----------011-----1010111`, which computes to opcode `0x7c003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsgt.vi` is emitted.
- Check the generated entry has opcode `0x7c003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmsgt.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer
greater-than comparison producing mask results. This is the vector-scalar integer form; `xs1`
occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2431 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsgt.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011111-----------100-----1010111`, which computes to opcode `0x7c004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsgt.vx` is emitted.
- Check the generated entry has opcode `0x7c004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgt.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vi.yaml` is a riscv-unified-db
YAML descriptor for `vmsgtu.vi`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer
greater-than comparison producing mask results. This is the vector-immediate form; the five-bit
immediate occupies bits 19-15 and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2293 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsgtu.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011110-----------011-----1010111`, which computes to opcode `0x78003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsgtu.vi` is emitted.
- Check the generated entry has opcode `0x78003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vx.yaml` is a riscv-unified-db
YAML descriptor for `vmsgtu.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer
greater-than comparison producing mask results. This is the vector-scalar integer form; `xs1`
occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2432 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsgtu.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011110-----------100-----1010111`, which computes to opcode `0x78004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsgtu.vx` is emitted.
- Check the generated entry has opcode `0x78004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsgtu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsif.m.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsif.m.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsif.m.yaml` is a riscv-unified-db YAML
descriptor for `vmsif.m`, a first-set mask prefix operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vm`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask-set-including-first,
setting output bits through the first selected set source bit. This is a mask-producing mask-source
form; the destination and source are mask registers and bit 25 controls masking.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 69
lines / 1862 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsif.m`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010100------00011010-----1010111`, which computes to opcode `0x5001a057` and opcode mask
`0xfc0ff07f` with 21 fixed bits and 11 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow scans mask bits from low to high with a `found_elem` flag to build the
before/inclusive/only-first result, then writes the destination mask and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vm` must describe the
same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The first-set mask template scans all mask bits (`vlenb * 8`), requires `vstart == 0` and `vd !=
vs2`, tracks whether a selected source bit has been found, and produces before/inclusive/only-first
masks.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsif.m` is emitted.
- Check the generated entry has opcode `0x5001a057`, mask `0xfc0ff07f`, and fields `vm, vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include no set source bits, first bit set, later set bits, masked-off first bits, `vstart != 0`, and `vd == vs2` illegal cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsif.m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vi.yaml` is a riscv-unified-db YAML
descriptor for `vmsle.vi`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer less-
than-or-equal comparison producing mask results. This is the vector-immediate form; the five-bit
immediate occupies bits 19-15 and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2292 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsle.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011101-----------011-----1010111`, which computes to opcode `0x74003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsle.vi` is emitted.
- Check the generated entry has opcode `0x74003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmsle.vv`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer less-
than-or-equal comparison producing mask results. This is the vector-vector form; both element
operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2332 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsle.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011101-----------000-----1010111`, which computes to opcode `0x74000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsle.vv` is emitted.
- Check the generated entry has opcode `0x74000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmsle.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer less-
than-or-equal comparison producing mask results. This is the vector-scalar integer form; `xs1`
occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2431 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsle.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011101-----------100-----1010111`, which computes to opcode `0x74004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsle.vx` is emitted.
- Check the generated entry has opcode `0x74004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsle.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vi.yaml` is a riscv-unified-db
YAML descriptor for `vmsleu.vi`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer less-
than-or-equal comparison producing mask results. This is the vector-immediate form; the five-bit
immediate occupies bits 19-15 and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2293 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsleu.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011100-----------011-----1010111`, which computes to opcode `0x70003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsleu.vi` is emitted.
- Check the generated entry has opcode `0x70003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vv.yaml` is a riscv-unified-db
YAML descriptor for `vmsleu.vv`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer less-
than-or-equal comparison producing mask results. This is the vector-vector form; both element
operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2333 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsleu.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011100-----------000-----1010111`, which computes to opcode `0x70000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsleu.vv` is emitted.
- Check the generated entry has opcode `0x70000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vx.yaml` is a riscv-unified-db
YAML descriptor for `vmsleu.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer less-
than-or-equal comparison producing mask results. This is the vector-scalar integer form; `xs1`
occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2432 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsleu.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011100-----------100-----1010111`, which computes to opcode `0x70004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsleu.vx` is emitted.
- Check the generated entry has opcode `0x70004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsleu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmslt.vv`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer less-
than comparison producing mask results. This is the vector-vector form; both element operands are
read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2332 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmslt.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011011-----------000-----1010111`, which computes to opcode `0x6c000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmslt.vv` is emitted.
- Check the generated entry has opcode `0x6c000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmslt.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents signed integer less-
than comparison producing mask results. This is the vector-scalar integer form; `xs1` occupies the
rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2431 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmslt.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011011-----------100-----1010111`, which computes to opcode `0x6c004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmslt.vx` is emitted.
- Check the generated entry has opcode `0x6c004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmslt.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vv.yaml` is a riscv-unified-db
YAML descriptor for `vmsltu.vv`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer less-
than comparison producing mask results. This is the vector-vector form; both element operands are
read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2333 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsltu.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011010-----------000-----1010111`, which computes to opcode `0x68000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsltu.vv` is emitted.
- Check the generated entry has opcode `0x68000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vx.yaml` is a riscv-unified-db
YAML descriptor for `vmsltu.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents unsigned integer less-
than comparison producing mask results. This is the vector-scalar integer form; `xs1` occupies the
rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2432 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsltu.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011010-----------100-----1010111`, which computes to opcode `0x68004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsltu.vx` is emitted.
- Check the generated entry has opcode `0x68004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsltu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vi.yaml` is a riscv-unified-db YAML
descriptor for `vmsne.vi`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents integer not-equal
comparison producing mask results. This is the vector-immediate form; the five-bit immediate
occupies bits 19-15 and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2292 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsne.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011001-----------011-----1010111`, which computes to opcode `0x64003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsne.vi` is emitted.
- Check the generated entry has opcode `0x64003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmsne.vv`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents integer not-equal
comparison producing mask results. This is the vector-vector form; both element operands are read
from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 77
lines / 2332 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsne.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011001-----------000-----1010111`, which computes to opcode `0x64000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsne.vv` is emitted.
- Check the generated entry has opcode `0x64000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmsne.vx`, a integer compare-to-mask in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents integer not-equal
comparison producing mask results. This is the vector-scalar integer form; `xs1` occupies the rs1
field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 79
lines / 2431 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsne.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`011001-----------100-----1010111`, which computes to opcode `0x64004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow reads vector/scalar/immediate operands according to the suffix,
initializes the destination mask, evaluates the selected comparison predicate for active elements,
writes the resulting mask, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body follows the integer comparison template: read mask and operands, initialize comparison
mask output, evaluate the selected signed/unsigned/equality predicate per active element, write `vd`
as a mask, and clear `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsne.vx` is emitted.
- Check the generated entry has opcode `0x64004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsne.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsof.m.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsof.m.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsof.m.yaml` is a riscv-unified-db YAML
descriptor for `vmsof.m`, a first-set mask prefix operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vm`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask-set-only-first,
setting only the first selected set source bit. This is a mask-producing mask-source form; the
destination and source are mask registers and bit 25 controls masking.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 73
lines / 1919 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmsof.m`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010100------00010010-----1010111`, which computes to opcode `0x50012057` and opcode mask
`0xfc0ff07f` with 21 fixed bits and 11 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow scans mask bits from low to high with a `found_elem` flag to build the
before/inclusive/only-first result, then writes the destination mask and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vm` must describe the
same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The first-set mask template scans all mask bits (`vlenb * 8`), requires `vstart == 0` and `vd !=
vs2`, tracks whether a selected source bit has been found, and produces before/inclusive/only-first
masks.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmsof.m` is emitted.
- Check the generated entry has opcode `0x50012057`, mask `0xfc0ff07f`, and fields `vm, vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include no set source bits, first bit set, later set bits, masked-off first bits, `vstart != 0`, and `vd == vs2` illegal cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmsof.m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmul.vv`, a integer multiply/divide/remainder template operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
low-half signed integer multiply. This is the vector-vector form; both element operands are read
from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 116
lines / 5189 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmul.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100101-----------010-----1010111`, which computes to opcode `0x94002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmul.vv` is emitted.
- Check the generated entry has opcode `0x94002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmul.vx`, a integer multiply/divide/remainder template operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
low-half signed integer multiply. This is the vector-scalar integer form; `xs1` occupies the rs1
field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 125
lines / 5817 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmul.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100101-----------110-----1010111`, which computes to opcode `0x94006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmul.vx` is emitted.
- Check the generated entry has opcode `0x94006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmul.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vv.yaml` is a riscv-unified-db YAML
descriptor for `vmulh.vv`, a integer multiply/divide/remainder template operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
high-half signed integer multiply. This is the vector-vector form; both element operands are read
from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 116
lines / 5190 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmulh.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100111-----------010-----1010111`, which computes to opcode `0x9c002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmulh.vv` is emitted.
- Check the generated entry has opcode `0x9c002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vx.yaml` is a riscv-unified-db YAML
descriptor for `vmulh.vx`, a integer multiply/divide/remainder template operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
high-half signed integer multiply. This is the vector-scalar integer form; `xs1` occupies the rs1
field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 125
lines / 5818 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmulh.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100111-----------110-----1010111`, which computes to opcode `0x9c006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmulh.vx` is emitted.
- Check the generated entry has opcode `0x9c006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulh.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vv.yaml` is a riscv-unified-db
YAML descriptor for `vmulhsu.vv`, a integer multiply/divide/remainder template operation in the
RISC-V Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative
instruction metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit
encoding pattern, operand bit ranges, and an optional Sail reference body. Semantically, this
descriptor represents high-half signed-by-unsigned integer multiply. This is the vector-vector form;
both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 116
lines / 5192 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmulhsu.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100110-----------010-----1010111`, which computes to opcode `0x98002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmulhsu.vv` is emitted.
- Check the generated entry has opcode `0x98002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vx.yaml` is a riscv-unified-db
YAML descriptor for `vmulhsu.vx`, a integer multiply/divide/remainder template operation in the
RISC-V Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative
instruction metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit
encoding pattern, operand bit ranges, and an optional Sail reference body. Semantically, this
descriptor represents high-half signed-by-unsigned integer multiply. This is the vector-scalar
integer form; `xs1` occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 125
lines / 5820 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmulhsu.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100110-----------110-----1010111`, which computes to opcode `0x98006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmulhsu.vx` is emitted.
- Check the generated entry has opcode `0x98006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhsu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vv.yaml` is a riscv-unified-db
YAML descriptor for `vmulhu.vv`, a integer multiply/divide/remainder template operation in the
RISC-V Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative
instruction metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit
encoding pattern, operand bit ranges, and an optional Sail reference body. Semantically, this
descriptor represents high-half unsigned integer multiply. This is the vector-vector form; both
element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 116
lines / 5191 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmulhu.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100100-----------010-----1010111`, which computes to opcode `0x90002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmulhu.vv` is emitted.
- Check the generated entry has opcode `0x90002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vx.yaml` is a riscv-unified-db
YAML descriptor for `vmulhu.vx`, a integer multiply/divide/remainder template operation in the
RISC-V Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative
instruction metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit
encoding pattern, operand bit ranges, and an optional Sail reference body. Semantically, this
descriptor represents high-half unsigned integer multiply. This is the vector-scalar integer form;
`xs1` occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 125
lines / 5819 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmulhu.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100100-----------110-----1010111`, which computes to opcode `0x90006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply template computes products per active element and selects low or high SEW bits with
signed, unsigned, or mixed signedness according to the mnemonic.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmulhu.vx` is emitted.
- Check the generated entry has opcode `0x90006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmulhu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.s.x.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.s.x.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.s.x.yaml` is a riscv-unified-db YAML
descriptor for `vmv.s.x`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, xs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents scalar integer-to-vector-element move
into element 0 of a vector register. This is one of the vector move encodings with fixed mask
behavior and a reduced operand set.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 70
lines / 1921 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv.s.x`,
`definedBy.extension.name: V`, `assembly: vd, xs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010000100000-----110-----1010111`, which computes to opcode `0x42006057` and opcode mask
`0xfff0707f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `xs1` bits 19-15; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, xs1` must describe the same
architectural operands that ``xs1` bits 19-15; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv.s.x` is emitted.
- Check the generated entry has opcode `0x42006057`, mask `0xfff0707f`, and fields `xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.s.x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.i.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.i.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.i.yaml` is a riscv-unified-db YAML
descriptor for `vmv.v.i`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, imm`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole-vector immediate splat move.
This is one of the vector move encodings with fixed mask behavior and a reduced operand set.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1700 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv.v.i`,
`definedBy.extension.name: V`, `assembly: vd, imm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010111100000-----011-----1010111`, which computes to opcode `0x5e003057` and opcode mask
`0xfff0707f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `imm` bits 19-15; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, imm` must describe the same
architectural operands that ``imm` bits 19-15; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv.v.i` is emitted.
- Check the generated entry has opcode `0x5e003057`, mask `0xfff0707f`, and fields `imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.i.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.v.yaml` is a riscv-unified-db YAML
descriptor for `vmv.v.v`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole-vector register copy move. This
is one of the vector move encodings with fixed mask behavior and a reduced operand set.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1725 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv.v.v`,
`definedBy.extension.name: V`, `assembly: vd, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010111100000-----000-----1010111`, which computes to opcode `0x5e000057` and opcode mask
`0xfff0707f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `vs1` bits 19-15; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs1` must describe the same
architectural operands that ``vs1` bits 19-15; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv.v.v` is emitted.
- Check the generated entry has opcode `0x5e000057`, mask `0xfff0707f`, and fields `vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.x.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.x.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.x.yaml` is a riscv-unified-db YAML
descriptor for `vmv.v.x`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, xs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole-vector scalar integer splat
move. This is one of the vector move encodings with fixed mask behavior and a reduced operand set.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1702 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv.v.x`,
`definedBy.extension.name: V`, `assembly: vd, xs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`010111100000-----100-----1010111`, which computes to opcode `0x5e004057` and opcode mask
`0xfff0707f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `xs1` bits 19-15; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, xs1` must describe the same
architectural operands that ``xs1` bits 19-15; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv.v.x` is emitted.
- Check the generated entry has opcode `0x5e004057`, mask `0xfff0707f`, and fields `xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.v.x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.x.s.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.x.s.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.x.s.yaml` is a riscv-unified-db YAML
descriptor for `vmv.x.s`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `xd, vs2`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents vector-element-to-integer-register
move from element 0. This is one of the vector move encodings with fixed mask behavior and a reduced
operand set.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 54
lines / 1359 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv.x.s`,
`definedBy.extension.name: V`, `assembly: xd, vs2`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0100001-----00000010-----1010111`, which computes to opcode `0x42002057` and opcode mask
`0xfe0ff07f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `vs2` bits 24-20; `xd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `xd, vs2` must describe the same
architectural operands that ``vs2` bits 24-20; `xd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv.x.s` is emitted.
- Check the generated entry has opcode `0x42002057`, mask `0xfe0ff07f`, and fields `vs2, xd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv.x.s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv1r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv1r.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv1r.v.yaml` is a riscv-unified-db YAML
descriptor for `vmv1r.v`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, vs2`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole vector register group move for
EMUL 1. The assembly form is `vd, vs2`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1771 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv1r.v`,
`definedBy.extension.name: V`, `assembly: vd, vs2`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`1001111-----00000011-----1010111`, which computes to opcode `0x9e003057` and opcode mask
`0xfe0ff07f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2` must describe the same
architectural operands that ``vs2` bits 24-20; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Whole-register moves rely on fixed immediate bits to select EMUL; changing those fixed bits can make the Sail EMUL legality check disagree with the mnemonic.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv1r.v` is emitted.
- Check the generated entry has opcode `0x9e003057`, mask `0xfe0ff07f`, and fields `vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv1r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv2r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv2r.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv2r.v.yaml` is a riscv-unified-db YAML
descriptor for `vmv2r.v`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, vs2`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole vector register group move for
EMUL 2. The assembly form is `vd, vs2`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1771 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv2r.v`,
`definedBy.extension.name: V`, `assembly: vd, vs2`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`1001111-----00001011-----1010111`, which computes to opcode `0x9e00b057` and opcode mask
`0xfe0ff07f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2` must describe the same
architectural operands that ``vs2` bits 24-20; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Whole-register moves rely on fixed immediate bits to select EMUL; changing those fixed bits can make the Sail EMUL legality check disagree with the mnemonic.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv2r.v` is emitted.
- Check the generated entry has opcode `0x9e00b057`, mask `0xfe0ff07f`, and fields `vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv2r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv4r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv4r.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv4r.v.yaml` is a riscv-unified-db YAML
descriptor for `vmv4r.v`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, vs2`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole vector register group move for
EMUL 4. The assembly form is `vd, vs2`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1771 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv4r.v`,
`definedBy.extension.name: V`, `assembly: vd, vs2`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`1001111-----00011011-----1010111`, which computes to opcode `0x9e01b057` and opcode mask
`0xfe0ff07f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2` must describe the same
architectural operands that ``vs2` bits 24-20; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Whole-register moves rely on fixed immediate bits to select EMUL; changing those fixed bits can make the Sail EMUL legality check disagree with the mnemonic.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv4r.v` is emitted.
- Check the generated entry has opcode `0x9e01b057`, mask `0xfe0ff07f`, and fields `vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv4r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv8r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv8r.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv8r.v.yaml` is a riscv-unified-db YAML
descriptor for `vmv8r.v`, a vector move operation in the RISC-V Vector (`V`) extension. It supplies
syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic, assembly
operands `vd, vs2`, access policy, a 32-bit encoding pattern, operand bit ranges, and an optional
Sail reference body. Semantically, this descriptor represents whole vector register group move for
EMUL 8. The assembly form is `vd, vs2`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 62
lines / 1771 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmv8r.v`,
`definedBy.extension.name: V`, `assembly: vd, vs2`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`1001111-----00111011-----1010111`, which computes to opcode `0x9e03b057` and opcode mask
`0xfe0ff07f` with 22 fixed bits and 10 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vd` bits 11-7. The access policy is s=always, u=always,
vs=always, vu=always; because user and virtual-user access are both `always`, `gen.go` should
serialize this instruction with `Priv: false`. The Go integration types and functions are
`instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and `riscv64.InsnField` in
`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and `pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the move flow reads the required scalar or vector source, applies fixed unmasked
destination behavior, copies the selected element/vector/register group, handles tail or pre-start
preservation where the Sail body calls for it, writes the destination, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2` must describe the same
architectural operands that ``vs2` bits 24-20; `vd` bits 11-7` exposes to generated randomization.
The Sail body, when present, is an integration point for external architecture validation and for
auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Whole-register moves rely on fixed immediate bits to select EMUL; changing those fixed bits can make the Sail EMUL legality check disagree with the mnemonic.

Move semantics use unmasked fixed behavior for the architectural operation: scalar/vector moves
update element 0 or every active element, while whole-register moves preserve pre-`vstart` elements
and copy entire EMUL groups.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmv8r.v` is emitted.
- Check the generated entry has opcode `0x9e03b057`, mask `0xfe0ff07f`, and fields `vs2, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include element 0 moves, sign extension/truncation for scalar transfers, tail handling, `vstart` behavior, and EMUL legality for whole-register moves.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmv8r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxnor.mm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxnor.mm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxnor.mm.yaml` is a riscv-unified-db
YAML descriptor for `vmxnor.mm`, a mask logical operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask XNOR, writing
equality of two mask source bits. This is a mask-register logical form; operands and destination are
mask registers and there is no separate `vm` masking operand.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 75
lines / 2158 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmxnor.mm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0111111----------010-----1010111`, which computes to opcode `0x7e002057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the mask logical flow reads source masks, applies the Boolean operation bit by bit,
writes the destination mask, and resets `vstart` where a Sail body is provided.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Mask logical descriptors operate over mask-register bit vectors. Sail bodies, when present, read
mask sources with mask semantics, compute the Boolean operation per bit, write a mask destination,
and reset `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmxnor.mm` is emitted.
- Check the generated entry has opcode `0x7e002057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxnor.mm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxor.mm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxor.mm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxor.mm.yaml` is a riscv-unified-db YAML
descriptor for `vmxor.mm`, a mask logical operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1`, access policy, a 32-bit encoding pattern, operand bit ranges, and
an optional Sail reference body. Semantically, this descriptor represents mask XOR over two mask
sources. This is a mask-register logical form; operands and destination are mask registers and there
is no separate `vm` masking operand.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 75
lines / 2157 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vmxor.mm`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`0110111----------010-----1010111`, which computes to opcode `0x6e002057` and opcode mask
`0xfe00707f` with 17 fixed bits and 15 operand/free bits.

Variable fields are: `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access policy is
s=always, u=always, vs=always, vu=always; because user and virtual-user access are both `always`,
`gen.go` should serialize this instruction with `Priv: false`. The Go integration types and
functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the mask logical flow reads source masks, applies the Boolean operation bit by bit,
writes the destination mask, and resets `vstart` where a Sail body is provided.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1` must describe the
same architectural operands that ``vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7` exposes to
generated randomization. The Sail body, when present, is an integration point for external
architecture validation and for auditors comparing generated encodings with RISC-V Vector behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.

Mask logical descriptors operate over mask-register bit vectors. Sail bodies, when present, read
mask sources with mask semantics, compute the Boolean operation per bit, write a mask destination,
and reset `vstart`.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vmxor.mm` is emitted.
- Check the generated entry has opcode `0x6e002057`, mask `0xfe00707f`, and fields `vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vmxor.mm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wi.yaml` is a riscv-unified-db
YAML descriptor for `vnclip.wi`, a narrowing fixed-point clip operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents signed
narrowing fixed-point clip with rounding and signed saturation. This is a narrowing wide-source
form; `vs2` is read at double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 87
lines / 2832 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnclip.wi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101111-----------011-----1010111`, which computes to opcode `0xbc003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The clip template reads a double-width source, gets a shift amount from an immediate/vector/scalar
operand, applies fixed-point rounding via `get_fixed_rounding_incr`, and saturates to the narrow
destination width.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnclip.wi` is emitted.
- Check the generated entry has opcode `0xbc003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wv.yaml` is a riscv-unified-db
YAML descriptor for `vnclip.wv`, a narrowing fixed-point clip operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents signed
narrowing fixed-point clip with rounding and signed saturation. This is a narrowing wide-source
form; `vs2` is read at double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 87
lines / 2859 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnclip.wv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101111-----------000-----1010111`, which computes to opcode `0xbc000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The clip template reads a double-width source, gets a shift amount from an immediate/vector/scalar
operand, applies fixed-point rounding via `get_fixed_rounding_incr`, and saturates to the narrow
destination width.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnclip.wv` is emitted.
- Check the generated entry has opcode `0xbc000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wx.yaml` is a riscv-unified-db
YAML descriptor for `vnclip.wx`, a narrowing fixed-point clip operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents signed
narrowing fixed-point clip with rounding and signed saturation. This is a narrowing wide-source
form; `vs2` is read at double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 87
lines / 2835 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnclip.wx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101111-----------100-----1010111`, which computes to opcode `0xbc004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The clip template reads a double-width source, gets a shift amount from an immediate/vector/scalar
operand, applies fixed-point rounding via `get_fixed_rounding_incr`, and saturates to the narrow
destination width.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnclip.wx` is emitted.
- Check the generated entry has opcode `0xbc004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclip.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wi.yaml` is a riscv-unified-db
YAML descriptor for `vnclipu.wi`, a narrowing fixed-point clip operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents unsigned
narrowing fixed-point clip with rounding and unsigned saturation. This is a narrowing wide-source
form; `vs2` is read at double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 87
lines / 2833 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnclipu.wi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101110-----------011-----1010111`, which computes to opcode `0xb8003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The clip template reads a double-width source, gets a shift amount from an immediate/vector/scalar
operand, applies fixed-point rounding via `get_fixed_rounding_incr`, and saturates to the narrow
destination width.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnclipu.wi` is emitted.
- Check the generated entry has opcode `0xb8003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wv.yaml` is a riscv-unified-db
YAML descriptor for `vnclipu.wv`, a narrowing fixed-point clip operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents unsigned
narrowing fixed-point clip with rounding and unsigned saturation. This is a narrowing wide-source
form; `vs2` is read at double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 87
lines / 2860 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnclipu.wv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101110-----------000-----1010111`, which computes to opcode `0xb8000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The clip template reads a double-width source, gets a shift amount from an immediate/vector/scalar
operand, applies fixed-point rounding via `get_fixed_rounding_incr`, and saturates to the narrow
destination width.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnclipu.wv` is emitted.
- Check the generated entry has opcode `0xb8000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wx.yaml` is a riscv-unified-db
YAML descriptor for `vnclipu.wx`, a narrowing fixed-point clip operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents unsigned
narrowing fixed-point clip with rounding and unsigned saturation. This is a narrowing wide-source
form; `vs2` is read at double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 87
lines / 2836 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnclipu.wx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101110-----------100-----1010111`, which computes to opcode `0xb8004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The clip template reads a double-width source, gets a shift amount from an immediate/vector/scalar
operand, applies fixed-point rounding via `get_fixed_rounding_incr`, and saturates to the narrow
destination width.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnclipu.wx` is emitted.
- Check the generated entry has opcode `0xb8004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnclipu.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vv.yaml` is a riscv-unified-db
YAML descriptor for `vnmsac.vv`, a integer multiply-add/subtract operation in the RISC-V Vector
(`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs1, vs2, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
negative multiply-subtract accumulate, subtracting the product from the accumulator. This is the
vector-vector form; both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 74
lines / 2329 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnmsac.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101111-----------010-----1010111`, which computes to opcode `0xbc002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow reads vector operands plus the destination accumulator/addend, computes
signed products for active elements, applies the negative multiply-subtract form selected by the
fixed encoding, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs1, vs2, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply-add/subtract template reads `vd` as an accumulator or addend, computes the low SEW bits
of a signed product, subtracts that product for the negative forms, and writes the vector
destination.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnmsac.vv` is emitted.
- Check the generated entry has opcode `0xbc002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vx.yaml` is a riscv-unified-db
YAML descriptor for `vnmsac.vx`, a integer multiply-add/subtract operation in the RISC-V Vector
(`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, xs1, vs2, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
negative multiply-subtract accumulate, subtracting the product from the accumulator. This is the
vector-scalar integer form; `xs1` occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 74
lines / 2298 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnmsac.vx`,
`definedBy.extension.name: V`, `assembly: vd, xs1, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101111-----------110-----1010111`, which computes to opcode `0xbc006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow reads vector operands plus the destination accumulator/addend, computes
signed products for active elements, applies the negative multiply-subtract form selected by the
fixed encoding, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, xs1, vs2, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply-add/subtract template reads `vd` as an accumulator or addend, computes the low SEW bits
of a signed product, subtracts that product for the negative forms, and writes the vector
destination.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnmsac.vx` is emitted.
- Check the generated entry has opcode `0xbc006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsac.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vv.yaml` is a riscv-unified-db
YAML descriptor for `vnmsub.vv`, a integer multiply-add/subtract operation in the RISC-V Vector
(`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs1, vs2, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
negative multiply-subtract, subtracting a product from the addend form selected by the template.
This is the vector-vector form; both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 74
lines / 2329 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnmsub.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101011-----------010-----1010111`, which computes to opcode `0xac002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow reads vector operands plus the destination accumulator/addend, computes
signed products for active elements, applies the negative multiply-subtract form selected by the
fixed encoding, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs1, vs2, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply-add/subtract template reads `vd` as an accumulator or addend, computes the low SEW bits
of a signed product, subtracts that product for the negative forms, and writes the vector
destination.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnmsub.vv` is emitted.
- Check the generated entry has opcode `0xac002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vx.yaml` is a riscv-unified-db
YAML descriptor for `vnmsub.vx`, a integer multiply-add/subtract operation in the RISC-V Vector
(`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, xs1, vs2, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
negative multiply-subtract, subtracting a product from the addend form selected by the template.
This is the vector-scalar integer form; `xs1` occupies the rs1 field and is read by Sail through
`get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 74
lines / 2298 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnmsub.vx`,
`definedBy.extension.name: V`, `assembly: vd, xs1, vs2, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101011-----------110-----1010111`, which computes to opcode `0xac006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow reads vector operands plus the destination accumulator/addend, computes
signed products for active elements, applies the negative multiply-subtract form selected by the
fixed encoding, writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, xs1, vs2, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The multiply-add/subtract template reads `vd` as an accumulator or addend, computes the low SEW bits
of a signed product, subtracts that product for the negative forms, and writes the vector
destination.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnmsub.vx` is emitted.
- Check the generated entry has opcode `0xac006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnmsub.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wi.yaml` is a riscv-unified-db YAML
descriptor for `vnsra.wi`, a narrowing shift operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents narrowing arithmetic
right shift from a double-width source. This is a narrowing wide-source form; `vs2` is read at
double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 86
lines / 2732 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnsra.wi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101101-----------011-----1010111`, which computes to opcode `0xb4003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The narrowing shift template reads a double-width source, computes a shift amount, then slices the
low SEW bits after either logical or sign-extended arithmetic right shift.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnsra.wi` is emitted.
- Check the generated entry has opcode `0xb4003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wv.yaml` is a riscv-unified-db YAML
descriptor for `vnsra.wv`, a narrowing shift operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents narrowing arithmetic
right shift from a double-width source. This is a narrowing wide-source form; `vs2` is read at
double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 86
lines / 2760 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnsra.wv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101101-----------000-----1010111`, which computes to opcode `0xb4000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The narrowing shift template reads a double-width source, computes a shift amount, then slices the
low SEW bits after either logical or sign-extended arithmetic right shift.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnsra.wv` is emitted.
- Check the generated entry has opcode `0xb4000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wx.yaml` is a riscv-unified-db YAML
descriptor for `vnsra.wx`, a narrowing shift operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents narrowing arithmetic
right shift from a double-width source. This is a narrowing wide-source form; `vs2` is read at
double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 86
lines / 2735 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnsra.wx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101101-----------100-----1010111`, which computes to opcode `0xb4004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The narrowing shift template reads a double-width source, computes a shift amount, then slices the
low SEW bits after either logical or sign-extended arithmetic right shift.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnsra.wx` is emitted.
- Check the generated entry has opcode `0xb4004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsra.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wi.yaml` is a riscv-unified-db YAML
descriptor for `vnsrl.wi`, a narrowing shift operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents narrowing logical
right shift from a double-width source. This is a narrowing wide-source form; `vs2` is read at
double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 86
lines / 2732 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnsrl.wi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101100-----------011-----1010111`, which computes to opcode `0xb0003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The narrowing shift template reads a double-width source, computes a shift amount, then slices the
low SEW bits after either logical or sign-extended arithmetic right shift.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnsrl.wi` is emitted.
- Check the generated entry has opcode `0xb0003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wv.yaml` is a riscv-unified-db YAML
descriptor for `vnsrl.wv`, a narrowing shift operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents narrowing logical
right shift from a double-width source. This is a narrowing wide-source form; `vs2` is read at
double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 86
lines / 2760 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnsrl.wv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101100-----------000-----1010111`, which computes to opcode `0xb0000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The narrowing shift template reads a double-width source, computes a shift amount, then slices the
low SEW bits after either logical or sign-extended arithmetic right shift.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnsrl.wv` is emitted.
- Check the generated entry has opcode `0xb0000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wx.yaml` is a riscv-unified-db YAML
descriptor for `vnsrl.wx`, a narrowing shift operation in the RISC-V Vector (`V`) extension. It
supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata: mnemonic,
assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern, operand bit ranges,
and an optional Sail reference body. Semantically, this descriptor represents narrowing logical
right shift from a double-width source. This is a narrowing wide-source form; `vs2` is read at
double SEW/LMUL and `vd` is written at the current SEW/LMUL.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 86
lines / 2735 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vnsrl.wx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`101100-----------100-----1010111`, which computes to opcode `0xb0004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow checks variable-width legality and overlap, reads a double-width source
group, computes a shift amount, performs narrowing shift or rounded clipping, writes the narrow
vector destination, clears `vstart`, and retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Wide-source/narrow-destination overlap and EMUL legality are critical in Sail and are not represented by the generated operand fields.

The narrowing shift template reads a double-width source, computes a shift amount, then slices the
low SEW bits after either logical or sign-extended arithmetic right shift.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vnsrl.wx` is emitted.
- Check the generated entry has opcode `0xb0004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include shift amounts around 0/SEW/2*SEW, rounding modes for clip forms, saturation boundaries, and invalid wide/narrow register overlaps.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vnsrl.wx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vi.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vi.yaml` is a riscv-unified-db YAML
descriptor for `vor.vi`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, imm, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
integer bitwise OR. This is the vector-immediate form; the five-bit immediate occupies bits 19-15
and is sign-extended by the Sail template where needed.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 101
lines / 3795 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vor.vi`,
`definedBy.extension.name: V`, `assembly: vd, vs2, imm, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`001010-----------011-----1010111`, which computes to opcode `0x28003057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, imm, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `imm` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vor.vi` is emitted.
- Check the generated entry has opcode `0x28003057`, mask `0xfc00707f`, and fields `vm, vs2, imm, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vv.yaml` is a riscv-unified-db YAML
descriptor for `vor.vv`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
integer bitwise OR. This is the vector-vector form; both element operands are read from vector
register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 134
lines / 6446 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vor.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`001010-----------000-----1010111`, which computes to opcode `0x28000057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vor.vv` is emitted.
- Check the generated entry has opcode `0x28000057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vx.yaml` is a riscv-unified-db YAML
descriptor for `vor.vx`, a single-width integer vector arithmetic/logical operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
integer bitwise OR. This is the vector-scalar integer form; `xs1` occupies the rs1 field and is read
by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 117
lines / 4887 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vor.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`001010-----------100-----1010111`, which computes to opcode `0x28004057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The Sail body is the broad VV/VX/VI integer ALU template. This fixed encoding selects the named
operation from the `funct6` match table while the generator records only the fixed opcode bits and
operand fields.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vor.vx` is emitted.
- Check the generated entry has opcode `0x28004057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vor.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredand.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredand.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredand.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredand.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents integer
reduction AND into destination element 0. This is a vector-scalar reduction form; `vs1[0]` seeds the
reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2680 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredand.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000001-----------010-----1010111`, which computes to opcode `0x04002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredand.vs` is emitted.
- Check the generated entry has opcode `0x04002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredand.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmax.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmax.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmax.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredmax.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents signed
integer reduction maximum into destination element 0. This is a vector-scalar reduction form;
`vs1[0]` seeds the reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2680 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredmax.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000111-----------010-----1010111`, which computes to opcode `0x1c002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredmax.vs` is emitted.
- Check the generated entry has opcode `0x1c002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmax.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmaxu.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmaxu.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmaxu.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredmaxu.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents unsigned
integer reduction maximum into destination element 0. This is a vector-scalar reduction form;
`vs1[0]` seeds the reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2681 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredmaxu.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000110-----------010-----1010111`, which computes to opcode `0x18002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredmaxu.vs` is emitted.
- Check the generated entry has opcode `0x18002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmaxu.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmin.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmin.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmin.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredmin.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents signed
integer reduction minimum into destination element 0. This is a vector-scalar reduction form;
`vs1[0]` seeds the reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2680 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredmin.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000101-----------010-----1010111`, which computes to opcode `0x14002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredmin.vs` is emitted.
- Check the generated entry has opcode `0x14002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredmin.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredminu.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredminu.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredminu.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredminu.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents unsigned
integer reduction minimum into destination element 0. This is a vector-scalar reduction form;
`vs1[0]` seeds the reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2681 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredminu.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000100-----------010-----1010111`, which computes to opcode `0x10002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredminu.vs` is emitted.
- Check the generated entry has opcode `0x10002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredminu.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredor.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredor.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredor.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredor.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents integer
reduction OR into destination element 0. This is a vector-scalar reduction form; `vs1[0]` seeds the
reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2679 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredor.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000010-----------010-----1010111`, which computes to opcode `0x08002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredor.vs` is emitted.
- Check the generated entry has opcode `0x08002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredor.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredsum.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredsum.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredsum.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredsum.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents integer
reduction sum into destination element 0. This is a vector-scalar reduction form; `vs1[0]` seeds the
reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2680 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredsum.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000000-----------010-----1010111`, which computes to opcode `0x00002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredsum.vs` is emitted.
- Check the generated entry has opcode `0x00002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredsum.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredxor.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredxor.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredxor.vs.yaml` is a riscv-unified-db
YAML descriptor for `vredxor.vs`, a integer vector reduction operation in the RISC-V Vector (`V`)
extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction metadata:
mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern, operand
bit ranges, and an optional Sail reference body. Semantically, this descriptor represents integer
reduction XOR into destination element 0. This is a vector-scalar reduction form; `vs1[0]` seeds the
reduction and `vd[0]` receives the final result.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 81
lines / 2680 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vredxor.vs`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`000011-----------010-----1010111`, which computes to opcode `0x0c002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the flow rejects illegal reductions, no-ops when `vl == 0`, seeds the accumulator
from `vs1[0]`, folds active `vs2` elements with the selected reduction operator, writes `vd[0]`, and
clears `vstart`.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.
- Reduction behavior depends on `vl`, mask policy, and `vs1[0]` seed state; generated encoding tests alone will not catch reduction-order or inactive-element mistakes.

The reduction template treats `vs1[0]` as the initial accumulator, scans active `vs2` elements under
the mask, writes only destination element 0, and leaves other destination elements as tail elements
in the current Sail model.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vredxor.vs` is emitted.
- Check the generated entry has opcode `0x0c002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should include `vl=0`, masked-off elements, different `vs1[0]` seeds, signed versus unsigned extrema, and destination element 0 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vredxor.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vv.yaml` is a riscv-unified-db YAML
descriptor for `vrem.vv`, a integer multiply/divide/remainder template operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, vs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
signed integer remainder with vector divide-by-zero and overflow semantics. This is the vector-
vector form; both element operands are read from vector register groups.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 116
lines / 5189 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vrem.vv`,
`definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100011-----------010-----1010111`, which computes to opcode `0x8c002057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, vs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `vs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The remainder template handles divide-by-zero by returning the dividend and relies on the Sail
signed-overflow comments for the -2^(SEW-1) / -1 case.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vrem.vv` is emitted.
- Check the generated entry has opcode `0x8c002057`, mask `0xfc00707f`, and fields `vm, vs2, vs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vx.yaml` is a riscv-unified-db YAML
descriptor for `vrem.vx`, a integer multiply/divide/remainder template operation in the RISC-V
Vector (`V`) extension. It supplies syzkaller's riscv64 ifuzz generator with declarative instruction
metadata: mnemonic, assembly operands `vd, vs2, xs1, vm`, access policy, a 32-bit encoding pattern,
operand bit ranges, and an optional Sail reference body. Semantically, this descriptor represents
signed integer remainder with vector divide-by-zero and overflow semantics. This is the vector-
scalar integer form; `xs1` occupies the rs1 field and is read by Sail through `get_scalar`.

The file is `kind: instruction`, is defined by extension `V`, uses the shared schema reference
`inst_schema.json#`, and carries the standard SPDX/import comments from the source corpus. It is 125
lines / 5817 bytes, with `data_independent_timing: False`. The local generator treats it as input
data rather than executable Go code.

## Important APIs, Types, and Functions

The schema-facing fields that matter locally are `$schema`, `kind`, `name: vrem.vx`,
`definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`,
`access`, `operation()`, and `sail()` when present. For this descriptor the encoding match string is
`100011-----------110-----1010111`, which computes to opcode `0x8c006057` and opcode mask
`0xfc00707f` with 16 fixed bits and 16 operand/free bits.

Variable fields are: `vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits 11-7. The access
policy is s=always, u=always, vs=always, vu=always; because user and virtual-user access are both
`always`, `gen.go` should serialize this instruction with `Priv: false`. The Go integration types
and functions are `instYAML`, `buildInsn`, `parseLocations`, `parseRange`, `riscv64.Insn`, and
`riscv64.InsnField` in `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` and
`pkg/ifuzz/riscv64/riscv64.go`.

The embedded Sail block is reference semantics for architectural validation. It names helper APIs
such as vector configuration readers, mask and vector register readers/writers, legality checks,
arithmetic/compare helpers, and `vstart` reset. The current ifuzz generator does not parse or
execute Sail; it only preserves the encoding-level instruction template.

## Control Flow

During generation, `gen.go` walks the YAML tree, unmarshals this file into `instYAML`, requires
`kind: instruction` and a 32-character top-level `encoding.match`, converts fixed `0`/`1` characters
into opcode and mask bits, expands each `encoding.variables` range with `parseLocations`, derives
`Priv` from `access.u`/`access.vu`, and serializes a `riscv64.Insn` entry into `generated/insns.go`.
Architecturally, the Sail flow computes vector configuration, checks normal vector legality, reads
mask/source/destination operands, preserves inactive destination elements, selects the mnemonic-
specific operation from a shared template, writes the vector destination, clears `vstart`, and
retires.

## State and Persistence Behavior

The YAML file itself is immutable source data and has no runtime persistence. Its persistent effect
is the generated `riscv64.Insn` entry in `sources/test-
tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `Name`, `OpcodeMask`, `Opcode`,
`Fields`, `AsUInt32`, `Generator`, and `Priv` are serialized. At fuzzer runtime, operand state
exists in a copied instruction word and decoded operands; architectural vector state such as vector
registers, mask registers, `vl`, `vtype`, `vstart`, `fcsr`, rounding state, or integer register
values is modeled only by CPUs/emulators or by the Sail text, not by this descriptor.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on the RISC-V `V` extension
namespace. In this repository it integrates with `pkg/ifuzz/riscv64/gen/gen.go`, which uses
`gopkg.in/yaml.v3` for unmarshalling, `serializer.Write` for generated Go output, and
`osutil.WriteFileAtomically` for replacing `generated/insns.go`. The generated table is registered
by `pkg/ifuzz/riscv64/generated` through `riscv64.Register` and is consumed by `Encode`,
`ParseInsn`, decode matching, and the generic syzkaller `ifuzz/iset` registry.

The assembly operand list and variable ranges must stay consistent: `vd, vs2, xs1, vm` must describe
the same architectural operands that ``vm` bits 25-25; `vs2` bits 24-20; `xs1` bits 19-15; `vd` bits
11-7` exposes to generated randomization. The Sail body, when present, is an integration point for
external architecture validation and for auditors comparing generated encodings with RISC-V Vector
behavior.

## Risks and Edge Cases

- The generator ignores `long_name`, `description`, `definedBy`, `data_independent_timing`, and the Sail body, so the fixed encoding string and variable locations are the effective ifuzz contract.
- A one-bit error in the 32-character match string changes `OpcodeMask`/`Opcode` and can alias another vector instruction or make this descriptor unreachable in decode.
- Bit 25 must remain the `vm` field for masked forms; fixing it would remove either masked or unmasked encodings from generated fuzzing.

The remainder template handles divide-by-zero by returning the dividend and relies on the Sail
signed-overflow comments for the -2^(SEW-1) / -1 case.

## Test Signals

- Run `go generate ./pkg/ifuzz/riscv64` or the equivalent `go run gen/gen.go gen/inst generated/insns.go` path and confirm `vrem.vx` is emitted.
- Check the generated entry has opcode `0x8c006057`, mask `0xfc00707f`, and fields `vm, vs2, xs1, vd` with the same bit ranges as this YAML.
- `go test ./pkg/ifuzz/riscv64/...` should compile the generated table and exercise encode/decode round trips whose randomized operands preserve all fixed bits.
- Architectural spot tests should compare selected legal and illegal vector states against the RISC-V Vector/Sail semantics for masks, SEW, LMUL, overlap, and edge operand values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrem.vx.yaml -->
