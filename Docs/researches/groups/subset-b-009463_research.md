# subset-b-009463 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vv.yaml` is a riscv-unified-db YAML descriptor for the `vdivu.vv` instruction, an integer vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 117 lines / 5190 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vdivu.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100000-----------010-----1010111` gives opcode `0x80002057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, vector register read, vector register write, integer divide rounding toward zero, integer remainder rounding toward zero. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, vector register read, vector register write, integer divide rounding toward zero, integer remainder rounding toward zero, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Unsigned divide has divide-by-zero behavior in Sail, but ifuzz only produces the instruction encoding and does not model operand values.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vdivu.vv` in `generated/insns.go`; the generated record has opcode `0x80002057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vx.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vx.yaml` is a riscv-unified-db YAML descriptor for the `vdivu.vx` instruction, an integer vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, xs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar integer register form. The descriptor is `instruction` kind data, is 126 lines / 5818 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vdivu.vx`, `definedBy.extension.name: V`, `assembly: vd, vs2, xs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100000-----------110-----1010111` gives opcode `0x80006057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `xs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, vector register read, vector register write, integer divide rounding toward zero, integer remainder rounding toward zero. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, vector register read, vector register write, integer divide rounding toward zero, integer remainder rounding toward zero, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Unsigned divide has divide-by-zero behavior in Sail, but ifuzz only produces the instruction encoding and does not model operand values.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vdivu.vx` in `generated/insns.go`; the generated record has opcode `0x80006057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `xs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vdivu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfadd.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3259 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfadd.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000000-----------101-----1010111` gives opcode `0x00005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfadd.vf` in `generated/insns.go`; the generated record has opcode `0x00005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfadd.vv` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2627 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfadd.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000000-----------001-----1010111` gives opcode `0x00001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfadd.vv` in `generated/insns.go`; the generated record has opcode `0x00001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfadd.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfclass.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfclass.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfclass.v.yaml` is a riscv-unified-db YAML descriptor for the `vfclass.v` instruction, an unary floating-point classification or estimate instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 98 lines / 3398 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfclass.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010011------10000001-----1010111` gives opcode `0x4c081057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfclass.v` in `generated/insns.go`; the generated record has opcode `0x4c081057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfclass.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.x.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.x.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.x.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.f.x.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4920 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.f.x.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00011001-----1010111` gives opcode `0x48019057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.f.x.v` in `generated/insns.go`; the generated record has opcode `0x48019057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.x.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.xu.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.xu.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.xu.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.f.xu.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4921 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.f.xu.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00010001-----1010111` gives opcode `0x48011057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.f.xu.v` in `generated/insns.go`; the generated record has opcode `0x48011057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.f.xu.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.x.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.x.f.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.x.f.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.rtz.x.f.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4924 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.rtz.x.f.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00111001-----1010111` gives opcode `0x48039057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.rtz.x.f.v` in `generated/insns.go`; the generated record has opcode `0x48039057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.x.f.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.xu.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.xu.f.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.xu.f.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.rtz.xu.f.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4925 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.rtz.xu.f.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00110001-----1010111` gives opcode `0x48031057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.rtz.xu.f.v` in `generated/insns.go`; the generated record has opcode `0x48031057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.rtz.xu.f.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.x.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.x.f.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.x.f.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.x.f.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4920 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.x.f.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00001001-----1010111` gives opcode `0x48009057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.x.f.v` in `generated/insns.go`; the generated record has opcode `0x48009057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.x.f.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.xu.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.xu.f.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.xu.f.v.yaml` is a riscv-unified-db YAML descriptor for the `vfcvt.xu.f.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 123 lines / 4921 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfcvt.xu.f.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------00000001-----1010111` gives opcode `0x48001057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfcvt.xu.f.v` in `generated/insns.go`; the generated record has opcode `0x48001057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfcvt.xu.f.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfdiv.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3259 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfdiv.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100000-----------101-----1010111` gives opcode `0x80005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfdiv.vf` in `generated/insns.go`; the generated record has opcode `0x80005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfdiv.vv` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2627 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfdiv.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100000-----------001-----1010111` gives opcode `0x80001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfdiv.vv` in `generated/insns.go`; the generated record has opcode `0x80001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfdiv.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfirst.m.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfirst.m.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfirst.m.yaml` is a riscv-unified-db YAML descriptor for the `vfirst.m` instruction, a mask query instruction in the RISC-V `V` vector extension. It records the assembler spelling `xd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the assembly form `xd, vs2, vm`. The descriptor is `instruction` kind data, is 67 lines / 1720 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfirst.m`, `definedBy.extension.name: V`, `assembly: xd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010000------10001010-----1010111` gives opcode `0x4008a057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `xd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, first active mask-bit index search. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_vd_unmasked`, `assert_vstart`, reads the mask and relevant operands (vs2), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, first active mask-bit index search, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. Sail writes `X(rd)` with the first active mask index or -1, while the generated metadata only exposes the `xd` bit field.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- The instruction writes an integer register (`xd`) rather than a vector destination; keeping the destination field name distinct is important for operand decoding.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfirst.m` in `generated/insns.go`; the generated record has opcode `0x4008a057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `xd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfirst.m.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmacc.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2584 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmacc.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101100-----------101-----1010111` gives opcode `0xb0005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmacc.vf` in `generated/insns.go`; the generated record has opcode `0xb0005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmacc.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2633 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmacc.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101100-----------001-----1010111` gives opcode `0xb0001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmacc.vv` in `generated/insns.go`; the generated record has opcode `0xb0001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmacc.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmadd.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2584 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmadd.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101000-----------101-----1010111` gives opcode `0xa0005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmadd.vf` in `generated/insns.go`; the generated record has opcode `0xa0005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmadd.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2633 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmadd.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101000-----------001-----1010111` gives opcode `0xa0001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmadd.vv` in `generated/insns.go`; the generated record has opcode `0xa0001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmadd.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmax.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3259 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmax.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000110-----------101-----1010111` gives opcode `0x18005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmax.vf` in `generated/insns.go`; the generated record has opcode `0x18005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmax.vv` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2627 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmax.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000110-----------001-----1010111` gives opcode `0x18001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmax.vv` in `generated/insns.go`; the generated record has opcode `0x18001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmax.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmerge.vfm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmerge.vfm.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmerge.vfm.yaml` is a riscv-unified-db YAML descriptor for the `vfmerge.vfm` instruction, a scalar/vector movement instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, v0`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 79 lines / 2421 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmerge.vfm`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, v0`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `0101110----------101-----1010111` gives opcode `0x5c005057`, mask `0xfe00707f`, and 15 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, vector register read, vector register write, masked scalar/vector merge. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, vector register read, vector register write, masked scalar/vector merge, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmerge.vfm` in `generated/insns.go`; the generated record has opcode `0x5c005057`, mask `0xfe00707f`, and fields `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmerge.vfm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmin.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3259 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmin.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000100-----------101-----1010111` gives opcode `0x10005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmin.vf` in `generated/insns.go`; the generated record has opcode `0x10005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmin.vv` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2627 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmin.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000100-----------001-----1010111` gives opcode `0x10001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmin.vv` in `generated/insns.go`; the generated record has opcode `0x10001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmin.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmsac.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2584 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmsac.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101110-----------101-----1010111` gives opcode `0xb8005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmsac.vf` in `generated/insns.go`; the generated record has opcode `0xb8005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmsac.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2633 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmsac.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101110-----------001-----1010111` gives opcode `0xb8001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmsac.vv` in `generated/insns.go`; the generated record has opcode `0xb8001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsac.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmsub.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2584 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmsub.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101010-----------101-----1010111` gives opcode `0xa8005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmsub.vf` in `generated/insns.go`; the generated record has opcode `0xa8005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmsub.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2633 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmsub.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101010-----------001-----1010111` gives opcode `0xa8001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmsub.vv` in `generated/insns.go`; the generated record has opcode `0xa8001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmsub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfmul.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3259 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmul.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100100-----------101-----1010111` gives opcode `0x90005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmul.vf` in `generated/insns.go`; the generated record has opcode `0x90005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfmul.vv` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2627 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmul.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100100-----------001-----1010111` gives opcode `0x90001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmul.vv` in `generated/insns.go`; the generated record has opcode `0x90001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmul.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.f.s.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.f.s.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.f.s.yaml` is a riscv-unified-db YAML descriptor for the `vfmv.f.s` instruction, a scalar/vector movement instruction in the RISC-V `V` vector extension. It records the assembler spelling `fd, vs2`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the scalar/vector move form. The descriptor is `instruction` kind data, is 59 lines / 1392 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmv.f.s`, `definedBy.extension.name: V`, `assembly: fd, vs2`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `0100001-----00000001-----1010111` gives opcode `0x42001057`, mask `0xfe0ff07f`, and 10 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vs2` at bits `24-20`; `fd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: vector register read, scalar/vector move. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vs2), initializes an inactive-lane-preserving result, loops across active elements, performs vector register read, scalar/vector move, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmv.f.s` in `generated/insns.go`; the generated record has opcode `0x42001057`, mask `0xfe0ff07f`, and fields `vs2`, `fd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.f.s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.s.f.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.s.f.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.s.f.yaml` is a riscv-unified-db YAML descriptor for the `vfmv.s.f` instruction, a scalar/vector movement instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the scalar/vector move form. The descriptor is `instruction` kind data, is 72 lines / 1980 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmv.s.f`, `definedBy.extension.name: V`, `assembly: vd, fs1`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010000100000-----101-----1010111` gives opcode `0x42005057`, mask `0xfff0707f`, and 10 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, vector register read, vector register write, scalar/vector move. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, vector register read, vector register write, scalar/vector move, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmv.s.f` in `generated/insns.go`; the generated record has opcode `0x42005057`, mask `0xfff0707f`, and fields `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.s.f.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.v.f.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.v.f.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.v.f.yaml` is a riscv-unified-db YAML descriptor for the `vfmv.v.f` instruction, a scalar/vector movement instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the scalar/vector move form. The descriptor is `instruction` kind data, is 65 lines / 1772 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfmv.v.f`, `definedBy.extension.name: V`, `assembly: vd, fs1`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010111100000-----101-----1010111` gives opcode `0x5e005057`, mask `0xfff0707f`, and 10 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: mask read, vector register read, vector register write, scalar/vector move. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs mask read, vector register read, vector register write, scalar/vector move, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfmv.v.f` in `generated/insns.go`; the generated record has opcode `0x5e005057`, mask `0xfff0707f`, and fields `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfmv.v.f.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.f.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.f.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.f.f.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6148 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.f.f.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10100001-----1010111` gives opcode `0x480a1057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.f.f.w` in `generated/insns.go`; the generated record has opcode `0x480a1057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.x.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.x.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.x.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.f.x.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6148 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.f.x.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10011001-----1010111` gives opcode `0x48099057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.f.x.w` in `generated/insns.go`; the generated record has opcode `0x48099057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.x.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.xu.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.xu.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.xu.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.f.xu.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6149 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.f.xu.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10010001-----1010111` gives opcode `0x48091057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.f.xu.w` in `generated/insns.go`; the generated record has opcode `0x48091057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.f.xu.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rod.f.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rod.f.f.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rod.f.f.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.rod.f.f.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6152 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.rod.f.f.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10101001-----1010111` gives opcode `0x480a9057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.rod.f.f.w` in `generated/insns.go`; the generated record has opcode `0x480a9057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rod.f.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.x.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.x.f.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.x.f.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.rtz.x.f.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6152 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.rtz.x.f.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10111001-----1010111` gives opcode `0x480b9057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.rtz.x.f.w` in `generated/insns.go`; the generated record has opcode `0x480b9057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.x.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.xu.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.xu.f.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.xu.f.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.rtz.xu.f.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6153 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.rtz.xu.f.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10110001-----1010111` gives opcode `0x480b1057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.rtz.xu.f.w` in `generated/insns.go`; the generated record has opcode `0x480b1057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.rtz.xu.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.x.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.x.f.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.x.f.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.x.f.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6148 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.x.f.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10001001-----1010111` gives opcode `0x48089057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.x.f.w` in `generated/insns.go`; the generated record has opcode `0x48089057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.x.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.xu.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.xu.f.w.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.xu.f.w.yaml` is a riscv-unified-db YAML descriptor for the `vfncvt.xu.f.w` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening or narrowing conversion form. The descriptor is `instruction` kind data, is 146 lines / 6149 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfncvt.xu.f.w`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------10000001-----1010111` gives opcode `0x48081057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, narrowing float conversion, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfncvt.xu.f.w` in `generated/insns.go`; the generated record has opcode `0x48081057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfncvt.xu.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfnmacc.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2585 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmacc.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101101-----------101-----1010111` gives opcode `0xb4005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmacc.vf` in `generated/insns.go`; the generated record has opcode `0xb4005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfnmacc.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2634 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmacc.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101101-----------001-----1010111` gives opcode `0xb4001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmacc.vv` in `generated/insns.go`; the generated record has opcode `0xb4001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmacc.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfnmadd.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2585 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmadd.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101001-----------101-----1010111` gives opcode `0xa4005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmadd.vf` in `generated/insns.go`; the generated record has opcode `0xa4005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfnmadd.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2634 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmadd.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101001-----------001-----1010111` gives opcode `0xa4001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmadd.vv` in `generated/insns.go`; the generated record has opcode `0xa4001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmadd.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfnmsac.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2585 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmsac.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101111-----------101-----1010111` gives opcode `0xbc005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmsac.vf` in `generated/insns.go`; the generated record has opcode `0xbc005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfnmsac.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2634 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmsac.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101111-----------001-----1010111` gives opcode `0xbc001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmsac.vv` in `generated/insns.go`; the generated record has opcode `0xbc001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsac.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfnmsub.vf` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, fs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2585 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmsub.vf`, `definedBy.extension.name: V`, `assembly: vd, fs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101011-----------101-----1010111` gives opcode `0xac005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmsub.vf` in `generated/insns.go`; the generated record has opcode `0xac005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfnmsub.vv` instruction, a floating-point fused multiply-add/subtract instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs1, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 81 lines / 2634 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfnmsub.vv`, `definedBy.extension.name: V`, `assembly: vd, vs1, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `101011-----------001-----1010111` gives opcode `0xac001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs fused multiply-add, negative fused multiply-add/subtract, fused multiply-subtract, negative fused multiply-subtract/add, floating-point multiply, mask read, vector register read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfnmsub.vv` in `generated/insns.go`; the generated record has opcode `0xac001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfnmsub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrdiv.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrdiv.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrdiv.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfrdiv.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3260 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfrdiv.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100001-----------101-----1010111` gives opcode `0x84005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfrdiv.vf` in `generated/insns.go`; the generated record has opcode `0x84005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrdiv.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrec7.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrec7.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrec7.v.yaml` is a riscv-unified-db YAML descriptor for the `vfrec7.v` instruction, an unary floating-point classification or estimate instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 98 lines / 3397 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfrec7.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010011------00101001-----1010111` gives opcode `0x4c029057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfrec7.v` in `generated/insns.go`; the generated record has opcode `0x4c029057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrec7.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmax.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmax.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmax.vs.yaml` is a riscv-unified-db YAML descriptor for the `vfredmax.vs` instruction, a floating-point reduction instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector reduction form. The descriptor is `instruction` kind data, is 51 lines / 1286 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfredmax.vs`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000111-----------001-----1010111` gives opcode `0x1c001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: vector reduction into element zero of the destination group. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs vector reduction into element zero of the destination group, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Reduction instructions read and write destination element zero specially; overlap and mask policy need architectural testing beyond encode/decode round trips.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfredmax.vs` in `generated/insns.go`; the generated record has opcode `0x1c001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmax.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmin.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmin.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmin.vs.yaml` is a riscv-unified-db YAML descriptor for the `vfredmin.vs` instruction, a floating-point reduction instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector reduction form. The descriptor is `instruction` kind data, is 51 lines / 1286 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfredmin.vs`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000101-----------001-----1010111` gives opcode `0x14001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: vector reduction into element zero of the destination group. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs vector reduction into element zero of the destination group, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Reduction instructions read and write destination element zero specially; overlap and mask policy need architectural testing beyond encode/decode round trips.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfredmin.vs` in `generated/insns.go`; the generated record has opcode `0x14001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredmin.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredosum.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredosum.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredosum.vs.yaml` is a riscv-unified-db YAML descriptor for the `vfredosum.vs` instruction, a floating-point reduction instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector reduction form. The descriptor is `instruction` kind data, is 51 lines / 1287 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfredosum.vs`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000011-----------001-----1010111` gives opcode `0x0c001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: vector reduction into element zero of the destination group. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs vector reduction into element zero of the destination group, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Reduction instructions read and write destination element zero specially; overlap and mask policy need architectural testing beyond encode/decode round trips.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfredosum.vs` in `generated/insns.go`; the generated record has opcode `0x0c001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredosum.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredusum.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredusum.vs.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredusum.vs.yaml` is a riscv-unified-db YAML descriptor for the `vfredusum.vs` instruction, a floating-point reduction instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector reduction form. The descriptor is `instruction` kind data, is 51 lines / 1287 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfredusum.vs`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000001-----------001-----1010111` gives opcode `0x04001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: vector reduction into element zero of the destination group. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks the instruction-specific legality checks, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs vector reduction into element zero of the destination group, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Reduction instructions read and write destination element zero specially; overlap and mask policy need architectural testing beyond encode/decode round trips.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfredusum.vs` in `generated/insns.go`; the generated record has opcode `0x04001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfredusum.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsqrt7.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsqrt7.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsqrt7.v.yaml` is a riscv-unified-db YAML descriptor for the `vfrsqrt7.v` instruction, an unary floating-point classification or estimate instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 98 lines / 3399 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfrsqrt7.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010011------00100001-----1010111` gives opcode `0x4c021057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfrsqrt7.v` in `generated/insns.go`; the generated record has opcode `0x4c021057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsqrt7.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsub.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsub.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsub.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfrsub.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3260 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfrsub.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `100111-----------101-----1010111` gives opcode `0x9c005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfrsub.vf` in `generated/insns.go`; the generated record has opcode `0x9c005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfrsub.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfsgnj.vf` instruction, a floating-point sign manipulation instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3260 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsgnj.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001000-----------101-----1010111` gives opcode `0x20005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsgnj.vf` in `generated/insns.go`; the generated record has opcode `0x20005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfsgnj.vv` instruction, a floating-point sign manipulation instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2628 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsgnj.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001000-----------001-----1010111` gives opcode `0x20001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsgnj.vv` in `generated/insns.go`; the generated record has opcode `0x20001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnj.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfsgnjn.vf` instruction, a floating-point sign manipulation instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3261 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsgnjn.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001001-----------101-----1010111` gives opcode `0x24005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsgnjn.vf` in `generated/insns.go`; the generated record has opcode `0x24005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfsgnjn.vv` instruction, a floating-point sign manipulation instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2629 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsgnjn.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001001-----------001-----1010111` gives opcode `0x24001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsgnjn.vv` in `generated/insns.go`; the generated record has opcode `0x24001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjn.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfsgnjx.vf` instruction, a floating-point sign manipulation instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3261 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsgnjx.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001010-----------101-----1010111` gives opcode `0x28005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsgnjx.vf` in `generated/insns.go`; the generated record has opcode `0x28005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfsgnjx.vv` instruction, a floating-point sign manipulation instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2629 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsgnjx.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001010-----------001-----1010111` gives opcode `0x28001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsgnjx.vv` in `generated/insns.go`; the generated record has opcode `0x28001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsgnjx.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1down.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1down.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1down.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfslide1down.vf` instruction, a scalar/vector movement instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3266 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfslide1down.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001111-----------101-----1010111` gives opcode `0x3c005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.
- Slide instructions combine vector and scalar floating-point register sources, making operand naming and assembler syntax drift a likely maintenance issue.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfslide1down.vf` in `generated/insns.go`; the generated record has opcode `0x3c005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1down.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1up.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1up.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1up.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfslide1up.vf` instruction, a scalar/vector movement instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3264 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfslide1up.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `001110-----------101-----1010111` gives opcode `0x38005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.
- Slide instructions combine vector and scalar floating-point register sources, making operand naming and assembler syntax drift a likely maintenance issue.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfslide1up.vf` in `generated/insns.go`; the generated record has opcode `0x38005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfslide1up.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsqrt.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsqrt.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsqrt.v.yaml` is a riscv-unified-db YAML descriptor for the `vfsqrt.v` instruction, an unary floating-point classification or estimate instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 98 lines / 3397 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsqrt.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010011------00000001-----1010111` gives opcode `0x4c001057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point classification, floating-point square root, 7-bit reciprocal-square-root estimate, 7-bit reciprocal estimate, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsqrt.v` in `generated/insns.go`; the generated record has opcode `0x4c001057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsqrt.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfsub.vf` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 93 lines / 3259 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsub.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000010-----------101-----1010111` gives opcode `0x08005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsub.vf` in `generated/insns.go`; the generated record has opcode `0x08005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfsub.vv` instruction, a basic floating-point vector arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2627 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfsub.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `000010-----------001-----1010111` gives opcode `0x08001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_normal`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point minimum, floating-point maximum, floating-point multiply, floating-point divide, mask read, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- The Sail model excludes SEW=8; ifuzz can still encode the instruction bits, so downstream execution may trap depending on vector state.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfsub.vv` in `generated/insns.go`; the generated record has opcode `0x08001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfsub.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vf.yaml` is a riscv-unified-db YAML descriptor for the `vfwadd.vf` instruction, a widening floating-point arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-scalar floating-point form. The descriptor is `instruction` kind data, is 81 lines / 2486 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwadd.vf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `110000-----------101-----1010111` gives opcode `0xc0005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point multiply, floating-point widening, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point multiply, floating-point widening, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwadd.vf` in `generated/insns.go`; the generated record has opcode `0xc0005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vv.yaml` is a riscv-unified-db YAML descriptor for the `vfwadd.vv` instruction, a widening floating-point arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the vector-vector form. The descriptor is `instruction` kind data, is 82 lines / 2580 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwadd.vv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `110000-----------001-----1010111` gives opcode `0xc0001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point multiply, floating-point widening, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point multiply, floating-point widening, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwadd.vv` in `generated/insns.go`; the generated record has opcode `0xc0001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wf.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wf.yaml` is a riscv-unified-db YAML descriptor for the `vfwadd.wf` instruction, a widening floating-point arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, fs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening vector-scalar form. The descriptor is `instruction` kind data, is 79 lines / 2327 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwadd.wf`, `definedBy.extension.name: V`, `assembly: vd, vs2, fs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `110100-----------101-----1010111` gives opcode `0xd0005057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `fs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point widening, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, reads the mask and relevant operands (vs2, vd, rs1), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point widening, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwadd.wf` in `generated/insns.go`; the generated record has opcode `0xd0005057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `fs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wv.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wv.yaml` is a riscv-unified-db YAML descriptor for the `vfwadd.wv` instruction, a widening floating-point arithmetic instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vs1, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the widening vector-vector form. The descriptor is `instruction` kind data, is 80 lines / 2419 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwadd.wv`, `definedBy.extension.name: V`, `assembly: vd, vs2, vs1, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `110100-----------001-----1010111` gives opcode `0xd0001057`, mask `0xfc00707f`, and 16 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vs1` at bits `19-15`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: floating-point add, floating-point subtract, floating-point widening, mask read, vector register read, vector register write. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs1, vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs floating-point add, floating-point subtract, floating-point widening, mask read, vector register read, vector register write, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwadd.wv` in `generated/insns.go`; the generated record has opcode `0xd0001057`, mask `0xfc00707f`, and fields `vm`, `vs2`, `vs1`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwadd.wv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.f.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.f.v.yaml` is a riscv-unified-db YAML descriptor for the `vfwcvt.f.f.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 138 lines / 5768 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwcvt.f.f.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------01100001-----1010111` gives opcode `0x48061057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwcvt.f.f.v` in `generated/insns.go`; the generated record has opcode `0x48061057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.f.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.x.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.x.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.x.v.yaml` is a riscv-unified-db YAML descriptor for the `vfwcvt.f.x.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 138 lines / 5768 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwcvt.f.x.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------01011001-----1010111` gives opcode `0x48059057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwcvt.f.x.v` in `generated/insns.go`; the generated record has opcode `0x48059057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.x.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.xu.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.xu.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.xu.v.yaml` is a riscv-unified-db YAML descriptor for the `vfwcvt.f.xu.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 138 lines / 5769 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwcvt.f.xu.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------01010001-----1010111` gives opcode `0x48051057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwcvt.f.xu.v` in `generated/insns.go`; the generated record has opcode `0x48051057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.f.xu.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.rtz.x.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.rtz.x.f.v.yaml

