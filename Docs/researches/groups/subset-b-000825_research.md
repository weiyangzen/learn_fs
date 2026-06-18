# Research: subset-b-000825

Grouped research for s390 kernel support files under `sources/distributed-fs/ceph-client/arch/s390/kernel`. Each section preserves the source path for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/hiperdispatch.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/hiperdispatch.c

Purpose: implements s390 hiperdispatch capacity steering. It tracks vertical CPU polarization, steal time, and topology state to decide whether all online cores should advertise high scheduler capacity or only entitled vertical-high/medium cores should do so.

Important APIs and state: exported topology hooks are `hd_reset_state()`, `hd_add_core()`, `hd_enable_hiperdispatch()`, and `hd_disable_hiperdispatch()`. Persistent runtime state is held in `hd_vl_coremask`, `hd_vmvl_cpumask`, `hd_high_capacity_cores`, `hd_entitled_cores`, `hd_online_cores`, `hd_previous_steal`, high/low time counters, and `hd_adjustments`. User controls are `/proc/sys/s390/hiperdispatch`, CPU root sysfs attributes `hiperdispatch/hd_steal_threshold` and `hiperdispatch/hd_delay_factor`, and debugfs counters under `s390/hiperdispatch`.

Control flow: topology rebuild code calls reset/add/enable while holding or coordinating with `smp_cpu_state_mutex`. The delayed work computes averaged steal percentage from vertical-medium/low CPUs and calls `topology_schedule_update()` when the desired high-capacity core count changes. `hd_update_capacities()` then assigns low/high capacity to vertical-low cores in core order.

Dependencies and integration: relies on s390 topology, CPU polarization, scheduler capacity constants, `kcpustat_cpu()`, `system_dfl_wq`, tracepoints, debugfs, sysctl, and CPU sysfs. Capacity reads/writes are serialized with `smp_cpu_state_mutex`; debug counters use `hd_counter_mutex`.

Risks and test signals: sensitive to CPU hotplug order, stale steal-time baselines, division/time units, and extra rebuilds if capacity state races. Test by toggling sysctl/sysfs controls, hotplugging CPUs, checking tracepoints/debugfs counters, and verifying scheduler domains rebuild only when thresholds are crossed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/hiperdispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/idle.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/idle.c

Purpose: provides s390 CPU idle entry and idle accounting. It loads an enabled-wait PSW and accounts time spent waiting when an interrupt exits idle.

Important APIs and state: `DEFINE_PER_CPU(struct s390_idle_data, s390_idle)` stores `clock_idle_enter`, `timer_idle_enter`, optional MT diagnostic cycles, `idle_time`, and `idle_count`. `arch_cpu_idle()` enters wait state; `account_idle_time_irq()` is called by interrupt entry code when `CIF_ENABLED_WAIT` was set. Sysfs device attributes expose `idle_count` and `idle_time_us`.

Control flow: `arch_cpu_idle()` clears delayed nohz, marks enabled-wait, optionally stores MT diagnostic counters with `stcctm()`, snapshots TOD and CPU timer values, enables branch prediction with `bpon()`, then loads a PSW accepting external, I/O, and machine-check interrupts. `do_io_irq()` and `do_ext_irq()` clear `CIF_ENABLED_WAIT`, update idle timers, call `account_idle_time_irq()`, and strip wait/enabled interrupt bits from the resumed PSW.

Dependencies and integration: depends on lowcore interrupt clocks, CPU timer helpers, CPU-MF MT diagnostics, power trace headers, s390 idle flags, and generic `account_idle_time()`. `arch_cpu_idle_dead()` delegates CPU death to `cpu_die()`.

Risks and test signals: incorrect flag handling can resume in wait state or double-account idle time. Validate with CPU idle stats, `/sys/devices/system/cpu/cpu*/idle_*`, interrupt wakeups from idle, NOHZ behavior, and CPU hotplug/offline paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ipl.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ipl.c

