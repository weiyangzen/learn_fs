# subset-b-009468 Research

Grouped research for `subset-b-009468`. Each delimited section preserves the source path in its title and can be split directly into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.yaml

## Purpose

`amoand.d` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-and doubleword` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise AND, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amoand.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoand.d`, and `encoding.match: 0110000----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::And, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::And`, width `64`, acquire bit `0`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoand.d`, opcode/mask derived from `0110000----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoand.d` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `And` operation (computes the stored value as the loaded memory value AND the rs2 operand), the `64`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoand.d` with match `0110000----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `And` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.aq.yaml

## Purpose

`amoand.w.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-and word (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise AND, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amoand.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoand.w.aq`, and `encoding.match: 0110010----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::And, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::And`, width `32`, acquire bit `1`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoand.w.aq`, opcode/mask derived from `0110010----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoand.w.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `And` operation (computes the stored value as the loaded memory value AND the rs2 operand), the `32`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoand.w.aq` with match `0110010----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `And` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.aqrl.yaml

## Purpose

`amoand.w.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-and word (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise AND, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amoand.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoand.w.aqrl`, and `encoding.match: 0110011----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::And, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::And`, width `32`, acquire bit `1`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoand.w.aqrl`, opcode/mask derived from `0110011----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoand.w.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `And` operation (computes the stored value as the loaded memory value AND the rs2 operand), the `32`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoand.w.aqrl` with match `0110011----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `And` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.rl.yaml

## Purpose

`amoand.w.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-and word (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise AND, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amoand.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoand.w.rl`, and `encoding.match: 0110001----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::And, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::And`, width `32`, acquire bit `0`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoand.w.rl`, opcode/mask derived from `0110001----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoand.w.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `And` operation (computes the stored value as the loaded memory value AND the rs2 operand), the `32`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoand.w.rl` with match `0110001----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `And` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.yaml

## Purpose

`amoand.w` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-and word` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise AND, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amoand.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoand.w`, and `encoding.match: 0110000----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::And, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::And`, width `32`, acquire bit `0`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoand.w`, opcode/mask derived from `0110000----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoand.w` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `And` operation (computes the stored value as the loaded memory value AND the rs2 operand), the `32`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoand.w` with match `0110000----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `And` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoand.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.aq.yaml

## Purpose

`amomax.d.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX doubleword (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.d.aq`, and `encoding.match: 1010010----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Max, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Max`, width `64`, acquire bit `1`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.d.aq`, opcode/mask derived from `1010010----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.d.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.d.aq` with match `1010010----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.aqrl.yaml

## Purpose

`amomax.d.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX doubleword (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.d.aqrl`, and `encoding.match: 1010011----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Max, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Max`, width `64`, acquire bit `1`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.d.aqrl`, opcode/mask derived from `1010011----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.d.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.d.aqrl` with match `1010011----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.rl.yaml

## Purpose

`amomax.d.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX doubleword (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.d.rl`, and `encoding.match: 1010001----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Max, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Max`, width `64`, acquire bit `0`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.d.rl`, opcode/mask derived from `1010001----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.d.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.d.rl` with match `1010001----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.yaml

## Purpose

`amomax.d` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX doubleword` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.d`, and `encoding.match: 1010000----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Max, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Max`, width `64`, acquire bit `0`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.d`, opcode/mask derived from `1010000----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.d` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.d` with match `1010000----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.aq.yaml

## Purpose

`amomax.w.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX word (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.w.aq`, and `encoding.match: 1010010----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Max, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Max`, width `32`, acquire bit `1`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.w.aq`, opcode/mask derived from `1010010----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.w.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.w.aq` with match `1010010----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.aqrl.yaml

## Purpose

`amomax.w.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX word (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.w.aqrl`, and `encoding.match: 1010011----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Max, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Max`, width `32`, acquire bit `1`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.w.aqrl`, opcode/mask derived from `1010011----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.w.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.w.aqrl` with match `1010011----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.rl.yaml

## Purpose

`amomax.w.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX word (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.w.rl`, and `encoding.match: 1010001----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Max, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Max`, width `32`, acquire bit `0`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.w.rl`, opcode/mask derived from `1010001----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.w.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.w.rl` with match `1010001----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.yaml

## Purpose

`amomax.w` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX word` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed maximum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amomax.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomax.w`, and `encoding.match: 1010000----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Max, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Max`, width `32`, acquire bit `0`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomax.w`, opcode/mask derived from `1010000----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomax.w` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Max` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomax.w` with match `1010000----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Max` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomax.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.aq.yaml

## Purpose

`amomaxu.d.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned doubleword (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.d.aq`, and `encoding.match: 1110010----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Maxu, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Maxu`, width `64`, acquire bit `1`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.d.aq`, opcode/mask derived from `1110010----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.d.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.d.aq` with match `1110010----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.aqrl.yaml

## Purpose

`amomaxu.d.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned doubleword (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.d.aqrl`, and `encoding.match: 1110011----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Maxu, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Maxu`, width `64`, acquire bit `1`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.d.aqrl`, opcode/mask derived from `1110011----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.d.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.d.aqrl` with match `1110011----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.rl.yaml

## Purpose

`amomaxu.d.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned doubleword (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.d.rl`, and `encoding.match: 1110001----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Maxu, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Maxu`, width `64`, acquire bit `0`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.d.rl`, opcode/mask derived from `1110001----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.d.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.d.rl` with match `1110001----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.yaml

## Purpose

`amomaxu.d` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned doubleword` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.d`, and `encoding.match: 1110000----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Maxu, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Maxu`, width `64`, acquire bit `0`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.d`, opcode/mask derived from `1110000----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.d` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.d` with match `1110000----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.aq.yaml

## Purpose

`amomaxu.w.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned word (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.w.aq`, and `encoding.match: 1110010----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Maxu, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Maxu`, width `32`, acquire bit `1`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.w.aq`, opcode/mask derived from `1110010----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.w.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.w.aq` with match `1110010----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.aqrl.yaml

## Purpose

`amomaxu.w.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned word (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.w.aqrl`, and `encoding.match: 1110011----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Maxu, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Maxu`, width `32`, acquire bit `1`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.w.aqrl`, opcode/mask derived from `1110011----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.w.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.w.aqrl` with match `1110011----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.rl.yaml

## Purpose

`amomaxu.w.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned word (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.w.rl`, and `encoding.match: 1110001----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Maxu, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Maxu`, width `32`, acquire bit `0`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.w.rl`, opcode/mask derived from `1110001----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.w.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.w.rl` with match `1110001----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.yaml

## Purpose

`amomaxu.w` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned word` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.w`, and `encoding.match: 1110000----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Maxu, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Maxu`, width `32`, acquire bit `0`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.w`, opcode/mask derived from `1110000----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.w` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.w` with match `1110000----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.aq.yaml

## Purpose

`amomin.d.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN doubleword (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.d.aq`, and `encoding.match: 1000010----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Min, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Min`, width `64`, acquire bit `1`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.d.aq`, opcode/mask derived from `1000010----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.d.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.d.aq` with match `1000010----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.aqrl.yaml

## Purpose

`amomin.d.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN doubleword (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.d.aqrl`, and `encoding.match: 1000011----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Min, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Min`, width `64`, acquire bit `1`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.d.aqrl`, opcode/mask derived from `1000011----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.d.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.d.aqrl` with match `1000011----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.rl.yaml

## Purpose

`amomin.d.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN doubleword (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.d.rl`, and `encoding.match: 1000001----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Min, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Min`, width `64`, acquire bit `0`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.d.rl`, opcode/mask derived from `1000001----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.d.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.d.rl` with match `1000001----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.yaml

## Purpose

`amomin.d` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN doubleword` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.d`, and `encoding.match: 1000000----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Min, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Min`, width `64`, acquire bit `0`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.d`, opcode/mask derived from `1000000----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.d` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.d` with match `1000000----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.aq.yaml

## Purpose

`amomin.w.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN word (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.w.aq`, and `encoding.match: 1000010----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Min, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Min`, width `32`, acquire bit `1`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.w.aq`, opcode/mask derived from `1000010----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.w.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.w.aq` with match `1000010----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.aqrl.yaml

## Purpose

`amomin.w.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN word (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.w.aqrl`, and `encoding.match: 1000011----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Min, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Min`, width `32`, acquire bit `1`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.w.aqrl`, opcode/mask derived from `1000011----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.w.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.w.aqrl` with match `1000011----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.rl.yaml

## Purpose

`amomin.w.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN word (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.w.rl`, and `encoding.match: 1000001----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Min, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Min`, width `32`, acquire bit `0`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.w.rl`, opcode/mask derived from `1000001----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.w.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.w.rl` with match `1000001----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.yaml

## Purpose

`amomin.w` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN word` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using signed minimum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amomin.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomin.w`, and `encoding.match: 1000000----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Min, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Min`, width `32`, acquire bit `0`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomin.w`, opcode/mask derived from `1000000----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomin.w` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Min` operation (uses signed comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomin.w` with match `1000000----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Min` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomin.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.aq.yaml

## Purpose

`amominu.d.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned doubleword (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.d.aq`, and `encoding.match: 1100010----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Minu, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Minu`, width `64`, acquire bit `1`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.d.aq`, opcode/mask derived from `1100010----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.d.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.d.aq` with match `1100010----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.aqrl.yaml

## Purpose

`amominu.d.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned doubleword (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.d.aqrl`, and `encoding.match: 1100011----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Minu, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Minu`, width `64`, acquire bit `1`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.d.aqrl`, opcode/mask derived from `1100011----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.d.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.d.aqrl` with match `1100011----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.rl.yaml

## Purpose

`amominu.d.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned doubleword (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.d.rl`, and `encoding.match: 1100001----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Minu, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Minu`, width `64`, acquire bit `0`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.d.rl`, opcode/mask derived from `1100001----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.d.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.d.rl` with match `1100001----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.yaml

## Purpose

`amominu.d` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned doubleword` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.d`, and `encoding.match: 1100000----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Minu, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Minu`, width `64`, acquire bit `0`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.d`, opcode/mask derived from `1100000----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.d` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `64`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.d` with match `1100000----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.aq.yaml

## Purpose

`amominu.w.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned word (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.w.aq`, and `encoding.match: 1100010----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Minu, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Minu`, width `32`, acquire bit `1`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.w.aq`, opcode/mask derived from `1100010----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.w.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.w.aq` with match `1100010----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.aqrl.yaml

## Purpose

`amominu.w.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned word (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.w.aqrl`, and `encoding.match: 1100011----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Minu, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Minu`, width `32`, acquire bit `1`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.w.aqrl`, opcode/mask derived from `1100011----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.w.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.w.aqrl` with match `1100011----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.rl.yaml

## Purpose

`amominu.w.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned word (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.w.rl`, and `encoding.match: 1100001----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Minu, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Minu`, width `32`, acquire bit `0`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.w.rl`, opcode/mask derived from `1100001----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.w.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.w.rl` with match `1100001----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.yaml

## Purpose

`amominu.w` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MIN unsigned word` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned minimum, and store the result back to the same address. This specific variant uses `unordered` ordering and comes from `spec/std/isa/inst/Zaamo/amominu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amominu.w`, and `encoding.match: 1100000----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Minu, 1'b0, 1'b0, $encoding);`, which selects `AmoOperation::Minu`, width `32`, acquire bit `0`, and release bit `0`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (none), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amominu.w`, opcode/mask derived from `1100000----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amominu.w` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Minu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amominu.w` with match `1100000----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Minu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `unordered` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amominu.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.aq.yaml

## Purpose

`amoor.d.aq` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-or doubleword (acquire)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise OR, and store the result back to the same address. This specific variant uses `acquire` ordering and comes from `spec/std/isa/inst/Zaamo/amoor.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoor.d.aq`, and `encoding.match: 0100010----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Or, 1'b1, 1'b0, $encoding);`, which selects `AmoOperation::Or`, width `64`, acquire bit `1`, and release bit `0`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoor.d.aq`, opcode/mask derived from `0100010----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoor.d.aq` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Or` operation (computes the stored value as the loaded memory value OR the rs2 operand), the `64`-bit memory width, and acquire/release flags `1/0`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoor.d.aq` with match `0100010----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Or` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.aqrl.yaml

## Purpose

`amoor.d.aqrl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic fetch-and-or doubleword (acquire-release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the doubleword at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using bitwise OR, and store the result back to the same address. This specific variant uses `acquire-release` ordering and comes from `spec/std/isa/inst/Zaamo/amoor.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amoor.d.aqrl`, and `encoding.match: 0100011----------011-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<64>(virtual_address, X[xs2], AmoOperation::Or, 1'b1, 1'b1, $encoding);`, which selects `AmoOperation::Or`, width `64`, acquire bit `1`, and release bit `1`. `X[xs2]` is passed whole to the 64-bit AMO helper.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_acquire() before the AMO helper, memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amoor.d.aqrl`, opcode/mask derived from `0100011----------011-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: allOf` with `Zaamo` plus `xlen: 64`, so it is RV64-only. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amoor.d.aqrl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Or` operation (computes the stored value as the loaded memory value OR the rs2 operand), the `64`-bit memory width, and acquire/release flags `1/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amoor.d.aqrl` with match `0100011----------011-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Or` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `acquire-release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.aqrl.yaml -->
