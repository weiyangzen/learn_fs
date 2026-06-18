# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.c

Purpose: this file simulates selected AArch64 instructions for kprobes and uprobes when executing them from an XOL slot would produce wrong PC-relative behavior or unsafe side effects.

Important APIs: simulator functions include `simulate_adr_adrp()`, `simulate_b_bl()`, `simulate_b_cond()`, `simulate_br_blr()`, `simulate_ret()`, `simulate_cbz_cbnz()`, `simulate_tbz_tbnz()`, `simulate_ldr_literal()`, `simulate_ldrsw_literal()`, and `simulate_nop()`. Helpers read/write pt_regs, compute signed displacements, and update LR through `update_lr()`.

Control flow: each simulator decodes register fields and immediates directly from the 32-bit opcode, mutates `pt_regs`, and sets PC to the architecturally expected next address or branch target. Branch-with-link and branch-register-with-link call `update_lr()`. Returns call `simulate_ret()`. Conditional branch simulators evaluate pstate or register bits before choosing fallthrough versus target. Literal loads read from the original instruction address plus displacement and write the target general register.

State and integration: state is entirely in `pt_regs` plus current-task guarded control stack state. When GCS is enabled for EL0, link updates push to user GCS and returns pop/validate it, forcing `SIGSEGV` on mismatch or access errors. The simulator is selected by `decode-insn.c` and invoked by `kprobes.c`/`uprobes.c`.

Risks: simulator correctness is ABI-critical; off-by-one displacement or register-width mistakes change user/kernel control flow. Literal load simulation dereferences original kernel text/data addresses for kprobes. GCS interactions can intentionally signal user tasks if a simulated call/return violates shadow-stack expectations.

Test signals: probe tests on ADR/ADRP, branches, BL/BLR, RET, CBZ/CBNZ, TBZ/TBNZ, LDR literal, and NOP. GCS-enabled uprobe tests should validate link/return shadow-stack behavior.
