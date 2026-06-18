# Research: subset-b-000826

Grouped research for s390 architecture perf CPU-measurement, Processor Activity Instrumentation, process/processor, ptrace, restart/kexec, rethook, runtime instrumentation, setup, signal, and storage-key support. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf_events.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf_events.c

Purpose: defines the s390 CPU-Measurement Counter Facility perf event sysfs inventory. It maps CPUMF hardware counter numbers to named perf PMU events, grouped by counter facility version, crypto counter version, and IBM Z machine generation.

Important APIs/types/functions: the file is almost entirely generated-style `CPUMF_EVENT_ATTR()` declarations and `CPUMF_EVENT_PTR()` arrays. It exports `cpumf_cf_event_group()`, which returns the `attribute_group` set used by the counter-facility PMU. The helper `merge_attr()` allocates one NULL-terminated attribute array from the selected generic CFVN set, CSVN crypto set, and model-specific set. The static groups are `cpumcf_pmu_events_group`, `cpumcf_pmu_format_group`, and `cpumcf_pmu_attr_groups`.

Control flow: initialization-time callers invoke `cpumf_cf_event_group()`. It queries counter metadata with `qctri()`, selects generic counters for `cfvn` 1 or 3, selects crypto counters for `csvn` 1-5 or 6+, then calls `get_cpu_id()` and dispatches on machine IDs for z10, z196, zEC12, z13, z14, z15, z16, and z17. The chosen arrays are concatenated and assigned to `cpumcf_pmu_events_group.attrs`; the format group exposes `event` as `config:0-63`.

State and persistence: state is static attribute data plus one allocated merged attribute pointer table retained after init. No runtime counter values are stored here and no persistent storage is touched.

Dependencies and integration points: depends on `linux/perf_event.h`, `asm/cpu_mf.h`, `qctri()`, `get_cpu_id()`, and `cpumf_events_sysfs_show()` from `perf_event.c`. It integrates with the counter-facility PMU registration path by supplying sysfs `events/` and `format/` groups.

Risks: the table is a hardware ABI surface; wrong event numbers or wrong model gating exposes misleading perf events. `merge_attr()` returns NULL on allocation failure, in which case callers get the groups but without newly populated event attrs. Adding machine generations must preserve unique CPUMF event identifiers across CF, sampling, and PAI spaces.

Test signals: boot on each supported IBM Z generation should show the expected `/sys/bus/event_source/devices/cpum_cf/events/*` names, `perf list` should contain model-appropriate counters, raw event encodings should match architecture manuals, and unsupported models should still expose valid generic/crypto sets when `qctri()` reports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_sf.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_sf.c

Purpose: implements perf PMU support for the s390 CPU-Measurement Sampling Facility. It supports basic sampling as normal perf samples and diagnostic/combined sampling through perf AUX trace buffers.

Important APIs/types/functions: key structures are `sf_buffer`, `aux_buffer`, and per-CPU `cpu_hw_sf`. Buffer management is handled by `alloc_sampling_buffer()`, `realloc_sampling_buffer()`, `free_sampling_buffer()`, `allocate_buffers()`, `extend_sampling_buffer()`, and AUX helpers such as `aux_buffer_setup()`, `aux_output_begin()`, `aux_reset_buffer()`, `hw_collect_aux()`, and `aux_output_end()`. PMU callbacks are `cpumsf_pmu_event_init()`, `cpumsf_pmu_add()`, `cpumsf_pmu_start()`, `cpumsf_pmu_stop()`, `cpumsf_pmu_del()`, `cpumsf_pmu_enable()`, `cpumsf_pmu_disable()`, `cpumsf_pmu_check_period()`, and `cpumsf_pmu_read()`. `cpumf_measurement_alert()` is the external IRQ handler. `init_cpum_sampling_pmu()` registers the PMU as `cpum_sf`.

Control flow: init checks `cpum_sf_avail()`, queries `qsi()`, validates the basic sample-entry size, conditionally exposes diagnostic sampling, registers s390dbf debug state, installs the measurement-alert IRQ handler, registers the perf PMU, and adds a CPU hotplug state. Event init validates raw or CPU-cycle sampling events, rejects branch/callchain/register/stack sampling, reserves the sampling facility globally, computes a hardware sample interval from `sample_period` or `sample_freq`, and allocates per-CPU basic SDB buffers unless diagnostic AUX mode is requested. Add/start programs `lsctl` with SDBT origins and enables basic/diagnostic controls; stop/delete flush pending samples and clears per-CPU in-use state. Measurement alerts harvest full SDBs into perf samples or advance AUX output windows.

