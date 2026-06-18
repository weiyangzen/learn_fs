# Research: subset-b-000743

Grouped research for MIPS kernel files under `sources/distributed-fs/ceph-client/arch/mips/kernel`. Each section preserves the source path for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event_mipsxx.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event_mipsxx.c

## Purpose
Implements the Linux perf PMU backend for MIPS hardware performance counters. It maps generic, cache, and raw perf events to CPU-family-specific CP0 PerfCtl/PerfCnt encodings, manages per-CPU counter allocation, handles overflows, and registers the MIPS PMU as the `"cpu"` perf provider during early boot.

## Important APIs, Types, and Functions
- `struct cpu_hw_events` stores per-CPU active `perf_event *` slots, counter-use bitmap, and saved PerfCtl values used when global PMU disable/enable pauses local counters.
- `struct mips_perf_event` describes a hardware event id, usable counter mask, and MIPS MT range (`T`, `V`, `P`) for thread/VPE/processor-wide counting.
- `struct mips_pmu mipspmu` is the selected runtime PMU descriptor: counter width, overflow bit, IRQ, event maps, raw mapper, and read/write counter callbacks.
- `mipspmu_event_init()`, `__hw_perf_event_init()`, `mipspmu_add()`, `mipspmu_del()`, `mipspmu_start()`, `mipspmu_stop()`, and `mipspmu_read()` implement the `struct pmu` operations.
- `mipsxx_pmu_read_counter*()`, `mipsxx_pmu_write_counter*()`, `mipsxx_pmu_read_control()`, and `mipsxx_pmu_write_control()` access CP0 performance registers, including VPE counter swizzling for shared TC counters.
- `mipsxx_pmu_map_raw_event()` and `octeon_pmu_map_raw_event()` validate raw perf configs and infer counter masks for CPU-specific event banks.
- `mipsxx_pmu_handle_shared_irq()` is the core overflow handler, used directly or via `mipsxx_pmu_handle_irq()`.
- `init_hw_perf_events()` detects supported CPU families, chooses event/cache maps, counter widths, IRQ source, resets counters, and calls `perf_pmu_register()`.

## Control Flow
Initialization starts at `early_initcall(init_hw_perf_events)`: it counts hardware counters, adjusts for shared TC counter mode, discovers the perf IRQ, selects maps based on `current_cpu_type()`, determines 32/48/64-bit counter behavior, resets all counters on all CPUs, and registers the PMU. When a perf event is opened, `mipspmu_event_init()` rejects branch stack sampling and unsupported types, lazily reserves the IRQ path using `active_events` and `pmu_reserve_mutex`, maps the requested event, initializes period accounting, validates group counter fit, and installs `hw_perf_event_destroy()`. Adding an event allocates a compatible counter from `used_mask`, disables any stale hardware state, attaches the event to `cpuc->events[idx]`, and optionally starts it. Starting programs the sample period and saved control word; stopping disables counting, updates software counts, and marks the perf event stopped/up-to-date. On overflow, the handler pauses local counters, takes the shared-TC read lock when configured, scans active counters for the overflow bit, updates periods, calls `perf_event_overflow()`, resumes counters, and runs pending irq work.

## State and Persistence
State is hardware and per-CPU rather than persistent across boots. `DEFINE_PER_CPU(cpu_hw_events)` tracks current counter assignment. `mipspmu` is global static runtime configuration chosen once at boot. `active_events` and `pmu_reserve_mutex` manage lazy IRQ reservation lifetime. `raw_event` is a shared scratch descriptor protected by `raw_event_mutex`. Hardware CP0 PerfCtl/PerfCnt registers hold programmed events and counts; `saved_ctrl[]` mirrors control words so counters can be paused/resumed around perf-wide disable and shared IRQ serialization. No filesystem persistence is involved.

## Dependencies and Integration Points
Integrates with the generic perf core (`struct pmu`, `perf_event_update_userpage()`, `perf_event_overflow()`), MIPS CP0 register accessors, CPU feature detection, MIPS MT/VPE topology, timer interrupt sharing through `perf_irq`, and platform IRQ discovery via `get_c0_perfcount_int` or `cp0_perfcount_irq`. CPU-family event tables cover MIPS 24K/34K/74K/proAptiv/P5600/P6600/I6400/I6500/1004K/1074K/interAptiv, Loongson32/64, Cavium Octeon, and BMIPS5000.

## Risks
Counter allocation is greedy and can reject valid groups if an earlier event occupies a counter needed by a more constrained event. Shared TC counters rely on careful pause/read-lock/write-lock ordering; mistakes can deadlock or count while disabled. Raw event validation is CPU-specific and easy to drift from hardware manuals. Loongson type 2 has 48-bit counters and 10-bit event ids, so generic 64-bit assumptions would misprogram counters. IRQ sharing with the timer depends on correct `perf_irq` save/restore. The overflow test relies on the configured overflow bit and counter masking.

## Test Signals
Boot logs should show `"Performance counters: <name> PMU enabled"` with expected counter count/width/IRQ. `perf stat` with generic events, cache events, and raw events should either count or return `EOPNOTSUPP` consistently per CPU. Event groups should fail cleanly when counter masks cannot fit. Overflow sampling should deliver samples and not lose timer interrupts when sharing the timer IRQ. CPU hotplug and perf open/close cycles should reset counters and release IRQ state without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event_mipsxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/perf_regs.c

## Purpose
Provides perf sampled-register support for MIPS. It reports the task ABI for sampled user registers, validates register masks, extracts selected registers from `struct pt_regs`, and wires user register sampling to the current task's saved pt_regs.

## Important APIs, Types, and Functions
- `perf_reg_abi()` returns `PERF_SAMPLE_REGS_ABI_32` on 32-bit kernels or for 32-bit-reg tasks on 64-bit kernels, otherwise `PERF_SAMPLE_REGS_ABI_64`.
- `perf_reg_validate()` rejects empty masks and masks with bits outside `PERF_REG_MIPS_MAX`.
- `perf_reg_value()` maps perf register indexes to `cp0_epc`, general registers r1-r25 and r28-r31, warning on unsupported indexes.
- `perf_get_regs_user()` fills `struct perf_regs` with `task_pt_regs(current)` and the ABI.

## Control Flow
The perf core calls these helpers when processing `PERF_SAMPLE_REGS_USER`/register masks. Validation occurs before sampling. During sample formatting, each requested index is translated from perf's compact MIPS register namespace to `pt_regs` fields and sign-extended through an `s64` return.

## State and Persistence
No persistent state. It reads task flags and pt_regs only at sample time.

## Dependencies and Integration Points
Depends on MIPS ptrace register layout, `TIF_32BIT_REGS`, `PERF_REG_MIPS_*` constants, and perf's generic sampled register ABI. It complements `ptrace.c`/`process.c` register dump helpers but intentionally exposes a perf-specific subset.

## Risks
Register namespace drift between perf constants and `pt_regs` layout would produce incorrect samples. Unsupported registers warn once and return zero, so mask validation must remain strict. Sign extension is intentional for 32-bit tasks but can surprise consumers expecting zero-extended values.

## Test Signals
Perf record/report with sampled user registers should show PC and requested GPRs for both 32-bit and 64-bit tasks. Invalid masks should return `-EINVAL`. ABI values in perf samples should match the traced task's execution mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/pm-cps.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/pm-cps.c

## Purpose
Implements power-management entry for MIPS CPS systems that can run cores non-coherently, clock-gate, or power-gate. It generates low-level entry/exit assembly at runtime so cache, CM, and CPC operations happen without compiler-inserted memory accesses in unsafe non-coherent windows.

