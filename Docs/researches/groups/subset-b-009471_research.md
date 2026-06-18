<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.rl.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoor.b.rl`, `long_name: Atomic fetch-and-or byte (release)`.

## Purpose

`amoor.b.rl.yaml` is a riscv-unified-db instruction descriptor for `amoor.b.rl`, the Zabha atomic fetch-and-or byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the bitwise OR result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0100001----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Or, 1'b0, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoor.b.rl` is present with match `0100001----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoor.b.rl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.yaml

Source read: complete local YAML (142 lines). Descriptor summary: `kind: instruction`, `name: amoor.b`, `long_name: Atomic fetch-and-or byte`.

## Purpose

`amoor.b.yaml` is a riscv-unified-db instruction descriptor for `amoor.b`, the Zabha atomic fetch-and-or byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the bitwise OR result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0100000----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Or, 1'b0, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with no acquire/release suffix; the ordering bits are fixed low or absent for this encoded form, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoor.b` is present with match `0100000----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoor.b` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.aq.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoor.h.aq`, `long_name: Atomic fetch-and-or halfword (acquire)`.

## Purpose

`amoor.h.aq.yaml` is a riscv-unified-db instruction descriptor for `amoor.h.aq`, the Zabha atomic fetch-and-or halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise OR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0100010----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Or, 1'b1, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoor.h.aq` is present with match `0100010----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoor.h.aq` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.aqrl.yaml

Source read: complete local YAML (146 lines). Descriptor summary: `kind: instruction`, `name: amoor.h.aqrl`, `long_name: Atomic fetch-and-or halfword (acquire-release)`.

## Purpose

`amoor.h.aqrl.yaml` is a riscv-unified-db instruction descriptor for `amoor.h.aqrl`, the Zabha atomic fetch-and-or halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise OR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0100011----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Or, 1'b1, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoor.h.aqrl` is present with match `0100011----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoor.h.aqrl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.rl.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoor.h.rl`, `long_name: Atomic fetch-and-or halfword (release)`.

## Purpose

`amoor.h.rl.yaml` is a riscv-unified-db instruction descriptor for `amoor.h.rl`, the Zabha atomic fetch-and-or halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise OR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0100001----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Or, 1'b0, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoor.h.rl` is present with match `0100001----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoor.h.rl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.yaml

Source read: complete local YAML (142 lines). Descriptor summary: `kind: instruction`, `name: amoor.h`, `long_name: Atomic fetch-and-or halfword`.

## Purpose

`amoor.h.yaml` is a riscv-unified-db instruction descriptor for `amoor.h`, the Zabha atomic fetch-and-or halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise OR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0100000----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Or, 1'b0, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with no acquire/release suffix; the ordering bits are fixed low or absent for this encoded form, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoor.h` is present with match `0100000----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoor.h` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.aq.yaml

Source read: complete local YAML (143 lines). Descriptor summary: `kind: instruction`, `name: amoswap.b.aq`, `long_name: Atomic SWAP byte (acquire)`.

## Purpose

`amoswap.b.aq.yaml` is a riscv-unified-db instruction descriptor for `amoswap.b.aq`, the Zabha atomic swap byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the replacement with xs2 result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000110----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Swap, 1'b1, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.b.aq` is present with match `0000110----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.b.aq` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.aqrl.yaml

Source read: complete local YAML (145 lines). Descriptor summary: `kind: instruction`, `name: amoswap.b.aqrl`, `long_name: Atomic SWAP byte (acquire-release)`.

## Purpose

`amoswap.b.aqrl.yaml` is a riscv-unified-db instruction descriptor for `amoswap.b.aqrl`, the Zabha atomic swap byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the replacement with xs2 result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000111----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Swap, 1'b1, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.b.aqrl` is present with match `0000111----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.b.aqrl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.rl.yaml

Source read: complete local YAML (143 lines). Descriptor summary: `kind: instruction`, `name: amoswap.b.rl`, `long_name: Atomic SWAP byte (release)`.

## Purpose

`amoswap.b.rl.yaml` is a riscv-unified-db instruction descriptor for `amoswap.b.rl`, the Zabha atomic swap byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the replacement with xs2 result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000101----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Swap, 1'b0, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.b.rl` is present with match `0000101----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.b.rl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.yaml

Source read: complete local YAML (141 lines). Descriptor summary: `kind: instruction`, `name: amoswap.b`, `long_name: Atomic SWAP byte`.