State and persistence: state is per-CPU `cpu_hw_sf` including QSI information, saved `lsctl` controls, current event, flags, SDB chain, and AUX output handle. Global state includes sampling buffer limits, diagnostic SDB factor, `num_events`, the reserve mutex, the debug feature, and the `cpum_sfb_size` core parameter. No disk state is written.

Dependencies and integration points: depends on `asm/cpu_mf.h` instructions (`qsi`, `lsctl`, `lpp`), lowcore LPP, external measurement-alert IRQ subclassing, perf event/AUX APIs, CPU hotplug, s390dbf, TOD clock base, RCU task lookup for PID namespace correction, and perf sysfs macros from the CPUMF support code.

Risks: SDB/SDBT chains are manipulated while hardware may be producing samples, so disable/enable sequencing and 128-bit trailer compare-and-swap are critical. Buffer growth can fail in atomic context, producing loss accounting rather than fatal errors. Diagnostic AUX alert placement races with hardware setting full bits and must avoid losing the producer head. Rate conversion mutates `attr->freq` to bypass generic perf adjustment. Guest/host attribution for old machines is heuristic.

Test signals: useful validation includes `perf record -e cpum_sf/SF_CYCLES_BASIC/`, diagnostic AUX mmap use, high-frequency sampling with overflow-driven buffer extension, `cpum_sfb_size=` parameter changes, CPU online/offline with active events, authorization-change alerts, invalid-buffer alerts, PID/TID sample attribution, and KVM guest/host exclusion filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_sf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_event.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_event.c

Purpose: supplies s390 architecture glue for the generic perf subsystem: instruction-pointer and misc flag classification, perf debug output, service-level reporting, callchain walking, and common CPUMF sysfs event formatting.

Important APIs/functions: exported perf hooks include `perf_arch_instruction_pointer()`, `perf_arch_misc_flags()`, `perf_event_print_debug()`, `perf_callchain_kernel()`, `perf_callchain_user()`, and `cpumf_events_sysfs_show()`. Internal helpers include `sie_block()`, `is_in_guest()`, `guest_is_user_mode()`, `perf_misc_flags_sf()`, `print_debug_cf()`, `print_debug_sf()`, and service-level print callbacks.

Control flow: perf sample classification first detects synthetic `pt_regs` built by `cpum_sf` using interrupt code `0x1407` and PRA interrupt parameter, then uses the embedded `perf_sf_sde_regs` guest indicator. Non-sampling-facility samples detect SIE guest execution by comparing the kernel instruction pointer with `sie_exit` and reading the guest PSW from the SIE block on the kernel stack. Debug printing queries counter and sampling facilities under local IRQ disable. The service-level initcall registers a printer that emits CPU-MF counter and sampling capabilities. Kernel callchains unwind through `unwind_for_each_frame()`, while user callchains use `arch_stack_walk_user_common()`.

State and persistence: only the static `service_level_perf` registration is retained. Debug output is generated on demand. There is no persistence beyond normal proc/sysfs/service-level reporting.

Dependencies and integration points: depends on KVM SIE stack frame layout, `sie_exit`, CPU-MF query instructions `qctri()` and `qsi()`, lowcore/stacktrace/unwind helpers, service-level infrastructure, perf sample headers, and CPUMF event attribute objects from counter/sampling/PAI files.

Risks: guest classification relies on stack layout and the SIE exit symbol; incorrect detection corrupts perf misc flags and guest IP reporting. Synthetic sampling regs must remain synchronized with `perf_cpum_sf.c`. Callchain behavior depends on reliable unwind metadata and user stack accessibility. Debug printers run with interrupts disabled and must remain bounded.

Test signals: KVM host profiling should attribute guest user/kernel samples correctly, `perf report` should show meaningful IPs for host and guest samples, `perf_event_print_debug()` should log CPUMF CF/SF status, `/proc/service_levels` should include CPU-MF lines when facilities exist, and `perf record -g` should produce kernel and user callchains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_pai.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_pai.c

Purpose: implements perf PMUs for the s390 Processor Activity Instrumentation facility: `pai_crypto` for cryptographic-function counters and `pai_ext` for extension/NNPA counters. It supports both counting and context-switch-driven sampling of aggregate events.

