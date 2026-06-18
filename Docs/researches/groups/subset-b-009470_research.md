# subset-b-009470 research

Grouped research report for the requested Zabha RISC-V instruction YAML files. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.rl.yaml

Source facts: `amocas.b.rl` / `Atomic compare-and-swap byte (release)`; 135 lines; width `8`; ordering `release`; match `0010101----------000-----0101111`.

## Purpose
Defines `amocas.b.rl`, a Zabha narrow atomic compare-and-swap instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010101----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.b.rl`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas8(..., X[xs2][7:0], X[xd][7:0], aq=0, rl=1, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.b.rl`. The 32-bit match string yields opcode-family bits `0010101`, aq/rl encoding bits `01` (release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `release` ordering, calls `memory_model_release()` after the atomic helper; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded byte with the low 8 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.b.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010101----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=0 and rl=1 semantics encoded through the memory calls.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.yaml

Source facts: `amocas.b` / `Atomic compare-and-swap byte`; 133 lines; width `8`; ordering `unordered`; match `0010100----------000-----0101111`.

## Purpose
Defines `amocas.b`, a Zabha narrow atomic compare-and-swap instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010100----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.b`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas8(..., X[xs2][7:0], X[xd][7:0], aq=0, rl=0, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.b`. The 32-bit match string yields opcode-family bits `0010100`, aq/rl encoding bits `00` (unordered), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `unordered` ordering, does not call the acquire or release memory-model hooks; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded byte with the low 8 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.b` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010100----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=0 and rl=0 semantics encoded through the memory calls.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aq.yaml

Source facts: `amocas.h.aq` / `Atomic compare-and-swap halfword (acquire)`; 135 lines; width `16`; ordering `acquire`; match `0010110----------001-----0101111`.

## Purpose
Defines `amocas.h.aq`, a Zabha narrow atomic compare-and-swap instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010110----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.h.aq`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas16(..., X[xs2][15:0], X[xd][15:0], aq=1, rl=0, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.h.aq`. The 32-bit match string yields opcode-family bits `0010110`, aq/rl encoding bits `10` (acquire), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded halfword with the low 16 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.h.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010110----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=1 and rl=0 semantics encoded through the memory calls.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aqrl.yaml

Source facts: `amocas.h.aqrl` / `Atomic compare-and-swap halfword (acquire-release)`; 137 lines; width `16`; ordering `acquire-release`; match `0010111----------001-----0101111`.

## Purpose
Defines `amocas.h.aqrl`, a Zabha narrow atomic compare-and-swap instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010111----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.h.aqrl`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas16(..., X[xs2][15:0], X[xd][15:0], aq=1, rl=1, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.h.aqrl`. The 32-bit match string yields opcode-family bits `0010111`, aq/rl encoding bits `11` (acquire-release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded halfword with the low 16 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.h.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010111----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=1 and rl=1 semantics encoded through the memory calls.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.rl.yaml

Source facts: `amocas.h.rl` / `Atomic compare-and-swap halfword (release)`; 135 lines; width `16`; ordering `release`; match `0010101----------001-----0101111`.

## Purpose
Defines `amocas.h.rl`, a Zabha narrow atomic compare-and-swap instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010101----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.h.rl`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas16(..., X[xs2][15:0], X[xd][15:0], aq=0, rl=1, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.h.rl`. The 32-bit match string yields opcode-family bits `0010101`, aq/rl encoding bits `01` (release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `release` ordering, calls `memory_model_release()` after the atomic helper; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded halfword with the low 16 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.h.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010101----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=0 and rl=1 semantics encoded through the memory calls.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.yaml

Source facts: `amocas.h` / `Atomic compare-and-swap halfword`; 133 lines; width `16`; ordering `unordered`; match `0010100----------001-----0101111`.

## Purpose
Defines `amocas.h`, a Zabha narrow atomic compare-and-swap instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0010100----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amocas.h`, binds it to extension `Zabha`, and describes a CAS operation over `X[xs1]`. The executable pseudocode currently checks `implemented?(ExtensionName::Zabha)`, derives `virtual_address = X[xs1]`, and leaves the real helper call commented as `amocas16(..., X[xs2][15:0], X[xd][15:0], aq=0, rl=0, $encoding)`.
For the current ifuzz generator, this source contributes one generated instruction template named `amocas.h`. The 32-bit match string yields opcode-family bits `0010100`, aq/rl encoding bits `00` (unordered), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject when Zabha is not implemented; for `unordered` ordering, does not call the acquire or release memory-model hooks; obtain the memory address from `xs1`; then the intended CAS helper would compare the loaded halfword with the low 16 bits of `xs2`, write the replacement value from `xd` on success, and return the loaded value in `xd` sign-extended. The embedded Sail block is more complete: it resolves and translates the data address, announces the write effective address, reads the memory value, compares it to `rs2_val`, conditionally writes `rd_val`, writes the loaded value back to `X(rd)`, and routes memory exceptions through the Sail exception handlers.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main risk is semantic incompleteness: `operation()` still contains `# TODO` and the helper call is commented, so any consumer that executes the operation DSL would not model the CAS side effect. A second risk is wording drift: the description mentions writing `xs2+1`, while the commented operation and Sail block use `xd`/`rd` as the replacement source. That mismatch should be resolved against the authoritative ISA source before relying on these comments for test generation.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amocas.h` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0010100----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `Zabha`, not the base A gate, which matches the source directory and `definedBy` extension. It uses `mem_read`/`mem_write_value` with aq=0 and rl=0 semantics encoded through the memory calls.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amocas.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.aq.yaml

Source facts: `amomax.b.aq` / `Atomic MAX byte (acquire)`; 143 lines; width `8`; ordering `acquire`; match `1010010----------000-----0101111`.

## Purpose
Defines `amomax.b.aq`, a Zabha narrow atomic signed maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010010----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.b.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Max, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.b.aq`. The 32-bit match string yields opcode-family bits `1010010`, aq/rl encoding bits `10` (acquire), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.b.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010010----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.aqrl.yaml

Source facts: `amomax.b.aqrl` / `Atomic MAX byte (acquire-release)`; 145 lines; width `8`; ordering `acquire-release`; match `1010011----------000-----0101111`.

## Purpose
Defines `amomax.b.aqrl`, a Zabha narrow atomic signed maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010011----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.b.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Max, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.b.aqrl`. The 32-bit match string yields opcode-family bits `1010011`, aq/rl encoding bits `11` (acquire-release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.b.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010011----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.rl.yaml

Source facts: `amomax.b.rl` / `Atomic MAX byte (release)`; 143 lines; width `8`; ordering `release`; match `1010001----------000-----0101111`.

## Purpose
Defines `amomax.b.rl`, a Zabha narrow atomic signed maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010001----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.b.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Max, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.b.rl`. The 32-bit match string yields opcode-family bits `1010001`, aq/rl encoding bits `01` (release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.b.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010001----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.yaml

Source facts: `amomax.b` / `Atomic MAX byte`; 141 lines; width `8`; ordering `unordered`; match `1010000----------000-----0101111`.

## Purpose
Defines `amomax.b`, a Zabha narrow atomic signed maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010000----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.b`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Max, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.b`. The 32-bit match string yields opcode-family bits `1010000`, aq/rl encoding bits `00` (unordered), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.b` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010000----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.aq.yaml

Source facts: `amomax.h.aq` / `Atomic MAX halfword (acquire)`; 143 lines; width `16`; ordering `acquire`; match `1010010----------001-----0101111`.

## Purpose
Defines `amomax.h.aq`, a Zabha narrow atomic signed maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010010----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.h.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Max, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.h.aq`. The 32-bit match string yields opcode-family bits `1010010`, aq/rl encoding bits `10` (acquire), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.h.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010010----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.aqrl.yaml

Source facts: `amomax.h.aqrl` / `Atomic MAX halfword (acquire-release)`; 145 lines; width `16`; ordering `acquire-release`; match `1010011----------001-----0101111`.

## Purpose
Defines `amomax.h.aqrl`, a Zabha narrow atomic signed maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010011----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.h.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Max, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.h.aqrl`. The 32-bit match string yields opcode-family bits `1010011`, aq/rl encoding bits `11` (acquire-release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.h.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010011----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.rl.yaml

Source facts: `amomax.h.rl` / `Atomic MAX halfword (release)`; 143 lines; width `16`; ordering `release`; match `1010001----------001-----0101111`.

## Purpose
Defines `amomax.h.rl`, a Zabha narrow atomic signed maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010001----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.h.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Max, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.h.rl`. The 32-bit match string yields opcode-family bits `1010001`, aq/rl encoding bits `01` (release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.h.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010001----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.yaml

Source facts: `amomax.h` / `Atomic MAX halfword`; 141 lines; width `16`; ordering `unordered`; match `1010000----------001-----0101111`.

## Purpose
Defines `amomax.h`, a Zabha narrow atomic signed maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1010000----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomax.h`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Max, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomax.h`. The 32-bit match string yields opcode-family bits `1010000`, aq/rl encoding bits `00` (unordered), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomax.h` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1010000----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed maximum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomax.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.aq.yaml

Source facts: `amomaxu.b.aq` / `Atomic MAX unsigned byte (acquire)`; 143 lines; width `8`; ordering `acquire`; match `1110010----------000-----0101111`.

## Purpose
Defines `amomaxu.b.aq`, a Zabha narrow atomic unsigned maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110010----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.b.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Maxu, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.b.aq`. The 32-bit match string yields opcode-family bits `1110010`, aq/rl encoding bits `10` (acquire), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.b.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110010----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.aqrl.yaml

Source facts: `amomaxu.b.aqrl` / `Atomic MAX unsigned byte (acquire-release)`; 145 lines; width `8`; ordering `acquire-release`; match `1110011----------000-----0101111`.

## Purpose
Defines `amomaxu.b.aqrl`, a Zabha narrow atomic unsigned maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110011----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.b.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Maxu, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.b.aqrl`. The 32-bit match string yields opcode-family bits `1110011`, aq/rl encoding bits `11` (acquire-release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.b.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110011----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.rl.yaml

Source facts: `amomaxu.b.rl` / `Atomic MAX unsigned byte (release)`; 143 lines; width `8`; ordering `release`; match `1110001----------000-----0101111`.

## Purpose
Defines `amomaxu.b.rl`, a Zabha narrow atomic unsigned maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110001----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.b.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Maxu, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.b.rl`. The 32-bit match string yields opcode-family bits `1110001`, aq/rl encoding bits `01` (release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.b.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110001----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.yaml

Source facts: `amomaxu.b` / `Atomic MAX unsigned byte`; 141 lines; width `8`; ordering `unordered`; match `1110000----------000-----0101111`.

## Purpose
Defines `amomaxu.b`, a Zabha narrow atomic unsigned maximum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110000----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.b`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Maxu, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.b`. The 32-bit match string yields opcode-family bits `1110000`, aq/rl encoding bits `00` (unordered), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.b` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110000----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.aq.yaml

Source facts: `amomaxu.h.aq` / `Atomic MAX unsigned halfword (acquire)`; 143 lines; width `16`; ordering `acquire`; match `1110010----------001-----0101111`.

## Purpose
Defines `amomaxu.h.aq`, a Zabha narrow atomic unsigned maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110010----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.h.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Maxu, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.h.aq`. The 32-bit match string yields opcode-family bits `1110010`, aq/rl encoding bits `10` (acquire), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.h.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110010----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.aqrl.yaml

Source facts: `amomaxu.h.aqrl` / `Atomic MAX unsigned halfword (acquire-release)`; 145 lines; width `16`; ordering `acquire-release`; match `1110011----------001-----0101111`.

## Purpose
Defines `amomaxu.h.aqrl`, a Zabha narrow atomic unsigned maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110011----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.h.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Maxu, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.h.aqrl`. The 32-bit match string yields opcode-family bits `1110011`, aq/rl encoding bits `11` (acquire-release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.h.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110011----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.rl.yaml

Source facts: `amomaxu.h.rl` / `Atomic MAX unsigned halfword (release)`; 143 lines; width `16`; ordering `release`; match `1110001----------001-----0101111`.

## Purpose
Defines `amomaxu.h.rl`, a Zabha narrow atomic unsigned maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110001----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.h.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Maxu, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.h.rl`. The 32-bit match string yields opcode-family bits `1110001`, aq/rl encoding bits `01` (release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.h.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110001----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.yaml

Source facts: `amomaxu.h` / `Atomic MAX unsigned halfword`; 141 lines; width `16`; ordering `unordered`; match `1110000----------001-----0101111`.

## Purpose
Defines `amomaxu.h`, a Zabha narrow atomic unsigned maximum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1110000----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomaxu.h`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Maxu, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomaxu.h`. The 32-bit match string yields opcode-family bits `1110000`, aq/rl encoding bits `00` (unordered), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned maximum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomaxu.h` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1110000----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned maximum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomaxu.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.aq.yaml

Source facts: `amomin.b.aq` / `Atomic MIN byte (acquire)`; 143 lines; width `8`; ordering `acquire`; match `1000010----------000-----0101111`.

## Purpose
Defines `amomin.b.aq`, a Zabha narrow atomic signed minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000010----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.b.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Min, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.b.aq`. The 32-bit match string yields opcode-family bits `1000010`, aq/rl encoding bits `10` (acquire), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.b.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000010----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.aqrl.yaml

Source facts: `amomin.b.aqrl` / `Atomic MIN byte (acquire-release)`; 145 lines; width `8`; ordering `acquire-release`; match `1000011----------000-----0101111`.

## Purpose
Defines `amomin.b.aqrl`, a Zabha narrow atomic signed minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000011----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.b.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Min, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.b.aqrl`. The 32-bit match string yields opcode-family bits `1000011`, aq/rl encoding bits `11` (acquire-release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.b.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000011----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.rl.yaml

Source facts: `amomin.b.rl` / `Atomic MIN byte (release)`; 143 lines; width `8`; ordering `release`; match `1000001----------000-----0101111`.

## Purpose
Defines `amomin.b.rl`, a Zabha narrow atomic signed minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000001----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.b.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Min, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.b.rl`. The 32-bit match string yields opcode-family bits `1000001`, aq/rl encoding bits `01` (release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.b.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000001----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.yaml

Source facts: `amomin.b` / `Atomic MIN byte`; 141 lines; width `8`; ordering `unordered`; match `1000000----------000-----0101111`.

## Purpose
Defines `amomin.b`, a Zabha narrow atomic signed minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000000----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.b`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Min, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.b`. The 32-bit match string yields opcode-family bits `1000000`, aq/rl encoding bits `00` (unordered), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.b` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000000----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.aq.yaml

Source facts: `amomin.h.aq` / `Atomic MIN halfword (acquire)`; 143 lines; width `16`; ordering `acquire`; match `1000010----------001-----0101111`.

## Purpose
Defines `amomin.h.aq`, a Zabha narrow atomic signed minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000010----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.h.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Min, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.h.aq`. The 32-bit match string yields opcode-family bits `1000010`, aq/rl encoding bits `10` (acquire), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.h.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000010----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.aqrl.yaml

Source facts: `amomin.h.aqrl` / `Atomic MIN halfword (acquire-release)`; 145 lines; width `16`; ordering `acquire-release`; match `1000011----------001-----0101111`.

## Purpose
Defines `amomin.h.aqrl`, a Zabha narrow atomic signed minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000011----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.h.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Min, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.h.aqrl`. The 32-bit match string yields opcode-family bits `1000011`, aq/rl encoding bits `11` (acquire-release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.h.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000011----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.rl.yaml

Source facts: `amomin.h.rl` / `Atomic MIN halfword (release)`; 143 lines; width `16`; ordering `release`; match `1000001----------001-----0101111`.

## Purpose
Defines `amomin.h.rl`, a Zabha narrow atomic signed minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000001----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.h.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Min, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.h.rl`. The 32-bit match string yields opcode-family bits `1000001`, aq/rl encoding bits `01` (release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.h.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000001----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.yaml

Source facts: `amomin.h` / `Atomic MIN halfword`; 141 lines; width `16`; ordering `unordered`; match `1000000----------001-----0101111`.

## Purpose
Defines `amomin.h`, a Zabha narrow atomic signed minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1000000----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amomin.h`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Min, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amomin.h`. The 32-bit match string yields opcode-family bits `1000000`, aq/rl encoding bits `00` (unordered), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `signed minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amomin.h` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1000000----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `signed minimum` through the AMO operation match. For this instruction, uses signed comparison after sign-extending the loaded byte/halfword and the xs2 operand.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amomin.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.aq.yaml

Source facts: `amominu.b.aq` / `Atomic MIN unsigned byte (acquire)`; 143 lines; width `8`; ordering `acquire`; match `1100010----------000-----0101111`.

## Purpose
Defines `amominu.b.aq`, a Zabha narrow atomic unsigned minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100010----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.b.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Minu, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.b.aq`. The 32-bit match string yields opcode-family bits `1100010`, aq/rl encoding bits `10` (acquire), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.b.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100010----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.aqrl.yaml

Source facts: `amominu.b.aqrl` / `Atomic MIN unsigned byte (acquire-release)`; 145 lines; width `8`; ordering `acquire-release`; match `1100011----------000-----0101111`.

## Purpose
Defines `amominu.b.aqrl`, a Zabha narrow atomic unsigned minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100011----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.b.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Minu, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.b.aqrl`. The 32-bit match string yields opcode-family bits `1100011`, aq/rl encoding bits `11` (acquire-release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.b.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100011----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.rl.yaml

Source facts: `amominu.b.rl` / `Atomic MIN unsigned byte (release)`; 143 lines; width `8`; ordering `release`; match `1100001----------000-----0101111`.

## Purpose
Defines `amominu.b.rl`, a Zabha narrow atomic unsigned minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100001----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.b.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Minu, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.b.rl`. The 32-bit match string yields opcode-family bits `1100001`, aq/rl encoding bits `01` (release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.b.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100001----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.yaml

Source facts: `amominu.b` / `Atomic MIN unsigned byte`; 141 lines; width `8`; ordering `unordered`; match `1100000----------000-----0101111`.

## Purpose
Defines `amominu.b`, a Zabha narrow atomic unsigned minimum instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100000----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.b`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Minu, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.b`. The 32-bit match string yields opcode-family bits `1100000`, aq/rl encoding bits `00` (unordered), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.b` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100000----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.b.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.aq.yaml

Source facts: `amominu.h.aq` / `Atomic MIN unsigned halfword (acquire)`; 143 lines; width `16`; ordering `acquire`; match `1100010----------001-----0101111`.

## Purpose
Defines `amominu.h.aq`, a Zabha narrow atomic unsigned minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100010----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.h.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Minu, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.h.aq`. The 32-bit match string yields opcode-family bits `1100010`, aq/rl encoding bits `10` (acquire), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.h.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100010----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.aqrl.yaml

Source facts: `amominu.h.aqrl` / `Atomic MIN unsigned halfword (acquire-release)`; 145 lines; width `16`; ordering `acquire-release`; match `1100011----------001-----0101111`.

## Purpose
Defines `amominu.h.aqrl`, a Zabha narrow atomic unsigned minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100011----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.h.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Minu, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.h.aqrl`. The 32-bit match string yields opcode-family bits `1100011`, aq/rl encoding bits `11` (acquire-release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.h.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100011----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.aqrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.rl.yaml

Source facts: `amominu.h.rl` / `Atomic MIN unsigned halfword (release)`; 143 lines; width `16`; ordering `release`; match `1100001----------001-----0101111`.

## Purpose
Defines `amominu.h.rl`, a Zabha narrow atomic unsigned minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100001----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.h.rl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Minu, aq=0, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.h.rl`. The 32-bit match string yields opcode-family bits `1100001`, aq/rl encoding bits `01` (release), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `release` ordering, calls `memory_model_release()` after the atomic helper; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.h.rl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100001----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.rl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.yaml

Source facts: `amominu.h` / `Atomic MIN unsigned halfword`; 141 lines; width `16`; ordering `unordered`; match `1100000----------001-----0101111`.

## Purpose
Defines `amominu.h`, a Zabha narrow atomic unsigned minimum instruction for a 16-bit halfword memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `1100000----------001-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amominu.h`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Minu, aq=0, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amominu.h`. The 32-bit match string yields opcode-family bits `1100000`, aq/rl encoding bits `00` (unordered), funct3 `001` (halfword), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `unordered` ordering, does not call the acquire or release memory-model hooks; load the address from `X[xs1]`; call `amo<16>` with the low 16 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `unsigned minimum` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded halfword, and correct aq/rl propagation with aq clear and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amominu.h` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `1100000----------001-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=0, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `unsigned minimum` through the AMO operation match. For this instruction, uses zero-extension for the comparison operand and loaded memory value, while still returning the loaded narrow value sign-extended into xd.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amominu.h.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aq.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aq.yaml

Source facts: `amoor.b.aq` / `Atomic fetch-and-or byte (acquire)`; 143 lines; width `8`; ordering `acquire`; match `0100010----------000-----0101111`.

## Purpose
Defines `amoor.b.aq`, a Zabha narrow atomic bitwise OR instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0100010----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amoor.b.aq`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Or, aq=1, rl=0, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amoor.b.aq`. The 32-bit match string yields opcode-family bits `0100010`, aq/rl encoding bits `10` (acquire), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire` ordering, calls `memory_model_acquire()` before the atomic helper; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `bitwise OR` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl clear.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amoor.b.aq` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0100010----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=0 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `bitwise OR` through the AMO operation match. For this instruction, ORs the narrow xs2 operand with the loaded byte/halfword and writes the narrow result.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aq.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aqrl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aqrl.yaml

Source facts: `amoor.b.aqrl` / `Atomic fetch-and-or byte (acquire-release)`; 145 lines; width `8`; ordering `acquire-release`; match `0100011----------000-----0101111`.

## Purpose
Defines `amoor.b.aqrl`, a Zabha narrow atomic bitwise OR instruction for a 8-bit byte memory operand. The assembly form is `xd, xs2, (xs1)` and the fixed encoding pattern is `0100011----------000-----0101111`, with `xs2` in bits 24-20, `xs1` in bits 19-15, and `xd` in bits 11-7.

## Important APIs, Types, and Fields
The YAML record exposes an `instruction` named `amoor.b.aqrl`, declares extension `Zabha`, and maps the operation to the shared AMO helper as `amo<8>(virtual_address, X[xs2][7:0], AmoOperation::Or, aq=1, rl=1, $encoding)`. The operation block checks the base atomic extension through `ExtensionName::A` and optional `CSR[misa].A`, then applies the ordering hooks required by the suffix.
For the current ifuzz generator, this source contributes one generated instruction template named `amoor.b.aqrl`. The 32-bit match string yields opcode-family bits `0100011`, aq/rl encoding bits `11` (acquire-release), funct3 `000` (byte), opcode `0101111`, and a common mask over all fixed bits; variable fields become three five-bit `InsnField` entries. Access is `s/u/vs/vu: always`, so `Priv` remains false.

## Control Flow
Control flow is: reject if the A extension gate fails; for `acquire-release` ordering, calls `memory_model_acquire()` before the atomic helper and `memory_model_release()` after it; load the address from `X[xs1]`; call `amo<8>` with the low 8 bits of `xs2`; store the helper return value in `X[xd]`. The embedded Sail reference expands that helper into effective-address validation, address translation, write-effective-address announcement, read, `bitwise OR` result calculation, write-back of the narrow result, sign-extended return of the original loaded value into `rd`, and memory-exception handling.

## State and Persistence
The YAML file has no runtime persistence of its own. Persistence is through generated Go source: after `go generate`, the opcode, mask, field layout, name, and default `AsUInt32` are stored in `generated/insns.go`. Runtime encode/decode state is transient: encoding returns the template word and decoding extracts operand values from a candidate word.

## Dependencies and Integration Points
Dependencies are the riscv-unified-db instruction schema (`inst_schema.json#`), the generated YAML layout comments, syzkaller `pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the runtime `riscv64.Insn`/`InsnField`/`Register` APIs. The embedded Sail block depends on Sail memory helpers such as `ext_data_get_addr`, `translateAddr`, `mem_write_ea`, `mem_read`, and `mem_write_value` but is not consumed by the current Go generator.
The active syzkaller integration reads only a narrow subset of this YAML: `gen/gen.go` unmarshals `kind`, `name`, `encoding.match`, `encoding.variables`, and user/virtual-user access, then emits a `riscv64.Insn` in `generated/insns.go`. `riscv64.Register` appends the generated templates to the instruction set, `Encode` serializes `AsUInt32` little-endian, and `ParseInsn` matches incoming 32-bit words with `OpcodeMask`/`Opcode` before extracting operands with `extractBits`.

## Risks and Edge Cases
The main semantic risk is extension-gate drift: the file is under `Zabha` and `definedBy.extension.name` is `Zabha`, but both the operation block and Sail block use the base A-extension gate. That may be inherited from the wider Zaamo templates; for byte/halfword AMOs it should be checked against the intended Zabha availability rules. Ifuzz generation itself ignores this semantic block, so the risk affects semantic consumers more than the current opcode table.
Additional edge cases are illegal-instruction gating, virtual-memory translation failures, access-fault propagation, exact sign-extension of the loaded byte, and correct aq/rl propagation with aq set and rl set.

## Test Signals
Useful test signals are: run `go generate ./pkg/ifuzz/riscv64` from the syzkaller module and verify `amoor.b.aqrl` appears once in `generated/insns.go`; run `go test ./pkg/ifuzz/riscv64` to cover field extraction; add a decode smoke test for a concrete word matching `0100011----------000-----0101111` that asserts operands land in `xs2`, `xs1`, and `xd`; and, for semantic consumers, compare the operation/Sail ordering behavior for aq=1, rl=1 against RISC-V Zabha conformance cases.
The Sail reference gates on extension `A` and calculates `bitwise OR` through the AMO operation match. For this instruction, ORs the narrow xs2 operand with the loaded byte/halfword and writes the narrow result.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoor.b.aqrl.yaml -->