## Important APIs, Types, and Functions
- `cps_nc_entry_fn` is the generated function signature used to enter a CPS PM state.
- `nc_asm_enter`, `ready_count`, `online_coupled`, `pm_barrier`, and `cps_cpu_state` are per-CPU/per-core state used for generated entry stubs and sibling VPE coordination.
- `cps_pm_support_state()` exposes state availability.
- `cps_pm_enter_state()` coordinates online coupled VPEs, prepares CPS boot config for power-gated restore, maps `ready_count` noncoherently, calls generated code, and restores coherent CPU tracking.
- `cps_gen_entry_code()` emits the state-specific assembly sequence using uasm.
- `cps_gen_cache_routine()`, `cps_gen_flush_fsb()`, and `cps_gen_set_top_bit()` emit cache loops, fill/store-buffer workaround code, and LL/SC synchronization snippets.
- `cps_pm_online_cpu()` generates per-core entry functions during CPU hotplug online.
- `cps_pm_power_notifier()` blocks suspend when a JTAG probe would make CPC power gating unsafe.
- `cps_pm_init()` detects CM/CPC capabilities and registers hotplug and PM notifiers.

## Control Flow
`arch_initcall(cps_pm_init)` checks for a CM, verifies that the idle wait function is safe with IRQs off for noncoherent wait, detects CPC clock-gate support, enables power-gating support only when CPS SMP is active, registers a suspend notifier, and installs a CPUHP online callback. On CPU online, `cps_pm_online_cpu()` generates missing entry routines per supported state and shares them with sibling VPEs, then allocates one core `ready_count`. Runtime entry via `cps_pm_enter_state()` calculates the online sibling set, optionally writes restart PC/GP/SP for power-gated restore, clears the CPU from `cpu_coherent_mask`, maps `ready_count` through `kmap_noncoherent()`, synchronizes coupled VPEs, calls the generated function, unmaps, restores `cpu_coherent_mask`, and for noncoherent wait may IPI siblings that remained in `wait`.

## State and Persistence
All state is runtime-only. Generated code buffers are allocated with `kcalloc()` and stored in per-CPU arrays for the life of the boot. `state_support` records available states. Per-core `ready_count` and `pm_barrier` coordinate sibling VPE state transitions. `cps_cpu_state` preserves CPU state for power gating. CM/CPC hardware registers carry the actual coherency and power commands.

## Dependencies and Integration Points
Depends on MIPS CPS/CM/CPC register helpers, CPU topology (`cpu_sibling_map`, `cpu_core`, `cpu_cluster`, `cpu_vpe_id`), cpuhotplug, suspend notifiers, uasm, cache descriptors, `mips_cps_pm_save/restore`, and `cpu_coherent_mask`. It integrates with cpuidle-like state entry even though it cannot use the generic coupled cpuidle barrier directly.

## Risks
This code is highly timing and ordering sensitive. Incorrect barriers or LL/SC loops can let a VPE touch L1 while another disables coherence. Generated code size/label arrays are fixed. The FSB flush workaround temporarily uses perf counters and can perturb counts. Power gating depends on valid CPS SMP boot config and correct restore entry addresses. Noncoherent mappings of `ready_count` must be initialized and unmapped exactly once. JTAG suspend blocking is essential to avoid NoC hangs.

## Test Signals
Boot logs should advertise available/unavailable PM states with warnings for missing CM/CPC or unsafe wait functions. CPU hotplug online should generate entry functions without `"Failed to generate"` errors. Repeated cpuidle/suspend cycles should not corrupt data or hang sibling VPEs. Suspend with EJTAG probe should abort. Cache coherency stress across idle transitions is the primary behavioral signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/pm-cps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/pm.c

## Purpose
Registers CPU power-management notifiers that save and restore generic MIPS CPU context around CPU PM entry/exit events.

## Important APIs, Types, and Functions
- `mips_static_suspend_state` is the global suspend-state storage used by macros in `asm/pm.h`.
- `mips_cpu_save()` saves live FPU state through `lose_fpu(1)` and DSP state through `save_dsp(current)`.
- `mips_cpu_restore()` restores ASID, DSP, UserLocal, and hardware watch registers.
- `mips_pm_notifier()` handles `CPU_PM_ENTER`, `CPU_PM_ENTER_FAILED`, and `CPU_PM_EXIT`.
- `mips_pm_init()` registers the notifier with `cpu_pm_register_notifier()`.

## Control Flow
At `arch_initcall`, the notifier is registered. Before CPU PM entry, `mips_cpu_save()` forces live architectural extension state into the task context. On failed entry or exit, `mips_cpu_restore()` rewrites CP0 EntryHi ASID for the current mm, restores DSP, restores TLS/UserLocal if supported, and reloads watch registers.

## State and Persistence
State is transient CPU/task context, persisted only across a CPU low-power transition. No filesystem persistence exists.

## Dependencies and Integration Points
Integrates with the generic CPU PM notifier chain, MIPS FPU/DSP/watch helpers, MMU ASID management, and UserLocal TLS support. CPS PM power gating uses these lower-level save/restore guarantees.

## Risks
Missing a register class here causes state loss after CPU PM. Restore only writes ASID for tasks with `current->mm`; kernel-thread behavior relies on that distinction. Watch register restore must match ptrace watchpoint state.

## Test Signals
Suspend/resume and CPU idle transitions should preserve FPU/DSP calculations, TLS, watchpoints, and address-space correctness. CPU PM notifier registration failures should be visible during init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/probes-common.h -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/probes-common.h

## Purpose
Provides common instruction classification helpers for MIPS kprobes/uprobes-style code. It declares compact-branch detection and implements delay-slot detection for classic MIPS branch/jump encodings.

## Important APIs, Types, and Functions
- `__insn_is_compact_branch()` is declared for external implementation.
- `__insn_has_delay_slot()` inspects `union mips_instruction` opcode/function fields and returns whether the instruction has a branch delay slot.

## Control Flow
The inline helper switches first on the primary opcode, then on nested function/rt fields for `spec_op` and `bcond_op`. It recognizes `jr`, `jalr`, conditional branches, branch-likely variants, `j`, `jal`, FPU/coprocessor branch opcodes, and Octeon bbit encodings when configured.

## State and Persistence
No state. Pure instruction classification.

## Dependencies and Integration Points
Depends on `asm/inst.h` instruction unions and opcode constants. Consumers are probe implementations that need to know whether placing or single-stepping a probe must account for a delay slot.

## Risks
Incomplete opcode coverage can make probes mishandle control flow. MIPS revisions with compact branches or vendor encodings require coordination with `__insn_is_compact_branch()` and architecture-specific configs. Returning true for all `cop1_op` is conservative but broad.

## Test Signals
Probe tests on branches, branch-likely instructions, `jr/jalr`, FPU branches, and Octeon bbit instructions should single-step correctly and not execute wrong delay-slot instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/probes-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/proc.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/proc.c

## Purpose
Formats MIPS `/proc/cpuinfo` output and provides a raw notifier chain for platform code to append CPU-specific cpuinfo lines.

## Important APIs, Types, and Functions
- `vced_count` and `vcei_count` track VCE D/I exception counters printed in cpuinfo.
- `register_proc_cpuinfo_notifier()` and `proc_cpuinfo_notifier_call_chain()` expose extension hooks.
- `show_cpuinfo()` emits per-CPU model, ISA, ASEs, options, topology, watchpoint, timer, cache, and platform data.
- `cpuinfo_op` is the exported `seq_operations` for procfs iteration.