Purpose: central Initial Program Load, re-IPL, dump, shutdown, secure-boot, and kexec report support for Linux on s390. It exposes current boot information, lets users configure reboot/dump targets, and issues DIAG 308 firmware calls during shutdown.

Important APIs and state: global preserved boot data includes `ipl_block`, `ipl_block_valid`, `ipl_secure_flag`, certificate list addresses, and component list data. Public integration points include `diag308()`, `ipl_info`, `setup_ipl()`, `s390_reset_system()`, `arch_get_secureboot()`, `set_os_info_reipl_block()`, and, under kexec-file, `ipl_report_*()` helpers. Mutable state tracks reipl/dump capabilities, selected `reipl_type`/`dump_type`, allocated IPL parameter blocks for CCW/FCP/NVMe/ECKD/NSS, clear flags, shutdown triggers, and optional z/VM commands.

Control flow: early setup derives `ipl_info` from the preserved parameter block and registers the panic notifier. Init creates firmware sysfs ksets: `ipl`, `reipl`, `dump`, `vmcmd`, and `shutdown_actions`. Sysfs store methods validate and mutate parameter blocks, loadparm, VM parm, SCP data, boot program selectors, and selected shutdown actions. Shutdown entry points stop CPUs and invoke trigger actions, which either issue `DIAG308_SET` plus load subcodes, request dump loops, run VM CP commands, or stop in disabled wait.

Persistence behavior: configured reipl blocks are copied into OS info for crash/kdump handoff; dump-reipl also writes lowcore `ipib` and checksum. Kexec-file report construction serializes the IPL block, component entries, and certificates for secure IPL reporting.

Dependencies and integration: tightly coupled to firmware kobjects, SCLP IPL info, DIAG 308, lowcore, OS info, kexec, panic/reboot hooks, z/VM CP commands, EBCDIC conversion, and secure boot.

Risks and test signals: high-risk areas are sysfs input bounds, EBCDIC/ASCII conversion, firmware capability mismatches, stale OS-info reipl blocks, and shutdown paths that intentionally do not return. Test via sysfs attribute read/write, VM vs LPAR boot modes, dump/reipl dry runs where available, secure boot reporting, kexec-file load with certificates, and panic/restart/halt trigger selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ipl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ipl_vmparm.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/ipl_vmparm.c

Purpose: converts the VM IPL parameter field from an IPL parameter block into a NUL-terminated ASCII string.

Important API: `ipl_block_get_ascii_vmparm(char *dest, size_t size, const struct ipl_parameter_block *ipb)` checks the CCW VM parameter-present flag and length, copies at most `size - 1` bytes, normalizes all-uppercase EBCDIC to lowercase EBCDIC when no lowercase is present, converts from EBCDIC to ASCII, terminates the buffer, and returns the copied length.

Control flow and state: this file is stateless. It only reads `ipb->ccw.vm_flags`, `vm_parm_len`, and `vm_parm`. The lowercase detection scans EBCDIC lowercase byte ranges before applying `EBC_TOLOWER()` and `EBCASC()`.

Dependencies and integration: used by `ipl.c` for `/sys/firmware/ipl/parm` and reipl VM parameter display. Depends on `asm/ipl.h` layout and EBCDIC helpers.

Risks and test signals: callers must pass nonzero `size`, because the function computes `size - 1`. Test empty/no-flag cases, maximum `DIAG308_VMPARM_SIZE`, mixed case preservation, uppercase normalization, and sysfs display consistency after reipl parameter writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/ipl_vmparm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/irq.c

Purpose: handles s390 external and I/O interrupt entry, interrupt accounting display, external interrupt handler registration, and interrupt subclass reference management.