Important APIs/types/functions: central types are `pai_userdata`, `paiext_cb`, `pai_map`, `pai_mapptr`, `pai_root`, and `pai_pmu`. Allocation and lifetime are managed by `pai_root_alloc()`, `pai_root_free()`, `pai_alloc_cpu()`, `pai_alloc()`, `pai_event_destroy_cpu()`, and `pai_free()`. Event validation and operation flow through `pai_event_valid()`, `pai_event_init()`, `pai_add()`, `pai_start()`, `pai_stop()`, `pai_del()`, `pai_read()`, and PMU-specific wrappers for crypto and extension. Sampling uses `pai_copy()`, `pai_push_sample()`, `pai_have_sample()`, `paicrypt_sched_task()`, and `paiext_sched_task()`. `paipmu_setup()` and `pai_init()` register PMUs.

Control flow: device init creates an s390dbf debug area, probes facility bits 196 and 197, calls `qpaci()` for available crypto and NNPA counter counts, dynamically builds sysfs event attributes, and registers each supported PMU. Event init validates the config range and disallows sampling of individual counters; sampling is limited to `*_ALL`, forces raw sample output, disables inheritance, and requests perf sched callbacks. Add enables the appropriate lowcore pointer and control register bit: `ccd` plus `CR0_CRYPTOGRAPHY_COUNTER_BIT` for crypto, or `aicd` plus `CR0_PAI_EXTENSION_BIT` for extension. Stop/delete reads final counts or emits deltas and disables hardware when the last active event on a CPU is removed.

State and persistence: per-PMU roots hold dynamically allocated per-CPU map pointers. Each CPU map owns the hardware counter area, optional PAIE1 control block, save buffer for nonzero deltas, active-event count, refcount, current per-task event, and system-wide sampling list. `pai_key` is a static key for crypto instrumentation users. State is runtime-only.

Dependencies and integration points: depends on PAI facility instructions and lowcore fields, control register bit helpers, perf PMU and sched callback APIs, CPU masks, `cpumf_events_sysfs_show()`, s390dbf, and named counter inventories in the file. It intersects with crypto/NNPA instruction execution through the architecture counter hardware.

Risks: reference counting spans global roots, per-CPU maps, system-wide events, and per-thread events; mistakes leak counter pages or disable hardware under active users. Sampling occurs at context switch and can overflow perf output. `pai_ext` rejects `exclude_user` and then forces `exclude_kernel`, reflecting hardware limitations. Dynamic sysfs event generation must cap hardware-reported counter counts to named/valid ranges.

Test signals: check `/sys/bus/event_source/devices/pai_crypto/events` and `pai_ext/events`, run counting on named and ALL counters, run sampling with raw payloads and context switches, test simultaneous system-wide and per-task sampling, verify counter wrap deltas, validate facility-absent registration failure, and confirm control bits/lowcore fields clear on event deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_pai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_regs.c

Purpose: implements s390 perf register sampling support for general registers, selected floating-point registers, PSW mask, and program counter.

Important APIs/functions: `perf_reg_value()` returns one requested register from `pt_regs` or the current task FPU save area. `perf_reg_validate()` rejects empty masks and masks containing bits outside `PERF_REG_S390_MAX`. `perf_reg_abi()` reports `PERF_SAMPLE_REGS_ABI_64`. `perf_get_regs_user()` points perf at the task's user interrupt regs and saves user FPU state when needed.

Control flow: register reads branch by perf register index. GPR indices map directly to `regs->gprs[]`; FP indices are available only for user-mode samples and are read from `current->thread.ufpu.vxrs`; mask and PC map to `regs->psw`. User-reg collection intentionally uses `task_pt_regs(current)` from the first interruption, leaving nested interrupt handling to perf core.

State and persistence: the file does not own persistent state. It may refresh the current task's saved FPU registers before perf copies sampled registers.

Dependencies and integration points: depends on `linux/perf_event.h`, `linux/perf_regs.h`, `asm/ptrace.h`, and `asm/fpu.h`. It is called by generic perf when users request `PERF_SAMPLE_REGS_USER` or related register masks.

Risks: FP register reads are current-task specific and return zero for kernel-mode contexts. Register index assumptions must track `enum perf_event_s390_regs`. Failing to save user FPU state before sampling would expose stale vector/FPU content.

Test signals: `perf record --user-regs` on s390 should return GPR/FP/PC/mask data for user samples, invalid masks should return `-EINVAL`, kernel samples should not expose FP values, and ABI should report 64-bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/process.c

Purpose: implements s390 process and thread mechanics: fork return, task duplication, thread creation, context switching, exec cleanup, wait-channel lookup, and userspace address randomization.

