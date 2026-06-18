# Research: subset-b-000793

Grouped research for PowerPC BPF JIT and perf sources. Each section preserves its source path and is bounded for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp64.c

## Purpose

This file implements the 64-bit PowerPC eBPF JIT compiler backend. It maps BPF virtual registers to PowerPC GPRs, emits prologue and epilogue code, emits helper/kfunc/BPF-to-BPF calls, supports tail calls, exception-boundary callbacks, private stacks, arena/probe memory, atomic operations, byte swapping, speculation barriers, and the main BPF instruction translation loop.

## Important APIs, Types, And Functions

- `bpf_jit_init_reg_mapping()` assigns BPF registers to PowerPC registers: return value to `r8`, args to `r3`-`r7`, callee-saved BPF registers to `r27`-`r31`, AX to `r12`, temporaries to `r9`/`r10`, and arena VM base to `r26`.
- Stack helpers `bpf_has_stack_frame()`, `bpf_jit_stack_local()`, `bpf_jit_stack_tailcallinfo_offset()`, `bpf_jit_stack_offsetof()`, and `bpf_jit_stack_size()` compute frame/redzone offsets for normal programs, subprograms, tail calls, and exception callbacks.
- `bpf_jit_build_prologue()` saves LR and nonvolatile registers when needed, initializes or propagates tail-call accounting, handles exception-boundary extra saves (`r14`-`r25`), reuses an exception boundary frame for callbacks, configures BPF frame pointer/private stack, and loads `arena_vm_start`.
- `bpf_jit_emit_common_epilogue()` and `bpf_jit_build_epilogue()` restore saved registers, tear down the frame, move BPF return value to ABI return register `r3`, return via `blr`, and append fentry stubs.
- `arch_bpf_stack_walk()` walks PowerPC stack frames for BPF callbacks using `current_stack_frame()` and `validate_sp()`.
- `bpf_jit_emit_func_call_rel()` emits direct helper/kfunc/subprogram calls, handling PC-relative kernels, TOC-relative addressing, module functions, ELF ABI v1 function descriptors, and initial-pass placeholder NOPs.
- `prepare_for_kfunc_call()` uses BTF function model metadata to sign-extend or zero-extend kfunc arguments according to the PowerPC C ABI.
- `bpf_jit_emit_tail_call()` emits bounds checks, tail-call count checks, program lookup from `struct bpf_array`, tail-call counter writeback, common epilogue teardown, and branch through CTR.
- `bpf_jit_bypass_spec_v1()`, `bpf_jit_bypass_spec_v4()`, and `bpf_stf_barrier()` implement JIT-side Spectre/STF mitigation decisions and fallback barrier code.
- `bpf_jit_emit_atomic_ops()` emits LL/SC loops for BPF atomic add/and/or/xor/xchg/cmpxchg and applies full `sync` ordering around fetch operations.
- `emit_atomic_ld_st()` emits acquire loads and release stores with `lwsync`.
- `bpf_jit_build_body()` is the central instruction dispatcher translating BPF ALU, endian, memory, atomic, load, call, branch, exit, tail-call, and probe-memory opcodes into PowerPC instructions.

## Control Flow

JIT compilation first initializes register mapping and runs sizing/codegen passes over the BPF instruction array. Prologue emission decides between redzone use and a real stack frame, then saves only seen nonvolatile registers except where exception handling forces broader saves. The body loop records `addrs[i]` offsets for each BPF instruction, marks seen nonvolatile registers, translates each opcode, and updates address entries for 64-bit immediates and verifier-generated zero-extension insns. Branch translation relies on the populated `addrs` table. Calls mark `SEEN_FUNC`, resolve function targets through BPF core helpers, optionally prepare kfunc arguments, and emit ABI-aware calls. Exits branch to the epilogue unless they are the final instruction. Tail calls bypass normal return by tearing down the current frame and branching to the target program body past its prologue.

## State And Persistence

The file does not persist state outside generated code and the passed `codegen_context`. Important mutable state is in `ctx`: register-use bitmaps, stack size, pass index, exception flags, `arena_vm_start`, user VM base, private stack pointer/size, and `seen` flags. Generated code stores runtime state in the current stack frame or redzone, especially saved nonvolatile registers and `tail_call_info`. Tail-call count is kept in the main program frame and subprogram frames may hold a pointer to that count. Atomic operations use CPU reservation state through `ldarx`/`lwarx` and `stdcx`/`stwcx`.

## Dependencies And Integration Points

This backend depends on Linux BPF core APIs (`struct bpf_prog`, BPF opcode helpers, `bpf_jit_get_func_addr()`, kfunc BTF models, extable support), PowerPC instruction emission macros from `bpf_jit.h`, PACA fields, TOC/kernelbase handling, security feature flags, cache/exception support, and kernel/module text helpers. It integrates with verifier decisions such as `verifier_zext`, kfunc metadata, arena/probe memory exception-table recovery, BPF tail-call arrays, fentry stubs, and architecture BPF stack walking.

## Risks And Edge Cases

High-risk areas are stack offset correctness across redzone, frame, private-stack, and exception-callback modes; ABI correctness for ELF v1/v2 and PC-relative kernels; branch offset calculations across multi-pass JIT emission; tail-call count interpretation as either value or pointer; probe-memory exception-table entries for multi-instruction unaligned loads/stores; arena base restoration; and memory-ordering semantics for atomic fetch operations. Speculation mitigation depends on runtime security features and CPU-specific barrier forms. Unsupported opcodes and unsupported byte/halfword atomics return errors, which must remain aligned with verifier expectations.

## Test Signals

Useful tests include BPF selftests on PowerPC64 for ALU32 zero extension, kfunc signed/unsigned arguments, helper calls from modules and core kernel, BPF-to-BPF calls, tail-call chains and limit enforcement, exception callbacks, arena/probe-memory loads/stores with fault injection, atomic fetch/cmpxchg behavior under SMP, endian conversion, Spectre/STF barrier selection, and branch offset stress programs. Kernel build coverage should include big/little endian, ELF ABI v1/v2, `CONFIG_PPC_KERNEL_PCREL`, Book3S/E500 security feature combinations, and private-stack/exception-boundary configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/net/bpf_jit_comp64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/8xx-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/8xx-pmu.c

## Purpose