## Control Flow
The procfs seq iterator maps positions to CPU indexes. `show_cpuinfo()` skips offline CPUs under SMP, prints system type and machine name for CPU 0, reports model/FPU/BogoMIPS/wait/timer/TLB/watch details, appends feature strings from `cpu_has_*` predicates, prints topology/VPE data, reports VCE counters, then invokes the notifier chain with `proc_cpuinfo_notifier_args`.

## State and Persistence
No persistent storage. It reads `cpu_data[]`, feature flags, topology, and exception counters at display time. The notifier chain is statically initialized and expected to be registered during early boot.

## Dependencies and Integration Points
Depends on MIPS CPU feature probing, `get_system_type()`, `mips_get_machine_name()`, seq_file, procfs, and optional platform notifiers. It consumes machine name set by `prom.c` and CPU data initialized by `setup.c`.

## Risks
Feature list drift can hide or misreport CPU capabilities. The raw notifier has no lock and is documented as early-boot-only for writes. CPU hotplug can produce sparse cpuinfo entries. Formatting changes may affect user-space parsers.

## Test Signals
`cat /proc/cpuinfo` should show correct system/machine names, online CPU entries, feature flags, watchpoint masks, topology, and notifier-provided platform lines. Offline CPUs should not print stale entries on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/process.c

## Purpose
Implements MIPS process/thread lifecycle support: starting user threads, copying task state, saving live CPU extension state, stack unwinding, blocked-task wait-channel reporting, user stack layout, SMP backtrace triggering, FP mode prctl support, and register dump helpers.

## Important APIs, Types, and Functions
- `start_thread()`, `exit_thread()`, `arch_dup_task_struct()`, and `copy_thread()` implement exec, exit cleanup, fork duplication, and kernel/user child register setup.
- `struct mips_frame_info`, instruction classifiers, `get_frame_info()`, `frame_info_init()`, `thread_saved_pc()`, `unwind_stack_by_address()`, `unwind_stack()`, and `__get_wchan()` implement schedule-prologue analysis and stack unwinding.
- `mips_stack_top()` and `arch_align_stack()` calculate user stack placement/randomization constraints.
- `arch_trigger_cpumask_backtrace()` sends asynchronous SMP backtrace IPIs.
- `mips_get_process_fp_mode()` and `mips_set_process_fp_mode()` implement MIPS FP mode reporting/switching.
- `mips_dump_regs32()` and `mips_dump_regs64()` format pt_regs for ptrace/core regsets.

## Control Flow
Exec through `start_thread()` drops kernel/FPU/MSA privileges, clears math state, initializes DSP, and sets PC/SP. Fork goes through `arch_dup_task_struct()` to save live FPU/MSA/DSP state before copying `task_struct`, then `copy_thread()` builds child pt_regs at the top of the kernel stack. Kernel threads get `ret_from_kernel_thread` and function arguments in saved registers; user clones inherit pt_regs, return zero in the child, optionally use a new user SP and TLS, and start at `ret_from_fork`. At init, `frame_info_init()` analyzes `__schedule`/`schedule` prologue so blocked task PCs can be recovered. Unwinding uses kallsyms function sizes and decoded stack-frame/RA-save instructions. FP mode changes validate support, update every thread's TIF flags, then schedule work on CPUs that may be running the process so old FPU modes are flushed.

## State and Persistence
State lives in `task_struct.thread`, `thread_info`, pt_regs on kernel stacks, TIF flags, and per-CPU call-single data for backtraces. `schedule_mfi` caches decoded scheduler frame info after boot. No disk persistence exists.

## Dependencies and Integration Points
Depends on low-level entry assembly (`ret_from_fork`, `ret_from_kernel_thread`), FPU/MSA/DSP helpers, delay-slot emulation cleanup, CPU feature flags, kallsyms, IRQ stacks, NMI backtrace framework, scheduler/task stack layout, MIPS ABI descriptors, VDSO sizing, GIC user page mapping, and ptrace regset dump consumers.

## Risks
Instruction decoding for stack unwinding is architecture-revision sensitive, especially microMIPS and Loongson encodings. Incorrect clone register setup can corrupt user ABI returns or kernel-thread startup. Live FPU/MSA/DSP state must be saved before task duplication to avoid stale child state. FP mode switching is process-wide and has races unless every potentially running CPU context-switches. User stack top calculation must leave space for delay-slot emulation, VDSO, GIC page, randomization, and cache coloring.

## Test Signals
Fork/clone/exec tests should validate child return values, TLS, and kernel-thread startup. Backtrace and `/proc/<pid>/wchan` should work through scheduler frames. `prctl(PR_SET_FP_MODE)` should accept/reject modes according to CPU and ABI and preserve FP results across threads. NMI backtrace should warn rather than corrupt state if a previous IPI is still busy. Core dumps/ptrace should show zeroed k0/k1 and correct register contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/prom.c

## Purpose
Provides generic MIPS device-tree/platform discovery helpers: machine name storage, early DT setup, DT bus population, and weak default device-tree unflattening.

## Important APIs, Types, and Functions
- `mips_set_machine_name()` stores a bounded machine name, logs it, and updates the dump-stack architecture description.
- `mips_get_machine_name()` returns the stored name.
- `__dt_setup_arch()` scans the flat DT and derives the machine name.
- `__dt_register_buses()` builds an OF match table for up to two bus compatibles and calls `of_platform_populate()`.
- `device_tree_init()` is a weak default that calls `unflatten_and_copy_device_tree()`.

## Control Flow
Platform setup may call `__dt_setup_arch()` with a boot parameter header. If `early_init_dt_scan()` succeeds, the flat DT machine name becomes the MIPS machine name. Later `__dt_register_buses()` requires a populated DT and turns selected buses into platform devices, panicking on missing DT or population failure.

## State and Persistence
The only persistent runtime state is the static `mips_machine_name[64]`, initialized to `"Unknown"`. DT nodes are copied/unflattened into normal kernel DT storage.

## Dependencies and Integration Points
Integrates with OF/flat-tree boot code, memblock-reserved DT handling in setup, debug/dump-stack descriptions, and proc cpuinfo machine-name reporting.

## Risks
Bus compatible strings are copied into a static local match table, so callers must fit OF compatible sizes. `__dt_register_buses()` panics instead of returning recoverable errors, appropriate for early platform bring-up but high impact. Machine names longer than 63 bytes are truncated.

## Test Signals
Boot with a DT should log `MIPS: machine is ...`, `/proc/cpuinfo` should show the same machine, and platform devices under the registered buses should appear. Missing DT for DT-only platforms should panic early and clearly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace.c

## Purpose
Implements native MIPS ptrace, user regset views, watchpoint access, FP/MSA/DSP regset access, register-name offset lookup, and syscall tracing entry/exit hooks.

## Important APIs, Types, and Functions
- `exception_ip()`, `ptrace_disable()`, `ptrace_getregs()`, and `ptrace_setregs()` expose basic exception PC and GPR access.
- `ptrace_get_watch_regs()` and `ptrace_set_watch_regs()` expose hardware watchpoint state with MIPS32/MIPS64 layouts.
- `gpr32_get/set()`, `gpr64_get/set()`, `fpr_get/set()`, `msa_get/set()`, `dsp32_get/set()`, `dsp64_get/set()`, and `fp_mode_get/set()` back ELF core/ptrace regsets.
- `task_user_regset_view()` chooses o32, n32, or n64 regset views from task flags.
- `regs_query_register_offset()` maps symbolic register names to `struct pt_regs` offsets.
- `arch_ptrace()` implements legacy ptrace requests.
- `syscall_trace_enter()` and `syscall_trace_leave()` integrate ptrace/seccomp/audit/tracepoints with syscall assembly paths.