## Purpose

`sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.rtz.x.f.v.yaml` is a riscv-unified-db YAML descriptor for the `vfwcvt.rtz.x.f.v` instruction, a floating-point/integer conversion instruction in the RISC-V `V` vector extension. It records the assembler spelling `vd, vs2, vm`, the 32-bit encoding pattern, operand bit fields, privilege/access availability, and a Sail reference body for architectural semantics. In syzkaller this file is input data for `pkg/ifuzz/riscv64/gen/gen.go`, which turns instruction YAML into static `riscv64.Insn` templates used by the riscv64 instruction fuzzer.

This is the unary vector form. The descriptor is `instruction` kind data, is 138 lines / 5772 bytes, and carries the standard Qualcomm/RISC-V Sail licensing comments plus `data_independent_timing: false`.

## Important APIs, types, and fields

- YAML contract fields: `$schema`, `kind: instruction`, `name: vfwcvt.rtz.x.f.v`, `definedBy.extension.name: V`, `assembly: vd, vs2, vm`, `encoding.match`, `encoding.variables`, `access`, `operation()`, and `sail()`.
- Encoding contract: match string `010010------01111001-----1010111` gives opcode `0x48079057`, mask `0xfc0ff07f`, and 11 variable bits. Fixed bits become `Opcode`/`OpcodeMask`; dashes become operand or free fields.
- Variable fields: `vm` at bits `25-25`; `vs2` at bits `24-20`; `vd` at bits `11-7`.
- Access policy: `s`=always, `u`=always, `vs`=always, `vu`=always. Because user and virtual-user access are not `never`, the generated `Priv` flag should remain false for this descriptor.
- Semantic helpers visible in Sail: float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual. These helpers document execution behavior but are not parsed by `gen.go`.