This file registers a minimal no-interrupt perf PMU for PPC 8xx processors. It exposes CPU cycles, instruction count, ITLB load misses, and DTLB load misses using timebase, instruction-count support, and patched TLB miss paths rather than a conventional programmable PMC block.

## Important APIs, Types, And Functions

- `event_type()` maps generic hardware/cache perf events to internal `PERF_8xx_ID_*` identifiers.
- `get_insn_ctr()` combines the software `instruction_counter` high part with `SPRN_COUNTA` into a stable instruction counter.
- `mpc8xx_pmu_event_init()` validates that the requested event is supported.
- `mpc8xx_pmu_add()` snapshots initial counter values and enables instruction counting or patches ITLB/DTLB miss exit sites on first use.
- `mpc8xx_pmu_read()` computes deltas for timebase cycles, descending instruction count, and TLB miss counters, updating `event->count`.
- `mpc8xx_pmu_del()` reads the final value and disables the underlying instrumentation when the last user of that counter type goes away.
- `init_mpc8xx_pmu()` initializes ICTRL/CMPA/COUNTA and registers the PMU as `"cpu"`.

## Control Flow

Perf calls `event_init`, then `add` snapshots a baseline and may enable backing instrumentation. Reads recompute deltas using `local64_cmpxchg()` on `prev_count`. Deletion reads one last time, decrements per-event-type reference counts, and restores original TLB miss instructions or disables instruction counting when no users remain.

## State And Persistence

State is held in external counters `itlb_miss_counter`, `dtlb_miss_counter`, and `instruction_counter`, plus local atomic reference counts `insn_ctr_ref`, `itlb_miss_ref`, and `dtlb_miss_ref`. The file patches kernel instruction sites while TLB miss events are active. No persistent storage is used.

## Dependencies And Integration Points

It depends on PPC 8xx SPRs (`ICTRL`, `CMPA`, `COUNTA`), timebase `get_tb()`, text patching symbols for TLB miss paths, and generic perf PMU callbacks. It integrates with low-level TLB miss handlers through `patch_branch_site()` and `patch_instruction_site()`.

## Risks And Edge Cases

Instruction counting uses a high/low read loop to avoid torn values. TLB patching must be exactly paired with reference counts or the kernel may retain unnecessary instrumentation. The PMU declares `PERF_PMU_CAP_NO_INTERRUPT` and `PERF_PMU_CAP_NO_NMI`, so sampling-style expectations are not supported. The instruction delta wraps a 48-bit-style value and counts down, which is easy to regress.

## Test Signals

