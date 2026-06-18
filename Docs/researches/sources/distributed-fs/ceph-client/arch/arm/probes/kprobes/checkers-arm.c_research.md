<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-arm.c

Purpose: provides ARM-mode decode checkers for stack usage and register usage metadata. These checkers run during instruction preparation after a decode-table action has matched.

Important functions: `arm_check_stack()` uses a nested decode table to classify stack effects for stores and LDM/STM. It maps normal instructions to `STACK_USE_NONE`, register-indexed stores using SP to `STACK_USE_UNKNOWN`, decrementing SP stores to fixed byte counts, and STMDX forms to register-list-derived stack usage. Register checkers include `arm_check_regs_nouse()`, `arm_check_regs_normal()`, `arm_check_regs_ldmstm()`, `arm_check_regs_mov_ip_sp()`, and `arm_check_regs_ldrdstrd()`.

Control flow: `kprobes_arm_checkers[]` chains `arm_stack_checker` and `arm_regs_checker`. The common decoder passes the matched action index into both arrays. Stack checkers may recursively call `probes_decode_insn()` on the original instruction with `stack_check_actions`; register checkers set `asi->register_usage_flags` directly from register fields, register lists, or known special cases.

State and persistence: no global state. It writes `asi->stack_space` and `asi->register_usage_flags`, which later affect `arch_prepare_kprobe()` rejection and optimized-probe direct execution decisions.

Dependencies and integration: depends on `decode.h`, `decode-arm.h`, and `checkers.h`. Integrated only for non-Thumb2 builds through `actions-arm.c` and `core.h`.

Risks: underestimated stack usage can allow probes on instructions that overwrite the kprobe exception stack frame; overestimated or unknown usage rejects valid probes or disables optimization. Register usage flags drive optprobe direct execution, so missing implicit registers such as `Rt+1` for LDRD/STRD would be unsafe.

Test signals: ARM tests include SP-relative negative stores at `MAX_STACK_SIZE`, unknown register-indexed SP stores, LDM/STM stack cases, LDRD/STRD implicit register pairs, and optprobe benchmarks that benefit from accurate register usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/checkers-arm.c -->
