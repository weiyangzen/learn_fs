# Research Group subset-b-009469

This grouped report covers the exact Zaamo and Zabha RISC-V AMO YAML descriptors assigned to subset B. Each section preserves the original source path in the title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.rl.yaml

## Purpose

`amoor.d.rl.yaml` describes `amoor.d.rl`, atomic fetch-and-or doubleword (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoor.d.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0100001----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x4200302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Or`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoor.d.rl` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then ORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Or`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoor.d.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoor.d.rl` is emitted with match `0100001----------011-----0101111`, opcode `0x4200302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoor.d.rl`, include operation-specific checks for `Or` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.yaml

## Purpose

`amoor.d.yaml` describes `amoor.d`, atomic fetch-and-or doubleword, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoor.d`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0100000----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x4000302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Or`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoor.d` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then ORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Or`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoor.d` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoor.d` is emitted with match `0100000----------011-----0101111`, opcode `0x4000302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoor.d`, include operation-specific checks for `Or` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.aq.yaml

## Purpose

`amoor.w.aq.yaml` describes `amoor.w.aq`, atomic fetch-and-or word (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoor.w.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0100010----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x4400202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Or`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoor.w.aq` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then ORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Or`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoor.w.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoor.w.aq` is emitted with match `0100010----------010-----0101111`, opcode `0x4400202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoor.w.aq`, include operation-specific checks for `Or` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.aqrl.yaml

## Purpose

`amoor.w.aqrl.yaml` describes `amoor.w.aqrl`, atomic fetch-and-or word (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoor.w.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0100011----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x4600202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Or`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoor.w.aqrl` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then ORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Or`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoor.w.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoor.w.aqrl` is emitted with match `0100011----------010-----0101111`, opcode `0x4600202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoor.w.aqrl`, include operation-specific checks for `Or` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.rl.yaml

## Purpose

`amoor.w.rl.yaml` describes `amoor.w.rl`, atomic fetch-and-or word (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoor.w.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0100001----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x4200202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Or`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoor.w.rl` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then ORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Or`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoor.w.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoor.w.rl` is emitted with match `0100001----------010-----0101111`, opcode `0x4200202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoor.w.rl`, include operation-specific checks for `Or` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.yaml

## Purpose

`amoor.w.yaml` describes `amoor.w`, atomic fetch-and-or word, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoor.w`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0100000----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x4000202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Or`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoor.w` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then ORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Or`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoor.w` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoor.w` is emitted with match `0100000----------010-----0101111`, opcode `0x4000202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoor.w`, include operation-specific checks for `Or` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoor.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.aq.yaml

## Purpose

`amoswap.d.aq.yaml` describes `amoswap.d.aq`, atomic swap doubleword (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.d.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000110----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0c00302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Swap`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.d.aq` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Swap`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.d.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.d.aq` is emitted with match `0000110----------011-----0101111`, opcode `0x0c00302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.d.aq`, include operation-specific checks for `Swap` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.aqrl.yaml

## Purpose

`amoswap.d.aqrl.yaml` describes `amoswap.d.aqrl`, atomic swap doubleword (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.d.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000111----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0e00302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Swap`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.d.aqrl` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Swap`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.d.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.d.aqrl` is emitted with match `0000111----------011-----0101111`, opcode `0x0e00302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.d.aqrl`, include operation-specific checks for `Swap` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.rl.yaml

## Purpose

`amoswap.d.rl.yaml` describes `amoswap.d.rl`, atomic swap doubleword (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.d.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000101----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0a00302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Swap`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.d.rl` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Swap`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.d.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.d.rl` is emitted with match `0000101----------011-----0101111`, opcode `0x0a00302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.d.rl`, include operation-specific checks for `Swap` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.yaml

## Purpose

`amoswap.d.yaml` describes `amoswap.d`, atomic swap doubleword, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.d`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000100----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0800302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Swap`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.d` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Swap`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.d` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.d` is emitted with match `0000100----------011-----0101111`, opcode `0x0800302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.d`, include operation-specific checks for `Swap` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.aq.yaml

## Purpose

`amoswap.w.aq.yaml` describes `amoswap.w.aq`, atomic swap word (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.w.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000110----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0c00202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Swap`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.w.aq` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Swap`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.w.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.w.aq` is emitted with match `0000110----------010-----0101111`, opcode `0x0c00202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.w.aq`, include operation-specific checks for `Swap` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.aqrl.yaml

## Purpose

`amoswap.w.aqrl.yaml` describes `amoswap.w.aqrl`, atomic swap word (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.w.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000111----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0e00202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Swap`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.w.aqrl` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Swap`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.w.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.w.aqrl` is emitted with match `0000111----------010-----0101111`, opcode `0x0e00202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.w.aqrl`, include operation-specific checks for `Swap` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.rl.yaml

## Purpose

`amoswap.w.rl.yaml` describes `amoswap.w.rl`, atomic swap word (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.w.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000101----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0a00202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Swap`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.w.rl` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Swap`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.w.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.w.rl` is emitted with match `0000101----------010-----0101111`, opcode `0x0a00202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.w.rl`, include operation-specific checks for `Swap` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.yaml

## Purpose

`amoswap.w.yaml` describes `amoswap.w`, atomic swap word, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoswap.w`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000100----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0800202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Swap`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoswap.w` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then stores the source operand as the new memory value. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Swap`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoswap.w` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoswap.w` is emitted with match `0000100----------010-----0101111`, opcode `0x0800202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoswap.w`, include operation-specific checks for `Swap` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoswap.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.aq.yaml

## Purpose

`amoxor.d.aq.yaml` describes `amoxor.d.aq`, atomic fetch-and-xor doubleword (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.d.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010010----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2400302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Xor`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.d.aq` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Xor`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.d.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.d.aq` is emitted with match `0010010----------011-----0101111`, opcode `0x2400302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.d.aq`, include operation-specific checks for `Xor` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.aqrl.yaml

## Purpose

`amoxor.d.aqrl.yaml` describes `amoxor.d.aqrl`, atomic fetch-and-xor doubleword (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.d.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010011----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2600302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Xor`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.d.aqrl` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Xor`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.d.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.d.aqrl` is emitted with match `0010011----------011-----0101111`, opcode `0x2600302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.d.aqrl`, include operation-specific checks for `Xor` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.rl.yaml

## Purpose

`amoxor.d.rl.yaml` describes `amoxor.d.rl`, atomic fetch-and-xor doubleword (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.d.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010001----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2200302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Xor`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.d.rl` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Xor`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.d.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.d.rl` is emitted with match `0010001----------011-----0101111`, opcode `0x2200302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.d.rl`, include operation-specific checks for `Xor` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.yaml

## Purpose

`amoxor.d.yaml` describes `amoxor.d`, atomic fetch-and-xor doubleword, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a doubleword atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.d`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010000----------011-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2000302f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo` and `xlen: 64`. The operation semantics use width `64` bits, source slice `X[xs2]`, operation `Xor`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.d` loads the doubleword at address `X[xs1]`, writes the loaded doubleword into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<64>` with `X[xs2]`, `AmoOperation::Xor`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.d` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. Doubleword form is RV64-only, so losing the `xlen: 64` gate would let the descriptor name survive generation while target semantics are invalid on RV32. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.d` is emitted with match `0010000----------011-----0101111`, opcode `0x2000302f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.d`, include operation-specific checks for `Xor` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.d.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.aq.yaml

## Purpose

`amoxor.w.aq.yaml` describes `amoxor.w.aq`, atomic fetch-and-xor word (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.w.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010010----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2400202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Xor`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.w.aq` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Xor`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.w.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.w.aq` is emitted with match `0010010----------010-----0101111`, opcode `0x2400202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.w.aq`, include operation-specific checks for `Xor` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.aqrl.yaml

## Purpose

`amoxor.w.aqrl.yaml` describes `amoxor.w.aqrl`, atomic fetch-and-xor word (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.w.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010011----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2600202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Xor`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.w.aqrl` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Xor`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.w.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.w.aqrl` is emitted with match `0010011----------010-----0101111`, opcode `0x2600202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.w.aqrl`, include operation-specific checks for `Xor` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.rl.yaml

## Purpose

`amoxor.w.rl.yaml` describes `amoxor.w.rl`, atomic fetch-and-xor word (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.w.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010001----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2200202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Xor`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.w.rl` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Xor`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.w.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.w.rl` is emitted with match `0010001----------010-----0101111`, opcode `0x2200202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.w.rl`, include operation-specific checks for `Xor` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.yaml

## Purpose

`amoxor.w.yaml` describes `amoxor.w`, atomic fetch-and-xor word, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a word atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoxor.w`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010000----------010-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2000202f` and opcode mask `0xfe00707f`. `definedBy` requires `Zaamo`. The operation semantics use width `32` bits, source slice `X[xs2][31:0]`, operation `Xor`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoxor.w` loads the word at address `X[xs1]`, writes the sign-extended loaded word into `xd`, then XORs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<32>` with `X[xs2][31:0]`, `AmoOperation::Xor`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoxor.w` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zaamo` while the executable operation checks extension `A`, matching the base atomic extension gating used by these Zaamo AMO descriptors. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoxor.w` is emitted with match `0010000----------010-----0101111`, opcode `0x2000202f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoxor.w`, include operation-specific checks for `Xor` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoxor.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.aq.yaml

## Purpose

`amoadd.b.aq.yaml` describes `amoadd.b.aq`, atomic fetch-and-add byte (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.b.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000010----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0400002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `Add`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.b.aq` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::Add`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.b.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.b.aq` is emitted with match `0000010----------000-----0101111`, opcode `0x0400002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.b.aq`, include operation-specific checks for `Add` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.aqrl.yaml

## Purpose

`amoadd.b.aqrl.yaml` describes `amoadd.b.aqrl`, atomic fetch-and-add byte (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.b.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000011----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0600002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `Add`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.b.aqrl` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::Add`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.b.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.b.aqrl` is emitted with match `0000011----------000-----0101111`, opcode `0x0600002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.b.aqrl`, include operation-specific checks for `Add` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.rl.yaml

## Purpose

`amoadd.b.rl.yaml` describes `amoadd.b.rl`, atomic fetch-and-add byte (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.b.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000001----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0200002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `Add`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.b.rl` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::Add`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.b.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.b.rl` is emitted with match `0000001----------000-----0101111`, opcode `0x0200002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.b.rl`, include operation-specific checks for `Add` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.yaml

## Purpose

`amoadd.b.yaml` describes `amoadd.b`, atomic fetch-and-add byte, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.b`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000000----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0000002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `Add`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.b` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::Add`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.b` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.b` is emitted with match `0000000----------000-----0101111`, opcode `0x0000002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.b`, include operation-specific checks for `Add` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.aq.yaml

## Purpose

`amoadd.h.aq.yaml` describes `amoadd.h.aq`, atomic fetch-and-add halfword (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.h.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000010----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0400102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `Add`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.h.aq` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::Add`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.h.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.h.aq` is emitted with match `0000010----------001-----0101111`, opcode `0x0400102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.h.aq`, include operation-specific checks for `Add` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.aqrl.yaml

## Purpose

`amoadd.h.aqrl.yaml` describes `amoadd.h.aqrl`, atomic fetch-and-add halfword (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.h.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000011----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0600102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `Add`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.h.aqrl` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::Add`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.h.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.h.aqrl` is emitted with match `0000011----------001-----0101111`, opcode `0x0600102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.h.aqrl`, include operation-specific checks for `Add` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.rl.yaml

## Purpose

`amoadd.h.rl.yaml` describes `amoadd.h.rl`, atomic fetch-and-add halfword (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.h.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000001----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0200102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `Add`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.h.rl` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::Add`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.h.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.h.rl` is emitted with match `0000001----------001-----0101111`, opcode `0x0200102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.h.rl`, include operation-specific checks for `Add` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.yaml

## Purpose

`amoadd.h.yaml` describes `amoadd.h`, atomic fetch-and-add halfword, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoadd.h`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0000000----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x0000102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `Add`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoadd.h` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then adds the source operand to the loaded memory value and stores the low-width sum. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::Add`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoadd.h` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoadd.h` is emitted with match `0000000----------001-----0101111`, opcode `0x0000102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoadd.h`, include operation-specific checks for `Add` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoadd.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.aq.yaml

## Purpose

`amoand.b.aq.yaml` describes `amoand.b.aq`, atomic fetch-and-and byte (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.b.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110010----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6400002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `And`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.b.aq` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::And`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.b.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.b.aq` is emitted with match `0110010----------000-----0101111`, opcode `0x6400002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.b.aq`, include operation-specific checks for `And` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.aqrl.yaml

## Purpose

`amoand.b.aqrl.yaml` describes `amoand.b.aqrl`, atomic fetch-and-and byte (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.b.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110011----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6600002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `And`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.b.aqrl` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::And`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.b.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.b.aqrl` is emitted with match `0110011----------000-----0101111`, opcode `0x6600002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.b.aqrl`, include operation-specific checks for `And` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.rl.yaml

## Purpose

`amoand.b.rl.yaml` describes `amoand.b.rl`, atomic fetch-and-and byte (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.b.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110001----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6200002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `And`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.b.rl` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::And`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.b.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.b.rl` is emitted with match `0110001----------000-----0101111`, opcode `0x6200002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.b.rl`, include operation-specific checks for `And` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.yaml

## Purpose

`amoand.b.yaml` describes `amoand.b`, atomic fetch-and-and byte, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.b`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110000----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6000002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `And`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.b` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<8>` with `X[xs2][7:0]`, `AmoOperation::And`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.b` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.b` is emitted with match `0110000----------000-----0101111`, opcode `0x6000002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.b`, include operation-specific checks for `And` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.aq.yaml

## Purpose

`amoand.h.aq.yaml` describes `amoand.h.aq`, atomic fetch-and-and halfword (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.h.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110010----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6400102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `And`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.h.aq` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::And`, aq=`1`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.h.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.h.aq` is emitted with match `0110010----------001-----0101111`, opcode `0x6400102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.h.aq`, include operation-specific checks for `And` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.aqrl.yaml

## Purpose

`amoand.h.aqrl.yaml` describes `amoand.h.aqrl`, atomic fetch-and-and halfword (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.h.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110011----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6600102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `And`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.h.aqrl` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::And`, aq=`1`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.h.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.h.aqrl` is emitted with match `0110011----------001-----0101111`, opcode `0x6600102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.h.aqrl`, include operation-specific checks for `And` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.rl.yaml

## Purpose

`amoand.h.rl.yaml` describes `amoand.h.rl`, atomic fetch-and-and halfword (release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.h.rl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110001----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6200102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `And`, aq bit `0`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.h.rl` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::And`, aq=`0`, rl=`1`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.h.rl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.h.rl` is emitted with match `0110001----------001-----0101111`, opcode `0x6200102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.h.rl`, include operation-specific checks for `And` and memory-order bits aq=`0`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.yaml

## Purpose

`amoand.h.yaml` describes `amoand.h`, atomic fetch-and-and halfword, for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a halfword atomic read-modify-write instruction with unordered ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amoand.h`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0110000----------001-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x6000102f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `16` bits, source slice `X[xs2][15:0]`, operation `And`, aq bit `0`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amoand.h` loads the halfword at address `X[xs1]`, writes the sign-extended loaded halfword into `xd`, then ANDs the source operand with the loaded memory value and stores the low-width result. The executable `operation()` block first rejects the instruction when extension `A` is not implemented or is disabled in `misa`, then applies any acquire hook, reads `X[xs1]` as the virtual address, calls `amo<16>` with `X[xs2][15:0]`, `AmoOperation::And`, aq=`0`, rl=`0`, and finally applies the release hook when present. The Sail block expands the helper into address checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, exception handling, and destination-register writeback.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amoand.h` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares a `Zabha` instruction, but the AMO operation snippets for byte/halfword add/and still check extension `A`; that mismatch is semantically important even though the current generator ignores it. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amoand.h` is emitted with match `0110000----------001-----0101111`, opcode `0x6000102f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amoand.h`, include operation-specific checks for `And` and memory-order bits aq=`0`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoand.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.aq.yaml

## Purpose

`amocas.b.aq.yaml` describes `amocas.b.aq`, atomic compare-and-swap byte (acquire), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with acquire ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amocas.b.aq`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010110----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2c00002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `CompareAndSwap`, aq bit `1`, and rl bit `0`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amocas.b.aq` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then compares the loaded memory value with `xs2` and conditionally stores the replacement value from `xd`. The executable `operation()` block checks `implemented?(ExtensionName::Zabha)`, applies acquire memory-order hooks, computes `virtual_address = X[xs1]`, and then leaves the actual compare-and-swap helper call commented out behind `# TODO`. The Sail block is the complete reference behavior: translate the address, read the memory value, compare it with `xs2`, write the replacement from `rd` only on success, and always return the loaded value in `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amocas.b.aq` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zabha` and the compare-and-swap operation checks `Zabha`, but the helper is still TODO-commented in the executable operation text. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amocas.b.aq` is emitted with match `0010110----------000-----0101111`, opcode `0x2c00002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amocas.b.aq`, include operation-specific checks for `CompareAndSwap` and memory-order bits aq=`1`/rl=`0`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.aqrl.yaml

## Purpose

`amocas.b.aqrl.yaml` describes `amocas.b.aqrl`, atomic compare-and-swap byte (acquire-release), for syzkaller's riscv64 ifuzz instruction corpus imported from riscv-unified-db YAML. It is declarative instruction metadata, not executable Go: the durable payload is the mnemonic, assembly form `xd, xs2, (xs1)`, access policy, fixed RISC-V AMO encoding bits, operand bit ranges, and embedded reference semantics for a byte atomic read-modify-write instruction with acquire-release ordering.

## Important APIs, Types, and Functions

The schema-facing fields are `$schema: inst_schema.json#`, `kind: instruction`, `name: amocas.b.aqrl`, `assembly: xd, xs2, (xs1)`, `encoding.match: 0010111----------000-----0101111`, and three variable operand fields: `xs2` at bits 24-20, `xs1` at bits 19-15, and `xd` at bits 11-7. The match string fixes 17 bits; `gen.go` turns it into opcode `0x2e00002f` and opcode mask `0xfe00707f`. `definedBy` requires `Zabha`. The operation semantics use width `8` bits, source slice `X[xs2][7:0]`, operation `CompareAndSwap`, aq bit `1`, and rl bit `1`. The embedded Sail helper names include `extension`, `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, `mem_write_value`, `handle_mem_exception`, `RETIRE_SUCCESS`, and `RETIRE_FAIL`.

## Control Flow

Generation flow is uniform across this directory. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` walks YAML files, unmarshals a narrow `instYAML`, skips non-instruction records and non-32-bit match strings, computes opcode/mask from fixed `0`/`1` bits, expands the variable ranges through `parseLocations` and `parseRange`, derives `Priv` only from `access.u` or `access.vu`, and serializes the resulting `riscv64.Insn` table. `gen.go` consumes only the instruction kind, name, 32-bit encoding match string, variable field locations, and `access.u`/`access.vu` privilege hints; the description, `operation()` body, Sail block, and `definedBy` details are retained as source semantics but do not affect the generated fuzzing table.

At architectural-semantics level, `amocas.b.aqrl` loads the byte at address `X[xs1]`, writes the sign-extended loaded byte into `xd`, then compares the loaded memory value with `xs2` and conditionally stores the replacement value from `xd`. The executable `operation()` block checks `implemented?(ExtensionName::Zabha)`, applies acquire-release memory-order hooks, computes `virtual_address = X[xs1]`, and then leaves the actual compare-and-swap helper call commented out behind `# TODO`. The Sail block is the complete reference behavior: translate the address, read the memory value, compare it with `xs2`, write the replacement from `rd` only on success, and always return the loaded value in `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent repository effect is indirect: when the generator is run, `amocas.b.aqrl` becomes an immutable entry in the generated riscv64 instruction table, normally under `pkg/ifuzz/riscv64/generated`, with `AsUInt32` seeded from the opcode and `Fields` describing the three register operands. Architectural state mentioned by the semantics is external to the YAML and generator: integer registers, memory, exception state, address-translation state, and memory-ordering effects are modeled by the reference operation text or downstream simulators rather than by syzkaller's YAML loader.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema and on syzkaller's local generator at `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The generator depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` `Insn`/`InsnField` model. Downstream integration is through generated instruction registration, encode/decode fuzzing, and any assembler/disassembler tests that expect `xd, xs2, (xs1)` to match the declared bit ranges.

## Risks and Edge Cases

Because access is `s/u/vs/vu: always`, `gen.go` marks the generated `Insn.Priv` flag false. Any future privilege restriction must change the access fields, not only prose or semantic text. The source declares `Zabha` and the compare-and-swap operation checks `Zabha`, but the helper is still TODO-commented in the executable operation text. This form is not gated by `xlen: 64`; width handling depends on the funct3 bits and the semantic helper width. The encoding is sensitive to funct7 aq/rl bits and funct3 width bits; a single fixed-bit drift can alias another AMO variant while still producing a valid 32-bit table entry. The generator ignores most semantic fields, so a stale Sail block, TODO operation helper, wrong `definedBy`, or wrong acquire/release hook will not be caught by table generation alone. AMO semantics also depend on sign-extension of subword and word return values, exception ordering around address translation and memory access, and correct no-write behavior for failed compare-and-swap.

## Test Signals

Useful generator checks assert that `amocas.b.aqrl` is emitted with match `0010111----------000-----0101111`, opcode `0x2e00002f`, mask `0xfe00707f`, and fields `xs2:24-20`, `xs1:19-15`, `xd:11-7`. Encode/decode round trips should randomize only those variable register fields and verify that all fixed bits remain intact. Semantic regression coverage should compare unordered, aq, rl, and aqrl variants for the same operation and width; include extension gating, RV64 gating for `.d` forms, subword sign-extension for Zabha forms, faulting or misaligned addresses, and loaded-value writeback. For `amocas.b.aqrl`, include operation-specific checks for `CompareAndSwap` and memory-order bits aq=`1`/rl=`1`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.aqrl.yaml -->