Test with `perf stat` for supported events, unsupported hardware/cache/raw events returning the right errors, concurrent users of the same event type, add/delete reference-count behavior, and post-delete verification that TLB miss exits are restored. Build coverage requires `CONFIG_PPC_8xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/8xx-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/Makefile

## Purpose

This Makefile wires PowerPC perf support into the kernel build. It selects common callchain/perf register objects, Book3S PMU cores and model drivers, Freescale embedded PMUs, hypervisor PMUs, PowerNV/KVM/VPA PMUs, 8xx PMU support, and architecture-width-specific objects.

## Important Rules

- Always builds `callchain.o`, `callchain_$(BITS).o`, and `perf_regs.o`.
- Adds `callchain_32.o` under `CONFIG_COMPAT`.
- Adds `core-book3s.o` under `CONFIG_PPC_PERF_CTRS`.
- Adds 64-bit Book3S model drivers, ISA 2.07 helpers, `generic-compat-pmu.o`, Power10, and `bhrb.o` through `obj64-*`.
- Adds `mpc7450-pmu.o` for 32-bit Book3S through `obj32-*`.
- Adds `imc-pmu.o`, Freescale embedded core/model drivers, hypervisor counter drivers, VPA PMU, KVM HV PMU, and 8xx PMU based on their config symbols.
- Appends `$(obj64-y)` only for `CONFIG_PPC64` and `$(obj32-y)` only for `CONFIG_PPC32`.

## Control Flow

Kbuild evaluates config symbols and architecture width, expanding the appropriate object lists into `obj-y`. There is no runtime control flow, but build-time selection controls which PMU registration initcalls are linked into the kernel.

## State And Persistence

No runtime state. Its persistent effect is build composition: enabling or disabling symbols changes the linked perf implementation set.

## Dependencies And Integration Points

The file integrates with Kbuild, PowerPC config symbols, and source files in this directory. Ordering matters because multiple PMU initcalls may attempt registration, and the selected object set determines which registration paths are available.

## Risks And Edge Cases

Duplicate inclusion risk exists when compatibility or width-specific objects overlap; here `callchain_32.o` can be built both as native 32-bit and compat support intentionally depending on config. Missing an object from the correct `obj32`/`obj64` list can cause unresolved symbols only for specific architecture builds.

## Test Signals

Useful signals are allmodconfig/allyesconfig and targeted PPC32/PPC64 builds for `CONFIG_COMPAT`, `CONFIG_PPC_PERF_CTRS`, `CONFIG_FSL_EMB_PERF_EVENT`, `CONFIG_HV_PERF_CTRS`, `CONFIG_PPC_8xx`, and KVM/PowerNV combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/bhrb.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/bhrb.S

## Purpose

This assembly file provides `read_bhrb(n)`, a small helper used by Book3S perf code to read a Branch History Rolling Buffer entry by index.

## Important APIs, Types, And Functions

- `_GLOBAL(read_bhrb)` accepts an index in `r3`, returns the selected BHRB entry in `r3`, and returns zero for indexes greater than 31.
- `bhrb_table` contains 32 fixed instruction stubs generated by `MFBHRB_TABLE*` macros, each executing `PPC_MFBHRBE(R3,n)` followed by `blr`.

## Control Flow

The function bounds-checks `n <= 31`, loads the address of `bhrb_table`, scales the index by eight bytes because each entry is two instructions, branches through CTR to the selected stub, and returns the hardware BHRB value. Out-of-range indexes branch to a zero return.

## State And Persistence

No software state is stored. The helper reads processor BHRB state via the `mfbhrbe` instruction.

## Dependencies And Integration Points

It depends on PowerPC assembler macros from `ppc_asm.h` and `ppc-opcode.h`. `core-book3s.c` calls `read_bhrb()` while building perf branch stacks for sampled events.

## Risks And Edge Cases

The hard limit of 32 entries matches POWER8 implementation assumptions even though the instruction can address more entries. Table entry size and index scaling must stay in sync with the two-instruction stubs. Invalid indices safely return zero.

## Test Signals

Build coverage for Book3S 64-bit perf with BHRB support is essential. Runtime testing should use `perf record -b` or branch-stack sampling on BHRB-capable hardware and validate out-of-range reads do not fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/bhrb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.c

## Purpose

This file provides common PowerPC perf callchain collection. It handles kernel stack frame walking and dispatches user stack unwinding to 32-bit or 64-bit implementations.

## Important APIs, Types, And Functions

- `valid_next_sp()` validates 16-byte alignment, current-task stack validity, monotonic frame growth, and legitimate interrupt-stack-to-process-stack transitions.
- `perf_callchain_kernel()` stores the current instruction pointer, walks kernel frame records, detects interrupt frames using `STACK_FRAME_REGS_MARKER`, switches context back to kernel after interrupt frames, and records LR-derived caller addresses.
- `perf_callchain_user()` stores the current IP, checks `current->mm`, and dispatches to `perf_callchain_user_64()` or `perf_callchain_user_32()`.

## Control Flow

Kernel unwinding starts from `regs->gpr[1]` and `regs->link`. Each frame yields `next_sp`; interrupt frames replace `regs`, `next_ip`, and `lr` from saved registers. Normal frames use LR for the first caller and saved LR for later callers, filtering suspicious first frames to zero rather than deleting them. User unwinding is architecture-width-specific.

## State And Persistence

The file stores callchain entries into the perf-provided `perf_callchain_entry_ctx`. It does not persist data beyond the sample. It reads current task stack state and `pt_regs`.

## Dependencies And Integration Points

It depends on PowerPC stack frame layout constants, `validate_sp()`, `validate_sp_size()`, perf callchain APIs, `perf_arch_instruction_pointer()`, and the user unwind functions declared in `callchain.h`.

## Risks And Edge Cases

Stack validation is the safety boundary. Interrupt-frame detection must match actual stack layout. Early frame LR ambiguity is handled conservatively by recording zero for obviously invalid addresses. Kernel unwinding is marked `__no_sanitize_address` because it inspects raw stack frames.

## Test Signals

Use `perf record -g` in kernel-heavy workloads, interrupt-heavy workloads, and mixed user/kernel samples. Validate callchains around interrupt entry/exit, task stacks, and stack overflow guards. KASAN builds should confirm the sanitizer exclusion remains sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.h

## Purpose

This header shares declarations and helpers for PowerPC perf user callchain unwinding.

## Important APIs, Types, And Functions

- Declares `perf_callchain_user_64()` and `perf_callchain_user_32()`.
- `invalid_user_sp()` validates nonzero user stack pointer, architecture-specific alignment, and an upper bound below `STACK_TOP`.
- `__read_user_stack()` checks task address range and alignment before using `copy_from_user_nofault()`.

## Control Flow

The user unwind implementations call `invalid_user_sp()` before frame reads and `__read_user_stack()` for each nofault user memory access. The helper returns `-EFAULT` for out-of-range or misaligned pointers before attempting a copy.

## State And Persistence

No state is stored. The helpers read user memory only for the current sample.

## Dependencies And Integration Points

It depends on `is_32bit_task()`, `STACK_TOP`, `TASK_SIZE`, and Linux nofault copy APIs. It is included by common, 32-bit, and 64-bit callchain files.

## Risks And Edge Cases

The alignment mask differs between 32-bit and 64-bit tasks. Because callchains can be collected at interrupt level, the nofault copy path is mandatory. Bounds checks must avoid wraparound via `addr > TASK_SIZE - size`.

## Test Signals

Test 32-bit compat and 64-bit user callchains, invalid stack pointers, alternate signal stacks, and sampling at interrupt level where page faults cannot be handled normally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_32.c

## Purpose

This file implements 32-bit PowerPC user-space perf callchain unwinding, including native 32-bit and compat-on-64-bit signal frame handling.

## Important APIs, Types, And Functions

- Compatibility typedefs map 32-bit signal frame structures when not building `CONFIG_PPC64`.
- `read_user_stack_32()` wraps `__read_user_stack()` for 32-bit words.
- `struct signal_frame_32` and `struct rt_signal_frame_32` describe non-RT and RT signal frame layouts.
- `is_sigreturn_32_address()` and `is_rt_sigreturn_32_address()` detect trampoline addresses either inside the frame or in the VDSO.
- `sane_signal_32_frame()` and `sane_rt_signal_32_frame()` verify saved register pointers in signal frames.
- `signal_frame_32_regs()` identifies a valid signal frame and returns its saved GPR array.
- `perf_callchain_user_32()` walks user frames, handles signal frame restarts, and stores callchain IPs.

## Control Flow

The unwinder starts from `regs->gpr[1]`, `regs->link`, and `perf_arch_instruction_pointer()`. For each frame, it reads the next stack pointer and, after the first level, the saved return address. It checks whether the current frame is a signal frame using `next_ip` or early LR fallback. On signal frames, it reloads NIP/LR/R1 from saved user registers, resets level, emits a user context marker, and continues. Otherwise it stores LR for level zero or the frame return address for later levels.

## State And Persistence

State is local to a sample: stack pointer, LR, next IP, level, and perf callchain entry cursor. It reads user stack and signal frame memory with nofault copies.

## Dependencies And Integration Points

It depends on 32-bit PowerPC signal frame layout, VDSO symbols `sigtramp32` and `sigtramp_rt32`, `PT_NIP`/`PT_LNK`/`PT_R1`, perf callchain storage, and helpers from `callchain.h`.

## Risks And Edge Cases

Signal frame size checks intentionally allow `next_sp < sp` for alternate signal stack transitions. Incorrect VDSO or frame layout assumptions can break unwinding through signal handlers. User memory reads can fail at any point and terminate the unwind safely.

## Test Signals

Use 32-bit user processes, compat tasks on PPC64, signal handlers, RT and non-RT signals, alternate signal stacks, and corrupted stack tests under `perf record -g`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_64.c

## Purpose

This file implements 64-bit PowerPC user-space perf callchain unwinding, including signal frame recovery.

## Important APIs, Types, And Functions

- `read_user_stack_64()` wraps `__read_user_stack()` for 64-bit words.
- `struct signal_frame_64` models the 64-bit signal frame including ucontext, trampoline, siginfo, and ABI gap.
- `is_sigreturn_64_address()` detects frame-local or VDSO `sigtramp_rt64` return trampolines.
- `sane_signal_64_frame()` verifies `pinfo` and `puc` pointers point to the signal frame's embedded `info` and `uc`.
- `perf_callchain_user_64()` walks frame records and restarts unwinding from signal frame saved registers.

## Control Flow

The unwinder reads the next stack pointer from the frame and, after level zero, reads saved IP from `fp[2]`. It treats a sufficiently large frame with a recognized sigreturn address and sane embedded pointers as a signal frame, then loads saved NIP/LR/R1 from `uc.uc_mcontext.gp_regs`, emits a user context marker, stores the resumed IP, and continues. Normal frames store LR at level zero and saved frame IP thereafter.

## State And Persistence

Only per-sample local variables and the perf callchain entry are modified. User memory is accessed through nofault copies.

## Dependencies And Integration Points

It depends on 64-bit PowerPC ABI frame layout, VDSO `sigtramp_rt64`, signal/ucontext structures, `PT_*` register indexes, and common callchain helpers.

## Risks And Edge Cases

The saved return address slot differs from 32-bit (`fp[2]`). Alternate signal stack transitions rely on unsigned size arithmetic. Bad user memory terminates the unwind safely. Signal-frame pointer sanity protects against mistaking arbitrary frames for signal frames.

## Test Signals

Run `perf record -g` on 64-bit processes with nested calls, signal handlers, alternate stacks, and VDSO trampolines. Include tests for invalid stack alignment and unreadable user pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/callchain_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/core-book3s.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/core-book3s.c

## Purpose

This is the central Book3S PowerPC perf PMU implementation. It manages per-CPU hardware event state, event constraint solving, MMCR/PMC programming, BHRB branch stacks, EBB support, sampling data, PMU interrupts, CPU hotplug preparation, and registration of model-specific `struct power_pmu` backends.

## Important APIs, Types, And Functions

- `struct cpu_hw_events` holds per-CPU active events, event encodings, flags, computed MMCRs, limited-counter tracking, transaction state, BHRB state, and sampled PMC snapshots.
- `ppmu` is the registered model-specific `struct power_pmu`.
- Register helpers `read_pmc()`, `write_pmc()`, `write_mmcr0()`, `perf_read_regs()`, `perf_get_misc_flags()`, `perf_get_data_addr()`, and `perf_arch_instruction_pointer()` abstract PMC/MMCR/SIAR/SDAR/SIER behavior across CPU generations.
- BHRB helpers `power_pmu_bhrb_enable()`, `power_pmu_bhrb_disable()`, `power_pmu_sched_task()`, `power_pmu_bhrb_read()`, and `power_pmu_bhrb_to()` reset, configure, and export branch history.
- EBB helpers `is_ebb_event()`, `ebb_event_check()`, `ebb_event_add()`, `ebb_switch_out()`, and `ebb_switch_in()` validate exclusive per-task EBB events and context-switch user-visible PMU registers.
- Constraint and scheduling helpers `power_check_constraints()`, `check_excludes()`, `collect_events()`, `can_go_on_limited_pmc()`, and `normal_pmc_alternative()` decide if event groups fit hardware constraints and alternatives.
- PMU callbacks include `power_pmu_event_init()`, `power_pmu_add()`, `power_pmu_del()`, `power_pmu_start()`, `power_pmu_stop()`, `power_pmu_read()`, and transaction callbacks.
- Interrupt path functions `record_and_restart()`, `__perf_event_interrupt()`, and `perf_event_interrupt()` account overflows, generate samples, and restart counters.
- `register_power_pmu()` installs a model PMU and registers the generic `"cpu"` PMU.
- `init_ppc64_pmu()` probes model-specific PMUs then falls back to `init_generic_compat_pmu()`.

## Control Flow

Model drivers call `register_power_pmu()`, which sets `ppmu`, configures sysfs groups and capabilities, registers the perf PMU, and installs CPU hotplug preparation. Event initialization translates generic/cache/raw perf events through `ppmu`, checks blacklist and config validity, adjusts hypervisor exclusion, handles limited PMC alternatives, validates EBB and branch stack options, tests group constraints, reserves PMU hardware, and initializes period counters. Adding an event disables the PMU, appends the event, optionally checks constraints immediately or defers under transaction, enables BHRB if needed, and re-enables the PMU. Enabling recomputes MMCRs when events changed, moves counters if necessary, initializes PMCs, handles limited counters, configures BHRB and EBB, and unfreezes counters. Disabling freezes counters, clears pending PMI state, disables instruction sampling/BHRB, saves EBB user state, and clears SIAR/SDAR on capable CPUs. PMIs read all PMCs, identify overflows, account and restart events, handle POWER7 rollback quirks, restore MMCR0, and publish sample timing.

## State And Persistence

Runtime state is per-CPU in `cpu_hw_events`, global in `ppmu`, `freeze_events_kernel`, `num_events`, and `pmc_reserve_mutex`, and per-event in `event->hw`. EBB state persists in `current->thread` fields across context switches. BHRB context is tracked per CPU to avoid leaking branch entries between tasks. PMU hardware reservation is reference-counted by `num_events`.

## Dependencies And Integration Points

This file integrates deeply with Linux perf core, PowerPC SPR accessors, model PMU drivers (`power5` through `power11`, `ppc970`, generic compat), firmware feature detection, CPU hotplug, hard/soft IRQ handling, branch target decoding, BHRB assembly helper `read_bhrb()`, KVM/PMU in-use tracking, sysfs PMU attributes, and generic sample data APIs.

## Risks And Edge Cases

Risk concentrates around concurrency and hardware quirks: PMIs can behave like NMIs under soft-disabled interrupts; limited PMC5/6 counters do not respect freeze conditions; POWER7 can roll back speculative counts; POWER8E requires the PMAO restore workaround; SIAR/SIER validity varies across generations; Power10 privilege bits can be unreliable; BHRB can leak kernel or cross-task branch data if not reset/filtered; EBB has strict grouping semantics and user-visible register state; and event alternatives/constraints must match model-specific encodings exactly.

## Test Signals

Test signals include model-specific PowerPC perf selftests, `perf stat`/`perf record` for generic, raw, cache, branch-stack, and memory data source events; grouped event schedulability; EBB exclusive task events; limited PMC behavior; CPU hotplug; interrupt-heavy sampling; POWER7/POWER8E/POWER10 quirk coverage; sysfs event/caps exposure; and `perf_event_print_debug()` output on supported hardware. Build coverage should include PPC32 stubs and PPC64 Book3S configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/core-book3s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/core-fsl-emb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/core-fsl-emb.c

## Purpose

This file implements the Freescale embedded PowerPC perf PMU core used by e500/e6500-style model drivers. It registers a `"cpu"` PMU, manages PMR counters and control registers, allocates restricted/nonrestricted counters, translates perf events through model-specific tables, handles overflows, and reserves PMU hardware.

## Important APIs, Types, And Functions

- `struct cpu_hw_events` tracks per-CPU active events, disabled state, and whether PMCs have been enabled.
- `ppmu` points to the active `struct fsl_emb_pmu` model backend.
- `read_pmc()`, `write_pmc()`, `write_pmlca()`, and `write_pmlcb()` access PMR counter and local control registers.
- `fsl_emb_pmu_read()` atomically accounts 32-bit counter deltas.
- `fsl_emb_pmu_disable()` freezes counters via `PMGC0_FAC`; `fsl_emb_pmu_enable()` enables interrupts/counter exceptions when events exist.
- `fsl_emb_pmu_add()` allocates a counter top-down, preserving restricted-capable counters when possible, programs PMC/PMLCA/PMLCB, and updates userpage state.
- `fsl_emb_pmu_del()`, `fsl_emb_pmu_start()`, and `fsl_emb_pmu_stop()` remove or control sampled counters.
- `fsl_emb_pmu_event_init()` translates hardware/cache/raw events via `ppmu`, validates restricted event capacity in groups, sets PMLCA freeze bits, initializes periods, and reserves hardware.
- `record_and_restart()` and `perf_event_interrupt()` account overflows and call `perf_event_overflow()`.
- `register_fsl_emb_pmu()` installs the model PMU and CPU hotplug prepare callback.

## Control Flow

A model driver calls `register_fsl_emb_pmu()`. On event initialization, generic/cache/raw events are translated by the model `xlate_event()` and checked for validity/restriction. Adding an event disables the PMU, finds a usable counter, initializes count and state, writes PMC/PMLCB/PMLCA, and re-enables the PMU. Reads account 32-bit deltas. Interrupt handling scans all model counters for negative values, restarts active overflowed events, clears inactive overflowed counters, sets `MSR_PMM`, and re-enables PMGC0 interrupt/freeze behavior.

## State And Persistence

Per-CPU state is in `cpu_hw_events`. Global hardware reservation state is in `num_events` and `pmc_reserve_mutex`. Per-event state is in `event->hw.idx`, `config`, `config_base`, `prev_count`, `period_left`, and `state`. The PMU hardware registers persist programmed event selection until changed or cleared.

## Dependencies And Integration Points

It depends on `asm/reg_fsl_emb.h` PMR definitions, generic perf PMU callbacks, PowerPC PMU reservation hooks, firmware/hardware PMC enable hooks, CPU hotplug state `CPUHP_PERF_POWER`, and model data from `e500-pmu.c`/`e6500-pmu.c`.

## Risks And Edge Cases

Restricted counters are capacity-checked but there is a TODO to migrate nonrestricted events if restricted needs change. Counter allocation from the top down is important for restricted events. Counters are 32-bit, so delta masking must remain correct. Interrupt handling assumes negative counter values indicate overflow. Exclude idle is unsupported. Hardware reservation must be balanced by `event->destroy`.

## Test Signals

Use `perf stat` and sampling on e500/e6500 systems for generic, cache, raw, restricted threshold events, group capacity failures, add/delete/start/stop paths, and overflow sampling. Build and boot test `CONFIG_FSL_EMB_PERF_EVENT` with both model drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/core-fsl-emb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/e500-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/e500-pmu.c

## Purpose

This model driver supplies e500-family event maps and validation for the Freescale embedded PMU core.

## Important APIs, Types, And Functions

- `e500_generic_events[]` maps standard perf hardware events to e500 raw event codes.
- `e500_cache_events[][][]` maps perf cache event tuples to e500 raw event codes, with `0` unsupported and `-1` nonsensical.
- `e500_xlate_event()` validates raw event range, marks events 76-81 as restricted threshold-capable events, accepts threshold fields only for those events, and returns `FSL_EMB_EVENT_VALID` plus optional restriction/threshold bits.
- `e500_pmu` describes the PMU as `"e500 family"` with four counters and two restricted-capable counters.
- `init_e500_pmu()` checks PVR for e500v1/e500v2/e500mc/e5500, adjusts `num_events` to 256 for e500mc/e5500, and registers with `register_fsl_emb_pmu()`.

## Control Flow

At early init, PVR detection chooses whether this driver applies. If so, the PMU descriptor is registered. Later, the core calls `e500_xlate_event()` during perf event initialization and uses the generic/cache maps for standard perf event translation.

## State And Persistence

The file holds static event map tables and mutable `num_events`, changed during init for newer e500 variants. Runtime per-event/per-CPU state is managed by `core-fsl-emb.c`.

## Dependencies And Integration Points

It depends on PowerPC PVR constants, Freescale embedded event flag definitions, perf event enum values, and `register_fsl_emb_pmu()`.

## Risks And Edge Cases

Threshold bits on non-threshold events are rejected. The restricted event range must match hardware documentation. Generic cache mappings intentionally collapse or omit several cache concepts, so user-facing perf cache events may be unsupported or approximate.

## Test Signals

Test PVR-specific registration, raw events below and above `num_events`, threshold and non-threshold validation, restricted event group capacity through the core, and standard perf cache/hardware events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/e500-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/e6500-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/e6500-pmu.c

## Purpose

This model driver supplies e6500-family event maps and validation for the Freescale embedded PMU core.

## Important APIs, Types, And Functions

- `e6500_generic_events[]` maps CPU cycles, instructions, cache misses, branch instructions, and branch misses to raw codes.
- `e6500_cache_events[][][]` maps perf cache tuples to e6500 event codes.
- `e6500_xlate_event()` accepts raw event IDs below `num_events` and rejects all threshold fields.
- `e6500_pmu` describes the PMU as `"e6500 family"` with six counters and no restricted counter class.
- `init_e6500_pmu()` registers the PMU only when PVR is `PVR_VER_E6500`.

## Control Flow

Early init checks the CPU PVR. If it matches, the PMU descriptor is registered with the Freescale core. Perf event initialization later uses the tables and `e6500_xlate_event()`.

## State And Persistence

Static event tables and `num_events = 512` are the only local state. Runtime state is owned by `core-fsl-emb.c`.

## Dependencies And Integration Points

It depends on PVR definitions, Freescale PMU flags, perf event enums, and `register_fsl_emb_pmu()`.

## Risks And Edge Cases

Threshold fields are always invalid for e6500, unlike e500 restricted events. Several cache event tuples are unsupported or nonsensical. Raw event range must remain aligned with hardware documentation.

## Test Signals

Test PVR gating, raw event range limits, threshold rejection, six-counter allocation, generic hardware events, and cache events through `perf stat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/e6500-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/generic-compat-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/generic-compat-pmu.c

