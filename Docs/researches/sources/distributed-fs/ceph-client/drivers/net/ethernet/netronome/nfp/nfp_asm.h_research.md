# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_asm.h

## Purpose
Defines the NFP microengine instruction encoding constants, register abstractions, operand conversion structures, branch/immediate helper prototypes, command target encodings, CSR constants, ECC helpers, and multiply instruction fields.

## Important APIs, Types, and Functions
- Instruction masks cover branch, branch-bit, branch-ALU, byte/ALU/shift/load-field/command/local-CSR/carb/multiply encodings.
- `nfp_is_br()` identifies branch instructions by base/mask.
- Enums define branch conditions, immediate width/shift, shift/ALU ops, command modes/context swap, local CSR write source, register types, LM modes, command target map, multiply type/step, and operand destination bank.
- `swreg` and inline constructors (`reg_a`, `reg_b`, `reg_both`, `reg_nnr`, `reg_xfer`, `reg_imm`, `reg_lm`, etc.) define a driver-internal register representation independent of operand format.
- `struct nfp_insn_ur_regs` and `struct nfp_insn_re_regs` carry converted operand encodings for unrestricted and restricted instruction forms.

## Control Flow
No runtime flow beyond inline helpers. Instruction generation code composes constants and calls `nfp_asm.c` functions declared here to produce hardware instruction words.

## State and Persistence Behavior
No state. The header is a declarative ABI/encoding contract between code generators and hardware instruction format.

## Dependencies and Integration Points
Depends on Linux bitfield, bug, and types headers. Used by NFP assembler/JIT code in the driver, especially BPF offload paths. `cmd_tgt_act[]` is exported from `nfp_asm.c`.

## Risks
Constants must exactly match NFP hardware. The `swreg` bitwise typedef helps avoid accidental raw integer misuse, but many macros still allow constructing invalid logical combinations that later conversion must reject. `__enc_swreg_lm()` only WARNs on invalid local-memory parameters.

## Test Signals
Build coverage for BPF/offload configs, static tests that instruction masks produce expected encodings, and round-trip tests for software register helpers. Hardware/JIT tests should detect wrong op fields through rejected programs or incorrect packet processing.
