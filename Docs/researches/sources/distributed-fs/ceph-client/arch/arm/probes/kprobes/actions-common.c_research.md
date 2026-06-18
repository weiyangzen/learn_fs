<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-common.c

Purpose: implements common ARM/Thumb kprobe action logic for block data transfer instructions, especially LDM/STM forms that can be emulated through rewritten slots or simulated in software.

Important functions: `simulate_ldm1stm1()` interprets load/store multiple register lists, addressing modes, and writeback. `simulate_stm1_pc()` handles STM with PC in the register list using `str_pc_offset`. `simulate_ldm1_pc()` runs LDM then applies `load_write_pc()` for PC loads. `emulate_generic_r0_12_noflags()`, `emulate_generic_r2_14_noflags()`, and `emulate_ldm_r3_15()` provide fast slot execution for register ranges. `kprobe_decode_ldmstm()` chooses the best path and writes a modified instruction when possible.

Control flow: `kprobe_decode_ldmstm()` inspects the base register, register list, and load/store bit. If all operands fit one of the supported contiguous register windows, it rewrites the instruction and returns `INSN_GOOD` with an emulation handler. Otherwise it falls back to simulation, selecting special PC-aware handlers when the register list includes R15.

State and persistence: no global state. The decoder writes `asi->insn[0]` and `asi->insn_handler`; runtime handlers mutate memory, `pt_regs`, PC, and optional base-register writeback.

Dependencies and integration: included by both ARM and Thumb action paths through `core.h`; Thumb32 wraps `kprobe_decode_ldmstm()` to reorder halfwords after ARM-style rewriting.

Risks: LDM/STM addressing uses pre/post and up/down bits; off-by-one address adjustment would corrupt register restore or stack behavior. Fast emulation depends on legal register windows and must not include unsupported SP/PC combinations except where the dedicated PC load handler applies.

Test signals: ARM and Thumb test catalogs include many LDM/STM variants, stack forms, PC-loading branches, and register-list combinations, while stack checkers constrain dangerous SP stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/actions-common.c -->