## Control Flow
Native ptrace requests enter `arch_ptrace()`, which dispatches peek/poke memory to generic helpers, handles `PTRACE_PEEKUSR/POKEUSR` by switching on MIPS register numbers, delegates bulk GPR/FPR/watch requests, and falls back to `ptrace_request()`. Regset users call through selected `user_regset_view` based on task ABI flags. FPU setters initialize FP context before writes and mask FCSR writable bits. MSA getters pad unavailable vector lanes with all-ones fill and append control registers; setters mask exception/cause bits. Syscall assembly calls `syscall_trace_enter()` before dispatch when TIF flags require it; that function runs ptrace entry reporting, seccomp, tracepoints, audit, and negative-syscall cleanup. Exit tracing reports audit, tracepoints, ptrace exit, and re-enters user context tracking.

## State and Persistence
State resides in child task pt_regs, `thread.fpu`, `thread.dsp`, `thread.watch`, TIF flags, and `thread_info()->syscall`. Watchpoint load state is controlled through `TIF_LOAD_WATCH`. No persistent storage exists.

## Dependencies and Integration Points
Depends on generic ptrace/regset infrastructure, MIPS syscall helpers, audit, seccomp, ftrace syscall tracepoints, FPU/MSA/DSP/watch helpers, process FP mode functions, ELF note definitions, ABI flags, and syscall entry assembly. `process.c` provides register dump helpers and FP mode changes.

## Risks
ABI width and sign-extension behavior is subtle: GPR bulk access uses 64-bit formats for old native requests but regsets differ by view. Poking syscall registers must refresh `thread_info()->syscall`, including indirect syscall cases. FCSR/MSACSR masking prevents user injection of reserved exception bits. Watchpoint address validation differs for 32-bit address tasks on 64-bit kernels. The GPR set loops use `for (i = start; i < num_regs; i++)`, so partial writes must be reviewed carefully against intended `start + num_regs` semantics.

## Test Signals
`strace`, `gdb`, core dumps, and `PTRACE_GETREGSET/SETREGSET` should work for o32, n32, and n64 tasks. Hardware watchpoint tests should load/unload watch registers correctly. FP/MSA/DSP regset tests should preserve state and reject unavailable features with `-EIO`/`-ENODEV`. Seccomp and syscall tracepoints should skip or report syscalls exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace32.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace32.c

## Purpose
Implements compat ptrace handling for 32-bit tracers/tasks on 64-bit-capable MIPS configurations, including special 3264 memory peek/poke requests and 32-bit USER-area access.

## Important APIs, Types, and Functions
- `compat_arch_ptrace()` is the compat dispatcher.
- Handles `PTRACE_PEEKTEXT_3264`, `PTRACE_PEEKDATA_3264`, `PTRACE_POKETEXT_3264`, and `PTRACE_POKEDATA_3264` using a user-provided 64-bit target address pointer.
- Reuses native helpers for bulk GPR/FPR/watch register requests.
- Supports `PTRACE_GET_THREAD_AREA` and `PTRACE_GET_THREAD_AREA_3264`.

## Control Flow
The dispatcher narrows compat `addr`/`data`, then switches on request. The 3264 peek/poke cases first fetch the target process address from the tracer's user memory, then call `ptrace_access_vm()` with `FOLL_FORCE` and optional `FOLL_WRITE`. USER-area peek/poke mirrors native handling with 32-bit values, including FPU odd-register layout for 32-bit FP regs, DSP checks, PC/HI/LO writes, and syscall-number updates when r2 or indirect r4 changes. Unknown requests fall back to `compat_ptrace_request()`.

## State and Persistence
Mutates traced task pt_regs, FPU, DSP, and thread TLS/watch state. No persistent storage.

## Dependencies and Integration Points
Integrates with compat ptrace, native `ptrace_getregs/setregs`, `ptrace_getfpregs/setfpregs`, watch helpers from `ptrace.c`, FPU/DSP helpers, and MIPS syscall update helpers.

## Risks
Tracing mixed 32/64-bit processes is explicitly limited by comments. Pointer truncation/extension is the main risk: compat addresses must be cast carefully, while 3264 requests fetch a wider target address indirectly. Unlike native `ptrace_setfcr31()`, compat direct FCSR writes assign `fcr31` directly in some paths, so writable-bit masking differences are worth auditing. Partial VM access must return `-EIO`.

## Test Signals
32-bit `strace`/`gdb` on compat kernels should read/write GPRs, FPRs, DSP, watchpoints, TLS, and target memory. 3264 peek/poke should correctly access 64-bit target addresses supplied from compat user memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ptrace32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_fpu.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_fpu.S

## Purpose
Provides R2300/MIPS I floating-point save/restore routines and signal-context FPU copy helpers.

## Important APIs, Types, and Functions
- `_save_fp` and `_restore_fp` save/restore the thread FP context using single-precision macro helpers and export `_save_fp`.
- `_save_fp_context()` copies FP registers and FCSR from hardware to user signal context.
- `_restore_fp_context()` restores FP registers and FCSR from user signal context.
- `fault` returns `-EFAULT` via exception-table fixups.

## Control Flow
The thread context helpers are direct leaf routines that invoke `fpu_save_single`/`fpu_restore_single`. Signal helpers set `v0` to success, read/write `fcr31`, and store/load even double FP slots using exception-table-wrapped memory operations. On user fault, fixup redirects to `fault`, returning `-EFAULT`.

## State and Persistence
Moves state between hardware FP registers, task FP save area, and user signal frames. No persistent storage.

## Dependencies and Integration Points
Used by MIPS FPU context-switch and signal code through declarations in `signal-common.h` and FPU helpers. Depends on assembler FPU macros, `__ex_table`, and MIPS I instruction mode.

## Risks
User signal-frame copies must be exactly exception-protected. The R2300 path only handles the older single/paired register model, so using it on newer FP layouts would corrupt state. FCSR restore can trigger pending FP exception behavior expected by signal code.

## Test Signals
Signal delivery/return with FP-using programs on R2300-class builds should preserve FP registers and return `-EFAULT` for invalid signal-frame addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_switch.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_switch.S

## Purpose
Implements R2300-specific low-level task switching through the `resume` assembly entry.

## Important APIs, Types, and Functions
- `resume(prev, next, next_ti)` saves non-scratch CPU state in `prev`, restores `next`, updates kernel stack tracking, status, and returns `prev`.

## Control Flow
`resume` saves CP0 status, non-scratch registers, and RA into the previous task. It updates the stack protector canary on non-SMP stack-protector builds, moves `$28` to the next thread_info pointer, restores non-scratch registers from `next`, calculates the saved kernel stack pointer, writes `kernelsp`, merges preserved interrupt/status bits with `next` saved status, writes CP0 status, returns `prev` in `v0`, and jumps to the restored RA.

## State and Persistence
State is task context in `thread_struct`, `thread_info`, `kernelsp`, CP0 status, and optional `__stack_chk_guard`.

## Dependencies and Integration Points
Called by the scheduler's architecture switch path. Depends on `cpu_save_nonscratch`, `cpu_restore_nonscratch`, stackframe offsets, and R2300/MIPS I register conventions.

## Risks
The ordering around `$28`, `$29`, and `kernelsp` is intentional to avoid races without disabling interrupts. Incorrect status-bit masking can leak privilege or interrupt state. Stack protector update is only for !SMP and must match task canary storage.