## Purpose

`amoswap.b.yaml` is a riscv-unified-db instruction descriptor for `amoswap.b`, the Zabha atomic swap byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the replacement with xs2 result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000100----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Swap, 1'b0, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with no acquire/release suffix; the ordering bits are fixed low or absent for this encoded form, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.b` is present with match `0000100----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.b` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.aq.yaml

Source read: complete local YAML (143 lines). Descriptor summary: `kind: instruction`, `name: amoswap.h.aq`, `long_name: Atomic SWAP halfword (acquire)`.

## Purpose

`amoswap.h.aq.yaml` is a riscv-unified-db instruction descriptor for `amoswap.h.aq`, the Zabha atomic swap halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the replacement with xs2 result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000110----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Swap, 1'b1, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.h.aq` is present with match `0000110----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.h.aq` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.aqrl.yaml

Source read: complete local YAML (145 lines). Descriptor summary: `kind: instruction`, `name: amoswap.h.aqrl`, `long_name: Atomic SWAP halfword (acquire-release)`.

## Purpose

`amoswap.h.aqrl.yaml` is a riscv-unified-db instruction descriptor for `amoswap.h.aqrl`, the Zabha atomic swap halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the replacement with xs2 result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000111----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Swap, 1'b1, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.h.aqrl` is present with match `0000111----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.h.aqrl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.rl.yaml

Source read: complete local YAML (143 lines). Descriptor summary: `kind: instruction`, `name: amoswap.h.rl`, `long_name: Atomic SWAP halfword (release)`.

## Purpose

`amoswap.h.rl.yaml` is a riscv-unified-db instruction descriptor for `amoswap.h.rl`, the Zabha atomic swap halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the replacement with xs2 result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000101----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Swap, 1'b0, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.h.rl` is present with match `0000101----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.h.rl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.yaml

Source read: complete local YAML (141 lines). Descriptor summary: `kind: instruction`, `name: amoswap.h`, `long_name: Atomic SWAP halfword`.

## Purpose

`amoswap.h.yaml` is a riscv-unified-db instruction descriptor for `amoswap.h`, the Zabha atomic swap halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the replacement with xs2 result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0000100----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Swap, 1'b0, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with no acquire/release suffix; the ordering bits are fixed low or absent for this encoded form, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoswap` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoswap.h` is present with match `0000100----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoswap.h` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoswap.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.aq.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoxor.b.aq`, `long_name: Atomic fetch-and-xor byte (acquire)`.

## Purpose

`amoxor.b.aq.yaml` is a riscv-unified-db instruction descriptor for `amoxor.b.aq`, the Zabha atomic fetch-and-xor byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the bitwise XOR result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010010----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Xor, 1'b1, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.b.aq` is present with match `0010010----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.b.aq` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.aqrl.yaml

Source read: complete local YAML (146 lines). Descriptor summary: `kind: instruction`, `name: amoxor.b.aqrl`, `long_name: Atomic fetch-and-xor byte (acquire-release)`.

## Purpose

`amoxor.b.aqrl.yaml` is a riscv-unified-db instruction descriptor for `amoxor.b.aqrl`, the Zabha atomic fetch-and-xor byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the bitwise XOR result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010011----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Xor, 1'b1, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.b.aqrl` is present with match `0010011----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.b.aqrl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.rl.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoxor.b.rl`, `long_name: Atomic fetch-and-xor byte (release)`.

## Purpose

`amoxor.b.rl.yaml` is a riscv-unified-db instruction descriptor for `amoxor.b.rl`, the Zabha atomic fetch-and-xor byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the bitwise XOR result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010001----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Xor, 1'b0, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.b.rl` is present with match `0010001----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.b.rl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.yaml

Source read: complete local YAML (142 lines). Descriptor summary: `kind: instruction`, `name: amoxor.b`, `long_name: Atomic fetch-and-xor byte`.

## Purpose

`amoxor.b.yaml` is a riscv-unified-db instruction descriptor for `amoxor.b`, the Zabha atomic fetch-and-xor byte instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a byte, computes the bitwise XOR result, and writes the low 8 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010000----------000-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Xor, 1'b0, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with no acquire/release suffix; the ordering bits are fixed low or absent for this encoded form, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded byte, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `000` selects byte, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.b` is present with match `0010000----------000-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.b` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aq.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoxor.h.aq`, `long_name: Atomic fetch-and-xor halfword (acquire)`.