## Purpose

This file provides a generic ISA v3-compatible Book3S PMU backend for systems that implement architected Power ISA PMU events but do not match a more specific IBM PMU driver.

## Important APIs, Types, And Functions

- The event enum defines architected ISA v3.0B raw event codes such as cycles, instructions completed, branch mispredicts, cache/TLB misses, and run events.
- `generic_event_alternatives` and `generic_get_alternatives()` provide alternate encodings via `isa207_get_alternatives()`.
- `GENERIC_EVENT_ATTR()` and `CACHE_EVENT_ATTR()` declarations create sysfs event aliases.
- Format attributes expose `event`, `pmcxsel`, and `pmc` bit fields.
- `compat_generic_events[]` and `generic_compat_cache_events[][][]` map standard perf hardware/cache events to raw ISA event codes.
- `generic_compute_mmcr()` delegates to `isa207_compute_mmcr()` and then sets `MMCR0_C56RUN` for counters 5 and 6.
- `generic_compat_pmu` is the `struct power_pmu` descriptor using ISA207 constraint, alternative, disable, and compute helpers.
- `init_generic_compat_pmu()` requires `CPU_FTR_ARCH_300`, registers the PMU, and advertises EBB to userspace.

## Control Flow

When model-specific Book3S PMU probes fail, `init_ppc64_pmu()` calls this initializer. If the CPU supports ISA 3.0, it registers the generic PMU. Later, `core-book3s.c` uses this descriptor to translate events, compute MMCR settings, expose sysfs aliases, and manage perf callbacks.