## Test Signals
Context-switch stress should preserve callee-saved registers, stack pointer, status, and kernel stack tracking. Scheduler/fork tests on R2300 builds should return through `ret_from_fork` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r2300_switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r4k-bugs64.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/r4k-bugs64.c

## Purpose
Detects known 64-bit R4000/R4400 errata at boot and panics if required compiler/CPU workarounds are missing.

## Important APIs, Types, and Functions
- `check_mult_sh()` tests multiply/shift interaction errata across instruction alignments.
- `do_daddi_ov()` is a temporary overflow exception handler for DADDI testing.
- `check_daddi()` tests whether `daddi` correctly raises overflow.
- `check_daddiu()` tests DADDIU result correctness and records `daddiu_bug`.
- `check_bugs64_early()` runs early multiply/shift and DADDIU checks.
- `check_bugs64()` runs the later DADDI overflow check.

## Control Flow
Early setup calls `check_bugs64_early()` when configured. It runs carefully aligned inline assembly with interrupts disabled to detect errata-sensitive instruction sequences, compares raw and workaround results, and panics with a targeted workaround message if the workaround is absent. Later CPU finalize calls `check_bugs64()`, which installs an overflow exception vector, executes the DADDI sequence, restores the old handler, and verifies that either no bug exists or the workaround triggers expected overflow.

## State and Persistence
`daddiu_bug` records DADDIU bug detection. `daddi_ov` records whether the temporary overflow handler ran. No persistent storage.

## Dependencies and Integration Points
Integrated from `setup.c` via `check_bugs64_early()` and `arch_cpu_finalize_init()`/`check_bugs64()`. Depends on CP0 exception vector installation, context tracking in exception handlers, local IRQ control, and compiler workaround Kconfig options.

## Risks
The detection code intentionally executes errata-triggering sequences; incorrect alignment or compiler optimization could hide a bug. It manipulates exception vectors and must restore them. False negatives would allow unreliable CPU operation; false positives panic otherwise bootable systems.

## Test Signals
Boot logs should print the three bug checks and either `no`, `yes, workaround... yes`, or panic with a clear workaround instruction. Known affected CPUs should require the matching workaround configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r4k-bugs64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_fpu.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_fpu.S

## Purpose
Provides R4K/newer FPU and MSA context save/restore assembly, including signal-frame FP copy helpers and MSA upper-lane user-copy helpers.

## Important APIs, Types, and Functions
- `_save_fp`, `_restore_fp`, `_save_msa`, `_restore_msa`, and `_init_msa_upper` move task FP/MSA state to/from hardware.
- `_save_fp_context()` and `_restore_fp_context()` copy FPU state between hardware and user signal context with exception fixups.
- `read_msa_wr_*` and `write_msa_wr_*` generated leaf routines read/write one MSA vector register element width.
- `_save_msa_all_upper()` and `_restore_msa_all_upper()` copy upper 64-bit MSA lanes for signal context.
- `fault` returns `-EFAULT` for protected user-memory faults.

## Control Flow
Thread FP helpers read CP0 status when needed and invoke double-precision FPU macros. MSA helpers call MSA save/restore/init macros. Signal save reads FCSR, conditionally stores odd double registers only when FR=1 on relevant CPUs, stores even registers, stores FCSR, and returns zero. Restore loads FCSR and registers in the inverse order and writes FCSR. MSA indexed helpers jump through an inline table of 32 register-specific operations. Upper-lane helpers unroll all 32 vector registers, with endian and 32/64-bit-specific lane extraction/insertion.

## State and Persistence
Moves state among hardware FPU/MSA registers, task `thread.fpu`, and user signal buffers. No disk persistence.

## Dependencies and Integration Points
Used by FPU ownership/context switch code, ptrace/MSA regsets, and signal code through `signal-common.h`. Depends on hardfloat/MSA assembler support, `__ex_table`, CP0 status FR mode, endian configuration, and FPU/MSA macros.

## Risks
FR mode handling is critical: saving odd registers when FR=0 or failing to save them when FR=1 corrupts FP state. MSA upper-lane endian handling must match user ABI. All user stores/loads must have exception-table fixups. Indexed MSA helpers rely on exact table stride and register ordering.

## Test Signals
FP and MSA context-switch stress, signal delivery/return, ptrace MSA regset get/set, and invalid signal-frame fault injection should preserve registers or return `-EFAULT` correctly across endian and FR modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_switch.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_switch.S

## Purpose
Implements R4K/newer low-level task switching through the `resume` assembly entry.

## Important APIs, Types, and Functions
- `resume(prev, next, next_ti)` saves previous task nonscratch state, restores next task state, updates stack tracking, CP0 status, and returns the previous task.

## Control Flow
The routine stores CP0 status and callee-saved registers into `prev`, stores RA, updates stack canary on supported !SMP builds, sets `$28` to the next thread_info pointer, restores `next` nonscratch registers, computes the top-of-thread kernel stack, calls `set_saved_sp`, merges current status low bits with `next` saved status, writes CP0 status, returns `prev` in `v0`, and jumps to restored RA.

## State and Persistence
Task state is persisted in `thread_struct` across scheduler switches. Per-CPU kernel stack tracking is updated by `set_saved_sp`. CP0 status changes are hardware state.

## Dependencies and Integration Points
Scheduler switch path, stackframe macros, thread-info offsets, stack protector, and MIPS interrupt/status conventions.

## Risks
Race-sensitive ordering of `$28`, stack pointer, and saved kernel SP must be preserved. Status masking must not leak FPU/kernel/user bits. Assembly offset mismatches would corrupt tasks.

## Test Signals
Heavy context-switch and preemption tests should preserve callee-saved registers, per-task status, stack protector canary, and return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/r4k_switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/relocate.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/relocate.c

## Purpose
Implements boot-time kernel relocation and KASLR support for MIPS, including relocation-table application, exception-table relocation, optional FDT movement, command-line handling, and panic-time relocation reporting.

## Important APIs, Types, and Functions
- `plat_post_relocation()` and `plat_get_fdt()` are weak platform hooks.
- `sync_icache()` uses `synci` over the relocated image.
- `reloc_handler()` and relocation-specific helpers apply `R_MIPS_64`, `R_MIPS_32`, `R_MIPS_26`, and `R_MIPS_HI16`.
- `do_relocations()` walks `_relocation_start` to `_relocation_end`.
- `relocate_exception_table()` adjusts exception table entries.
- KASLR helpers `get_random_boot()`, `kaslr_disabled()`, and `determine_relocation_address()` choose relocation offset when `CONFIG_RANDOMIZE_BASE` is enabled.
- `relocate_kernel()` is the main entry returning the actual `start_kernel` address.
- `register_kernel_offset_dumper()` adds a panic notifier that prints relocated section addresses.

## Control Flow
`relocate_kernel()` initializes firmware command-line state and early DT, computes kernel and BSS lengths, chooses a relocation address, validates alignment/non-overlap, clears `arcs_cmdline` to avoid duplicates, optionally relocates an overlapping external FDT, copies text/data to the new location, applies relocations, syncs I-cache, relocates exception tables, copies BSS, notifies platform of FDT relocation and post-relocation fixups, updates `__current_thread_info`/`$gp` for the relocated image, computes relocated `start_kernel`, and records `__kaslr_offset`. If anything fails, it returns the original `start_kernel`.

## State and Persistence
Relocation mutates the in-memory kernel image copy, relocated BSS, exception table, FDT pointer/platform state, command-line buffers, `__current_thread_info`, and `__kaslr_offset`. No disk persistence.

