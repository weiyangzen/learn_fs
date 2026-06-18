## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/actions-arm.c

### Purpose
Implements ARM-specific uprobe decode actions for instructions that need PC substitution, writeback handling, branch simulation, or rejection before execution out of line.

### Important APIs, Types, And Functions
Key helpers are `uprobes_substitute_pc`, `uprobe_set_pc`, `uprobe_unset_pc`, `uprobe_aluwrite_pc`, `uprobe_write_pc`, `decode_pc_ro`, `decode_wb_pc`, `decode_rd12rn16rm0rs8_rwflags`, `decode_ldr`, and `uprobe_decode_ldmstm`. The exported action table is `uprobes_probes_actions[]`, mapping `PROBES_*` decode classes to simulation handlers or per-class decoders.

### Control Flow
The generic ARM probe decoder classifies an instruction and indexes `uprobes_probes_actions[]`. PC-relative instructions are rewritten in the copied XOL instruction to use a free general register; prehandlers seed that register with `ARM_pc + 8`; posthandlers restore it or route writes through `alu_write_pc`/`load_write_pc`. LDM/STM with PC in the register list is either rejected or rewritten to use LR so the posthandler can apply branch semantics.

### State, Persistence, And Dependencies
Persistent per-probe state lives in `struct arch_uprobe`: `ixol`, `pcreg`, `prehandler`, and `posthandler`. Per-task temporary state uses `struct arch_uprobe_task.backup`. Dependencies include `decode-arm.h`, `core.h`, generic `linux/uprobes.h`, ARM opcode conversion helpers, and probe simulation functions such as `simulate_bbl`.

### Integration Points
Called by `arch_uprobe_analyze_insn()` in `core.c`; its action table is the ARM uprobe policy for what can be simulated, executed in XOL, or rejected. It also integrates with ARM PC write semantics through `alu_write_pc` and `load_write_pc`.

### Risks
Incorrect free-register selection corrupts user registers. PC bias must remain ARM-state `+8`; Thumb is not supported here. LDM/STM rewriting must reject LR conflicts, or return-path behavior can be corrupted.

### Test Signals
Exercise uprobes on PC-relative loads/stores, ALU writes to PC, branches, and LDM/STM forms. Verify rejected instructions return `-EINVAL` and successful probes preserve user register state and branch destinations.