## State And Persistence

The file contains static maps and one static `struct power_pmu`. It mutates `cur_cpu_spec->cpu_user_features2` to advertise EBB after successful registration.

## Dependencies And Integration Points

It depends on `isa207-common.h` for constraints/MMCR computation and sysfs helper macros, Book3S core registration via `register_power_pmu()`, CPU feature flags, and perf sysfs attribute groups.

## Risks And Edge Cases

The fallback applies only to ISA 3.0+ because older ISA 2.07 lacks required events. Generic mappings may be less precise than model-specific drivers. Setting `MMCR0_C56RUN` is required for counters 5/6 on selected events. Advertising EBB assumes generic ISA support is sufficient.

## Test Signals

Test fallback registration on non-IBM ISA v3 systems, sysfs event aliases and format fields, generic/cache event counting, grouped events through ISA207 constraints, counters 5/6 behavior, and EBB visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/generic-compat-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-catalog.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-catalog.h

## Purpose

This header defines packed structures for the Power hypervisor 24x7 event catalog, including the page-zero catalog header and individual event records used to generate perf sysfs events.

## Important APIs, Types, And Functions

- `struct hv_24x7_catalog_page_0` describes catalog magic, page length, version, timestamp, and offsets/lengths/counts for schema, event, group, and formula sections.
- `HV_24X7_CATALOG_MAGIC` is the ASCII `"24x7"` marker.
- `struct hv_24x7_event_data` describes one variable-length event entry with domain, group record offsets, counter offset, flags, group metadata, event name length, and trailing name/description/long-description data.