Important APIs and state: per-CPU `irq_stat` tracks arch interrupt subclasses. `do_io_irq()` and `do_ext_irq()` are noinstr entry points. `show_interrupts()` backs `/proc/interrupts`; `arch_dynirq_lower_bound()` reserves base IRQs. `register_external_irq()` and `unregister_external_irq()` maintain an RCU hlist hash of external interrupt handlers. `irq_subclass_register()` and `irq_subclass_unregister()` manage CR0 subclass bits with refcounts.

Control flow: interrupt entry saves/restores irq regs, enters generic irqentry/RCU accounting, handles idle exit accounting, updates user-mode timer state and BEAR last-break data, then dispatches on async stack when needed. I/O entry loops on pending interrupts on LPAR and selects thin vs regular I/O based on lowcore TPI info. External entry copies lowcore external parameters and calls the registered handler chain for the code.

Dependencies and integration: integrates generic IRQ, `/proc/interrupts`, CIO/AIRQ init, clock comparator work, lowcore, irqentry, vtime, async stacks, RCU, and control-register subclass management. CPU-MF, virtio, IUCV, PCI, AP, and other facilities register external handlers here.

Risks and test signals: stack switching, idle accounting, RCU lifetime of handlers, and subclass refcount underflow are sensitive. Test with `/proc/interrupts`, external IRQ register/unregister users, CPU hotplug, timer-heavy idle workloads, LPAR pending I/O loops, and lockdep/RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/jump_label.c

Purpose: implements s390 jump-label static branch patching by replacing six-byte `brcl` encodings between no-op and unconditional branch forms.

Important APIs and types: `struct insn` is the packed opcode/offset form. `arch_jump_label_transform()`, `arch_jump_label_transform_queue()`, and `arch_jump_label_transform_apply()` are the architecture hooks used by the generic jump-label core.

Control flow: helpers build expected old and desired new instruction bytes from `jump_entry_code()` and `jump_entry_target()`. `jump_label_transform()` validates that the live text matches the expected form, panics on mismatch via `jump_label_bug()`, writes the replacement with `s390_kernel_write()`, and callers synchronize text poking through `text_poke_sync()`.

Dependencies and integration: depends on generic jump labels, module jump entries, s390 text patching, and IPL panic behavior. Queued transforms write immediately but defer the sync to `arch_jump_label_transform_apply()`.

Risks and test signals: wrong offsets or patching corrupted text is fatal by design. Test static keys in built-in and module code, queued batch patching, module load/unload with jump labels, and mismatch detection in fault-injection or debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kdebugfs.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/kdebugfs.c

Purpose: creates the architecture debugfs root directory for s390.

Important API and state: exports `struct dentry *arch_debugfs_dir` for other s390 code to place debugfs files under `/sys/kernel/debug/s390`. `arch_kdebugfs_init()` creates the directory at `postcore_initcall` time.

Control flow: initialization calls `debugfs_create_dir("s390", NULL)` and stores the returned dentry. There is no teardown path, matching kernel debugfs lifetime.

Dependencies and integration: used by files such as `hiperdispatch.c` for architecture-scoped debug counters. Depends only on debugfs, initcall ordering, and symbol export.

Risks and test signals: users must tolerate NULL when debugfs is disabled or creation fails. Test by mounting debugfs and checking `/sys/kernel/debug/s390`, plus callers that create children before/after postcore init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kdebugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_elf.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_elf.c

Purpose: loader for ELF kernels passed to the `kexec_file_load` syscall on s390.

Important APIs: `s390_kexec_elf_ops` supplies `.probe`, `.load`, and optional `.verify_sig`. `s390_elf_probe()` only checks ELF magic so invalid ELF-like images are rejected by the stricter loader. `s390_elf_load()` validates executable 64-bit s390 ELF headers, program header bounds, no `PT_INTERP`, and segment sizing. `kexec_file_add_kernel_elf()` adds each `PT_LOAD` segment through `kexec_add_buffer()`.

