<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/module.c

## Purpose
Applies OpenRISC ELF RELA relocations while loading kernel modules.

## Important APIs, Types, And Functions
`apply_relocate_add()` handles `R_OR1K_32`, `LO_16_IN_INSN`, `HI_16_IN_INSN`, `INSN_REL_26`, `32_PCREL`, `AHI16`, and `SLO16` relocations.

## Control Flow
For each relocation, the loader finds the target location, resolves symbol value plus addend, rewrites the instruction/data word or halfword, and logs unknown relocation types.

## State And Persistence
Mutates module text/data sections before module execution. No global state.

## Dependencies And Integration Points
Depends on UAPI ELF relocation constants, module loader section layout, OpenRISC instruction encoding, and module symbol resolution.

## Risks
Unknown relocations only log an error and still return success, which can leave a broken module loaded. Halfword writes are endian/layout-sensitive. Branch relocation range is not explicitly checked.

## Test Signals
Load modules using each supported relocation type; verify unknown relocations fail expectations; run module text execution and symbol reference tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/module.c -->
