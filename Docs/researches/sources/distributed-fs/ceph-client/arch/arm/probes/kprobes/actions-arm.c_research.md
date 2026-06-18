<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-arm.c

Purpose: provides ARM-mode kprobe action handlers and the `kprobes_arm_actions` dispatch table used by the common decoder to simulate or emulate supported ARM instructions.

Important functions: `emulate_ldrdstrd()`, `emulate_ldr()`, and `emulate_str()` handle extra and normal load/store forms with PC/SP/writeback fixups. `emulate_rd12rn16rm0rs8_rwflags()`, `emulate_rd12rn16rm0_rwflags_nopc()`, `emulate_rd16rn12rm0rs8_rwflags_nopc()`, `emulate_rd12rm0_noflags_nopc()`, and `emulate_rdlo12rdhi16rn0rm8_rwflags_nopc()` implement common register shuffles around an executable slot. `kprobes_arm_actions[]` maps `PROBES_*` action IDs to these handlers or shared simulators.

Control flow: each handler copies original registers into fixed ABI registers expected by rewritten slot instructions, calls `asi->insn_fn` via `BLX`, then writes results and APSR flags back into `pt_regs`. Loads to PC use `load_write_pc()`, ALU writes use `alu_write_pc()`, and stores from PC use `str_pc_offset`.

State and persistence: no global mutable state. It mutates trapped task register state (`struct pt_regs`) and uses `asi->insn_fn` and prepared instruction slots created during decode.

Dependencies and integration: includes `decode-arm.h`, `core.h`, and `checkers.h`. Exports `kprobes_arm_actions` and `kprobes_arm_checkers`, consumed by `arch_prepare_kprobe()` for non-Thumb2 kernels. It relies on shared simulators such as `simulate_blx1`, `simulate_mrs`, `simulate_bbl`, and `simulate_mov_ipsp` from ARM probe decode infrastructure.

Risks: inline assembly clobber lists and register constraints must match rewritten instruction operands. PC alignment/interworking differences across ARM versions are high risk. Incorrect writeback handling can corrupt base registers or stack.

Test signals: `test-arm.c` exercises each action class across condition codes, PC/SP operands, writeback addressing, ALU flags, multiply/media operations, branches, and supported/rejected encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-arm.c -->