## Purpose

`amoxor.h.aq.yaml` is a riscv-unified-db instruction descriptor for `amoxor.h.aq`, the Zabha atomic fetch-and-xor halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise XOR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010010----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Xor, 1'b1, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.h.aq` is present with match `0010010----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.h.aq` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aqrl.yaml

Source read: complete local YAML (146 lines). Descriptor summary: `kind: instruction`, `name: amoxor.h.aqrl`, `long_name: Atomic fetch-and-xor halfword (acquire-release)`.

## Purpose

`amoxor.h.aqrl.yaml` is a riscv-unified-db instruction descriptor for `amoxor.h.aqrl`, the Zabha atomic fetch-and-xor halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise XOR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010011----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Xor, 1'b1, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.h.aqrl` is present with match `0010011----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.h.aqrl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.rl.yaml

Source read: complete local YAML (144 lines). Descriptor summary: `kind: instruction`, `name: amoxor.h.rl`, `long_name: Atomic fetch-and-xor halfword (release)`.

## Purpose

`amoxor.h.rl.yaml` is a riscv-unified-db instruction descriptor for `amoxor.h.rl`, the Zabha atomic fetch-and-xor halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise XOR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010001----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Xor, 1'b0, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.h.rl` is present with match `0010001----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.h.rl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.yaml

Source read: complete local YAML (142 lines). Descriptor summary: `kind: instruction`, `name: amoxor.h`, `long_name: Atomic fetch-and-xor halfword`.

## Purpose

`amoxor.h.yaml` is a riscv-unified-db instruction descriptor for `amoxor.h`, the Zabha atomic fetch-and-xor halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise XOR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010000----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Xor, 1'b0, 1'b0, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with no acquire/release suffix; the ordering bits are fixed low or absent for this encoded form, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.h` is present with match `0010000----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.h` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.aq.yaml

Source read: complete local YAML (136 lines). Descriptor summary: `kind: instruction`, `name: amocas.d.aq`, `long_name: Atomic compare-and-swap doubleword (acquire)`.

## Purpose

`amocas.d.aq.yaml` describes `amocas.d.aq`, the Zacas atomic compare-and-swap doubleword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the doubleword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010110----------011-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas64(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.d.aq` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `011` for doubleword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.d.aq` is present with opcode match `0010110----------011-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.aqrl.yaml

Source read: complete local YAML (138 lines). Descriptor summary: `kind: instruction`, `name: amocas.d.aqrl`, `long_name: Atomic compare-and-swap doubleword (acquire-release)`.

## Purpose