Important APIs/functions: architecture entry points include `__ret_from_fork()`, `flush_thread()`, `arch_setup_new_exec()`, `arch_release_task_struct()`, `arch_dup_task_struct()`, `copy_thread()`, `execve_tail()`, `__switch_to()`, `__get_wchan()`, `arch_align_stack()`, and `arch_randomize_brk()`.

Control flow: forked tasks enter `ret_from_fork`, call `schedule_tail()`, execute the kernel-thread function if the saved regs are not user mode, then go through `syscall_exit_to_user_mode()`. `arch_dup_task_struct()` snapshots FPU state and copies the task, but clears runtime instrumentation and guarded-storage pointers to avoid double ownership. `copy_thread()` builds the fake switch frame and child `pt_regs`, clears PER/debug state, initializes timers and restart metadata, handles kernel threads separately, returns zero in the user child, optionally installs TLS in access registers 0/1, and clears the RI PSW bit for forked user threads. `__switch_to()` saves FPU/access/runtime-instrumentation/guarded-storage state, updates control registers for the next task, restores next state, then jumps to assembly switching.

State and persistence: per-task `thread_struct` owns kernel stack pointer, access registers, FPU state, PER state, timers, last-break address, RI and guarded-storage control blocks, and restart-block architecture data. No persistent external state is written.

Dependencies and integration points: depends on scheduler context switching, lowcore LPP updates, access-register and FPU helpers, runtime instrumentation, guarded storage, ptrace PER flags, unwind stack walking, randomization helpers, and s390 assembly entry code.

Risks: copy/switch ownership of RI and guarded-storage buffers is subtle; copying pointers would cause premature frees or cross-task state corruption. Kernel-thread frames must match `ret_from_fork` assembly expectations. `__switch_to()` must update control registers before restoring hardware state that depends on them. TLS is carried in access registers rather than an architecture-neutral slot.

Test signals: fork/clone with and without `CLONE_SETTLS`, kernel thread creation, exec clearing FPC, context-switch stress with FPU/VX/RI/guarded-storage users, ptrace single-step across forks, wait-channel reporting, and ASLR entropy for stacks and brk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/processor.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/processor.c

Purpose: provides s390 CPU identity, HWCAP/platform setup, CPU frequency reporting, CPU relax/yield behavior, text-patching synchronization, per-CPU initialization, and `/proc/cpuinfo` rendering.

Important APIs/functions: exported or architecture-visible functions include `cpu_detect_mhz_feature()`, `s390_update_cpu_mhz()`, `stop_machine_yield()`, `text_poke_sync()`, `text_poke_sync_lock()`, `cpu_init()`, and `cpuinfo_op`. Initcalls `setup_hwcaps()` and `setup_elf_platform()` populate ELF auxiliary-vector capability state. Helpers render facilities, cache info, topology, IDs, and MHz data.

Control flow: early boot detects whether ECAG CPU MHz attributes are available. MHz updates adjust jiffies and run an on-each-CPU ECAG query. Stop-machine spin loops periodically yield to preempted target virtual CPUs. Text patching broadcasts `sync_core()` to all CPUs, optionally under the CPU read lock. `cpu_init()` captures the CPU ID, initializes dynamic/static MHz, attaches `init_mm` as `active_mm`, and enters lazy TLB mode. HWCAP setup checks facility bits and machine features, then sets ELF flags for vector, guarded storage, NNPA, DFLT, SORT, SIE, and other capabilities. Platform setup maps machine IDs to strings such as `z13`, `z16`, or `z17`.

State and persistence: global `elf_hwcap` and `elf_platform` become user ABI through ELF aux vectors. Per-CPU `cpu_info` stores dynamic/static MHz and CPUID. Per-CPU `cpu_relax_retry` throttles yield attempts. State is runtime-only but visible through `/proc/cpuinfo`.

Dependencies and integration points: depends on ECAG, STFL facility lists, CPU feature helpers, SCLP virtualization flags, scheduler topology, cacheinfo, SMP CPU masks, text patching, stop_machine, `init_mm`, and ELF core/loader interfaces.

Risks: HWCAP bits are userspace ABI and must only be set when instructions are truly available. Platform strings guide optimized libraries. Text-patching synchronization must reach all online CPUs. CPU MHz reporting is optional and must tolerate machines without the ECAG attribute. Virtual CPU yielding must avoid excessive hypervisor calls.