## Control Flow

The architectural Sail flow computes `SEW`, `LMUL_pow`, and element count, checks `illegal_fp_variable_width`, `valid_reg_overlap`, reads the mask and relevant operands (vs2, vd), initializes an inactive-lane-preserving result, loops across active elements, performs float-to-unsigned-integer conversion, float-to-signed-integer conversion, integer/float widening or narrowing conversion to float, mask read, vector register read, vector register write, floating-point flag accrual, writes the destination, clears `vstart`, and retires success. The syzkaller generator does not execute this flow; it serializes the encoding metadata so `riscv64.ParseInsn`, `Encode`, and random instruction generation can recognize or emit the 32-bit instruction word.

For generation, `filepath.WalkDir` reads this YAML, `yaml.Unmarshal` fills `instYAML`, `buildInsn` checks the 32-character match string, constructs the opcode/mask bit by bit, expands each variable location with `parseLocations`, derives privilege from `access.u` and `access.vu`, appends the instruction, and `serializer.Write` emits the generated Go table.

## State and Persistence Behavior

As a YAML descriptor, the file has no runtime persistence of its own. During generation it becomes one immutable `riscv64.Insn` template with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, `Generator: nil`, and a privilege flag derived from access policy. At fuzzer runtime, operand state exists only in the encoded instruction word and decoded `Operands`; architectural vector register, mask, `vstart`, `fcsr`, and `fflags` state are effects of a CPU or emulator executing the instruction, not state stored in the metadata table. The Sail body accrues floating-point exception flags, which is a semantic test concern but is intentionally outside the ifuzz encoding table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema, the `V` extension namespace, and the local Go generator in `pkg/ifuzz/riscv64/gen/gen.go`. Generation uses `gopkg.in/yaml.v3` to unmarshal into `instYAML`, `parseLocations` to convert bit ranges into `riscv64.InsnField` entries, `serializer.Write` to emit Go, and `osutil.WriteFileAtomically` for the generated file. The resulting instruction integrates with `pkg/ifuzz/riscv64/generated/insns.go`, whose `init` function calls `riscv64.Register`; the registered templates are then consumed by `Encode`, `Decode`, `ParseInsn`, and the generic `iset` architecture registry.

