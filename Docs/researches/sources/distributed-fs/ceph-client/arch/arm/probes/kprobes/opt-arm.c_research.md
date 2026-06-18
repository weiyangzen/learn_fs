<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/opt-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/opt-arm.c

Purpose: implements ARM-mode optimized kprobes by replacing an armed probe breakpoint with a direct branch to an out-of-line template that saves registers, calls the optimized kprobe callback, optionally executes the original instruction directly, restores state, and branches back.

Important functions: `arch_prepared_optinsn()`, `arch_check_optimized_kprobe()`, `arch_prepare_optimized_kprobe()`, `arch_optimize_kprobes()`, `arch_unoptimize_kprobe()`, `arch_unoptimize_kprobes()`, `arch_within_optimized_kprobe()`, and `arch_remove_optimized_kprobe()`. `optimized_callback()` invokes `opt_pre_handler()` and falls back to single-step when direct execution is unavailable.

Control flow: `arch_prepare_optimized_kprobe()` rejects unknown or too-large stack usage, allocates an optinsn slot, checks that the branch from original address to slot is within ARM's signed 24-bit branch range, copies the assembly template, patches stack-protection immediates, stores callback operands, and may embed the original instruction in the restore path if `register_usage_flags` shows PC is unused and a return branch can be generated. `arch_optimize_kprobes()` patches the original instruction with a conditional branch preserving the original condition code.

State and persistence: allocates and frees optimized instruction slots, stores copied original instruction bytes in `op->optinsn.copied_insn`, sets `orig->ainsn.kprobe_direct_exec`, and patches live kernel text.

Dependencies and integration: depends on ARM branch generation, cache flushing, text patching, kprobe optimizer core, and metadata from ARM checkers (`stack_space`, `register_usage_flags`). Built only for non-Thumb2 `CONFIG_OPTPROBES`.

Risks: branch range and alignment checks are critical; wrong template offsets corrupt saved register layout. Direct execution is unsafe if register usage omitted PC or if the original instruction has side effects incompatible with template restore. Stack protection must account for probed instruction stores below SP.

Test signals: kprobe benchmarks in `test-core.c` include push/pop patterns meant to compare optimized and unoptimized paths; ARM instruction tests and stack checkers provide the metadata this optimizer trusts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/opt-arm.c -->