Test signals: `/proc/cpuinfo` should show correct feature strings, facilities, topology, machine IDs, and MHz fields; auxv should expose expected HWCAP bits; text patching and alternatives should synchronize under SMP; stop_machine loops under virtualization should make forward progress; boot on new machine IDs should choose a sensible platform string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ptrace.c

Purpose: implements the s390 ptrace user area, PER single-step/block-step controls, transactional-execution ptrace commands, and ELF/core user regsets for GPRs, FPRs, vector registers, guarded storage, and runtime instrumentation.

Important APIs/functions: hardware-state control is in `update_cr_regs()`, `user_enable_single_step()`, `user_disable_single_step()`, `user_enable_block_step()`, and `ptrace_disable()`. Legacy user-area access is implemented by `__peek_user()`, `peek_user()`, `__poke_user()`, and `poke_user()`. `arch_ptrace()` handles s390-specific requests. Regset callbacks include `s390_regs_get/set`, `s390_fpregs_get/set`, `s390_vxrs_low/high_get/set`, `s390_gs_cb_get/set`, `s390_gs_bc_get/set`, `s390_runtime_instr_get/set`, `s390_tdb_get`, `s390_last_break_get`, and system-call regset access.

Control flow: `update_cr_regs()` compares current and desired control-register state, enabling/disabling transactional execution, guarded storage, and PER. It merges user PER settings with kernel single-step or uprobe single-step state and loads CR9-CR11 only when changed. Legacy ptrace peeks/pokes map sparse `struct user` offsets onto stack `pt_regs`, access registers, FPU/vector storage, and PER state while preserving historical gdb quirks. `arch_ptrace()` dispatches peek/poke area operations, last-break access, TE enable/disable, and TE abort randomization before falling back to generic ptrace. Regset setters validate PSW masks, FPC reserved bits, guarded-storage availability, and runtime-instrumentation control-block invariants.

State and persistence: modifies per-task `thread_struct` fields: access registers, FPU/vector state, PER user/event controls, PER flags, last break, syscall number, guarded-storage control blocks, runtime-instrumentation control block, and saved transaction diagnostic block. State is task-local and appears in core dumps via user regsets.

Dependencies and integration points: depends on scheduler switch code calling `update_cr_regs()`, machine facility checks for TX/VX/GS/RI, `entry.h` syscall flags, generic ptrace/regset/core-dump infrastructure, access-register and FPU helpers, guarded storage, runtime instrumentation, and seccomp/audit-visible syscall state.

Risks: ptrace is ABI-sensitive; offsets and historical access-register quirks cannot be casually changed. PSW validation must prevent invalid addressing and unauthorized RI bits. Runtime instrumentation and guarded storage setters allocate control blocks and may update live hardware under preemption disable. Single-step PER merging must not lose debugger-installed PER ranges.

Test signals: gdb register read/write, `PTRACE_PEEKUSR_AREA`/`POKEUSR_AREA`, single-step and block-step, transactional execution ptrace commands, core dumps containing all regsets, vector-reg access on VX and non-VX machines, guarded-storage and RI regset validation, and syscall-number modification while stopped in a syscall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/reipl.S -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/reipl.S

Purpose: provides the low-level `store_status` routine used around restart/re-IPL paths to store the current CPU status into lowcore and then branch to a caller-provided function.

Important APIs/symbols: defines `store_status` as `SYM_CODE_START(store_status)` and a local BSS `clkcmp` scratch word. It uses lowcore save-area offsets from `asm/asm-offsets.h` and branch thunk support from `asm/nospec-insn.h`.

Control flow: caller passes a function pointer in `%r2` and an argument in `%r3`. The routine stores GPRs, obtains the lowcore pointer, stores control registers, access registers, floating-point registers, FPC, CPU timer, prefix register, seven bytes of clock comparator, and a PSW image. It records the callback address in the saved PSW area, moves the argument into `%r2`, and branches through `%r9` with `BR_EX`.

State and persistence: writes architectural register state into the current CPU lowcore save areas. This is machine restart/status state rather than filesystem persistence.

Dependencies and integration points: depends on lowcore layout, s390 register-save instructions, restart/re-IPL callers, nospec branch thunk generation, and code that later consumes stored status from lowcore.

Risks: offsets and register ordering must match lowcore definitions exactly. The routine runs in a sensitive restart context and cannot rely on normal C calling conventions beyond the documented register inputs. Clock comparator handling intentionally copies seven bytes; changing it can break architectural status layout.