Control flow and state: loader chooses the entry point from ELF `e_entry` or `STARTUP_KDUMP_OFFSET` for crash kernels, aligns segment memory by `p_align`, offsets crash images by `crashk_res.start`, records the segment containing the entry as `data->kernel_buf`, `kernel_mem`, and `parm`, accumulates `data->memsz`, and adds signed/verified components to the IPL report.

Dependencies and integration: called by `machine_kexec_file.c` through `kexec_file_add_components()`. Depends on generic kexec buffers, ELF helpers, crash dump resource state, and IPL report helpers.

Risks and test signals: segment bound validation and alignment drive memory placement. Test malformed ELF headers, missing/oversized program headers, crash vs normal load, entry-in-segment detection, command line parm area writes, and secure IPL report contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_elf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_image.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_image.c

Purpose: fallback/raw image loader for `kexec_file_load` on s390 when no reliable image format probe is possible.

Important APIs: `s390_kexec_image_ops` always probes successfully, loads through `s390_image_load()`, and optionally uses `s390_verify_sig`. `kexec_file_add_kernel_image()` adds the entire kernel buffer as one kexec buffer.

Control flow and state: normal images are loaded at physical 0; crash images are offset by `crashk_res.start`. The function sets `data->kernel_buf`, `data->kernel_mem`, `data->parm` at `PARMAREA`, and increases `data->memsz` by image length. The loaded image is added to the IPL report as signed and verified.

Dependencies and integration: this is the second loader in `kexec_file_loaders[]` after ELF. It relies on `kexec_file_add_components()` for command line, initrd, purgatory, and IPL report assembly.

Risks and test signals: because probe always succeeds, validation is deferred to later boot/purgatory behavior. Test loader ordering, raw image kexec, crash image offsetting, too-small parm area rejection in the common component path, and secure signature behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_image.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/kprobes.c

Purpose: s390 architecture implementation of kprobes, including instruction slot allocation, breakpoint patching, PER-based single stepping, reentrancy handling, and exception notifier integration.

Important APIs and state: per-CPU `current_kprobe` and `kprobe_ctlblk` hold active probe state. Hooks include `alloc_insn_page()`, `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_fault_handler()`, `kprobe_exceptions_notify()`, `arch_populate_kprobe_blacklist()`, and `arch_trampoline_kprobe()`.

Control flow: preparation verifies instruction boundaries with symbol-size decoding, rejects prohibited opcodes, allocates executable instruction slots, and copies/adjusts relative-long instructions. Arm/disarm writes a breakpoint or original opcode using `s390_kernel_write()` and either `text_poke_sync()` or `stop_machine_cpuslocked()`. Breakpoint notification disables preemption, pushes probe state, runs pre-handlers, enables PER single-step on the copied instruction, resumes/fixes PSW/registers after the single-step trap, then runs post-handlers. Fault paths restore state or try exception fixups.

Dependencies and integration: depends on disassembler helpers, extable fixups, text patching, executable memory, stop_machine, ftrace/kdebug notifier events, PER control registers, and irqentry blacklist sections.

Risks and test signals: instruction decoding, relative displacement fixup, PER mask restore, and reentrant probe BUG paths are critical. Test probes on branches, modules, faulting instructions, nested handlers, remove races, irqentry blacklist rejection, and systems without sequential instruction patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/lgr.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/lgr.c

Purpose: detects and logs Linux Guest Relocation-relevant machine identity changes using facility and STSI data.

Important APIs and state: `struct lgr_info` stores STFL facility bits, system level, CEC, LPAR, and up to two z/VM nesting levels. `lgr_info_log()` is exported GPL and records changes to s390 debug feature data. Static state includes a page-aligned STSI buffer, last/current snapshots, debug feature handle, and a deferrable timer.

Control flow: `lgr_info_get()` clears the snapshot, stores facility bits, determines STSI level, and fills level-specific fields while converting EBCDIC to ASCII. `lgr_info_log()` uses a trylock, compares current vs previous snapshots, and writes changed records to s390dbf. A timer calls this every 30 minutes after `lgr_init()` records the initial state.