## Risks and Maintenance Notes

- The generator ignores most descriptive YAML fields, so a correct `encoding.match` and variable location list are the real contract for ifuzz generation.
- All fixed bits in the 32-character match string participate in decode through `OpcodeMask`; a single misplaced `0`, `1`, or `-` can alias another vector instruction or make this instruction unreachable.
- Mask handling depends on bit 25 being modeled as variable `vm`; if it is fixed accidentally, the fuzzer would lose masked or unmasked encodings.
- Floating-point semantics depend on FRM and accrued fflags, but the generated ifuzz table records only opcode fields, not rounding-mode side effects.
- Variable-width and widening/narrowing instructions have architectural register-overlap constraints that are documented in Sail but are not enforced by the generic field randomizer.

## Test Signals

Useful signals are: `go generate ./pkg/ifuzz/riscv64` or the equivalent generator invocation includes `vfwcvt.rtz.x.f.v` in `generated/insns.go`; the generated record has opcode `0x48079057`, mask `0xfc0ff07f`, and fields `vm`, `vs2`, `vd`; `go test ./pkg/ifuzz/riscv64/...` compiles and decode round trips accept values where the fixed bits match this mask; assembler/disassembler or architectural-vector tests cover the Sail semantics such as masks, illegal SEW/LMUL cases, overlap restrictions, rounding, fflags, and edge values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vfwcvt.rtz.x.f.v.yaml -->