## Control Flow

No executable control flow. `hv-24x7.c` reads catalog pages through hcalls, interprets page zero, validates event entries with these layouts, and builds sysfs attributes from the variable-length event fields.

## State And Persistence

No local state. The packed structs describe hypervisor-provided persistent catalog data for the current platform.

## Dependencies And Integration Points

It depends on Linux fixed-width big-endian types and is consumed by `hv-24x7.c`. The field layout must match the external 24x7 catalog format.

## Risks And Edge Cases

Variable-length trailing data requires strict bounds checks. All multibyte fields are big-endian. Comments note uncertainty around catalog version semantics. Mismatches with firmware catalog format can corrupt sysfs event generation or cause skipped events.

## Test Signals

Validate catalog parsing on POWER systems with 24x7 support, malformed/truncated catalog simulation if available, sysfs event/description generation, and endian correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-catalog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-domains.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-domains.h

## Purpose

This macro include file defines the 24x7 performance domains and their metadata for enum generation, validation, sysfs formatting, and physical-domain permission checks.

## Important APIs, Types, And Functions

- `DOMAIN(PHYS_CHIP, 0x01, chip, true)`
- `DOMAIN(PHYS_CORE, 0x02, core, true)`
- `DOMAIN(VCPU_HOME_CORE, 0x03, vcpu, false)`
- `DOMAIN(VCPU_HOME_CHIP, 0x04, vcpu, false)`
- `DOMAIN(VCPU_HOME_NODE, 0x05, vcpu, false)`
- `DOMAIN(VCPU_REMOTE_NODE, 0x06, vcpu, false)`

Each entry carries an enum token, numeric hypervisor domain value, index-kind token, and physical/virtual flag.

## Control Flow

The file is included multiple times with different `DOMAIN` definitions. `hv-24x7.h` uses it to build `enum hv_perf_domains`; `hv-24x7.c` uses it to generate validation and physical-domain checks.

## State And Persistence