Dependencies and integration: uses `stfle`, `stsi`, EBCDIC conversion, s390 debug feature views, timers, and is called by kdump/kexec paths to log relocation state before reset.

Risks and test signals: STSI failures leave partial zero fields; trylock can skip concurrent logs. Test debugfs/s390dbf output, timer firing, manual calls around guest relocation, VM nesting truncation, and EBCDIC field conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/lgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec.c

Purpose: executes normal kexec and crash kdump transitions on s390, including system reset, purgatory checksum checks, status save, crashkernel protection, and relocation-code handoff.

Important APIs and state: implements `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, `machine_kexec()`, crash resource protect/unprotect, and `crash_free_reserved_phys_range()`. It uses external `relocate_kernel` code and calls purgatory entry points via `call_nodat()`.

Control flow: normal kexec copies relocation code into the control code page, disables tracing/locks, stops CPUs, resets the system, and calls the relocation stub with the image list, entry, and DIAG 308 reset flags. Crash kexec validates purgatory checksum, logs LGR info, stores other CPU statuses, saves boot CPU vector/guarded-storage state, then tail-calls through `store_status()` into `__do_machine_kdump()`, which resets and calls purgatory.

Dependencies and integration: tied to kexec core, crash dump resources, lowcore, guarded storage, vector registers, pfault/CIO/SCLP reset, OS info reipl block preservation, SMP IPL CPU calls, and memory attribute helpers for crashkernel protection.

Risks and test signals: non-returning reset paths, crash CPU status consistency, purgatory checksum failures, and crashkernel memory permissions are high risk. Test normal kexec, kdump under load, crashkernel protect/unprotect, reserved range freeing, VM `diag10_range()`, and dump analysis backchains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_file.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_file.c

Purpose: s390 `kexec_file_load` common component assembly, signature verification, purgatory symbol patching, initrd placement, IPL report placement, and purgatory relocation handling.

Important APIs and state: exports `kexec_file_loaders[]`, optional `s390_verify_sig()`, `kexec_file_add_components()`, `arch_kexec_apply_relocations_add()`, and `arch_kimage_file_post_load_cleanup()`. `struct s390_load_data` carries kernel buffer, parm area, memory size, and report during load.

Control flow: signature verification is enforced only when secure IPL is active, requiring module-signature marker, PKCS#7 signature metadata, and secondary or platform keyring success. Component assembly initializes an IPL report, delegates kernel loading, validates parm area and command line capacity, copies command line and crash oldmem data, adds initrd and purgatory, patches purgatory symbols such as `kernel_entry`, `kernel_type`, `crash_start`, and `crash_size`, handles the restart PSW special case for memory 0, then writes the IPL report as another kexec buffer and stores its lowcore pointer.

Dependencies and integration: depends on loader ops from ELF/raw image files, generic kexec buffers/purgatory, verification keyrings, boot data, lowcore offsets, crash resources, and IPL report/certificate helpers in `ipl.c`.

Risks and test signals: secure IPL signature parsing, command-line bounds, certificate list walking, crash offset arithmetic, and purgatory relocations are key. Test signed/unsigned secure boot, platform keyring fallback, initrd placement, malformed signature trailers, relocation types, cleanup freeing `image->arch.ipl_buf`, and normal/crash kexec-file boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_reloc.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_reloc.c

Purpose: applies s390 ELF relocation records used while relocating kexec purgatory code.

Important API: `arch_kexec_do_relocs(int r_type, void *loc, unsigned long val, unsigned long addr)` supports direct 8/12/16/20/32/64 relocations, GOT/JMP slot absolute 64-bit writes, PC-relative 16/32/64 forms with optional halfword shifting, and `R_390_RELATIVE`.

Control flow and state: stateless switch over relocation type writes directly into the temporary purgatory buffer. Unsupported types return 1 so callers report an invalid relocation.

Dependencies and integration: called by `arch_kexec_apply_relocations_add()` in `machine_kexec_file.c`; relocation constants come from ELF/s390 ABI headers.

Risks and test signals: relocation truncation is not range-checked here, so callers and generated purgatory must only use supported safe forms. Test purgatory link changes, `R_390_PLT32DBL` remapping in caller, and byte layout of 12/20-bit split fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec_reloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/mcount.S -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/mcount.S

Purpose: assembly trampolines for s390 ftrace, function graph tracing, hotpatch branch thunks, and rethook return interception.

Important symbols: `ftrace_stub`, `ftrace_stub_direct_tramp`, `ftrace_regs_caller`, `ftrace_caller`, `ftrace_common`, optional `return_to_handler`, `ftrace_shared_hotpatch_trampoline_br`, optional `ftrace_shared_hotpatch_trampoline_exrl`, and optional `arch_rethook_trampoline`.

Control flow: ftrace caller entries build packed traced-function frames plus `ftrace_regs`/`pt_regs`-compatible data, compute the traced function address from `%r0 - MCOUNT_INSN_SIZE`, load `function_trace_op` and `ftrace_func`, call the active tracer, restore registers, and branch to the selected return address. Function graph support calls `ftrace_return_to_handler()` and returns to its chosen address. Hotpatch trampolines load target registers and branch directly or through expoline `exrl`. Rethook builds full pt_regs, calls `arch_rethook_trampoline_callback()`, then restores PSW/registers through `lpswe`.

Dependencies and integration: depends on generated asm offsets, ftrace ABI, nospec branch macros, expoline config, rethook config, and kprobes text section placement.

Risks and test signals: stack frame layout, PSW preservation, `%r14/%r15` handling, and expoline return paths are critical. Test function tracer with and without full regs, graph tracer, direct trampolines, live ftrace patching, rethook users, and expoline-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/module.c

Purpose: s390 module loader architecture support for GOT/PLT sizing, ELF relocation application, module finalization patching, stack protector setup, alternatives, expoline reversion, and ftrace trampoline allocation.

Important APIs and state: `module_frob_arch_sections()` scans symbols and relocations, initializes `mod->arch.syminfo`, and grows module text memory for GOT/PLT. `apply_relocate_add()` applies relocations with `memcpy` during early unformed state or `s390_kernel_write()` later. `module_finalize()` applies alternatives, nospec reverts, stack-protector locations, and ftrace callsite trampoline allocation. Cleanup frees syminfo and optional ftrace executable memory.

Control flow: `check_rela()` assigns per-symbol GOT/PLT offsets. `apply_rela_bits()` validates alignment, signedness, bit width, and shifted values before writing split/direct fields. `apply_rela()` handles direct, PC-relative, GOT, PLT, GOTOFF, GOTPC, and unsupported dynamic relocations. PLT entries are synthesized with optional expoline tail thunk when speculation mitigation is active.

Dependencies and integration: depends on module core memory classes, s390 ABI relocation constants, executable memory, alternatives, nospec branch state, stack protector, ftrace linker sections, and livepatch module lifetime.

Risks and test signals: relocation range errors, PLT fallback selection, expoline thunk sizing, late text writes, and livepatch cleanup are sensitive. Test modules with far calls, GOT-heavy code, livepatch modules, ftrace-enabled modules, expoline on/off, stack protector, alternatives, and unknown relocation rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/nmi.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/nmi.c

Purpose: machine-check/NMI handling for s390, including MCESA allocation, emergency reporting, recoverability decisions, guest machine-check backup, deferred handling, and control-register mask setup.

Important APIs and state: per-CPU `cpu_mcck` accumulates `kill_task`, `channel_report`, `warning`, `stp_queue`, and machine-check code. Public helpers include `nmi_alloc_mcesa_early()`, `nmi_alloc_mcesa()`, `nmi_free_mcesa()`, `s390_handle_mcck()`, and `s390_do_machine_check()`.

Control flow: early and hotplug allocation provide machine-check extended save areas for vector/guarded-storage capable systems. Fatal damage path emergency-stops CPUs, resets via DIAG 308, disables low-address protection, prints lowcore/register state through SCLP emergency output, restores analyzable state, and enters disabled wait. The NMI handler enters irqentry NMI context, validates register-save bits, distinguishes host vs KVM guest damage, backs up guest interruption data when needed, handles storage/timing/channel/warning/STP subclasses, schedules deferred machine-check work, and clears guest flags.

Dependencies and integration: uses lowcore, control registers, SCLP, SMP emergency stop, KVM SIE state, STP, CRW handling, process signal delivery, vtime, irq stats, vector/GS save helpers, and kprobes blacklist markers.

Risks and test signals: recovery logic is safety-critical; wrong validity decisions can kill tasks, damage guests, or hang systems. Test with machine-check injection/facility simulation, KVM guest paths, warning masks, STP external damage, vector/GS systems, crash dump readability, and repeated instruction-processing damage thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-branch.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-branch.c

Purpose: controls s390 Spectre v2 branch prediction mitigations, including limited branch prediction (`nobp`), expoline enable/disable, automatic detection, status reporting, and runtime reversion of expoline call/return sites.

Important APIs and state: global `nobp` and, with `CONFIG_EXPOLINE`, `nospec_disable` represent selected mitigations. Early parameters include `nobp=`, `nospec`, `nospectre_v2`, and `spectre_v2=on/off/auto`. Runtime hooks include `nospec_auto_detect()`, `nospec_init_branches()`, and `nospec_revert()`.

Control flow: early params set policy based on user input, compiler expoline support, facility 82/156, and global CPU mitigation mode. Reporting prints active etokens, execute trampolines, or limited branch prediction. Reversion scans offset tables, recognizes `brcl`/`brasl` calls into expoline thunks, verifies thunk `exrl` and branch-register layout, then patches the call site to direct branch/basr plus NOP.

Dependencies and integration: used by module finalization for `.s390_indirect*` and `.s390_return*` sections, by boot init for built-in nospec sections, and by sysfs vulnerability reporting.

Risks and test signals: patch recognition must be exact to avoid corrupting text. Test boot params, facility 156 machines, expoline compiler vs non-expoline builds, module loading with nospec sections, and `/sys/devices/system/cpu/vulnerabilities/spectre_v2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-sysfs.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-sysfs.c

