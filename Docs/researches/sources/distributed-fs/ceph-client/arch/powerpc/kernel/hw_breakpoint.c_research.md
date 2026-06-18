# sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint.c

## Purpose
Implements PowerPC hardware watchpoint support for the generic Linux perf/hw_breakpoint and ptrace breakpoint facilities using DABR/DAWR-like debug registers.

## Important APIs, Types, And Functions
Public architecture hooks include `hw_breakpoint_slots`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `thread_change_pc`, `hw_breakpoint_handler`, `hw_breakpoint_exceptions_notify`, `flush_ptrace_hw_breakpoint`, `hw_breakpoint_pmu_read`, and `ptrace_triggered`. Internal helpers include `hw_breakpoint_validate_len`, `stepping_handler`, `handle_p10dd1_spurious_exception`, `single_step_dabr_instruction`, `handler_error`, and `larx_stcx_err`. Per-CPU state is `bp_per_reg[HBP_NUM_MAX]`.

## Control Flow
Install searches the current CPU's breakpoint slots, stores the `perf_event`, and programs hardware unless the breakpoint is waiting for single-step rearming. Parse translates perf attributes into PowerPC type bits, privilege filters, address, length, and hardware-aligned length. On DABR/DAWR exceptions, the handler disables breakpoints, reads instruction details, checks constraints for every active slot, handles ptrace one-shot semantics, rejects larx/stcx and unemulatable kernel instructions, emulates or arranges single-step, invokes perf callbacks after the triggering instruction, and finally reprograms surviving breakpoints. Single-step exceptions complete pending callback delivery and rearm hardware.

## State And Persistence
State lives in per-CPU breakpoint slot arrays, each `perf_event`'s `arch_hw_breakpoint`, debug registers programmed by `__set_breakpoint`, and `perf_single_step` flags used across an exception/single-step pair. Ptrace breakpoints are stored in `task_struct.thread.ptrace_bps[]`. State is in-memory and CPU-local; no durable persistence exists.

## Dependencies And Integration Points
Depends on perf events, generic hw_breakpoint callbacks, ptrace, notifier `DIE_DABR_MATCH`/`DIE_SSTEP`, PowerPC instruction analysis and emulation (`wp_get_instr_detail`, `analyse_instr`, `emulate_step`), DABR/DAWR helpers, CPU features including ARCH_31, and 8xx-specific behavior. It integrates with debug exception delivery, task PC changes, and ptrace SIGTRAP behavior.

## Risks And Edge Cases
Risks include DAWR length and 512-byte boundary constraints, extraneous hardware matches caused by alignment granularity, Power10 DD1 spurious VSX octword exceptions, larx/stcx instructions that cannot be emulated safely, user-mode single-step interactions with ptrace, concurrent perf event release under RCU, and forgetting to rearm breakpoints after exception handling. Kernel-mode emulation failure disables the breakpoint to prevent livelock.

## Test Signals
Useful tests include perf watchpoint selftests for read/write and privilege filters, ptrace hardware watchpoints, multi-slot watchpoints, unaligned and boundary-crossing lengths, user versus kernel watchpoints, single-step interaction, larx/stcx and VSX access cases, 8xx watchpoints, and fault injection around instruction fetch failure. Hardware coverage should include DABR-only, DAWR, Power10, and ARCH_31 systems.
