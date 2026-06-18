# subset-b-000693 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/ftrace.c

Purpose: dynamic ftrace patching, ftrace-call replacement, function graph return rewriting, and SMP instruction-cache synchronization.

Important APIs/types/functions: functions: `make_jbsr`, `ftrace_check_current_nop`, `ftrace_modify_code`, `ftrace_make_call`, `ftrace_make_nop`, `ftrace_update_ftrace_func`, `ftrace_modify_call`, `prepare_ftrace_return`, `ftrace_enable_ftrace_graph_caller`, `ftrace_disable_ftrace_graph_caller`, `__ftrace_modify_code`, `arch_ftrace_update_code`; types: `ftrace_modify_param`; macros: `NOP`, `NOP32_HI`, `NOP32_LO`, `PUSH_LR`, `MOVIH_LINK`, `ORI_LINK`, `JSR_LINK`, `BSR_LINK`; exports: `_mcount`

Control flow: Runtime flow is organized around `make_jbsr`, `ftrace_check_current_nop`, `ftrace_modify_code`, `ftrace_make_call`, `ftrace_make_nop`, `ftrace_update_ftrace_func`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/ftrace.h`, `linux/uaccess.h`, `linux/stop_machine.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/head.S

Purpose: early architecture boot entry and handoff before normal C kernel setup is available.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/linkage.h`, `linux/init.h`, `asm/page.h`, `abi/entry.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/irq.c

Purpose: architecture interrupt initialization and generic irqchip hookup.

Important APIs/types/functions: functions: `init_IRQ`

Control flow: Runtime flow is organized around `init_IRQ`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/init.h`, `linux/interrupt.h`, `linux/irq.h`, `linux/irqchip.h`, `asm/traps.h`, `asm/smp.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/jump_label.c

Purpose: static-branch/jump-label text patching between NOP and branch instructions.

Important APIs/types/functions: functions: `arch_jump_label_transform`, `arch_jump_label_transform_static`; types: `jump_label_type`; macros: `NOP32_HI`, `NOP32_LO`, `BSR_LINK`

Control flow: Runtime flow is organized around `arch_jump_label_transform`, `arch_jump_label_transform_static`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/jump_label.h`, `linux/kernel.h`, `linux/memory.h`, `linux/mutex.h`, `linux/uaccess.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/module.c

Purpose: ELF module relocation and C-SKY branch/call fixups for loadable modules.

Important APIs/types/functions: functions: `jsri_2_lrw_jsr`, `apply_relocate_add`; macros: `IS_BSR32(hi16,`, `IS_JSRI32(hi16,`, `CHANGE_JSRI_TO_LRW(addr)`, `SET_JSR32_R26(addr)`

Control flow: Runtime flow is organized around `jsri_2_lrw_jsr`, `apply_relocate_add`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/moduleloader.h`, `linux/elf.h`, `linux/mm.h`, `linux/vmalloc.h`, `linux/slab.h`, `linux/fs.h`, `linux/string.h`, `linux/kernel.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/perf_callchain.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/perf_callchain.c

Purpose: perf user and kernel callchain unwinding from frame records.

Important APIs/types/functions: functions: `unwind_frame_kernel`, `walk_stackframe`, `user_backtrace`, `perf_callchain_user`, `perf_callchain_kernel`; types: `stackframe`, `perf_callchain_entry_ctx`, `pt_regs`

Control flow: Runtime flow is organized around `unwind_frame_kernel`, `walk_stackframe`, `user_backtrace`, `perf_callchain_user`, `perf_callchain_kernel`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/perf_event.h`, `linux/uaccess.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; perf stat/record, callchain, and overflow tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/perf_callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/perf_event.c

Purpose: C-SKY CPU PMU registration, event mapping, counter programming, and overflow handling.

Important APIs/types/functions: functions: `csky_pmu_read_cc`, `csky_pmu_write_cc`, `csky_pmu_read_ic`, `csky_pmu_write_ic`, `csky_pmu_read_icac`, `csky_pmu_write_icac`, `csky_pmu_read_icmc`, `csky_pmu_write_icmc`, `csky_pmu_read_dcac`, `csky_pmu_write_dcac`, `csky_pmu_read_dcmc`, `csky_pmu_write_dcmc`, `csky_pmu_read_l2ac`, `csky_pmu_write_l2ac`, `csky_pmu_read_l2mc`, `csky_pmu_write_l2mc`, `csky_pmu_read_iutlbmc`, `csky_pmu_write_iutlbmc`; types: `pmu_hw_events`, `perf_event`, `pmu`, `platform_device`, `hw_perf_event`, `perf_sample_data`, `pt_regs`, `device_node`; macros: `CSKY_PMU_MAX_EVENTS`, `DEFAULT_COUNT_WIDTH`, `HPCR`, `HPSPR`, `HPEPR`, `HPSIR`, `HPCNTENR`, `HPINTENR`, `HPOFSR`, `to_csky_pmu(p)`, `cprgr(reg)`, `cpwgr(reg,`

Control flow: Probe allocates per-CPU PMU state, maps perf attributes to counter indexes, programs coprocessor registers, requests per-CPU IRQs, registers CPU hotplug callbacks, and handles overflow by updating counts, sampling, and reloading periods.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/errno.h`, `linux/interrupt.h`, `linux/module.h`, `linux/of.h`, `linux/perf_event.h`, `linux/platform_device.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; perf stat/record, callchain, and overflow tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/perf_regs.c

Purpose: perf register mask validation and pt_regs register-value extraction.

Important APIs/types/functions: functions: `perf_reg_value`, `perf_reg_validate`, `perf_reg_abi`, `perf_get_regs_user`; types: `pt_regs`; macros: `REG_RESERVED`

Control flow: Runtime flow is organized around `perf_reg_value`, `perf_reg_validate`, `perf_reg_abi`, `perf_get_regs_user`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/errno.h`, `linux/kernel.h`, `linux/perf_event.h`, `linux/bug.h`, `asm/perf_regs.h`, `asm/ptrace.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; perf stat/record, callchain, and overflow tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/power.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/power.c

Purpose: architecture reboot and power-off hooks.

Important APIs/types/functions: functions: `machine_power_off`, `machine_halt`, `machine_restart`; exports: `pm_power_off`

Control flow: Runtime flow is organized around `machine_power_off`, `machine_halt`, `machine_restart`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/reboot.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/Makefile

Purpose: selects C-SKY kprobes, kprobes-on-ftrace, uprobes, decoder, simulator, and trampoline objects.

Important APIs/types/functions: build rules: `obj-$(CONFIG_KPROBES) += kprobes.o decode-insn.o simulate-insn.o`; `obj-$(CONFIG_KPROBES) += kprobes_trampoline.o`; `obj-$(CONFIG_KPROBES_ON_FTRACE) += ftrace.o`; `obj-$(CONFIG_UPROBES) += uprobes.o decode-insn.o simulate-insn.o`; `CFLAGS_REMOVE_simulate-insn.o = $(CC_FLAGS_FTRACE)`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.c