Purpose: provides s390 CPU vulnerability sysfs strings for Spectre v1 and v2.

Important APIs: `cpu_show_spectre_v1()` always reports `__user` pointer sanitization. `cpu_show_spectre_v2()` reports etokens when facility 156 is present, execute trampolines when expolines are active, limited branch prediction when `nobp` is active, otherwise vulnerable.

Control flow and state: stateless display functions read mitigation state through `test_facility(156)`, `nospec_uses_trampoline()`, and `nobp_enabled()`.

Dependencies and integration: called by generic CPU vulnerability sysfs code and depends on mitigation policy set in `nospec-branch.c`.

Risks and test signals: reporting must track actual mitigation policy. Test combinations of boot parameters, CPU facilities, expoline config, and expected contents of `/sys/devices/system/cpu/vulnerabilities/spectre_v1` and `spectre_v2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/numa.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/numa.c

Purpose: minimal s390 NUMA setup that presents a single online node while allocating `pg_data_t` structures for all possible nodes.

Important API and state: `numa_setup()` clears possible nodes, marks node 0 possible and online, allocates `NODE_DATA(nid)` for each `MAX_NUMNODES` entry from memblock, and sets node 0 span to all DRAM pages.

Control flow: runs during early memory setup; there is no dynamic state beyond node maps and `NODE_DATA`.

Dependencies and integration: depends on generic NUMA node maps, memblock allocation, `memblock_end_of_DRAM()`, and `asm/numa.h`.

Risks and test signals: this intentionally does not model multi-node topology. Test boot memory maps, `/sys/devices/system/node`, `numactl --hardware`, node 0 span, and boot with unusual memory holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/os_info.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/os_info.c

Purpose: maintains the page-aligned s390 OS info block used by firmware/crash kernels to discover kernel layout, crashkernel state, vmcoreinfo, and reipl data from lowcore.

Important APIs and state: static `os_info` is one page. `os_info_csum()` checksums the version-to-end range. Writers include `os_info_crashkernel_add()`, `os_info_entry_add_data()`, `os_info_entry_add_val()`, and `os_info_init()`. Under `CONFIG_CRASH_DUMP`, `os_info_old_entry()` lazily copies and validates entries from old memory.

Control flow: init fills magic/version, identity/KASLR/vmemmap/amode31/image addresses, computes checksum, and writes the physical OS info pointer into absolute lowcore. Runtime writers update entries and recompute checksum. Crash-dump old-info loading checks oldmem availability or dump IPL type, reads old lowcore pointer, validates alignment, magic, checksum, and version, then copies selected entries with per-entry checksums.

Dependencies and integration: used by IPL/reipl, kexec crash, vmcoreinfo, lowcore, oldmem access, checksum helpers, physical memory info, and KASLR/layout symbols.

Risks and test signals: checksum, physical-vs-virtual address handling, and alignment are critical for crash kernels. Test normal boot lowcore pointer, crash dump old-info discovery, corrupted checksums, missing oldmem, reipl block persistence, and crashkernel address updates after reserved memory changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/os_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf.c -->
# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf.c

Purpose: implements s390 CPU Measurement Counter Facility support for perf (`cpum_cf`), complete counter-set diagnostic sampling (`cpum_cf_diag`), and the `/dev/hwctr` ioctl interface.

Important APIs and state: `struct cpu_cf_events` holds per-CPU refcounts, counter-set reference counts, perf state, device state, flags, and page buffers for start/stop/data. Global `cpu_cf_root` anchors per-CPU pointers; `pmc_reserve_mutex` serializes perf allocation/removal; `cfset_ctrset_mutex`, `cfset_session`, and `cfset_opencnt` serialize `/dev/hwctr`. PMUs are `cpumf_pmu` and `cf_diag`; the misc device is `cfset_dev`.

Control flow: init queries CPU-MF info with `qctri()`, derives counter-set sizes, clears problem-state extraction auth, registers measurement-alert external IRQ, creates s390dbf, registers the perf PMU, optional `/dev/hwctr`, diagnostic PMU, and CPU hotplug state. Perf event init maps hardware/raw events to counter sets, validates authorization/version, and allocates per-CPU structures. PMU enable/disable writes LCCTL state; start/stop updates counter-set activation, snapshots ECCTR or full counter sets, computes deltas, and pushes raw samples for CF_DIAG.

Device behavior: `/dev/hwctr` open requires `perfmon_capable()`, allocates all online CPUs on first open, START copies a user cpumask and counter-set mask, starts sets on requested CPUs, READ extracts complete sets to user buffers, STOP/release deactivates and frees sessions. CPU hotplug extends or shrinks active device sessions.

Dependencies and integration: uses CPU-MF instructions `lcctl`, `ecctr`, `stcctm`, `qctri`, measurement-alert external interrupts, perf core, miscdevice, CPU hotplug, debug feature, irq subclass control, and user ABI structs from `asm/hwctrset.h`.

Risks and test signals: authorization changes, hotplug races, shared perf/device state, buffer sizing, user copy bounds, and counter wrap handling are key. Test perf raw/hardware events, exclude modifiers, CF_DIAG raw samples, `/dev/hwctr` START/READ/STOP, CPU hotplug with active sessions, measurement alerts, SMT MT-diagnostic counters, and machines with varying counter versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kernel/perf_cpum_cf.c -->