## Dependencies and Integration Points
Depends on linker-provided relocation and section symbols, firmware command-line helpers, OF/FDT scanning, mem layout, cache synchronization instructions, panic notifier list, and platform hooks. `setup.c` later exports and reports `__kaslr_offset`.

## Risks
Relocation address must be 64 KiB aligned and not overlap the original image. `R_MIPS_26` can overflow if target high bits differ after relocation. `R_MIPS_HI16` handling is simplified and must match generated relocation records. External FDT movement must avoid overwriting the target image. Clang `$gp` workaround is delicate. A failed relocation path must leave original command-line and FDT state usable.

## Test Signals
Boots with and without `nokaslr` should reach `start_kernel`; `/proc/kallsyms`/panic notifier should reflect relocation when enabled. FDT bootargs should not duplicate. KASLR offset should vary with entropy and respect max offset. Relocation failures should fall back rather than crash before `start_kernel`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/relocate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/relocate_kernel.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/relocate_kernel.S

## Purpose
Provides the kexec relocation trampoline that copies pages described by the kexec indirection page, synchronizes caches, coordinates secondary CPUs, and jumps to the new kernel.

## Important APIs, Types, and Functions
- `relocate_new_kernel` is the primary kexec relocation entry.
- `kexec_smp_wait` is the secondary CPU wait path under SMP.
- Exported data: `kexec_args`, `secondary_kexec_args`, `kexec_start_address`, `kexec_indirection_page`, and `relocate_new_kernel_size`.

## Control Flow
`relocate_new_kernel` loads new-kernel arguments into `a0-a3`, loads the indirection page and start address, and loops over entries. Entries tagged as destination update `s4`; indirection entries redirect the descriptor pointer; source entries copy one page word-by-word to the current destination; done entries break. On completion, SMP builds clear a relocated `kexec_flag` so waiting CPUs may proceed, synchronize caches (`syncw/synci` for Octeon, `sync` otherwise), and jump to `kexec_start_address`. `kexec_smp_wait` loads secondary arguments and start address, computes relocated `kexec_flag`, spins until primary clears it, performs a final sync/hook, and jumps.

## State and Persistence
Uses exported in-memory argument and control words populated by the kexec core. Copies physical/virtual page contents during shutdown; no persistent storage.

## Dependencies and Integration Points
Integrated with generic kexec machine code. Depends on MIPS kexec page-list flag conventions, register ABI, cache synchronization requirements, SMP stop/wait protocol, and optional platform `kexec_smp_wait_final`.

## Risks
The trampoline runs while the old kernel may be overwritten, so it must use only safe addresses and relocated flag computation. Incorrect interpretation of page flags corrupts the new kernel image. Cache sync is CPU-specific. Secondary CPUs must not jump before relocation is complete.

## Test Signals
`kexec -e` and crash-kdump boots should transfer control with correct arguments. SMP kexec should not leave secondaries spinning forever. New kernel instruction fetch should work immediately after relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/reset.c

## Purpose
Provides generic MIPS restart, halt, poweroff, and final hang behavior, with platform hooks for machine-specific reset/halt implementations.

## Important APIs, Types, and Functions
- `_machine_restart`, `_machine_halt`, and exported `pm_power_off` are platform callback pointers.
- `machine_hang()` disables/masks interrupts and loops in low-power wait or busy loop.
- `machine_restart()`, `machine_halt()`, and `machine_power_off()` call platform/generic hooks, stop SMP, then hang if control returns.

## Control Flow
Restart first calls `_machine_restart` if installed, stops other CPUs on SMP, calls `do_kernel_restart()`, waits one second, logs failure, then hangs. Halt calls `_machine_halt`, stops SMP, and hangs. Poweroff calls `do_kernel_power_off()`, stops SMP, and hangs. `machine_hang()` disables interrupts, masks all interrupt lines, repeatedly executes `wait` directly on MIPS R CPUs or calls `cpu_wait()`, and clears Compare to avoid timer interrupts repeatedly waking the CPU.

## State and Persistence
Only runtime hardware state: interrupt masks, CP0 Compare, SMP stop state, and platform power/reset side effects. No persistence.

## Dependencies and Integration Points
Integrates with Linux reboot/poweroff core, platform reset hooks, SMP stop, CPU wait implementations, CP0 status/compare, and exported `pm_power_off` used by drivers/platforms.

## Risks
If platform hooks return, the system must reliably stop doing useful work. Calling `cpu_wait()` can re-enable interrupts, so the code remasks/disables afterward. Some CPUs wake from wait despite masked interrupts, requiring Compare clearing.