Purpose: probe instruction decoding and classification for kprobes and uprobes.

Important APIs/types/functions: functions: `csky_probe_decode_insn`; types: `probe_insn`

Control flow: Runtime flow is organized around `csky_probe_decode_insn`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/kernel.h`, `linux/kprobes.h`, `linux/module.h`, `linux/kallsyms.h`, `asm/sections.h`, `decode-insn.h`, `simulate-insn.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.h -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.h

Purpose: probe decoder declarations and C-SKY instruction-width helpers.

Important APIs/types/functions: types: `probe_insn`; macros: `__CSKY_KERNEL_KPROBES_DECODE_INSN_H`, `is_insn32(insn)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/sections.h`, `asm/kprobes.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/ftrace.c

Purpose: dynamic ftrace patching, ftrace-call replacement, function graph return rewriting, and SMP instruction-cache synchronization.

Important APIs/types/functions: functions: `kprobe_ftrace_handler`, `arch_prepare_kprobe_ftrace`; types: `ftrace_ops`, `kprobe`, `kprobe_ctlblk`, `pt_regs`

Control flow: Runtime flow is organized around `kprobe_ftrace_handler`, `arch_prepare_kprobe_ftrace`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/kprobes.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes.c

Purpose: kprobe breakpoint planting, single-step/simulation, reentry, fault, and kretprobe trampoline handling.

Important APIs/types/functions: functions: `patch_text_cb`, `patch_text`, `arch_prepare_ss_slot`, `arch_prepare_simulate`, `arch_simulate_insn`, `arch_prepare_kprobe`, `arch_arm_kprobe`, `arch_disarm_kprobe`, `arch_remove_kprobe`, `save_previous_kprobe`, `restore_previous_kprobe`, `set_current_kprobe`, `kprobes_save_local_irqflag`, `kprobes_restore_local_irqflag`, `set_ss_context`, `clear_ss_context`, `setup_singlestep`, `reenter_kprobe`; types: `csky_insn_patch`, `kprobe_ctlblk`, `pt_regs`, `kprobe`; macros: `pr_fmt(fmt)`, `TRACE_MODE_SI`, `TRACE_MODE_MASK`, `TRACE_MODE_RUN`

Control flow: Preparation decodes and copies the probed instruction, patching text with a breakpoint. Trap handling runs pre-handlers, single-steps or simulates the instruction, restores PC/status, handles faults/reentry, and then invokes post-handlers.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/kprobes.h`, `linux/extable.h`, `linux/slab.h`, `linux/stop_machine.h`, `asm/ptrace.h`, `linux/uaccess.h`, `asm/sections.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes_trampoline.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes_trampoline.S

Purpose: assembly trampoline used for C-SKY kretprobe return interception.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/linkage.h`, `abi/entry.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes_trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.c

Purpose: simulation of C-SKY control-flow and literal-load instructions that cannot safely run out of line.

Important APIs/types/functions: functions: `csky_insn_reg_get_val`, `csky_insn_reg_set_val`, `simulate_br16`, `simulate_br32`, `simulate_bt16`, `simulate_bt32`, `simulate_bf16`, `simulate_bf32`, `simulate_jmp16`, `simulate_jmp32`, `simulate_jsr16`, `simulate_jsr32`, `simulate_lrw16`, `simulate_lrw32`, `simulate_pop16`, `simulate_pop32`, `simulate_bez32`, `simulate_bnez32`

Control flow: Runtime flow is organized around `csky_insn_reg_get_val`, `csky_insn_reg_set_val`, `simulate_br16`, `simulate_br32`, `simulate_bt16`, `simulate_bt32`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/bitops.h`, `linux/kernel.h`, `linux/kprobes.h`, `decode-insn.h`, `simulate-insn.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.h -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.h

Purpose: probe simulation table macros and simulator declarations.

Important APIs/types/functions: macros: `__CSKY_KERNEL_PROBES_SIMULATE_INSN_H`, `__CSKY_INSN_FUNCS(name,`, `CSKY_INSN_SET_SIMULATE(name,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/uprobes.c

Purpose: C-SKY user-space probe breakpoint, xol slot, cache flush, and resume handling.

Important APIs/types/functions: functions: `is_swbp_insn`, `uprobe_get_swbp_addr`, `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_skip_sstep`, `arch_uprobe_abort_xol`, `arch_uretprobe_is_alive`, `arch_uretprobe_hijack_return_addr`, `arch_uprobe_exception_notify`, `uprobe_breakpoint_handler`, `uprobe_single_step_handler`; types: `uprobe_task`, `pt_regs`; macros: `UPROBE_TRAP_NR`

Control flow: Runtime flow is organized around `is_swbp_insn`, `uprobe_get_swbp_addr`, `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/highmem.h`, `linux/ptrace.h`, `linux/uprobes.h`, `asm/cacheflush.h`, `decode-insn.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/probes/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/process.c

Purpose: thread creation, context-switch frame setup, idle/thread hooks, and task register inspection.

Important APIs/types/functions: functions: `copy_thread`, `elf_core_copy_task_fpregs`, `dump_task_regs`, `arch_cpu_idle`; types: `cpuinfo_csky`, `switch_stack`, `pt_regs`; exports: `__stack_chk_guard`

Control flow: Runtime flow is organized around `copy_thread`, `elf_core_copy_task_fpregs`, `dump_task_regs`, `arch_cpu_idle`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/module.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/sched/debug.h`, `linux/delay.h`, `linux/kallsyms.h`, `linux/uaccess.h`, `linux/ptrace.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/ptrace.c

Purpose: ptrace regsets, single-step control, syscall trace/audit hooks, and diagnostic register dumps.

Important APIs/types/functions: functions: `singlestep_disable`, `singlestep_enable`, `user_enable_single_step`, `user_disable_single_step`, `gpr_get`, `gpr_set`, `fpr_get`, `fpr_set`, `USER_REGSET_NOTE_TYPE`, `task_user_regset_view`, `regs_query_register_offset`, `regs_within_kernel_stack`, `regs_get_kernel_stack_nth`, `ptrace_disable`, `arch_ptrace`, `syscall_trace_enter`, `syscall_trace_exit`, `show_iutlb`; types: `pt_regs`, `csky_regset`, `membuf`, `user_fp`, `pt_regs_offset`; macros: `CREATE_TRACE_POINTS`, `TRACE_MODE_SI`, `TRACE_MODE_RUN`, `TRACE_MODE_MASK`, `REG_OFFSET_NAME(r)`, `REG_OFFSET_END`

Control flow: Ptrace and syscall-trace entry points toggle single-step bits, expose GPR/FPR regsets, sanitize status-register writes, emit audit/tracepoint records, and print diagnostic register/TLB state.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/audit.h`, `linux/elf.h`, `linux/errno.h`, `linux/kernel.h`, `linux/mm.h`, `linux/ptrace.h`, `linux/regset.h`, `linux/sched.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/setup.c

Purpose: early command line, device tree, memblock, initrd, and architecture setup.

Important APIs/types/functions: functions: `setup_initrd`, `arch_zone_limits_init`, `csky_memblock_init`, `if`, `setup_arch`, `read_mmu_msa`, `csky_start`; exports: `va_pa_offset`

Control flow: Runtime flow is organized around `setup_initrd`, `arch_zone_limits_init`, `csky_memblock_init`, `if`, `setup_arch`, `read_mmu_msa`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/console.h`, `linux/memblock.h`, `linux/initrd.h`, `linux/of.h`, `linux/of_fdt.h`, `linux/start_kernel.h`, `linux/dma-map-ops.h`, `asm/sections.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/signal.c

Purpose: real-time signal frame setup, rt_sigreturn restore, syscall restart, and user-resume work.

Important APIs/types/functions: functions: `restore_fpu_state`, `save_fpu_state`, `restore_sigcontext`, `SYSCALL_DEFINE0`, `setup_sigcontext`, `get_sigframe`, `setup_rt_frame`, `handle_signal`, `do_signal`, `do_notify_resume`; types: `user_fp`, `rt_sigframe`, `siginfo`, `ucontext`, `sigcontext`, `pt_regs`, `ksignal`; macros: `restore_fpu_state(sigcontext)`, `save_fpu_state(sigcontext)`; syscalls: `rt_sigreturn`

Control flow: Signal delivery saves pt_regs/FPU state into an rt signal frame, points LR at the VDSO sigreturn stub, sets handler arguments, and adjusts syscall restart state; sigreturn validates the frame and restores masks, altstack, and registers.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/signal.h`, `linux/uaccess.h`, `linux/syscalls.h`, `linux/resume_user_mode.h`, `asm/traps.h`, `asm/ucontext.h`, `asm/vdso.h`, `abi/regdef.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/smp.c

Purpose: SMP CPU bring-up, IPI dispatch, cache/TLB broadcast, and hotplug integration.

Important APIs/types/functions: functions: `handle_ipi`, `set_send_ipi`, `send_ipi_message`, `arch_show_interrupts`, `arch_send_call_function_ipi_mask`, `arch_send_call_function_single_ipi`, `ipi_stop`, `smp_send_stop`, `arch_smp_send_reschedule`, `arch_irq_work_raise`, `smp_prepare_cpus`, `setup_smp_ipi`, `setup_smp`, `for_each_of_cpu_node`, `__cpu_up`, `smp_cpus_done`, `csky_start_secondary`, `__cpu_disable`; types: `ipi_message_type`, `ipi_data_struct`, `device_node`, `mm_struct`

Control flow: Runtime flow is organized around `handle_ipi`, `set_send_ipi`, `send_ipi_message`, `arch_show_interrupts`, `arch_send_call_function_ipi_mask`, `arch_send_call_function_single_ipi`, called by generic kernel subsystems through architecture hooks.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/module.h`, `linux/init.h`, `linux/kernel.h`, `linux/mm.h`, `linux/sched.h`, `linux/kernel_stat.h`, `linux/notifier.h`, `linux/cpu.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/stacktrace.c

Purpose: frame-pointer-based stack unwinding for stack traces and perf.

Important APIs/types/functions: functions: `walk_stackframe`, `if`, `print_trace_address`, `show_stack`, `save_wchan`, `__get_wchan`, `__save_trace`, `save_trace`, `save_stack_trace_tsk`, `save_stack_trace`; types: `stackframe`, `pt_regs`, `stack_trace`; exports: `save_stack_trace_tsk`, `save_stack_trace`

Control flow: Runtime flow is organized around `walk_stackframe`, `if`, `print_trace_address`, `show_stack`, `save_wchan`, `__get_wchan`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/sched/debug.h`, `linux/sched/task_stack.h`, `linux/stacktrace.h`, `linux/ftrace.h`, `linux/ptrace.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/syscall.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/syscall.c

Purpose: syscall number, argument, return-value, and skip helpers for tracing/seccomp/audit.

Important APIs/types/functions: functions: `SYSCALL_DEFINE1`, `SYSCALL_DEFINE6`, `SYSCALL_DEFINE4`; types: `thread_info`, `pt_regs`; syscalls: `set_thread_area`, `mmap2`, `csky_fadvise64_64`

Control flow: Runtime flow is organized around `SYSCALL_DEFINE1`, `SYSCALL_DEFINE6`, `SYSCALL_DEFINE4`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is stored in task_struct, thread_info, pt_regs, signal frames, and saved thread context rather than durable storage.

Dependencies and integration: Depends on `linux/syscalls.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Register layout and restart semantics are ABI-sensitive and must stay compatible with libc, debuggers, audit, seccomp, and core dumps.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/syscall_table.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/syscall_table.c

Purpose: C-SKY syscall dispatch table generated from syscall metadata.

Important APIs/types/functions: macros: `__SYSCALL(nr,`, `__SYSCALL_WITH_COMPAT(nr,`, `sys_fadvise64_64`, `sys_sync_file_range`

Control flow: Runtime flow is small and callback-oriented, with the generic architecture or subsystem code invoking this file where needed.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/syscalls.h`, `asm/syscalls.h`, `asm/syscall_table_32.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/syscall_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/time.c

Purpose: clocksource/timer initialization from device tree.

Important APIs/types/functions: functions: `time_init`

Control flow: Runtime flow is organized around `time_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/clocksource.h`, `linux/of_clk.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/traps.c

Purpose: exception/trap dispatch, breakpoint integration, signal delivery, and oops reporting.

Important APIs/types/functions: functions: `pre_trap_init`, `trap_init`, `die`, `do_trap`, `do_trap_error`, `do_trap_misaligned`, `do_trap_bkpt`, `do_trap_illinsn`, `do_trap_fpe`, `do_trap_priv`, `trap_c`; types: `task_struct`; macros: `DO_ERROR_INFO(name,`

Control flow: Runtime flow is organized around `pre_trap_init`, `trap_init`, `die`, `do_trap`, `do_trap_error`, `do_trap_misaligned`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/cpu.h`, `linux/sched.h`, `linux/signal.h`, `linux/kernel.h`, `linux/mm.h`, `linux/module.h`, `linux/user.h`, `linux/string.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso.c

Purpose: VDSO image mapping and mm-context VDSO state setup.

Important APIs/types/functions: functions: `vdso_init`, `arch_setup_additional_pages`; types: `page`, `vm_area_struct`, `mm_struct`

Control flow: Runtime flow is organized around `vdso_init`, `arch_setup_additional_pages`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/binfmts.h`, `linux/elf.h`, `linux/err.h`, `linux/mm.h`, `linux/slab.h`, `asm/page.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/Makefile

Purpose: builds the C-SKY VDSO shared object, symbol assembly, and embedded kernel object.

Important APIs/types/functions: build rules: `include $(srctree)/lib/vdso/Makefile.include`; `vdso-syms += rt_sigreturn`; `obj-vdso = $(patsubst %, %.o, $(vdso-syms)) note.o`; `ifneq ($(c-gettimeofday-y),)`; `CFLAGS_vgettimeofday.o += -include $(c-gettimeofday-y)`; `endif`; `ccflags-y := -fno-stack-protector -DBUILD_VDSO32`; `targets := $(obj-vdso) vdso.so vdso.so.dbg vdso.lds vdso-dummy.o`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/note.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/note.S

Purpose: implements architecture support for `note`.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/elfnote.h`, `linux/version.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/rt_sigreturn.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/rt_sigreturn.S

Purpose: implements architecture support for `rt_sigreturn`.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/linkage.h`, `asm/unistd.h`, `abi/vdso.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/rt_sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/so2s.sh -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/so2s.sh

Purpose: implements architecture support for `so2s`.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: Runtime flow is small and callback-oriented, with the generic architecture or subsystem code invoking this file where needed.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/so2s.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.S

Purpose: implements architecture support for `vdso`.

Important APIs/types/functions: labels: `vdso_start`, `vdso_end`

Control flow: Control enters through `vdso_start`, `vdso_end`, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/init.h`, `linux/linkage.h`, `asm/page.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.lds.S

Purpose: implements architecture support for `vdso.lds`.

Important APIs/types/functions: labels: `global`, `local`

Control flow: Control enters through `global`, `local`, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `asm/page.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/csky/kernel/vmlinux.lds.S

Purpose: kernel link layout for text/data/init/BSS, vectors, and C-SKY memory regions.

Important APIs/types/functions: functions: `AT`; macros: `VBR_BASE`, `ITCM_SIZE`

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `asm/vmlinux.lds.h`, `asm/page.h`, `asm/memory.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/lib/Makefile

Purpose: selects C-SKY library objects for usercopy, delay, error injection, and fallback string routines.

Important APIs/types/functions: build rules: `lib-y := usercopy.o delay.o`; `obj-$(CONFIG_FUNCTION_ERROR_INJECTION) += error-inject.o`; `ifneq ($(CONFIG_HAVE_EFFICIENT_UNALIGNED_STRING_OPS), y)`; `lib-y += string.o`; `endif`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/csky/lib/delay.c

Purpose: busy-wait delay calibration wrappers.

Important APIs/types/functions: functions: `__aligned`, `__const_udelay`, `__udelay`, `__ndelay`; exports: `__delay`, `__const_udelay`, `__udelay`, `__ndelay`

Control flow: Runtime flow is organized around `__aligned`, `__const_udelay`, `__udelay`, `__ndelay`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/kernel.h`, `linux/module.h`, `linux/init.h`, `linux/delay.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/csky/lib/error-inject.c

Purpose: architecture participation in function error-injection validation.

Important APIs/types/functions: functions: `override_function_with_return`

Control flow: Runtime flow is organized around `override_function_with_return`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/error-injection.h`, `linux/kprobes.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/string.c -->
# sources/distributed-fs/ceph-client/arch/csky/lib/string.c

Purpose: fallback memcpy/memmove/memset routines for C-SKY.

Important APIs/types/functions: functions: `memcpy`, `memmove`, `memset`; types: `types`, `const_types`; macros: `BYTES_LONG`, `WORD_MASK`, `MIN_THRESHOLD`; exports: `memcpy`, `memmove`, `memset`

Control flow: Runtime flow is organized around `memcpy`, `memmove`, `memset`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/types.h`, `linux/module.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/usercopy.c -->
# sources/distributed-fs/ceph-client/arch/csky/lib/usercopy.c

Purpose: raw user copy and clear-user primitives with exception fixups.

Important APIs/types/functions: functions: `raw_copy_from_user`, `raw_copy_to_user`, `__clear_user`; exports: `raw_copy_from_user`, `raw_copy_to_user`, `__clear_user`

Control flow: Runtime flow is organized around `raw_copy_from_user`, `raw_copy_to_user`, `__clear_user`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/uaccess.h`, `linux/types.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/lib/usercopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/csky/mm/Makefile

Purpose: selects C-SKY memory-management objects according to cache, highmem, and TCM configuration.

Important APIs/types/functions: build rules: `ifeq ($(CONFIG_CPU_HAS_CACHEV2),y)`; `obj-y += cachev2.o`; `CFLAGS_REMOVE_cachev2.o = $(CC_FLAGS_FTRACE)`; `else`; `obj-y += cachev1.o`; `CFLAGS_REMOVE_cachev1.o = $(CC_FLAGS_FTRACE)`; `endif`; `obj-y += dma-mapping.o`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: C-SKY cross-build; defconfig, allyesconfig, and allmodconfig build checks; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/asid.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/asid.c

Purpose: ASID allocation, generation rollover, and reserved-ASID tracking.

Important APIs/types/functions: functions: `flush_context`, `for_each_possible_cpu`, `check_update_reserved_asid`, `new_context`, `asid_new_context`, `asid_allocator_init`; types: `mm_struct`; macros: `reserved_asid(info,`, `ASID_MASK(info)`, `ASID_FIRST_VERSION(info)`, `asid2idx(info,`, `idx2asid(info,`

Control flow: Runtime flow is organized around `flush_context`, `for_each_possible_cpu`, `check_update_reserved_asid`, `new_context`, `asid_new_context`, `asid_allocator_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/slab.h`, `linux/mm_types.h`, `asm/asid.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/asid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/cachev1.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/cachev1.c

Purpose: first-generation C-SKY cache maintenance through cache control registers.

Important APIs/types/functions: functions: `cache_op_line`, `cache_op_all`, `cache_op_range`, `dcache_wb_line`, `icache_inv_range`, `icache_inv_all`, `local_icache_inv_all`, `dcache_wb_range`, `dcache_wbinv_all`, `cache_wbinv_range`, `cache_wbinv_all`, `dma_wbinv_range`, `dma_inv_range`, `dma_wb_range`; macros: `INS_CACHE`, `DATA_CACHE`, `CACHE_INV`, `CACHE_CLR`, `CACHE_OMS`, `CACHE_ITS`, `CACHE_LICF`, `CR22_LEVEL_SHIFT`, `CR22_SET_SHIFT`, `CR22_WAY_SHIFT`, `CR22_WAY_SHIFT_L2`, `CCR2_L2E`; exports: `cache_wbinv_range`

Control flow: Runtime flow is organized around `cache_op_line`, `cache_op_all`, `cache_op_range`, `dcache_wb_line`, `icache_inv_range`, `icache_inv_all`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/spinlock.h`, `asm/cache.h`, `abi/reg_ops.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/cachev1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/cachev2.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/cachev2.c

Purpose: newer C-SKY cache maintenance and SMP range flushing.

Important APIs/types/functions: functions: `local_icache_inv_all`, `icache_inv_range`, `cache_op_line`, `local_icache_inv_range`, `dcache_wb_line`, `dcache_wb_range`, `cache_wbinv_range`, `dma_wbinv_range`, `dma_inv_range`, `dma_wb_range`; types: `cache_range`; macros: `INS_CACHE`, `DATA_CACHE`, `CACHE_INV`, `CACHE_CLR`, `CACHE_OMS`; exports: `cache_wbinv_range`

Control flow: Runtime flow is organized around `local_icache_inv_all`, `icache_inv_range`, `cache_op_line`, `local_icache_inv_range`, `dcache_wb_line`, `dcache_wb_range`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/spinlock.h`, `linux/smp.h`, `linux/mm.h`, `asm/cache.h`, `asm/barrier.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/cachev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/context.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/context.c

Purpose: MM context activation backed by ASID and TLB state.

Important APIs/types/functions: functions: `check_and_switch_context`, `asid_flush_cpu_ctxt`, `asids_init`; types: `asid_info`

Control flow: Runtime flow is organized around `check_and_switch_context`, `asid_flush_cpu_ctxt`, `asids_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/bitops.h`, `linux/sched.h`, `linux/slab.h`, `linux/mm.h`, `asm/asid.h`, `asm/mmu_context.h`, `asm/smp.h`, `asm/tlbflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/dma-mapping.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/dma-mapping.c

Purpose: DMA cache synchronization for pages and scatterlists.

Important APIs/types/functions: functions: `cache_op`, `dma_wbinv_set_zero_range`, `arch_dma_prep_coherent`, `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`; types: `page`, `dma_data_direction`

Control flow: Runtime flow is organized around `cache_op`, `dma_wbinv_set_zero_range`, `arch_dma_prep_coherent`, `arch_sync_dma_for_device`, `arch_sync_dma_for_cpu`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/cache.h`, `linux/dma-map-ops.h`, `linux/genalloc.h`, `linux/highmem.h`, `linux/io.h`, `linux/mm.h`, `linux/scatterlist.h`, `linux/types.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/dma-mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/fault.c

Purpose: page-fault handling for user and kernel accesses.

Important APIs/types/functions: functions: `fixup_exception`, `is_write`, `csky_cmpxchg_fixup`, `no_context`, `mm_fault_error`, `if`, `bad_area_nosemaphore`, `vmalloc_fault`, `access_error`, `do_page_fault`; types: `task_struct`, `vm_area_struct`, `mm_struct`

Control flow: Runtime flow is organized around `fixup_exception`, `is_write`, `csky_cmpxchg_fixup`, `no_context`, `mm_fault_error`, `if`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/extable.h`, `linux/kprobes.h`, `linux/mmu_context.h`, `linux/perf_event.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/highmem.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/highmem.c

Purpose: highmem/fixmap cache and TLB maintenance.

Important APIs/types/functions: functions: `kmap_flush_tlb`, `kmap_init`; exports: `kmap_flush_tlb`

Control flow: Runtime flow is organized around `kmap_flush_tlb`, `kmap_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/module.h`, `linux/highmem.h`, `linux/smp.h`, `linux/memblock.h`, `asm/fixmap.h`, `asm/tlbflush.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/highmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/init.c

Purpose: physical memory, paging, zones, memblock handoff, and init-memory release.

Important APIs/types/functions: functions: `free_initmem`, `pgd_init`, `mmu_init`, `fixrange_init`, `fixaddr_init`; macros: `PTRS_KERN_TABLE`; exports: `invalid_pte_table`

Control flow: Runtime flow is organized around `free_initmem`, `pgd_init`, `mmu_init`, `fixrange_init`, `fixaddr_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/bug.h`, `linux/module.h`, `linux/init.h`, `linux/signal.h`, `linux/sched.h`, `linux/kernel.h`, `linux/errno.h`, `linux/string.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/ioremap.c

Purpose: I/O remapping with architecture page protections.

Important APIs/types/functions: functions: `phys_mem_access_prot`, `if`; exports: `phys_mem_access_prot`

Control flow: Runtime flow is organized around `phys_mem_access_prot`, `if`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/export.h`, `linux/mm.h`, `linux/io.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/syscache.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/syscache.c

Purpose: outer/system cache maintenance hooks.

Important APIs/types/functions: functions: `SYSCALL_DEFINE3`; syscalls: `cacheflush`

Control flow: Runtime flow is organized around `SYSCALL_DEFINE3`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/syscalls.h`, `asm/page.h`, `asm/cacheflush.h`, `asm/cachectl.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/syscache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/tcm.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/tcm.c

Purpose: tightly-coupled memory discovery, reservation, and setup.

Important APIs/types/functions: functions: `tcm_mapping_init`, `tcm_alloc`, `tcm_free`, `tcm_setup_pool`, `tcm_init`; exports: `tcm_alloc`, `tcm_free`

Control flow: Runtime flow is organized around `tcm_mapping_init`, `tcm_alloc`, `tcm_free`, `tcm_setup_pool`, `tcm_init`, called by generic kernel subsystems through architecture hooks.

State and persistence: State is hardware-visible MMU/cache/TLB or page-table state managed together with generic memory-management structures.

Dependencies and integration: Depends on `linux/highmem.h`, `linux/genalloc.h`, `asm/tlbflush.h`, `asm/fixmap.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/tcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/csky/mm/tlb.c

Purpose: TLB flush and update operations for C-SKY address spaces.

Important APIs/types/functions: functions: `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_tlb_page`, `flush_tlb_one`; macros: `TLB_ENTRY_SIZE`, `TLB_ENTRY_SIZE_MASK`, `restore_asid_inv_utlb(oldpid,`; exports: `flush_tlb_one`

Control flow: Runtime flow is organized around `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_range`, `flush_tlb_kernel_range`, `flush_tlb_page`, `flush_tlb_one`, called by generic kernel subsystems through architecture hooks.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/init.h`, `linux/mm.h`, `linux/module.h`, `linux/sched.h`, `asm/mmu_context.h`, `asm/setup.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: MMU/cache ordering or address-validation bugs can cause stale translations, data corruption, user-memory faults, or DMA coherency failures.

Test signals: C-SKY cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/csky/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/Kbuild -->
# sources/distributed-fs/ceph-client/arch/hexagon/Kbuild

Purpose: architecture Kbuild object aggregation and generated header selection.

Important APIs/types/functions: build rules: `obj-y += kernel/ mm/ lib/`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/Kconfig -->
# sources/distributed-fs/ceph-client/arch/hexagon/Kconfig

Purpose: architecture configuration symbols, feature selections, and build-time options.

Important APIs/types/functions: build rules: `comment "Linux Kernel Configuration for Hexagon"`; `config HEXAGON`; `def_bool y`; `select ARCH_32BIT_OFF_T`; `select ARCH_HAS_SYNC_DMA_FOR_DEVICE`; `select ARCH_NO_PREEMPT`; `select ARCH_WANT_FRAME_POINTERS`; `select DMA_GLOBAL_POOL`

Control flow: Configuration is declarative: symbols select generic kernel facilities, architecture features, and build options before compilation.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/Makefile -->
# sources/distributed-fs/ceph-client/arch/hexagon/Makefile

Purpose: architecture Kbuild compiler/linker flags and object selection.

Important APIs/types/functions: build rules: `KBUILD_DEFCONFIG = comet_defconfig`; `KBUILD_CFLAGS += -G0`; `LDFLAGS_vmlinux += -G0`; `KBUILD_CFLAGS += -fno-short-enums`; `KBUILD_CFLAGS += -mlong-calls`; `KBUILD_CFLAGS_MODULE += -mlong-calls`; `cflags-y += $(call cc-option,-mv${CONFIG_HEXAGON_ARCH_VERSION})`; `aflags-y += $(call cc-option,-mv${CONFIG_HEXAGON_ARCH_VERSION})`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/Kbuild

Purpose: architecture Kbuild object aggregation and generated header selection.

Important APIs/types/functions: build rules: `syscall-y += syscall_table_32.h`; `generic-y += extable.h`; `generic-y += iomap.h`; `generic-y += kvm_para.h`; `generic-y += mcs_spinlock.h`; `generic-y += text-patching.h`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/asm-offsets.h

Purpose: provides Hexagon architecture declarations for `asm-offsets`.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `generated/asm-offsets.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/atomic.h

Purpose: Hexagon atomic operations implemented around compare-exchange loops.

Important APIs/types/functions: functions: `arch_atomic_set`, `arch_atomic_fetch_add_unless`; macros: `_ASM_ATOMIC_H`, `arch_atomic_set_release(v,`, `arch_atomic_read(v)`, `ATOMIC_OP(op)`, `ATOMIC_OP_RETURN(op)`, `ATOMIC_FETCH_OP(op)`, `ATOMIC_OPS(op)`, `arch_atomic_add_return`, `arch_atomic_sub_return`, `arch_atomic_fetch_add`, `arch_atomic_fetch_sub`, `arch_atomic_fetch_and`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/types.h`, `asm/cmpxchg.h`, `asm/barrier.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/bitops.h

Purpose: Hexagon bit operations and generic bitops integration.

Important APIs/types/functions: functions: `test_and_clear_bit`, `test_and_set_bit`, `test_and_change_bit`, `clear_bit`, `set_bit`, `change_bit`, `arch___clear_bit`, `arch___set_bit`, `arch___change_bit`, `arch___test_and_clear_bit`, `arch___test_and_set_bit`, `arch___test_and_change_bit`, `arch_test_bit`, `arch_test_bit_acquire`, `ffz`, `fls`, `ffs`, `__ffs`; macros: `_ASM_BITOPS_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/compiler.h`, `asm/byteorder.h`, `asm/atomic.h`, `asm/barrier.h`, `asm-generic/bitops/lock.h`, `asm-generic/bitops/non-instrumented-non-atomic.h`, `asm-generic/bitops/fls64.h`, `asm-generic/bitops/sched.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cache.h

Purpose: Hexagon cacheline size and alignment constants.

Important APIs/types/functions: macros: `__ASM_CACHE_H`, `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `__cacheline_aligned`, `____cacheline_aligned`, `__read_mostly`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cacheflush.h

Purpose: Hexagon cache flush interfaces and user-page copy coherence hooks.

Important APIs/types/functions: functions: `update_mmu_cache_range`; types: `vm_area_struct`; macros: `_ASM_CACHEFLUSH_H`, `LINESIZE`, `LINEBITS`, `flush_dcache_range`, `flush_icache_range`, `update_mmu_cache(vma,`, `copy_to_user_page`, `copy_from_user_page(vma,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/mm_types.h`, `asm-generic/cacheflush.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/checksum.h

Purpose: Hexagon checksum API declarations and generic checksum integration.

Important APIs/types/functions: macros: `_ASM_CHECKSUM_H`, `do_csum`, `csum_tcpudp_nofold`, `csum_tcpudp_magic`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/checksum.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cmpxchg.h

Purpose: Hexagon exchange and compare-exchange primitives.

Important APIs/types/functions: functions: `__arch_xchg`; macros: `_ASM_CMPXCHG_H`, `arch_xchg(ptr,`, `arch_cmpxchg(ptr,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/delay.h

Purpose: Hexagon delay API declarations and udelay mapping.

Important APIs/types/functions: macros: `_ASM_DELAY_H`, `udelay(usecs)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/param.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/dma.h

Purpose: Hexagon legacy DMA constants.

Important APIs/types/functions: macros: `_ASM_DMA_H`, `MAX_DMA_CHANNELS`, `MAX_DMA_ADDRESS`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/io.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/elf.h

Purpose: Hexagon ELF machine constants, relocations, and executable/core-dump ABI.

Important APIs/types/functions: types: `elf32_hdr`, `linux_binprm`; macros: `__ASM_ELF_H`, `R_HEXAGON_NONE`, `R_HEXAGON_B22_PCREL`, `R_HEXAGON_B15_PCREL`, `R_HEXAGON_B7_PCREL`, `R_HEXAGON_LO16`, `R_HEXAGON_HI16`, `R_HEXAGON_32`, `R_HEXAGON_16`, `R_HEXAGON_8`, `R_HEXAGON_GPREL16_0`, `R_HEXAGON_GPREL16_1`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/ptrace.h`, `asm/user.h`, `linux/elf-em.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/exec.h

Purpose: Hexagon stack alignment policy for exec.

Important APIs/types/functions: macros: `_ASM_EXEC_H`, `STACK_MASK`, `arch_align_stack(x)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/fixmap.h

Purpose: Hexagon fixed-address mapping declarations.

Important APIs/types/functions: macros: `_ASM_FIXMAP_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/mem-layout.h`, `asm-generic/fixmap.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/fpu.h

Purpose: placeholder FPU architecture header for Hexagon.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/futex.h

Purpose: Hexagon futex atomic user-memory operations.

Important APIs/types/functions: functions: `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`; macros: `_ASM_HEXAGON_FUTEX_H`, `__futex_atomic_op(insn,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/hexagon_vm.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/hexagon_vm.h

Purpose: Hexagon virtual-machine trap IDs, cache/interrupt ops, and MMU bitfields.

Important APIs/types/functions: functions: `__vmcache_ickill`, `__vmcache_dckill`, `__vmcache_l2kill`, `__vmcache_dccleaninva`, `__vmcache_icinva`, `__vmcache_idsync`, `__vmcache_fetch_cfg`, `__vmintop_nop`, `__vmintop_globen`, `__vmintop_globdis`, `__vmintop_locen`, `__vmintop_locdis`, `__vmintop_affinity`, `__vmintop_get`, `__vmintop_peek`, `__vmintop_status`, `__vmintop_post`, `__vmintop_clear`; types: `VM_CACHE_OPS`, `VM_INT_OPS`; macros: `ASM_HEXAGON_VM_H`, `HVM_TRAP1_VMVERSION`, `HVM_TRAP1_VMRTE`, `HVM_TRAP1_VMSETVEC`, `HVM_TRAP1_VMSETIE`, `HVM_TRAP1_VMGETIE`, `HVM_TRAP1_VMINTOP`, `HVM_TRAP1_VMCLRMAP`, `HVM_TRAP1_VMNEWMAP`, `HVM_TRAP1_FORMERLY_VMWIRE`, `HVM_TRAP1_VMCACHE`, `HVM_TRAP1_VMGETTIME`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/hexagon_vm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/intrinsics.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/intrinsics.h

Purpose: compiler builtin aliases for Hexagon instructions.

Important APIs/types/functions: macros: `_ASM_HEXAGON_INTRINSICS_H`, `HEXAGON_P_vrmpyhacc_PP`, `HEXAGON_P_vrmpyh_PP`, `HEXAGON_R_cl0_R`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/intrinsics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/io.h

Purpose: Hexagon raw I/O accessors, ioremap protection, and phys/virt conversion.

Important APIs/types/functions: functions: `virt_to_phys`, `phys_to_virt`, `__raw_readb`, `__raw_readw`, `__raw_readl`, `__raw_writeb`, `__raw_writew`, `__raw_writel`; macros: `_ASM_IO_H`, `__raw_readb`, `__raw_readw`, `__raw_readl`, `__raw_writeb`, `__raw_writew`, `__raw_writel`, `_PAGE_IOREMAP`, `virt_to_phys`, `phys_to_virt`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/types.h`, `asm/page.h`, `asm/cacheflush.h`, `asm-generic/io.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irq.h

Purpose: Hexagon IRQ count and CPU interrupt declarations.

Important APIs/types/functions: types: `pt_regs`; macros: `_ASM_IRQ_H_`, `HEXAGON_CPUINTS`, `NR_IRQS`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/irq.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irqflags.h

Purpose: local interrupt enable/disable/save/restore over Hexagon VM calls.

Important APIs/types/functions: functions: `arch_local_save_flags`, `arch_local_irq_save`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_irq_restore`; macros: `_ASM_IRQFLAGS_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/hexagon_vm.h`, `linux/types.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/kgdb.h

Purpose: KGDB register sizing and breakpoint constants.

Important APIs/types/functions: functions: `arch_kgdb_breakpoint`; macros: `__HEXAGON_KGDB_H__`, `BREAK_INSTR_SIZE`, `CACHE_FLUSH_IS_SAFE`, `BUFMAX`, `DBG_USER_REGS`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/linkage.h

Purpose: assembly alignment/linkage constants.

Important APIs/types/functions: macros: `__ASM_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mem-layout.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mem-layout.h

Purpose: Hexagon virtual-memory layout constants and fixmap ranges.

Important APIs/types/functions: types: `fixed_addresses`; macros: `_ASM_HEXAGON_MEM_LAYOUT_H`, `PAGE_OFFSET`, `PHYS_OFFSET`, `PHYS_PFN_OFFSET`, `ARCH_PFN_OFFSET`, `TASK_SIZE`, `STACK_TOP`, `STACK_TOP_MAX`, `MIN_KERNEL_SEG`, `VMALLOC_START`, `VMALLOC_OFFSET`, `FIXADDR_TOP`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/const.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mem-layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu.h

Purpose: Hexagon mm context state including VDSO pointer.

Important APIs/types/functions: types: `mm_context`, `hexagon_vdso`; macros: `_ASM_MMU_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/vdso.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu_context.h

Purpose: Hexagon mm activation and context-switch hooks.

Important APIs/types/functions: functions: `switch_mm`, `activate_mm`; types: `task_struct`; macros: `_ASM_MMU_CONTEXT_H`, `activate_mm`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/mm_types.h`, `asm/setup.h`, `asm/page.h`, `asm/pgalloc.h`, `asm/mem-layout.h`, `asm-generic/mm_hooks.h`, `asm-generic/mmu_context.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/page.h

Purpose: Hexagon page-size, page-type, huge-page, and address-conversion definitions.

Important APIs/types/functions: functions: `clear_page`, `virt_to_pfn`; types: `page`; macros: `_ASM_PAGE_H`, `HEXAGON_L1_PTE_SIZE`, `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `HVM_HUGEPAGE_SIZE`, `pte_val(x)`, `pgd_val(x)`, `pgprot_val(x)`, `__pte(x)`, `__pgd(x)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/const.h`, `vdso/page.h`, `linux/pfn.h`, `asm/mem-layout.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/perf_event.h

Purpose: minimal perf-event architecture header.

Important APIs/types/functions: macros: `_ASM_PERF_EVENT_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; perf stat/record, callchain, and overflow tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgalloc.h

Purpose: Hexagon page-table allocation/free helpers.

Important APIs/types/functions: functions: `pgd_alloc`, `pmd_populate`, `pmd_populate_kernel`; macros: `_ASM_PGALLOC_H`, `__pte_free_tlb(tlb,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/mem-layout.h`, `asm/atomic.h`, `asm-generic/pgalloc.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgtable.h

Purpose: Hexagon page-table bit layout, protection helpers, and swap encoding.

Important APIs/types/functions: functions: `set_pte`, `pmd_clear`, `pte_clear`, `pmd_none`, `pmd_present`, `pmd_bad`, `pte_none`, `pte_present`, `pte_mkold`, `pte_mkyoung`, `pte_mkclean`, `pte_mkdirty`, `pte_young`, `pte_dirty`, `pte_modify`, `pte_wrprotect`, `pte_mkwrite_novma`, `pte_mkexec`; macros: `_ASM_PGTABLE_H`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXECUTE`, `_PAGE_USER`, `_PAGE_PRESENT`, `_PAGE_DIRTY`, `_PAGE_ACCESSED`, `_PAGE_VALID`, `_PAGE_SWP_EXCLUSIVE`, `PGDIR_SHIFT`, `PTRS_PER_PGD`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/page.h`, `asm-generic/pgtable-nopmd.h`, `asm/vm_mmu.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/processor.h

Purpose: Hexagon thread state, switch stack, task register accessors, and CPU relax.

Important APIs/types/functions: types: `task_struct`, `thread_struct`, `hexagon_switch_stack`; macros: `_ASM_PROCESSOR_H`, `INIT_THREAD`, `cpu_relax()`, `TASK_UNMAPPED_BASE`, `task_pt_regs(task)`, `KSTK_EIP(tsk)`, `KSTK_ESP(tsk)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/mem-layout.h`, `asm/registers.h`, `asm/hexagon_vm.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/ptrace.h

Purpose: Hexagon ptrace helpers layered on the UAPI register layout.

Important APIs/types/functions: macros: `_ASM_HEXAGON_PTRACE_H`, `current_pt_regs()`, `arch_has_single_step()`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `uapi/asm/ptrace.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/setup.h

Purpose: Hexagon setup declarations and UAPI setup inclusion.

Important APIs/types/functions: macros: `_ASM_HEXAGON_SETUP_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/init.h`, `uapi/asm/setup.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/signal.h

Purpose: Hexagon signal header integration with generic signal definitions.

Important APIs/types/functions: macros: `_ASM_SIGNAL_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/signal.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/smp.h

Purpose: Hexagon SMP declarations and current CPU lookup.

Important APIs/types/functions: types: `ipi_message_type`; macros: `__ASM_SMP_H`, `raw_smp_processor_id()`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/cpumask.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/spinlock.h

Purpose: Hexagon raw spinlock and rwlock operations.

Important APIs/types/functions: functions: `arch_read_lock`, `arch_read_unlock`, `arch_read_trylock`, `arch_write_lock`, `arch_write_trylock`, `arch_write_unlock`, `arch_spin_lock`, `arch_spin_unlock`, `arch_spin_trylock`; macros: `_ASM_SPINLOCK_H`, `arch_spin_is_locked(x)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/irqflags.h`, `asm/barrier.h`, `asm/processor.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/spinlock_types.h

Purpose: Hexagon raw lock type initializers.

Important APIs/types/functions: macros: `_ASM_SPINLOCK_TYPES_H`, `__ARCH_SPIN_LOCK_UNLOCKED`, `__ARCH_RW_LOCK_UNLOCKED`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/string.h

Purpose: provides Hexagon architecture declarations for `string`.

Important APIs/types/functions: macros: `_ASM_STRING_H_`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMSET`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/suspend.h

Purpose: Hexagon suspend header guard placeholder.

Important APIs/types/functions: functions: `arch_prepare_suspend`; macros: `_ASM_SUSPEND_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/switch_to.h

Purpose: Hexagon context-switch macro and switch entry declarations.

Important APIs/types/functions: types: `thread_struct`, `task_struct`; macros: `_ASM_SWITCH_TO_H`, `switch_to(p,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscall.h

Purpose: Hexagon syscall register access helpers for tracing and seccomp.

Important APIs/types/functions: functions: `syscall_get_nr`, `syscall_set_nr`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arch`; types: `pt_regs`; macros: `_ASM_HEXAGON_SYSCALL_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `uapi/linux/audit.h`, `linux/err.h`, `asm/ptrace.h`, `asm-generic/syscalls.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscalls.h

Purpose: Hexagon syscall declarations via generic syscall header.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/syscalls.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/thread_info.h

Purpose: Hexagon thread_info layout, fixed register lookup, and thread flags.

Important APIs/types/functions: types: `thread_info`, `task_struct`, `pt_regs`; macros: `_ASM_THREAD_INFO_H`, `THREAD_SHIFT`, `THREAD_SIZE`, `THREAD_SIZE_ORDER`, `INIT_THREAD_INFO(tsk)`, `qqstr(s)`, `qstr(s)`, `QUOTED_THREADINFO_REG`, `current_thread_info()`, `TIF_SYSCALL_TRACE`, `TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/processor.h`, `asm/registers.h`, `asm/page.h`, `asm/asm-offsets.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/time.h

Purpose: Hexagon time header placeholder.

Important APIs/types/functions: macros: `ASM_TIME_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/timex.h

Purpose: Hexagon timer frequency and current-timer support.

Important APIs/types/functions: functions: `read_current_timer`; macros: `_ASM_TIMEX_H`, `CLOCK_TICK_RATE`, `ARCH_HAS_READ_CURRENT_TIMER`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/timex.h`, `asm/hexagon_vm.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/tlb.h

Purpose: Hexagon TLB gather integration.

Important APIs/types/functions: macros: `_ASM_TLB_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/pagemap.h`, `asm/tlbflush.h`, `asm-generic/tlb.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/tlbflush.h

Purpose: Hexagon TLB invalidation interfaces.

Important APIs/types/functions: macros: `_ASM_TLBFLUSH_H`, `flush_tlb_pgtables(mm,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/mm.h`, `asm/processor.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/traps.h

Purpose: Hexagon trap-number declarations.

Important APIs/types/functions: macros: `_ASM_HEXAGON_TRAPS_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/registers.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/uaccess.h

Purpose: Hexagon user access declarations and inline copy selection.

Important APIs/types/functions: macros: `_ASM_UACCESS_H`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `__clear_user(a,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/sections.h`, `asm-generic/uaccess.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; boot, mmap, page-fault, futex/locking, DMA, and usercopy stress tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/unistd.h

Purpose: Hexagon syscall-number UAPI inclusion and wanted legacy syscalls.

Important APIs/types/functions: macros: `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_SYS_VFORK`, `__ARCH_WANT_SYS_FORK`, `__ARCH_BROKEN_SYS_CLONE3`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `uapi/asm/unistd.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vdso.h

Purpose: Hexagon VDSO data structure declarations.

Important APIs/types/functions: types: `hexagon_vdso`; macros: `__ASM_VDSO_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/types.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vermagic.h

Purpose: Hexagon module version magic string.

Important APIs/types/functions: macros: `_ASM_VERMAGIC_H`, `MODULE_ARCH_VERMAGIC`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/stringify.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_fault.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_fault.h

Purpose: Hexagon VM fault declarations.

Important APIs/types/functions: macros: `_ASM_HEXAGON_VM_FAULT_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_fault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_mmu.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_mmu.h

Purpose: Hexagon VM MMU PDE/PTE encoding constants.

Important APIs/types/functions: macros: `_ASM_VM_MMU_H`, `__HVM_PDE_S`, `__HVM_PDE_S_4KB`, `__HVM_PDE_S_16KB`, `__HVM_PDE_S_64KB`, `__HVM_PDE_S_256KB`, `__HVM_PDE_S_1MB`, `__HVM_PDE_S_4MB`, `__HVM_PDE_S_16MB`, `__HVM_PDE_S_INVALID`, `__HVM_PDE_PTMASK_4KB`, `__HVM_PDE_PTMASK_16KB`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vm_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vmalloc.h

Purpose: Hexagon vmalloc architecture hook placeholder.

Important APIs/types/functions: macros: `_ASM_HEXAGON_VMALLOC_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/Kbuild

Purpose: architecture Kbuild object aggregation and generated header selection.

Important APIs/types/functions: build rules: `syscall-y += unistd_32.h`; `generic-y += ucontext.h`

Control flow: Kbuild evaluates these object lists and conditionals at build time; runtime flow comes from the selected objects.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on Linux Kbuild/Kconfig evaluation and the configuration symbols or objects named by the rules.

Risks: Configuration drift can silently omit required objects or expose unsupported option combinations in cross-builds.

Test signals: Hexagon cross-build; defconfig, allyesconfig, and allmodconfig build checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/byteorder.h

Purpose: Hexagon user ABI byte-order declaration.

Important APIs/types/functions: macros: `_ASM_BYTEORDER_H`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `linux/byteorder/little_endian.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/param.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/param.h

Purpose: Hexagon user ABI parameter constants.

Important APIs/types/functions: macros: `_ASM_PARAM_H`, `EXEC_PAGESIZE`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/param.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/ptrace.h

Purpose: Hexagon ptrace helpers layered on the UAPI register layout.

Important APIs/types/functions: macros: `_ASM_PTRACE_H`, `instruction_pointer(regs)`, `user_stack_pointer(regs)`, `profile_pc(regs)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/registers.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/hexagon/include/uapi/asm/ptrace.h -->