Test signals: restart/re-IPL and dump flows should see complete stored status, callback invocation should receive the original parameter in `%r2`, and saved lowcore register areas should match hardware state during crash/restart validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/reipl.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/relocate_kernel.S -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/relocate_kernel.S

Purpose: implements the s390 kexec relocation stub that copies a new kernel image to final physical destinations and transfers control via restart/diagnose.

Important APIs/symbols: defines `relocate_kernel`, local `load_psw`, and exported data `relocate_kernel_len`. It consumes the generic kexec indirection-page entry format via bit flags for destination, indirection, done, and source pages.

Control flow: `%r2` points at kimage entries, `%r3` holds the start address to jump to, and `%r4` holds the diagnose subcode. The loop reads entries, tracks destination pages, follows indirection pages, stops at the done marker, and copies source pages to destination pages using `mvcle` until a page is complete. At done, it places the subcode in `%r0`; if a start address is supplied, it patches a PSW template and copies it to absolute address zero. Finally it issues `diag 0x308`.

State and persistence: modifies physical memory by copying image pages and optionally writes a load PSW at absolute zero. No filesystem state is used.

Dependencies and integration points: depends on the generic kexec image entry encoding, s390 diagnose 0x308 restart semantics, page size constants, and the caller arranging execution from safe memory not overwritten by relocation.

Risks: the code runs without normal kernel services and must not clobber input state prematurely. Entry flag parsing and `0xf000` page masking must match kexec encoding. Wrong PSW patching or absolute-zero writes can hang the machine during kexec.

Test signals: `kexec -e` should boot the target kernel, crash-kernel paths should relocate reliably, image entries with indirection pages should copy correctly, zero start-address diagnose paths should behave as expected, and `relocate_kernel_len` should cover the exact stub range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.c

Purpose: provides s390 architecture callbacks for the generic rethook infrastructure used by kretprobes/fprobe-style return hooks.

Important APIs/functions: `arch_rethook_prepare()` saves the original return address and frame pointer from `%r14` and `%r15`, then replaces `%r14` with `arch_rethook_trampoline`. `arch_rethook_fixup_return()` restores the real return address into `%r14`. `arch_rethook_trampoline_callback()` calls `rethook_trampoline_handler(regs, regs->gprs[15])`. The trampoline symbol is declared elsewhere and marked not probeable here.

Control flow: when a probed function is prepared, its link register return path is redirected to the trampoline. When the trampoline runs, it calls back into generic rethook handling with the current frame pointer; generic code decides the correct return address, and fixup writes that address back into the register set.

State and persistence: per-hook state is stored in the generic `struct rethook_node` fields `ret_addr` and `frame`. The file itself owns no global state.

Dependencies and integration points: depends on `linux/rethook.h`, `linux/kprobes.h`, s390 `pt_regs` register numbering, the assembly `arch_rethook_trampoline`, and generic rethook/kprobe no-probe annotations.

Risks: s390 return conventions use `%r14`; saving or restoring the wrong register would corrupt returns. The trampoline and callbacks are marked `NOKPROBE_SYMBOL` to avoid recursive probing. Stack frame assumptions must match the low-level trampoline.

Test signals: kretprobe or fprobe return hooks should fire and return to the original caller, nested return hooks should unwind correctly, and kprobe blacklisting should prevent probing the trampoline/callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.h -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.h

Purpose: declares the s390 rethook trampoline callback for use by the assembly trampoline implementation.

Important APIs/types/functions: exposes `unsigned long arch_rethook_trampoline_callback(struct pt_regs *regs);` behind the `__S390_RETHOOK_H` include guard.

Control flow: no executable control flow exists in this header. It allows assembly/C boundary code to call the C callback implemented in `rethook.c`.

State and persistence: no state is defined.

Dependencies and integration points: depends on `struct pt_regs` being visible to users of the declaration. It integrates with `arch_rethook_trampoline` assembly and generic rethook handling.

Risks: prototype mismatch with the assembly trampoline would break calling convention expectations. The header is intentionally minimal, so additional declarations should be added only when needed by the trampoline path.

Test signals: compile/link of s390 rethook support, successful trampoline callback calls under kretprobe/fprobe tests, and no unresolved symbol or type conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/rethook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/runtime_instr.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/runtime_instr.c

Purpose: implements the `s390_runtime_instr` syscall and task cleanup for s390 runtime instrumentation control blocks.

