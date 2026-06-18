# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/opt.c

Purpose: Adds x86 optimized kprobes by replacing an int3 with a 5-byte relative jump to a generated detour buffer. The detour saves registers, calls the optimized callback, executes copied original instructions, and jumps back after the optimized range.

Important APIs/types/functions: defines `__recover_optprobed_insn()`, `arch_prepare_optimized_kprobe()`, `arch_check_optimized_kprobe()`, `arch_optimize_kprobes()`, `arch_unoptimize_kprobe()`, `arch_unoptimize_kprobes()`, `arch_remove_optimized_kprobe()`, `arch_within_optimized_kprobe()`, and `setup_detour_execution()`. Internal helpers include the assembly `optprobe_template_*` labels, `optimized_callback()`, `copy_optimized_instructions()`, and `can_optimize()`.

Control flow: preparation decodes the whole containing function to ensure no instruction jumps into the bytes that will be replaced, avoids entry text and exception-table code, allocates an optinsn slot, copies the trampoline template, copies enough boostable original instructions to cover 5 bytes, patches the template argument and callback call, appends a jump back, and writes it to RO executable memory. Optimization backs up the four bytes after int3 and atomically patches a relative jump. Unoptimization writes int3 first, synchronizes CPUs, restores the following bytes, and records perf text-poke events.

State and persistence: optimized state lives in `struct optimized_kprobe`: generated detour slot, copied original bytes, optimized size, and list state. Kernel text is modified from int3 to a relative jump while optimized.

Dependencies and integration points: depends on core kprobe instruction copying/recovery, text-poking, perf events, ftrace/alternatives/jump-label/static-call reservation checks, kallsyms, exception tables, KGDB breakpoint detection, nospec/SMAP CLAC handling, and `common.h` register-save templates.

Risks: relative jump reach must fit within 2 GB. Any branch into the overwritten range would execute corrupted code, so full-function decode is required. Retpoline/IBT assumptions affect indirect jump-table safety. Unoptimization order is critical to avoid CPUs executing mixed bytes. The detour register frame must match normal kprobe handler expectations.

Test signals: optprobe tests should verify optimization/unoptimization under load, probes near function starts and short functions, functions with direct and indirect branches, reserved text conflicts, KGDB breakpoint conflicts, SMAP-enabled CLAC patching, post-unopt instruction recovery, and perf text-poke notifications.
