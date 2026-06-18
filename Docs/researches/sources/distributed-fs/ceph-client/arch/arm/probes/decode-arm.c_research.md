# sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.c

Purpose: Provides the ARM-state instruction decode table and small simulation helpers for ARM kprobes/uprobes support. It maps instruction bit patterns to probe action IDs, emulation/simulation modes, register constraints, and rejection decisions.

Important APIs/functions: Simulation helpers include `simulate_bbl`, `simulate_blx1`, `simulate_blx2bx`, `simulate_mrs`, and `simulate_mov_ipsp`. The primary exported table is `probes_decode_arm_table`; `arm_probes_decode_insn()` initializes `arch_probes_insn` callbacks and delegates to the generic `probes_decode_insn()`.

Control flow: Branch simulations update `pt_regs` PC/LR/CPSR directly using ARM pipeline offsets and interworking bits. The decode tables are ordered from specific/unconditional/miscellaneous cases toward broad classes. `DECODE_REJECT`, `DECODE_SIMULATE`, `DECODE_EMULATE`, `DECODE_CUSTOM`, `DECODE_TABLE`, `DECODE_OR`, and `DECODE_*X` macros encode match masks, action IDs, and register safety constraints. The top-level table covers unconditional, miscellaneous, multiply, extra load/store, data processing, media, load/store, block transfer, branch, and rejects coprocessor/SVC classes.

State and dependencies: No persistent mutable state. It depends on `decode.h`, `decode-arm.h`, `pt_regs`, ARM PSR bits, generic condition check tables, and action/checker arrays supplied by kprobes or uprobes users.

Integration points: Used by ARM probes to decide whether an instruction can be probed, whether it needs an instruction slot, and which handler/action should execute. `arm_singlestep()` advances PC by 4 before invoking the selected handler. Under `CONFIG_ARM_KPROBES_TEST_MODULE`, the decode table is exported for tests.

Risks/tests: Table ordering is explicitly fragile because masks rely on earlier exclusions. Incorrect register constraints can allow probing instructions that corrupt PC/SP or processor state. Branch offset/interworking simulation must match ARM pipeline semantics. Tests should include the ARM kprobes test module, unsupported instruction rejection, PC/SP writeback constraints, conditional execution checks, BL/BLX/BX behavior, and decode coverage for every action enum.