No state. It is a compile-time source of truth for 24x7 domain metadata.

## Dependencies And Integration Points

It integrates with `hv-24x7.h`, `hv-24x7.c`, perf sysfs format naming, and hcall request construction.

## Risks And Edge Cases

Because it is macro-included, field order and arity must remain stable across all consumers. The comment warns that catalog and hcall domain numbering are assumed to match and may need future changes.

## Test Signals

Build test all macro consumers, inspect `/sys/bus/event_source/devices/hv_24x7/interface/domains`, and validate physical vs virtual permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7.c

## Purpose

This file implements the `hv_24x7` perf PMU for hypervisor-supplied PowerVM 24x7 counters. It discovers platform/catalog metadata, creates sysfs event and description attributes, validates user event encodings, performs `H_GET_24X7_DATA` hcalls, batches perf read transactions, aggregates multi-element results where required, and handles CPU hotplug migration for its invalid-context PMU.

## Important APIs, Types, And Functions

- Global state includes `interface_version`, `aggregate_result_elements`, `hv_24x7_cpumask`, physical topology fields, `hv_page_cache`, per-CPU transaction flags/errors, per-CPU request/result buffers, and per-CPU request-index-to-event arrays.
- Domain helpers `domain_is_valid()`, `is_physical_domain()`, `domain_needs_aggregation()`, `domain_name()`, and `catalog_entry_domain_is_valid()` validate domain IDs and handle POWER8 v1 physical-domain limits.
- `read_24x7_sys_info()` queries PAPR system parameter 43 for sockets, chips per socket, and cores per chip.
- Format macros from `hv-common.h` define bit ranges for `domain`, `core`, `chip`, `vcpu`, `offset`, `lpar`, and reserved fields.
- Catalog helpers `event_name()`, `event_desc()`, `event_long_desc()`, `event_end()`, `catalog_event_len_validate()`, `create_events_from_catalog()`, and `catalog_read()` parse hcall catalog pages and expose sysfs metadata.
- Attribute helpers `event_fmt()`, `device_str_attr_create()`, `event_to_attr()`, `event_to_desc_attr()`, and `event_to_long_desc_attr()` create event, short description, and long description sysfs attributes.
- Request helpers `init_24x7_request()`, `add_event_to_24x7_request()`, `make_24x7_request()`, `get_count_from_result()`, and `single_24x7_request()` build and submit hcall buffers and parse returned data.
- Perf callbacks `h_24x7_event_init()`, `h_24x7_event_read()`, `h_24x7_event_start()`, `h_24x7_event_stop()`, `h_24x7_event_add()`, `h_24x7_event_start_txn()`, `h_24x7_event_commit_txn()`, and `h_24x7_event_cancel_txn()` implement event lifecycle and batched reads.
- `hv_24x7_init()` performs firmware/PVR gating, capability discovery, catalog sysfs setup, CPU hotplug setup, PMU registration, and topology readout.

## Control Flow

At device init, the driver requires LPAR firmware, selects interface v1 on POWER8 and v2 otherwise, enables result aggregation for POWER9 SMT8, checks hypervisor performance capabilities, creates a 4K page cache, builds sysfs event arrays from the hypervisor catalog, registers hotplug callbacks, registers the PMU, and reads topology. Catalog creation first reads page zero, validates lengths and offsets, vmallocs the event-data section, fetches all event pages, pre-scans and validates entries to size attribute arrays, then creates attributes while de-duplicating event names by domain.

Event initialization rejects nonmatching types, nonzero reserved bits, branch stack sampling, unaligned offsets, invalid domains, and insufficient hypervisor privileges for physical or other-LPAR events. It performs a test hcall to seed `prev_count`. Reads either queue the event into a per-CPU transaction request buffer or immediately performs a single hcall and updates the event count. Commit submits all queued requests and walks variable-sized results by `result_ix` to update the corresponding events. Stop and delete read the latest value because counters are always counting.

## State And Persistence

The driver stores platform state in globals and per-CPU hcall buffers. The generated sysfs event/description strings are intentionally leaked until shutdown so partial catalog failures do not invalidate registered attributes. Per-event state is `event->hw.prev_count` and `event->count`. No disk persistence exists; counters are hypervisor state read on demand.

## Dependencies And Integration Points

It depends on PAPR/PowerVM hcalls (`H_GET_24X7_CATALOG_PAGE`, `H_GET_24X7_DATA`), `hv_perf_caps_get()`, PAPR system parameters, PowerPC PVR and SMT topology, Linux perf PMU APIs, sysfs attribute groups, CPU hotplug, endian conversion, vmalloc/SLAB, and domain/request structs from `hv-24x7.h` and catalog structs from `hv-24x7-catalog.h`.

## Risks And Edge Cases

Catalog parsing is security-sensitive because firmware controls lengths and offsets; the code has many bounds checks but variable-sized structures remain fragile. `vmalloc_to_phys()` use assumes `PAGE_SIZE` is divisible by 4096. Request/result buffers must not cross 4K boundaries and are per-CPU aligned. Transaction reads rely on result indices mapping back to queued events. Aggregation is conditional on interface/SMT behavior. Physical and cross-LPAR domains require privileged collection capability. CPU hotplug must always leave a valid collection CPU or migrate contexts safely. The init error path does not visibly destroy the page cache or partially allocated attributes on later failures.

## Test Signals

Test on POWER8 and POWER9+ LPARs with and without privileged 24x7 capabilities, SMT8 aggregation, catalog sysfs reads, duplicate event names, malformed catalog handling if hcall stubs are available, immediate and transaction `perf stat` reads, CPU hotplug migration, physical vs virtual domain permissions, unaligned/reserved config rejection, and non-sampling capability behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7.h

## Purpose

This header defines the hypervisor 24x7 request and result ABI structures shared by the `hv_24x7` perf driver.

## Important APIs, Types, And Functions

- `enum hv_perf_domains` is generated from `hv-24x7-domains.h`.
- `H24x7_REQUEST_SIZE(iface_version)` selects the 16-byte v1 or 32-byte v2 request size.
- `struct hv_24x7_request` describes one counter data request: domain, data size/offset, LPAR range, domain index range, and v2 thread-group fields.
- `struct hv_24x7_request_buffer` contains interface version, request count, and a variable-length request array.
- `struct hv_24x7_result_element_v1` and `struct hv_24x7_result_element_v2` describe per-result elements; v2 adds `thread_group_ix` and padding before data.
- `struct hv_24x7_result` describes one request result and its variable-length elements.
- `struct hv_24x7_data_result_buffer` describes the hcall result buffer with version, result count, error details, config/catalog versions, and variable results.