Important APIs/functions: `runtime_instr_empty_cb` is a zero/empty control block used to disable RI. `runtime_instr_release()` frees a task's RI control block. `disable_runtime_instr()` unloads RI state from the current CPU, frees the task block, clears the task pointer, and removes `PSW_MASK_RI`. `init_runtime_instr_cb()` fills safe defaults. `SYSCALL_DEFINE2(s390_runtime_instr)` handles `S390_RUNTIME_INSTR_START` and `S390_RUNTIME_INSTR_STOP`.

Control flow: the syscall first checks facility 64. STOP disables any current RI block and returns. START validates the command, allocates or reuses the current task's block, zeros it, initializes required fields such as range-limit alignment, storage key, and validity bit, then disables preemption while publishing the pointer and loading it into hardware. The obsolete signal-number argument is intentionally ignored for ABI compatibility.

State and persistence: per-task state is `current->thread.ri_cb`; hardware RI state is loaded/unloaded on the current CPU. No persistent storage is written.

Dependencies and integration points: depends on runtime-instrumentation assembly helpers, task stack regs, page default storage key, facility probing, syscall ABI, process cleanup in `arch_release_task_struct()`, context switch save/restore in `process.c`, and ptrace RI regset validation in `ptrace.c`.

Risks: RI must be disabled before freeing its control block, and the PSW RI bit must be cleared or user return can trigger a specification exception. Preemption is disabled around hardware load and pointer update to avoid migrating with mismatched state. User-supplied ptrace RI blocks are validated elsewhere, but syscall-created blocks still need architecture-correct defaults.

Test signals: syscall start/stop on facility-present and facility-absent machines, fork clearing RI in children, exec/signal return with RI bit behavior, context-switch save/restore of active RI, and ptrace reads of the RI control block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/runtime_instr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/setup.c

Purpose: performs architecture-dependent s390 boot setup: console selection, lowcore allocation, AMODE31 relocation, control register setup, memory reservation/discovery, crashkernel/initrd handling, machine restart wrappers, resource registration, randomness seeding, and the main `setup_arch()` sequence.

Important APIs/functions/state: public globals include `console_mode`, `console_devno`, `console_irq`, `vm_layout`, `stfle_fac_list`, `lowcore_ptr[]`, `mio_wb_bit_mask`, `VMALLOC_START/END`, `vmemmap`, and module address bounds. Key functions include `condev_setup()`, `conmode_setup()`, `conmode_default()`, `machine_restart()`, `machine_halt()`, `machine_power_off()`, `stack_alloc()`, `stack_free()`, `setup_lowcore()`, `setup_resources()`, `reserve_crashkernel()`, `reserve_initrd()`, `memblock_add_physmem_info()`, `setup_memory()`, `relocate_amode31_section()`, `setup_cr()`, `setup_randomness()`, `setup_control_program_code()`, `log_component_list()`, `setup_arch()`, and `arch_cpu_finalize_init()`.

Control flow: early parameters may set console device or mode. `setup_arch()` prints machine type and decompressor logs, sets the command line and root device, initializes `init_mm`, parses early params, initializes IPL/control-program state, reserves page tables, lowcore, kernel, initrd, certificates, and memory-detection metadata, adds physical memory to memblock, initializes storage keys, relocates AMODE31 code/data below 2GB, updates CR2/CR5/CR15, reserves DMA/CMA and crashkernel memory, handles crash-dump CPU save paths, registers resources, allocates boot lowcore/stacks, detects CPUs/topology/NUMA, builds page tables, chooses console defaults, applies alternatives/nospec setup, adjusts zfcp dump behavior, and seeds randomness.

State and persistence: establishes foundational boot-time kernel state: memblock layout, resource tree, lowcore pointers, control registers, crashkernel reservations, console globals, AMODE31 references, random pool input, CPU masks, and platform boot logs. It does not write persistent storage.

Dependencies and integration points: depends on decompressor boot data, SCLP, IPL data, physmem info, memblock, kexec/crash dump, NUMA, SMP, paging, lowcore/absolute lowcore, storage keys, user-copy control tables, ultravisor, alternatives/nospec branch logic, consoles, VM CP commands, and Linux init entry points.

Risks: boot ordering is critical. Memory must be reserved before memblock allocations consume it, AMODE31 references must be relocated before control registers are updated, and crash-dump secondary CPU capture triggers reset-like behavior before later initialization. Console auto-detection mutates z/VM console mode. Lowcore setup touches absolute lowcore for offline CPU restart behavior. Incorrect storage-key initialization can break non-default-key code.