`amocas.d.aqrl.yaml` describes `amocas.d.aqrl`, the Zacas atomic compare-and-swap doubleword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the doubleword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010111----------011-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas64(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.d.aqrl` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `011` for doubleword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.d.aqrl` is present with opcode match `0010111----------011-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.rl.yaml

Source read: complete local YAML (136 lines). Descriptor summary: `kind: instruction`, `name: amocas.d.rl`, `long_name: Atomic compare-and-swap doubleword (release)`.

## Purpose

`amocas.d.rl.yaml` describes `amocas.d.rl`, the Zacas atomic compare-and-swap doubleword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the doubleword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010101----------011-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas64(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.d.rl` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `011` for doubleword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.d.rl` is present with opcode match `0010101----------011-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.yaml

Source read: complete local YAML (134 lines). Descriptor summary: `kind: instruction`, `name: amocas.d`, `long_name: Atomic compare-and-swap doubleword`.

## Purpose

`amocas.d.yaml` describes `amocas.d`, the Zacas atomic compare-and-swap doubleword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the doubleword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. No acquire/release suffix; the ordering bits are fixed low or absent for this encoded form.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010100----------011-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas64(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.d` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `011` for doubleword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.d` is present with opcode match `0010100----------011-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.aq.yaml

Source read: complete local YAML (138 lines). Descriptor summary: `kind: instruction`, `name: amocas.q.aq`, `long_name: Atomic compare-and-swap quadword (acquire)`.

## Purpose

`amocas.q.aq.yaml` describes `amocas.q.aq`, the Zacas atomic compare-and-swap quadword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the quadword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`. This descriptor is RV64-only through `definedBy: xlen: 64`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010110----------100-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas128(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The quadword forms additionally require `xlen: 64` in `definedBy`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.q.aq` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `100` for quadword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.q.aq` is present with opcode match `0010110----------100-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.aqrl.yaml

Source read: complete local YAML (140 lines). Descriptor summary: `kind: instruction`, `name: amocas.q.aqrl`, `long_name: Atomic compare-and-swap quadword (acquire-release)`.

## Purpose

`amocas.q.aqrl.yaml` describes `amocas.q.aqrl`, the Zacas atomic compare-and-swap quadword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the quadword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it. This descriptor is RV64-only through `definedBy: xlen: 64`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010111----------100-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas128(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The quadword forms additionally require `xlen: 64` in `definedBy`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.q.aqrl` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `100` for quadword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.q.aqrl` is present with opcode match `0010111----------100-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.rl.yaml

Source read: complete local YAML (138 lines). Descriptor summary: `kind: instruction`, `name: amocas.q.rl`, `long_name: Atomic compare-and-swap quadword (release)`.

## Purpose

`amocas.q.rl.yaml` describes `amocas.q.rl`, the Zacas atomic compare-and-swap quadword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the quadword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`. This descriptor is RV64-only through `definedBy: xlen: 64`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010101----------100-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas128(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The quadword forms additionally require `xlen: 64` in `definedBy`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.q.rl` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `100` for quadword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.q.rl` is present with opcode match `0010101----------100-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.yaml

Source read: complete local YAML (136 lines). Descriptor summary: `kind: instruction`, `name: amocas.q`, `long_name: Atomic compare-and-swap quadword`.

## Purpose

`amocas.q.yaml` describes `amocas.q`, the Zacas atomic compare-and-swap quadword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the quadword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. No acquire/release suffix; the ordering bits are fixed low or absent for this encoded form. This descriptor is RV64-only through `definedBy: xlen: 64`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010100----------100-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas128(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The quadword forms additionally require `xlen: 64` in `definedBy`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.q` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `100` for quadword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.q` is present with opcode match `0010100----------100-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.q.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.aq.yaml

Source read: complete local YAML (136 lines). Descriptor summary: `kind: instruction`, `name: amocas.w.aq`, `long_name: Atomic compare-and-swap word (acquire)`.

## Purpose

`amocas.w.aq.yaml` describes `amocas.w.aq`, the Zacas atomic compare-and-swap word instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the word at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Acquire ordering; the match string fixes only the acquire bit high, and operation pseudocode calls `memory_model_acquire()`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010110----------010-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas32(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.w.aq` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `010` for word and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.w.aq` is present with opcode match `0010110----------010-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.aqrl.yaml

Source read: complete local YAML (138 lines). Descriptor summary: `kind: instruction`, `name: amocas.w.aqrl`, `long_name: Atomic compare-and-swap word (acquire-release)`.

## Purpose

`amocas.w.aqrl.yaml` describes `amocas.w.aqrl`, the Zacas atomic compare-and-swap word instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the word at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010111----------010-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas32(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.w.aqrl` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `010` for word and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.w.aqrl` is present with opcode match `0010111----------010-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.rl.yaml

Source read: complete local YAML (136 lines). Descriptor summary: `kind: instruction`, `name: amocas.w.rl`, `long_name: Atomic compare-and-swap word (release)`.

## Purpose

`amocas.w.rl.yaml` describes `amocas.w.rl`, the Zacas atomic compare-and-swap word instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the word at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. Release ordering; the match string fixes only the release bit high, and operation pseudocode calls `memory_model_release()`.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010101----------010-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas32(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.w.rl` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `010` for word and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.w.rl` is present with opcode match `0010101----------010-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.yaml

Source read: complete local YAML (134 lines). Descriptor summary: `kind: instruction`, `name: amocas.w`, `long_name: Atomic compare-and-swap word`.

## Purpose

`amocas.w.yaml` describes `amocas.w`, the Zacas atomic compare-and-swap word instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the word at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. No acquire/release suffix; the ordering bits are fixed low or absent for this encoded form.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010100----------010-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas32(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.w` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `010` for word and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.w` is present with opcode match `0010100----------010-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lb.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lb.aq.yaml

Source read: complete local YAML (63 lines). Descriptor summary: `kind: instruction`, `name: lb.aq`, `long_name: No synopsis available`.

## Purpose

`lb.aq.yaml` is a Zalasr descriptor for `lb.aq`, a acquire load byte instruction with assembly form `xd, (xs1)`. It uses `xs1` as address base and `xd` as destination. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `001101000000-----000-----0101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then calls `process_load` with an acquire memory read. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `lb.aq`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the loaded value to `xd`. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `000` for byte, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `lb.aq` appears with match `001101000000-----000-----0101111` and fields `xs1` at `19-15`; `xd` at `11-7`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lb.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/ld.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/ld.aq.yaml

Source read: complete local YAML (63 lines). Descriptor summary: `kind: instruction`, `name: ld.aq`, `long_name: No synopsis available`.

## Purpose

`ld.aq.yaml` is a Zalasr descriptor for `ld.aq`, a acquire load doubleword instruction with assembly form `xd, (xs1)`. It uses `xs1` as address base and `xd` as destination. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `001101000000-----011-----0101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then calls `process_load` with an acquire memory read. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `ld.aq`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the loaded value to `xd`. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `011` for doubleword, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `ld.aq` appears with match `001101000000-----011-----0101111` and fields `xs1` at `19-15`; `xd` at `11-7`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/ld.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lh.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lh.aq.yaml

Source read: complete local YAML (63 lines). Descriptor summary: `kind: instruction`, `name: lh.aq`, `long_name: No synopsis available`.

## Purpose

`lh.aq.yaml` is a Zalasr descriptor for `lh.aq`, a acquire load halfword instruction with assembly form `xd, (xs1)`. It uses `xs1` as address base and `xd` as destination. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `001101000000-----001-----0101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then calls `process_load` with an acquire memory read. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `lh.aq`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the loaded value to `xd`. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `001` for halfword, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `lh.aq` appears with match `001101000000-----001-----0101111` and fields `xs1` at `19-15`; `xd` at `11-7`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lh.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lw.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lw.aq.yaml

Source read: complete local YAML (63 lines). Descriptor summary: `kind: instruction`, `name: lw.aq`, `long_name: No synopsis available`.

## Purpose

`lw.aq.yaml` is a Zalasr descriptor for `lw.aq`, a acquire load word instruction with assembly form `xd, (xs1)`. It uses `xs1` as address base and `xd` as destination. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `001101000000-----010-----0101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then calls `process_load` with an acquire memory read. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `lw.aq`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the loaded value to `xd`. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `010` for word, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `lw.aq` appears with match `001101000000-----010-----0101111` and fields `xs1` at `19-15`; `xd` at `11-7`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/lw.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sb.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sb.rl.yaml

Source read: complete local YAML (78 lines). Descriptor summary: `kind: instruction`, `name: sb.rl`, `long_name: No synopsis available`.

## Purpose

`sb.rl.yaml` is a Zalasr descriptor for `sb.rl`, a release store byte instruction with assembly form `xs2, (xs1)`. It uses `xs1` as address base and `xs2` as the store value. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `0011101----------000000000101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then performs a release memory write of the selected width. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `sb.rl`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the low operand bits from `xs2` to memory and has no destination register. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `000` for byte, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `sb.rl` appears with match `0011101----------000000000101111` and fields `xs2` at `24-20`; `xs1` at `19-15`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sb.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sd.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sd.rl.yaml

Source read: complete local YAML (78 lines). Descriptor summary: `kind: instruction`, `name: sd.rl`, `long_name: No synopsis available`.

## Purpose

`sd.rl.yaml` is a Zalasr descriptor for `sd.rl`, a release store doubleword instruction with assembly form `xs2, (xs1)`. It uses `xs1` as address base and `xs2` as the store value. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `0011101----------011000000101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then performs a release memory write of the selected width. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `sd.rl`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the low operand bits from `xs2` to memory and has no destination register. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `011` for doubleword, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `sd.rl` appears with match `0011101----------011000000101111` and fields `xs2` at `24-20`; `xs1` at `19-15`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sd.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sh.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sh.rl.yaml

Source read: complete local YAML (78 lines). Descriptor summary: `kind: instruction`, `name: sh.rl`, `long_name: No synopsis available`.

## Purpose

`sh.rl.yaml` is a Zalasr descriptor for `sh.rl`, a release store halfword instruction with assembly form `xs2, (xs1)`. It uses `xs1` as address base and `xs2` as the store value. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `0011101----------001000000101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then performs a release memory write of the selected width. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `sh.rl`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the low operand bits from `xs2` to memory and has no destination register. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `001` for halfword, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `sh.rl` appears with match `0011101----------001000000101111` and fields `xs2` at `24-20`; `xs1` at `19-15`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sh.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sw.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sw.rl.yaml

Source read: complete local YAML (78 lines). Descriptor summary: `kind: instruction`, `name: sw.rl`, `long_name: No synopsis available`.

## Purpose

`sw.rl.yaml` is a Zalasr descriptor for `sw.rl`, a release store word instruction with assembly form `xs2, (xs1)`. It uses `xs1` as address base and `xs2` as the store value. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `0011101----------010000000101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then performs a release memory write of the selected width. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `sw.rl`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the low operand bits from `xs2` to memory and has no destination register. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `010` for word, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `sw.rl` appears with match `0011101----------010000000101111` and fields `xs2` at `24-20`; `xs1` at `19-15`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sw.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.d.yaml

Source read: complete local YAML (148 lines). Descriptor summary: `kind: instruction`, `name: lr.d`, `long_name: Load reserved doubleword`.

## Purpose

`lr.d.yaml` describes `lr.d`, a Zalrsc load-reserved doubleword instruction with assembly form `xd, (xs1)`. It participates in RISC-V LR/SC atomic sequences: LR establishes a reservation and returns the loaded value, while SC conditionally stores a value if the reservation is still valid and reports success/failure in `xd`. The descriptor includes extensive architecture prose about alignment, reservation sets, failure codes, and acquire/release ordering.

## Important APIs, Types, and Functions

The file is declarative input for `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, but it exposes a current generator limitation. Its match string is `00010--00000-----011-----0101111` with 20 fixed bits and 12 variable bits. Variables are `aq` at `26` (with not: 1); `rl` at `25` (with not: 1); `xs1` at `19-15`; `xd` at `11-7`. `aq` and `rl` are variable ordering bits, `xs1` is the address register, and `xd` is the result register. The operation block checks natural 64-bit alignment, calls `load_reserved<32>` in the current source text, and writes the reserved load result to `xd`.

## Control Flow

The intended generation flow is the same as other RISC-V descriptors: walk the YAML tree, unmarshal into `instYAML`, build opcode/mask bits, parse variable locations, and append a `riscv64.Insn`. For this file, `buildInsn` reaches `parseLocations` for `aq` at `26` and `rl` at `25`, but `parseRange` splits only `hi-lo` forms and therefore returns false for a bare single-bit location. The instruction is consequently skipped by the current generator unless single-bit locations are normalized or generator support is extended. Architecturally, the operation checks atomic availability, reads `X[xs1]`, handles misalignment with implementation-dependent exception choice, and then performs the LR/SC reservation action. The Sail block supplies the detailed memory translation, reservation matching, exception, and success/failure control flow.

## State and Persistence Behavior

If generator support is fixed, this descriptor would persist an `Insn` table row with variable `aq`/`rl` bits and register operands. In the current code path it is expected to be absent from `generated/insns.go` because of the single-bit parse limitation. Runtime architectural state includes the hart reservation state, memory at `X[xs1]`, and result register `xd`; LR has no `xs2` source operand. Access is s=always, u=always, vs=always, vu=always, so the instruction is architecturally user-visible and should not be marked privileged by ifuzz once generated.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema, the Zalrsc extension, and the shared RISC-V atomic memory model. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated ifuzz registry only after the location parser can handle single-bit variables. Extension metadata says `Zalrsc`; the operation text checks the atomic `A` architectural availability through `implemented?(ExtensionName::A)` / `misa.A`. The doubleword forms additionally require `xlen: 64` in `definedBy`. The semantic blocks reference helpers such as `load_reserved`, `store_conditional`, `is_naturally_aligned`, `LRSC_MISALIGNED_BEHAVIOR`, and Sail reservation helpers; none of these are executed by the ifuzz generator.

## Risks and Edge Cases

This descriptor is not currently consumable by `parseLocations` because `aq` and `rl` use single-bit locations (`26` and `25`) while `parseRange` accepts only `hi-lo` strings; `not: 1` is also ignored by the Go struct. That makes this file a table-coverage risk rather than just a semantic descriptor. There is also semantic complexity around misaligned LR/SC exceptions, reservation aliasing, device writes, SC failure codes, and ordering-bit combinations. For `lr.d`, the visible operation calls `load_reserved<32>` despite the doubleword name and 64-bit alignment check, which should be reviewed against the upstream source or generator import.

## Test Signals

Add a generator unit test for single-bit variable locations using this descriptor as a fixture, then assert `lr.d` is either intentionally skipped with a documented reason or generated with fields `aq` at `26` (with not: 1); `rl` at `25` (with not: 1); `xs1` at `19-15`; `xd` at `11-7`. After parser support exists, regenerate `generated/insns.go` and run encode/decode round trips over `aq`, `rl`, and register operands. Architectural tests should cover aligned success, reservation failure, misalignment exception choice, acquire/release bit combinations, and SC result values. For `lr.d`, include a targeted check that the generated/semantic width is truly 64 bits and not accidentally inherited from a 32-bit helper call.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.w.yaml

Source read: complete local YAML (156 lines). Descriptor summary: `kind: instruction`, `name: lr.w`, `long_name: Load reserved word`.

## Purpose

`lr.w.yaml` describes `lr.w`, a Zalrsc load-reserved word instruction with assembly form `xd, (xs1)`. It participates in RISC-V LR/SC atomic sequences: LR establishes a reservation and returns the loaded value, while SC conditionally stores a value if the reservation is still valid and reports success/failure in `xd`. The descriptor includes extensive architecture prose about alignment, reservation sets, failure codes, and acquire/release ordering.

## Important APIs, Types, and Functions

The file is declarative input for `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, but it exposes a current generator limitation. Its match string is `00010--00000-----010-----0101111` with 20 fixed bits and 12 variable bits. Variables are `aq` at `26` (with not: 1); `rl` at `25` (with not: 1); `xs1` at `19-15`; `xd` at `11-7`. `aq` and `rl` are variable ordering bits, `xs1` is the address register, and `xd` is the result register. The operation block checks natural 32-bit alignment, calls `load_reserved<32>` in the current source text, and writes the reserved load result to `xd`.

## Control Flow

The intended generation flow is the same as other RISC-V descriptors: walk the YAML tree, unmarshal into `instYAML`, build opcode/mask bits, parse variable locations, and append a `riscv64.Insn`. For this file, `buildInsn` reaches `parseLocations` for `aq` at `26` and `rl` at `25`, but `parseRange` splits only `hi-lo` forms and therefore returns false for a bare single-bit location. The instruction is consequently skipped by the current generator unless single-bit locations are normalized or generator support is extended. Architecturally, the operation checks atomic availability, reads `X[xs1]`, handles misalignment with implementation-dependent exception choice, and then performs the LR/SC reservation action. The Sail block supplies the detailed memory translation, reservation matching, exception, and success/failure control flow.

## State and Persistence Behavior

If generator support is fixed, this descriptor would persist an `Insn` table row with variable `aq`/`rl` bits and register operands. In the current code path it is expected to be absent from `generated/insns.go` because of the single-bit parse limitation. Runtime architectural state includes the hart reservation state, memory at `X[xs1]`, and result register `xd`; LR has no `xs2` source operand. Access is s=always, u=always, vs=always, vu=always, so the instruction is architecturally user-visible and should not be marked privileged by ifuzz once generated.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema, the Zalrsc extension, and the shared RISC-V atomic memory model. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated ifuzz registry only after the location parser can handle single-bit variables. Extension metadata says `Zalrsc`; the operation text checks the atomic `A` architectural availability through `implemented?(ExtensionName::A)` / `misa.A`. The semantic blocks reference helpers such as `load_reserved`, `store_conditional`, `is_naturally_aligned`, `LRSC_MISALIGNED_BEHAVIOR`, and Sail reservation helpers; none of these are executed by the ifuzz generator.

## Risks and Edge Cases

This descriptor is not currently consumable by `parseLocations` because `aq` and `rl` use single-bit locations (`26` and `25`) while `parseRange` accepts only `hi-lo` strings; `not: 1` is also ignored by the Go struct. That makes this file a table-coverage risk rather than just a semantic descriptor. There is also semantic complexity around misaligned LR/SC exceptions, reservation aliasing, device writes, SC failure codes, and ordering-bit combinations.

## Test Signals

Add a generator unit test for single-bit variable locations using this descriptor as a fixture, then assert `lr.w` is either intentionally skipped with a documented reason or generated with fields `aq` at `26` (with not: 1); `rl` at `25` (with not: 1); `xs1` at `19-15`; `xd` at `11-7`. After parser support exists, regenerate `generated/insns.go` and run encode/decode round trips over `aq`, `rl`, and register operands. Architectural tests should cover aligned success, reservation failure, misalignment exception choice, acquire/release bit combinations, and SC result values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/sc.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/sc.d.yaml

Source read: complete local YAML (240 lines). Descriptor summary: `kind: instruction`, `name: sc.d`, `long_name: Store conditional doubleword`.

## Purpose

`sc.d.yaml` describes `sc.d`, a Zalrsc store-conditional doubleword instruction with assembly form `xd, xs2, (xs1)`. It participates in RISC-V LR/SC atomic sequences: LR establishes a reservation and returns the loaded value, while SC conditionally stores a value if the reservation is still valid and reports success/failure in `xd`. The descriptor includes extensive architecture prose about alignment, reservation sets, failure codes, and acquire/release ordering.

## Important APIs, Types, and Functions

The file is declarative input for `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, but it exposes a current generator limitation. Its match string is `00011------------011-----0101111` with 15 fixed bits and 17 variable bits. Variables are `aq` at `26`; `rl` at `25`; `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. `aq` and `rl` are variable ordering bits, `xs1` is the address register, `xs2` is the store value register, and `xd` is the result register. The operation block checks natural 64-bit alignment, calls `store_conditional<64>`, writes zero to `xd` on success and one on failure, and invalidates/uses the reservation model.

## Control Flow

The intended generation flow is the same as other RISC-V descriptors: walk the YAML tree, unmarshal into `instYAML`, build opcode/mask bits, parse variable locations, and append a `riscv64.Insn`. For this file, `buildInsn` reaches `parseLocations` for `aq` at `26` and `rl` at `25`, but `parseRange` splits only `hi-lo` forms and therefore returns false for a bare single-bit location. The instruction is consequently skipped by the current generator unless single-bit locations are normalized or generator support is extended. Architecturally, the operation checks atomic availability, reads `X[xs1]`, handles misalignment with implementation-dependent exception choice, and then performs the LR/SC reservation action. The Sail block supplies the detailed memory translation, reservation matching, exception, and success/failure control flow.

## State and Persistence Behavior

If generator support is fixed, this descriptor would persist an `Insn` table row with variable `aq`/`rl` bits and register operands. In the current code path it is expected to be absent from `generated/insns.go` because of the single-bit parse limitation. Runtime architectural state includes the hart reservation state, memory at `X[xs1]`, source register `xs2`, and result register `xd`, which records zero for success and nonzero for failure. Access is s=always, u=always, vs=always, vu=always, so the instruction is architecturally user-visible and should not be marked privileged by ifuzz once generated.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema, the Zalrsc extension, and the shared RISC-V atomic memory model. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated ifuzz registry only after the location parser can handle single-bit variables. Extension metadata says `Zalrsc`; the operation text checks the atomic `A` architectural availability through `implemented?(ExtensionName::A)` / `misa.A`. The doubleword forms additionally require `xlen: 64` in `definedBy`. The semantic blocks reference helpers such as `load_reserved`, `store_conditional`, `is_naturally_aligned`, `LRSC_MISALIGNED_BEHAVIOR`, and Sail reservation helpers; none of these are executed by the ifuzz generator.

## Risks and Edge Cases

This descriptor is not currently consumable by `parseLocations` because `aq` and `rl` use single-bit locations (`26` and `25`) while `parseRange` accepts only `hi-lo` strings; `not: 1` is also ignored by the Go struct. That makes this file a table-coverage risk rather than just a semantic descriptor. There is also semantic complexity around misaligned LR/SC exceptions, reservation aliasing, device writes, SC failure codes, and ordering-bit combinations. For SC, failed stores may still be treated like stores for protection, and every SC invalidates a reservation; tests that check only successful stores will miss this behavior.

## Test Signals

Add a generator unit test for single-bit variable locations using this descriptor as a fixture, then assert `sc.d` is either intentionally skipped with a documented reason or generated with fields `aq` at `26`; `rl` at `25`; `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. After parser support exists, regenerate `generated/insns.go` and run encode/decode round trips over `aq`, `rl`, and register operands. Architectural tests should cover aligned success, reservation failure, misalignment exception choice, acquire/release bit combinations, and SC result values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/sc.d.yaml -->