## Test Signals
Reboot, halt, and poweroff commands should either transition platform state or end in a quiet hang with interrupts masked. Failed reboot should log `"Reboot failed -- System halted"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx-mt.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx-mt.c

## Purpose
Initializes RTLX support for MIPS MT/APRP systems by registering character devices, wiring VPE notifications, and handling inter-VPE software interrupts.

## Important APIs, Types, and Functions
- `rtlx_module_init()` creates `/dev/rtlx*` character devices and registers the RTLX interrupt path.
- `rtlx_module_exit()` destroys devices and unregisters the char major.
- `rtlx_interrupt()` acknowledges/reenables the RTLX software interrupt and wakes all channel queues.
- `_interrupt_sp()` signals the service processor VPE by setting C_SW0 in VPE1 cause.
- `rtlx_dispatch()` dispatches pending RTLX software interrupts through `do_IRQ()`.

## Control Flow
Module init rejects non-MIPS-MT CPUs and systems without reserved AP/SP TCs, registers a dynamic char major using `rtlx_fops`, initializes waitqueues/mutexes/open counters for each RTLX channel, creates devices, registers VPE start/stop notifications, assigns `aprp_hook` on vectored-interrupt CPUs, and requests the RTLX IRQ. The IRQ handler temporarily disables VPEs, enables the software interrupt status bit, restores VPE state, and wakes reader/writer queues. Writes call `_interrupt_sp()` from `rtlx.c` to notify the SP.

## State and Persistence
Runtime state includes char major, device nodes, waitqueues in `channel_wqs`, `rtlx_notify`, `aprp_hook`, and VPE interrupt cause/status bits. No persistent storage.

## Dependencies and Integration Points
Depends on MIPS MT/VPE APIs, `mt_class`, `rtlx_fops` from `rtlx.c`, `aprp_cpu_index()`, Linux IRQ/device/char-dev APIs, and vectored interrupt support.

## Risks
Failure cleanup must destroy already created devices and unregister the char major. `request_irq()` currently passes `rtlx` as dev_id, which may be NULL before shared memory is initialized; this must remain compatible with IRQ free semantics. Non-vectored interrupt CPUs are rejected after devices are created, so cleanup path matters.

## Test Signals
On supported MIPS MT systems, `/dev/rtlx0..` should appear, SP notifications should wake reads/writes, and unloading should remove devices. Unsupported systems should return `-ENODEV` with clear warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx-mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx.c

## Purpose
Implements the RTLX shared-memory ring-buffer channel operations and file operations used for communication between Linux and a service-processor VPE on MIPS MT systems.

## Important APIs, Types, and Functions
- Globals `rtlx`, `channel_wqs`, `rtlx_notify`, and exported `aprp_hook` hold shared state.
- `rtlx_starting()` and `rtlx_stopping()` respond to VPE lifecycle notifications.
- `rtlx_open()` validates and attaches shared RTLX metadata, enforces single opener per channel, and marks channel state opened.
- `rtlx_release()`, `rtlx_read_poll()`, `rtlx_write_poll()`, `rtlx_read()`, and `rtlx_write()` implement channel lifecycle and ring-buffer I/O.
- `rtlx_fops` exposes open/release/read/write/poll/noop_llseek to the char devices.

## Control Flow
Open validates the minor index, increments an atomic open guard, waits for `vpe_get_shared()` and a non-NULL shared pointer when blocking, validates the pointer and RTLX id, initializes `rtlx`, then atomically changes the channel Linux state to opened. Reads poll for data in the Linux-facing ring; blocking reads sleep unless the SP is stopping. Writes poll for free space in the RT-facing ring; blocking writes sleep until space is available. `rtlx_read()` and `rtlx_write()` lock the channel mutex, compute wrapped copy lengths, copy to/from user in up to two segments, update ring indexes with memory barriers, and writes notify the SP through `_interrupt_sp()`.

## State and Persistence
State is shared memory (`struct rtlx_info` and `struct rtlx_channel` indexes/buffers/states), waitqueues/mutexes/open counters, and `sp_stopping`. No disk persistence. Ring indexes are the durable state for in-flight channel data while the SP program is loaded.

## Dependencies and Integration Points
Integrates with VPE loader shared-memory APIs, RTLX IRQ init in `rtlx-mt.c`, Linux character device operations, waitqueue/poll APIs, user copy helpers, and MIPS memory barriers.

## Risks
Shared memory is concurrently accessed by another VPE, so `smp_rmb()`/`smp_wmb()` ordering is important. Ring buffers intentionally keep one byte empty to distinguish full from empty. Blocking open/read/write must handle signals and SP stopping. Invalid shared pointers or RTLX ids must be rejected before dereference. Partial user copies update indexes only for copied bytes.

## Test Signals
Opening the same channel twice should return `-EBUSY`. Nonblocking open without SP should return `-ENOSYS`; blocking open should wake when SP starts. Read/write wraparound should preserve byte order, poll should report readable/writable states, and writes should trigger SP interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/rtlx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall32-o32.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/scall32-o32.S

## Purpose
Implements 32-bit MIPS o32 syscall entry and the o32 indirect `sys_syscall` helper for 32-bit kernels.

## Important APIs, Types, and Functions
- `handle_sys` is the o32 syscall exception entry.
- `sys_syscall` implements the userspace `syscall(__NR_x, ...)` indirection helper.
- `sys_call_table` is exported from `asm/syscall_table_o32.h`.

## Control Flow
`handle_sys` saves partial pt_regs with `SAVE_SOME`, enables interrupts, advances EPC past the syscall instruction, saves `a3` for restart, copies arguments 5-8 from the user stack into pt_regs with exception-table fixups, stores the original syscall number in `TI_SYSCALL`, optionally calls `syscall_trace_enter()`, range-checks the o32 syscall number, loads the table entry, calls it, converts negative errno returns into positive errno plus error flag in `PT_R7`, stores the result in `PT_R2`, and exits through `syscall_exit_partial`. Bad user stack or missing syscall produces `EFAULT`/`ENOSYS`.

## State and Persistence
Mutates the current exception frame, thread-info syscall field, and return registers. No persistent storage.

## Dependencies and Integration Points
Depends on MIPS entry stackframe macros, user access macros, o32 syscall numbering, `syscall_trace_enter/leave` from `ptrace.c`, and generic syscall table generation. Optional MIPS MT FPU-affinity aliases scheduler affinity syscalls.

## Risks
Argument 5-8 stack copying is fragile and intentionally uses a coarse stack pointer sanity check. Indirect syscall handling must avoid recursion and shift arguments correctly. Error convention relies on `-EMAXERRNO` threshold and o32 `a3` error flag.

## Test Signals
o32 syscall ABI tests should validate six/eight-argument syscalls, indirect `syscall()`, invalid syscall numbers, bad user stack faulting, tracing/seccomp skip paths, and errno flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall32-o32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n32.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n32.S

## Purpose
Implements n32 compatibility syscall entry on 64-bit MIPS kernels and falls through to n64 handling for non-n32 syscall numbers.

## Important APIs, Types, and Functions
- `handle_sysn32` is the n32 syscall entry.
- `sysn32_call_table` is exported from `asm/syscall_table_n32.h`.

## Control Flow
When o32 is not configured, the entry performs the initial exception save and EPC advance itself; otherwise it can be reached after shared entry setup. It checks whether `v0` is in the n32 syscall range, saves `a3`, records `TI_SYSCALL`, optionally calls `syscall_trace_enter()`, dispatches through `sysn32_call_table`, applies MIPS error flag/negation convention, stores the return value, and exits. If the number is not n32, it jumps to `handle_sys64`.

## State and Persistence
Mutates pt_regs and thread-info syscall state only.

## Dependencies and Integration Points
Integrates with 64-bit syscall entry chaining, ptrace/seccomp/audit trace hook, n32 syscall table generation, and shared `syscall_exit_partial`.

## Risks
The entry must coordinate with o32/n64 files so register save/EPC advance happens exactly once. Tracing can modify the syscall number, requiring revalidation before dispatch. Table offset arithmetic subtracts the n32 base and scales by 8.

## Test Signals
n32 ABI syscall tests should pass for normal, traced, seccomp-rejected, invalid, and modified syscall-number cases. Mixed o32/n32/n64 builds should route non-n32 calls correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n64.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n64.S

## Purpose
Implements native n64 syscall entry for 64-bit MIPS kernels.

## Important APIs, Types, and Functions
- `handle_sys64` is the n64 syscall entry.
- `sys_call_table` is exported from `asm/syscall_table_n64.h`.

## Control Flow
When no 32-bit compatibility entry has already performed common setup, `handle_sys64` saves pt_regs, enables interrupts, and advances EPC. It saves `a3`, records `TI_SYSCALL`, optionally calls `syscall_trace_enter()`, validates the syscall number against the n64 range, loads the target from `sys_call_table`, calls it, converts errno returns into MIPS error flag format, stores result and restart syscall number, and exits through `syscall_exit_partial`. Invalid calls return `ENOSYS`.

## State and Persistence
Mutates pt_regs and thread-info syscall state. No persistence.

## Dependencies and Integration Points
Depends on stackframe macros, n64 syscall numbering/table generation, syscall trace hooks from `ptrace.c`, and compatibility entry routing from o32/n32 files.

## Risks
Initial save/EPC advancement is conditional on compat config and must not duplicate setup. Error conversion must preserve restart data in `PT_R0`. Null table entries are treated as illegal syscalls.

## Test Signals
n64 syscall ABI, invalid syscall, ptrace/seccomp/audit tracing, restartable syscall, and mixed compat routing tests should pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-n64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-o32.S -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-o32.S

## Purpose
Implements o32 compatibility syscall entry on 64-bit MIPS kernels and routes non-o32 calls to n32 or n64 handlers.

## Important APIs, Types, and Functions
- `handle_sys` is the shared 64-bit-kernel syscall entry for o32 compatibility.
- `sys32_syscall` implements the o32 indirect syscall helper using 64-bit registers.
- `sys32_call_table` exports compat entries from `asm/syscall_table_o32.h`.

## Control Flow
The entry saves pt_regs, enables interrupts, advances EPC, checks whether `v0` is in the o32 range, sign-clears upper halves of a0-a3 for o32 semantics, saves `a3`, loads stack arguments 5-8 as 32-bit values with exception-table fixups, records `TI_SYSCALL`, optionally traces via `syscall_trace_enter()`, dispatches through the compat table, applies errno/error-flag convention, and exits. If the number is not o32, it jumps to `handle_sysn32` when configured or `handle_sys64` otherwise. `sys32_syscall` range-checks indirect syscalls and shifts arguments before jumping to the real entry.

## State and Persistence
Mutates pt_regs, thread-info syscall field, and return/error registers only.

## Dependencies and Integration Points
Depends on o32 compat syscall table, n32/n64 handlers, ptrace syscall hooks, MIPS stackframe/user exception table support, and ABI-specific sign/argument-width rules.

## Risks
o32-on-64 argument translation is easy to break: upper halves must be discarded and stack args loaded as words. Bad stack fixups must zero only failed trailing args. Routing to n32/n64 must preserve the already-saved exception frame. Tracing can change syscall numbers and requires revalidation.

## Test Signals
o32 compat tests on 64-bit kernels should cover six/eight-argument calls, indirect syscall, bad stack, invalid syscall, tracing-modified syscall number, and fallback to n32/n64 handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/scall64-o32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/segment.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/segment.c

## Purpose
Creates a debugfs view of MIPS segment-control register configuration for CPUs implementing the segments feature.

## Important APIs, Types, and Functions
- `build_segment_config()` formats access mode, physical address field, caching mode, and exception behavior for one segment config halfword.
- `segments_show()` reads `SegCtl0..2` and prints six segment rows.
- `segments_info()` creates `debugfs` file `mips/segments` when `cpu_has_segments`.

## Control Flow
At device init, `segments_info()` checks CPU support and creates the file under `mips_debugfs_dir`. Reading the file prints a header, reads CP0 segment control registers, formats each halfword, and associates rows with fixed virtual ranges: two 512M high segments and four lower segments.

## State and Persistence
No persistent state. Reads live CP0 segment-control registers.

## Dependencies and Integration Points
Depends on MIPS debugfs root from `setup.c`, CP0 `read_c0_segctl*()`, segment field constants, and seq_file show helpers.

## Risks
Only available when debugfs and CPU segments are enabled. Formatting assumes known access-mode encodings. If `mips_debugfs_dir` is unavailable, file creation may silently fail depending on debugfs behavior.

## Test Signals
On segment-capable CPUs, `/sys/kernel/debug/mips/segments` should show six rows with access mode, physical, caching, and EU fields matching CP0 registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/segment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/setup.c

## Purpose
Performs core MIPS architecture setup: CPU probing, command-line construction, memory/initrd/crashkernel setup, device tree initialization, resource registration, SMP possible-map setup, cache/page table initialization, bootloader RNG seed ingestion, debugfs root creation, and CPU finalize bug checks.

## Important APIs, Types, and Functions
- Globals `cpu_data`, `mips_machtype`, `arcs_cmdline`, `mips_io_port_base`, `__kaslr_offset`, `ARCH_PFN_OFFSET`, `kernelsp`, firmware args, and `mips_debugfs_dir`.
- `detect_memory_region()` probes mirrored memory size and adds memblock RAM.
- Initrd helpers parse `rd_start`/`rd_size`, sanitize addresses, optionally byte-swap Octeon initrd, and reserve memory.
- `bootmem_init()`, `early_parse_mem()`, `early_parse_memmap()`, `mips_reserve_vmcore()`, `mips_parse_crashkernel()`, and `request_crashkernel()` establish memory limits/reservations.
- `bootcmdline_init()` combines built-in, DT, and bootloader command lines according to Kconfig policy.
- `arch_mem_init()` orchestrates platform memory setup, early params, FDT reserved memory, bootmem, SWIOTLB/CMA, nosave reservation, and early memtest.
- `resource_init()`, `prefill_possible_map()`, `setup_rng_seed()`, `setup_arch()`, `debugfs_mips()`, coherency early params, and `arch_cpu_finalize_init()`.

## Control Flow
`setup_arch()` probes CPU/CM, initializes PROM, early consoles, CPU reports, optional early R4K bug checks, then calls `arch_mem_init()`. Memory init calls platform memory setup, makes memblock bottom-up, builds the command line, parses early params, ensures kernel sections are in memblock, reserves FDT memory, initializes bootmem/initrd limits, reserves vmcore/crashkernel/device tree/SWIOTLB/CMA/nosave memory, and runs early memtest. Setup then registers resources for each RAM range, runs platform SMP setup and possible CPU prefill, initializes caches and page tables, dumps memblock, and ingests a firmware RNG seed. Later init creates the MIPS debugfs root. CPU finalize records `udelay_val` and runs bug checks.

## State and Persistence
Boot-only state includes memblock maps/reservations, command-line buffers, initrd globals, crash resources, resource tree entries, CPU data, possible CPU map, debugfs root, DMA coherency default, and random seed ingestion. No filesystem persistence.

## Dependencies and Integration Points
Depends on platform hooks (`plat_mem_setup`, `plat_smp_setup`, `prom_init`, `plat_swiotlb_setup`), OF/FDT, memblock, initrd, crash dump/kexec, DMI, DMA/CMA, highmem/NUMA, CPU/cache/page-table code, firmware environment, and bug checks in `r4k-bugs64.c`.

## Risks
Command-line precedence is Kconfig-dependent and easy to duplicate if relocation/FDT paths leave stale buffers. Memblock highmem/lowmem limits must be set after `max_low_pfn` is known. Initrd address conversion must handle bootloader sign-extension mistakes. User `mem=` wipes previous RAM maps. Crashkernel allocation is constrained to 64M alignment below 512M by default. RNG seed must be zeroed after use. Resource registration assumes `UNCAC_BASE == IO_BASE`.

## Test Signals
Boot logs should show correct command line, memory map, initrd, crashkernel, CPU/cache info, and memblock reservations. `mem=`/`memmap=`/`rd_start`/`rd_size`/`coherentio`/`nocoherentio` should alter behavior as expected. Debugfs `mips` directory should exist with debugfs enabled. Kdump and initrd boot tests are key integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal-common.h -->
# sources/distributed-fs/ceph-client/arch/mips/kernel/signal-common.h

## Purpose
Declares common MIPS signal-frame helpers and FPU/MSA context assembly hooks shared by signal implementation files.

## Important APIs, Types, and Functions
- `DEBUGP` macro optionally logs signal debugging.
- `get_sigframe()` selects/allocates a user signal frame.
- `fpcsr_pending()` checks and clears pending FP exceptions in saved FCSR.
- `lock_fpu_owner()` and `unlock_fpu_owner()` disable preemption and page faults while preserving FPU ownership.
- `_save_fp_context()`, `_restore_fp_context()`, `_save_msa_all_upper()`, and `_restore_msa_all_upper()` are assembly helpers.
- `setup_sigcontext()` and `restore_sigcontext()` convert between pt_regs/task state and user `sigcontext`.

## Control Flow
Signal delivery code includes this header to choose frame placement, protect FPU ownership while copying FP state, call assembly save/restore helpers, and build/restore sigcontext. The header itself contains declarations and small locking macros only.

## State and Persistence
No state. It defines access to transient user signal frames and CPU/task FP state.

## Dependencies and Integration Points
Integrates with `r2300_fpu.S` or `r4k_fpu.S`, MIPS signal C files, FPU ownership/page fault rules, and user `sigcontext` ABI.

## Risks
Lock macros disable both preemption and page faults; callers must always pair them. Assembly helper prototypes must match exact calling convention and user pointer semantics. Signal ABI changes must remain compatible with existing user-space frames.

## Test Signals
Signal delivery and `sigreturn` tests with FP/MSA-using programs should preserve context, detect pending FCSR exceptions, and handle invalid user signal frames without losing FPU ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/signal-common.h -->
