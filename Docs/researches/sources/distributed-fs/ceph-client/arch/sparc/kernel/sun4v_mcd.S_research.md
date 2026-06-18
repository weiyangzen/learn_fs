# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4v_mcd.S

Purpose: bridges sun4v precise memory-corruption-detected exceptions from assembly trap context to the C reporter.

Important APIs/symbols: defines `sun4v_mcd_detect_precise`, passes `pt_regs`, `%l4`, and `%l5` to `sun4v_mem_corrupt_detect_precise()`, then returns through `rtrap`.

Control flow: the trap frame has already been established by the trap table. The routine moves saved trap arguments into output registers, calls C with `pt_regs` at `sp + PTREGS_OFF`, and branches to normal trap return.

State and persistence: no owned state; it only forwards transient trap information.

Dependencies and integration points: depends on sun4v trap table setup, SPARC register convention used by etrap, and C MCD handling.

Risks: argument register expectations must match trap-entry code and the C function signature. It is intentionally minimal because memory corruption paths should avoid complex assembly.

Test signals: sun4v MCD fault injection or platform error simulation should invoke `sun4v_mem_corrupt_detect_precise()` with valid regs and return/terminate according to C policy.