Test signals: boot under z/VM, KVM, LPAR, and dump IPL; console selection via defaults and `condev=`/`conmode=`; crashkernel reservation and memory hotplug notifier behavior; initrd and certificate-list reservation; AMODE31 relocation logs; lowcore relocation and interrupt PSWs; resource tree contents; successful SMP/NUMA/paging bring-up; and random availability when PRNO TRNG exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/signal.c

Purpose: implements s390 signal frame creation, signal return syscalls, register save/restore, alternate stack selection, and syscall restart handling during signal delivery.

Important APIs/types/functions: frame layouts are `struct sigframe` for old-style handlers and `struct rt_sigframe` for SA_SIGINFO handlers. Register helpers are `store_sigregs()`, `load_sigregs()`, `save_sigregs()`, `restore_sigregs()`, `save_sigregs_ext()`, and `restore_sigregs_ext()`. User ABI syscalls are `sigreturn` and `rt_sigreturn`. Delivery helpers are `get_sigframe()`, `setup_frame()`, `setup_rt_frame()`, `handle_signal()`, and `arch_do_signal_or_restart()`.

Control flow: delivery saves the current syscall number for ptrace visibility, obtains a signal, handles syscall restart return codes if interrupted by a handler, clears syscall state, notifies rseq, and builds either classic or RT frames. Frame setup chooses normal or alternate stack, writes a backchain, saves signal mask/context/FPU/access/vector state, selects the restorer from SA_RESTORER or vDSO, forces default user addressing mode/address-space control, sets handler arguments, and records synchronous-signal extras. Return syscalls read the saved mask and altstack state, save current FPU, restore PSW/GPR/access/FPU/vector state, clear syscall flag, and return the restored `%r2`; bad frames force SIGSEGV.

State and persistence: signal frames are transient userspace stack ABI. Kernel task state touched includes blocked signal mask, altstack state, access registers, FPU/vector state, restart block, `thread.system_call`, and `last_break`. No persistent storage is written.

Dependencies and integration points: depends on vDSO symbols for `sigreturn`, `rt_sigreturn`, and `restart_syscall`, access-register and FPU helpers, vector facility detection, rseq, generic signal core, syscall restart conventions, ptrace syscall flags, and user-copy helpers.

Risks: frame layout is ABI and includes variable extensions for VX registers. PSW restoration must reject unauthorized RI, avoid HOME address-space control, and force valid addressing mode. Restart handling must distinguish handler delivery from no-signal restart. Alternate-stack overflow returns `-EFAULT` and leads to forced signal behavior. Missing FPU save before frame creation or return would corrupt user context.

Test signals: classic and RT signal handlers, SA_ONSTACK overflow, SA_RESTORER and vDSO restorers, vector-register preservation, RI-enabled and RI-disabled tasks, syscall restart cases for `ERESTART*`, ptrace modification before delivery, rseq signal delivery, and bad-frame SIGSEGV paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/skey.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/skey.c

Purpose: initializes storage keys for linker-registered memory regions that must be accessible from code running with a non-default access key.

Important APIs/functions/state: exports global `skey_regions_initialized`. `load_real_address()` uses the `lra` instruction to translate a virtual address to a real address. `__skey_regions_initialize()` iterates linker-defined `__skey_region_start` to `__skey_region_end`, sets each page's storage key to `PAGE_DEFAULT_KEY` with reference/change reset, and publishes completion.

Control flow: for every registered `struct skey_region`, the function rounds the start down to a page boundary, loops page by page until the region end, translates each page with `lra`, and calls `page_set_storage_key()`. A compiler barrier precedes `WRITE_ONCE(skey_regions_initialized, 1)` so observers do not see completion before key writes are ordered.

State and persistence: changes hardware storage-key metadata for registered real pages and sets a runtime completion flag. It is not filesystem persistence.

Dependencies and integration points: depends on linker-provided storage-key region tables, `asm/skey.h`, `PAGE_DEFAULT_KEY`, `page_set_storage_key()`, `lra`, and code paths that test `skey_regions_initialized` before running with non-default keys.

Risks: registered ranges must be valid mapped pages; `lra` on an invalid address would not produce the expected real address. The completion flag ordering matters for consumers that switch access keys. Every page in a region is modified, so incorrect region bounds can alter unrelated storage keys.

Test signals: boot/init paths that register skey regions should observe `skey_regions_initialized`, code using non-default access keys should access those regions successfully, and storage-key inspection should show `PAGE_DEFAULT_KEY` on each registered page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/skey.c -->