## Control Flow

No executable control flow. `hv-24x7.c` fills request buffers, submits them to the hypervisor, and walks result buffers using these packed layouts and interface-version-specific offsets.

## State And Persistence

No local state. These packed structures model hypervisor hcall memory buffers, which are transient per request.

## Dependencies And Integration Points

It depends on Linux fixed-width types, big-endian annotations, and the domain macro file. It is consumed by `hv-24x7.c` and must match PAPR/PowerVM 24x7 ABI.

## Risks And Edge Cases

Version-specific request size and result element data offset are critical. The comments warn that `struct hv_24x7_result.results` is only valid for the first result because later results are variable sized. All multibyte hcall fields are big-endian.

## Test Signals

Build-time structure packing checks, hcall success on v1 and v2 platforms, result walking with multiple elements, aggregation paths, and endian validation are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.c

## Purpose

This file implements shared hypervisor perf capability discovery for PowerPC hypervisor PMUs.

## Important APIs, Types, And Functions

- `hv_perf_caps_get(struct hv_perf_caps *caps)` issues `H_GET_PERF_COUNTER_INFO` for `HV_GPCI_system_performance_capabilities`, decodes the returned version and capability bits, and fills `struct hv_perf_caps`.

## Control Flow

The function builds an aligned packed parameter/result structure, initializes request type and starting index, calls `plpar_hcall_norets()`, returns the hcall error if nonzero, and otherwise decodes `perf_collect_privileged` plus GA/expanded/LAB capability-mask bits.

## State And Persistence

No persistent local state. It writes the caller-provided `hv_perf_caps` and reads hypervisor state on each call.

## Dependencies And Integration Points

It depends on `H_GET_PERF_COUNTER_INFO`, `hv-gpci.h` request/response structures, physical address conversion, endian helpers, and the shared header `hv-common.h`. It is used by `hv-24x7.c` and other hypervisor perf drivers.

## Risks And Edge Cases

The hcall argument structure must remain correctly packed and aligned to `uint64_t`. Capability interpretation must match the hypervisor GPCI ABI. Callers must handle nonzero hcall returns.

## Test Signals

Test on LPAR systems with different hypervisor capability masks, hcall failure paths, and consumers that require privileged collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.h

## Purpose

This header provides shared types and macros for PowerPC hypervisor perf drivers.

## Important APIs, Types, And Functions

- `struct hv_perf_caps` stores the hypervisor perf counter info version and bitfields for privileged collection, GA, expanded, and LAB capabilities.
- `hv_perf_caps_get()` is declared for shared capability discovery.
- `EVENT_DEFINE_RANGE_FORMAT()` creates a perf PMU format attribute plus helper functions for extracting a bit range from an event attr field.
- `EVENT_DEFINE_RANGE_FORMAT_LITE()` creates only the format attribute.
- `EVENT_DEFINE_RANGE()` generates `event_get_<name>_max()` and `event_get_<name>()` helpers.

## Control Flow

The macros expand at compile time into sysfs format attributes and static inline-like helper functions used by hypervisor PMU drivers to parse `perf_event_attr` bit fields.

## State And Persistence

No runtime state is stored by the header. Generated helper functions are pure readers of `event->attr`.

## Dependencies And Integration Points

It depends on Linux perf PMU format attribute macros and fixed-width types. `hv-24x7.c` uses it for domain/index/offset/lpar fields; GPCI-related drivers use the capability type and range macros.

## Risks And Edge Cases

The max helper uses shift arithmetic and includes a `BUILD_BUG_ON()` for invalid bit ranges. Macro-generated function names can collide if the same range name is reused in one translation unit. `EVENT_DEFINE_RANGE_FORMAT_LITE()` intentionally omits helper functions to avoid unused warnings.

## Test Signals

Build warnings/errors from macro use, sysfs `format/` files, and event parsing tests for boundary values in each configured bit range are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci-requests.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci-requests.h

## Purpose

This macro-driven include file lists hypervisor GPCI counter request definitions used by request-generation headers to produce GPCI perf event metadata and structures.

## Important APIs, Types, And Functions

- The file includes `req-gen/_begin.h`, repeatedly defines `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND`, includes `I(REQUEST_BEGIN)`, emits a `REQUEST(...)` body of `__field`, `__array`, and `__count` entries, then includes `I(REQUEST_END)`.
- It defines request groups such as `dispatch_timebase_by_processor` (`0x10`), partition entitlement/consumption (`0x20`), `system_performance_capabilities` (`0x40`), several optional bus/core utilization requests under `ENABLE_EVENTS_COUNTERINFO_V6`, hypervisor queuing/times requests (`0xE0`, `0xF0`, `0xF4`), and `partition_instruction_count_and_time` (`0x100`).
- `__count` entries are intended to become perf-exposed counters; `__field` and `__array` entries describe normal metadata and padding.

## Control Flow

There is no direct runtime control flow. The file is processed by macro includes to generate code/data for each request. Conditional compilation includes older counter-info v6 request sets only when enabled.

## State And Persistence

No runtime state. The definitions are compile-time metadata derived from the `getPerfCountInfo v1.07` document.

## Dependencies And Integration Points

It depends on the `req-gen` macro framework, `hv-gpci` request numbering, and the hypervisor GPCI hcall ABI. `hv-common.c` uses the generated `HV_GPCI_system_performance_capabilities` request identifier and response shape.

## Risks And Edge Cases

The generator requires byte sizes for `__count` and `__field` to be decimal numeral tokens, not expressions or hex. A comment notes a suspected spec error for `system_tlbie_count_and_time` offset. Several request types are intentionally skipped because they have no counters. Conditional v6 events may not apply to newer counter-info versions.

## Test Signals

Build the GPCI driver with and without `ENABLE_EVENTS_COUNTERINFO_V6`, inspect generated sysfs events, verify hcall request numbers and starting-index kinds, and compare counter offsets against hypervisor documentation and real `perf stat` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci-requests.h -->
