# subset-b-000887 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/itmt.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/itmt.c

Purpose: Provides x86 scheduler integration for Intel Turbo Boost Max Technology 3.0. On systems where some cores have higher maximum turbo capability, this file lets platform code publish per-CPU priorities and exposes a debugfs switch so scheduler domains can prefer stronger cores.

Important APIs/types/functions: exports `sched_set_itmt_support()`, `sched_clear_itmt_support()`, `sched_set_itmt_core_prio()`, and `arch_asym_cpu_priority()`. Global state is `DEFINE_PER_CPU_READ_MOSTLY(int, sched_core_priority)`, `sched_itmt_capable`, and `sysctl_sched_itmt_enabled`. Debugfs entries are `sched_itmt_enabled` and `sched_core_priority`.

Control flow: platform or pstate code first calls `sched_set_itmt_core_prio()` per CPU, then `sched_set_itmt_support()`. Support creation registers debugfs files under `arch_debugfs_dir`, marks the machine capable, enables the scheduler feature, sets `x86_topology_update`, and calls `rebuild_sched_domains()`. Writes to debugfs go through `sched_itmt_enabled_write()`, which compares the old boolean with the new value and rebuilds sched domains only on actual change. Clearing support removes debugfs files and disables scheduler preference if it was enabled.

State and persistence: all state is in kernel memory and per-CPU variables. CPU priorities persist for the running boot only. The debugfs control is not persistent across reboot and has no on-disk backing.

Dependencies and integration points: depends on scheduler asymmetry hooks, x86 topology rebuilds, cpuset/sched-domain rebuild machinery, debugfs, and `arch_debugfs_dir` from `kdebugfs.c`. Power-management code is expected to discover ITMT capability and call these APIs.

Risks: calling support before priorities are initialized can produce misleading scheduler preference. Rebuilds must not run under CPU hotplug locks as documented. Failure after creating the first debugfs file leaves capability disabled but does not remove the first file in this implementation path, so init-error cleanup assumptions should be checked if changed.

Test signals: boot on ITMT-capable hardware should create both debugfs files, show nonzero per-CPU priorities, and rebuild sched domains when toggled. Non-capable systems should not expose the files. CPU hotplug and pstate enable/disable paths should not deadlock with topology rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/itmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/jailhouse.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/jailhouse.c

Purpose: Implements x86 hypervisor detection and paravirtual platform setup for Jailhouse non-root cells. It replaces normal firmware, ACPI, SMP, PCI, timer, and restart assumptions with values supplied through Jailhouse setup data.

Important APIs/types/functions: main externally visible pieces are `jailhouse_paravirt()` and `x86_hyper_jailhouse`. Internal setup flows include `jailhouse_cpuid_base()`, `jailhouse_init_platform()`, `jailhouse_parse_smp_config()`, `jailhouse_pci_arch_init()`, `jailhouse_timer_init()`, `jailhouse_serial_workaround()`, and `jailhouse_no_restart()`. Static state is `setup_data` and `precalibrated_tsc_khz`.

Control flow: detection checks CPUID hypervisor leaves for the `Jailhouse` signature. Platform init overrides `x86_init` and `x86_platform` hooks, disables legacy PIC and ACPI, walks boot `setup_data` records to find `SETUP_JAILHOUSE`, validates version and size, then stores PM timer, APIC frequency, TSC frequency, PCI MMCONFIG, CPU IDs, and UART flags. SMP parsing registers LAPIC address, per-cell APIC IDs, optional IOAPIC, and legacy UART IRQs. PCI init enables direct config access and full root-bus scan because Jailhouse cells have no bridge topology.

State and persistence: state is boot-time only. Jailhouse-provided setup data is copied into a static structure and used to seed kernel platform globals such as `pmtmr_ioport`, `lapic_timer_period`, `pcibios_last_bus`, `pci_probe`, and TSC-known-frequency capability.

Dependencies and integration points: integrates with the x86 hypervisor table, APIC/x2APIC selection, mptable/IOAPIC registration, PCI direct/MMCONFIG code, serial 8250 ISA configurator, reboot machine ops, and ACPI disable path.

Risks: invalid or incompatible setup data panics early. x2APIC must use physical mode because interrupt remapping is unavailable. Version 1 UART handling assumes legacy IRQ mapping, while version 2 can selectively disable inaccessible UART ports. Restart is unsupported and halts instead.

Test signals: booting a Jailhouse non-root Linux cell should detect the hypervisor, avoid ACPI-table complaints, register the supplied CPU IDs and IOAPIC, set known TSC frequency, scan virtual PCI devices, and enforce UART access flags. Unsupported setup-data versions should panic with the expected message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/jailhouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/jump_label.c

Purpose: Provides x86 runtime patching for Linux static keys and jump labels. It switches compiled NOP sites to relative jumps, or back, using x86 text patching primitives.

Important APIs/types/functions: defines `arch_jump_entry_size()`, `arch_jump_label_transform()`, `arch_jump_label_transform_queue()`, and `arch_jump_label_transform_apply()`. Internal helper `__jump_label_patch()` validates the current instruction bytes and returns a `struct jump_label_patch` with replacement bytes and size.

Control flow: each jump entry identifies a code address and target. `arch_jump_entry_size()` decodes the instruction at the code address and accepts only 2-byte or 5-byte sites. `__jump_label_patch()` generates a short or near jump with `text_gen_insn()` or selects the matching x86 NOP sequence, then verifies the current bytes match the expected old state. Early boot and init transforms use `text_poke_early()`. Runtime single transforms use `smp_text_poke_single()`, while queued transforms add entries to the batch list and later flush them with `smp_text_poke_batch_finish()`.

State and persistence: no private persistent data is kept. State is encoded directly in kernel text as either an x86 NOP or JMP instruction. Batching state lives in the shared text-patching subsystem.

Dependencies and integration points: depends on `jump_entry` metadata emitted by the compiler/kernel, x86 instruction decoding, `x86_nops`, `text_mutex`, and SMP-safe text-poke APIs. It also respects boot state because text is still writable and single-CPU during early boot.

Risks: any byte mismatch is treated as fatal and triggers `BUG()` because it indicates text corruption or conflicting patchers. Instruction size assumptions must remain aligned with generated jump-label sites. Runtime callers must serialize through `text_mutex` to avoid races with other text patching such as alternatives, static calls, ftrace, or kprobes.

Test signals: static key selftests should toggle both 2-byte and 5-byte sites, exercise boot-time and runtime changes, and validate queued apply behavior. Fault-injection or debug builds should catch unexpected-byte detection if another patcher touches a site.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kdebugfs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kdebugfs.c

Purpose: Creates the architecture debugfs root `/sys/kernel/debug/x86` and, when enabled, exposes boot parameter and setup-data contents for debugging early boot handoff structures.

Important APIs/types/functions: exports `arch_debugfs_dir`. Under `CONFIG_DEBUG_BOOT_PARAMS`, defines `struct setup_data_node`, `setup_data_read()`, `create_setup_data_nodes()`, and `boot_params_kdebugfs_init()`. The init entry point is `arch_kdebugfs_init()` via `arch_initcall`.

Control flow: init creates the `x86` debugfs directory. With boot parameter debugging enabled, it creates `boot_params`, a scalar `version` file, a blob `data` file containing the whole `boot_params`, and one numbered directory per setup-data node. Setup-data enumeration follows `boot_params.hdr.setup_data`; for indirect nodes it remaps enough bytes to inspect `struct setup_indirect` and either exposes the indirect target or the raw invalid indirect payload. File reads remap the requested physical range, copy to user, and update the file offset.

State and persistence: `arch_debugfs_dir` is a global dentry used by other x86 debugfs providers such as ITMT. Each setup-data node is heap allocated and attached as debugfs private data. All content reflects in-memory boot parameters and physical setup-data payloads for the running kernel only.

Dependencies and integration points: depends on debugfs, `boot_params`, `memremap()`/`memunmap()`, setup-data type definitions, and user-copy helpers. It mirrors some of the same setup-data exposure implemented in `ksysfs.c`, but under debugfs and gated by `CONFIG_DEBUG_BOOT_PARAMS`.

Risks: exposing raw boot parameters and setup data can reveal platform information and should remain debug-only. Physical remap failures return `-ENOMEM`; user-copy failure returns `-EFAULT`. The allocated node objects are not freed after successful debugfs creation, matching debugfs lifetime for the boot.

Test signals: with `CONFIG_DEBUG_BOOT_PARAMS`, verify `/sys/kernel/debug/x86/boot_params/data`, `version`, and numbered `setup_data/*/data` files read expected sizes and handle offsets. Systems with indirect setup data should expose the indirect target length and type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kdebugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kexec-bzimage64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kexec-bzimage64.c

Purpose: Implements the file-based kexec loader for 64-bit x86 bzImage kernels. It validates bzImage protocol requirements, allocates kexec segments for purgatory, boot parameters, kernel, initrd, and optional metadata, then prepares purgatory registers for entering the new kernel.

Important APIs/types/functions: exposes `kexec_bzImage64_ops` with `.probe`, `.load`, `.cleanup`, and optional `.verify_sig`. Key helpers are `bzImage64_probe()`, `bzImage64_load()`, `bzImage64_cleanup()`, `setup_boot_parameters()`, `setup_cmdline()`, `setup_initrd()`, `setup_e820_entries()`, `setup_rng_seed()`, EFI setup helpers, `setup_dtb()`, `setup_ima_state()`, and `setup_kho()`. Loader-private state is `struct bzimage64_data`.

Control flow: probe checks file length, boot signature, `HdrS`, protocol >= 2.12, high-load bzImage flags, 64-bit support, above-4G loading, EFI bitness, and 5-level paging compatibility. Load computes setup-sector size, validates command-line length including crash additions, optionally loads crash backup and dm-crypt key segments, loads purgatory, allocates a combined bootparams/cmdline/EFI/setup-data buffer, adds it as a segment, adds the protected-mode kernel payload, optionally adds initrd, writes command line pointers, sets loader type, patches purgatory `entry64_regs`, and fills boot parameters from current boot state.

State and persistence: data persists only in the staged `kimage` until execution or cleanup. The bootparams buffer is stored in `bzimage64_data` so cleanup can free it after the kexec core copies segments. Setup-data chain entries may carry RNG seed, EFI, DTB, IMA, and KHO handover metadata to the next kernel.

Dependencies and integration points: integrates with generic kexec file load APIs, x86 boot protocol structures, e820/crash memory setup, EFI runtime map copying, FDT, IMA kexec buffer, kexec handover, random subsystem, sysfb screen info, purgatory symbol patching, and optional PE signature verification.

Risks: command-line sizing must include crash `elfcorehdr=` and `dmcryptkeys=` additions. EFI and setup-data offsets must remain aligned and non-overlapping. Carrying runtime maps, DTB, IMA, and KHO data requires correct setup-data chaining. Loading kernels incompatible with current 5-level paging or 32-bit EFI is explicitly rejected.

Test signals: kexec-file tests should cover normal and crash kernels, initrd/no-initrd, long command lines near protocol limits, EFI runtime services, forced DTB carryover, IMA buffer handoff, KHO enabled and disabled, RNG initialized and uninitialized, 5-level paging incompatibility, and signature verification when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kexec-bzimage64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kgdb.c

Purpose: Supplies x86 architecture support for KGDB, including GDB register mapping, software breakpoint patching, hardware breakpoint management, NMI CPU roundup, die-notifier exception routing, and PC adjustment for x86 trap semantics.

Important APIs/types/functions: defines `dbg_reg_def`, `dbg_set_reg()`, `dbg_get_reg()`, `sleeping_thread_to_gdb_regs()`, `kgdb_arch_handle_exception()`, `kgdb_roundup_cpus()`, `kgdb_ll_trap()`, `kgdb_arch_init()`, `kgdb_arch_late()`, `kgdb_arch_exit()`, `kgdb_skipexception()`, `kgdb_arch_pc()`, `kgdb_arch_set_pc()`, `kgdb_arch_set_breakpoint()`, `kgdb_arch_remove_breakpoint()`, and `arch_kgdb_ops`. Hardware breakpoint state lives in `breakinfo[]` and `early_dr7`.

Control flow: KGDB registers die and NMI handlers. Exceptions enter `__kgdb_notify()`, which ignores user-mode traps except special single-step cases, calls `kgdb_handle_exception()`, and touches the NMI watchdog. Continue and single-step packets clear or set TF in `pt_regs`. SMP roundup uses NMI IPIs. Late init preallocates wide perf hardware breakpoints for each debug register slot; setting/removing KGDB hardware watchpoints reserves/releases slots and later `kgdb_correct_hw_break()` installs them per CPU.

State and persistence: register values are transient in `pt_regs` or sleeping task frames. Breakpoint state persists in memory while KGDB is active: software breakpoints save original bytes in `kgdb_bkpt`, and hardware breakpoints track enabled address, type, length, and per-CPU perf events. No state survives reboot.

Dependencies and integration points: depends on KGDB core, die notifiers, x86 debug registers, APIC NMIs, perf hardware breakpoint APIs, text patching, user-copy-safe kernel memory access, and `text_mutex` coordination with other patchers.

Risks: software breakpoint insertion falls back to `text_poke_kgdb()` only when normal copy fails and `text_mutex` is not locked. Hardware breakpoint reservations must avoid leaking perf slots on partial failures. NMI handling uses `was_in_debug_nmi` to consume follow-up unknown NMIs. PC for int3 is reported as `ip - 1`, matching x86 breakpoint trap behavior.

Test signals: KGDB tests should read/write GDB registers on 32-bit and 64-bit builds, set and remove software breakpoints in read-only kernel text, set execute/write/access hardware breakpoints, single-step kernel code, round up secondary CPUs with NMIs, and verify removed int3 skip handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/Makefile

Purpose: Selects the x86 kprobes implementation objects for the kernel build based on probe-related configuration symbols.

Important APIs/types/functions: no runtime API. Build rules add `core.o` for `CONFIG_KPROBES`, `opt.o` for `CONFIG_OPTPROBES`, and `ftrace.o` for `CONFIG_KPROBES_ON_FTRACE`.

Control flow: kbuild evaluates the three `obj-$(CONFIG_...)` lines and links only the objects needed by the configured feature set. `core.o` is the baseline architecture implementation; `opt.o` adds jump-optimized probes; `ftrace.o` adds dynamic ftrace-backed probes.

State and persistence: no runtime state. The persistent effect is compile-time inclusion or exclusion of architecture probe features.

Dependencies and integration points: integrates with top-level x86 kernel build rules and Linux kbuild config expansion. It mirrors the dependency layering in source: `opt.c` and `ftrace.c` both include `common.h` and rely on core kprobes data structures.

Risks: missing `core.o` when optional objects are enabled would break symbols such as `current_kprobe` and instruction-copy helpers. Accidental unconditional linking of optional objects would introduce unresolved references when their feature configs are off.

Test signals: build matrix should include `CONFIG_KPROBES=n`, baseline kprobes only, optprobes enabled, ftrace kprobes enabled, and both optional features enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/common.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/common.h

Purpose: Shared x86 kprobes/optprobes header that defines assembly register save/restore templates and declares cross-file helpers for instruction recovery, copying, relative branch synthesis, and optimized probe detours.

Important APIs/types/functions: defines `SAVE_REGS_STRING` and `RESTORE_REGS_STRING` for x86_64 and x86_32. Declares `can_boost()`, `recover_probed_instruction()`, `__copy_instruction()`, `synthesize_reljump()`, `synthesize_relcall()`, `setup_detour_execution()`, and `__recover_optprobed_insn()`. Provides no-op inline fallbacks for optprobe helpers when `CONFIG_OPTPROBES` is disabled.

Control flow: the header itself has no runtime flow. Its strings are embedded by `opt.c` in the optprobe trampoline template. Its declarations allow `core.c`, `opt.c`, and `ftrace.c` to share instruction manipulation logic without exposing it outside the x86 kprobes directory.

State and persistence: no state is stored here. It codifies the exact `pt_regs` stack layout expected by optprobe trampoline code, including skipped slots for `cs`, `ip`, `orig_ax`, and segment registers.

Dependencies and integration points: depends on x86 assembly/frame macros and the x86 instruction decoder type `struct insn`. It is tightly integrated with `struct pt_regs` layout and with `core.c` and `opt.c` implementations.

Risks: register push/pop order is an ABI between inline assembly and C handlers. Any `pt_regs` layout change, 32-bit segment handling change, or frame-pointer encoding change must update these strings. Incorrect fallback behavior under `!CONFIG_OPTPROBES` would affect normal kprobe single-step flow.

Test signals: compile both 32-bit and 64-bit configurations with and without optprobes. Runtime optprobe tests should verify saved registers, flags, stack pointer, and segment fields delivered to pre-handlers match int3-based kprobes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/core.c

Purpose: Implements baseline x86 kprobes: deciding whether an address can be probed, copying and relocating the probed instruction, patching int3 breakpoints into kernel text, handling int3 traps, emulating control-flow-sensitive instructions, and restoring execution after out-of-line single stepping.

Important APIs/types/functions: defines per-CPU `current_kprobe` and `kprobe_ctlblk`, `kretprobe_blacklist`, `can_boost()`, `recover_probed_instruction()`, `arch_adjust_kprobe_addr()`, `__copy_instruction()`, `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_int3_handler()`, `kprobe_fault_handler()`, and blacklist/init hooks. Helper families handle relative instruction synthesis, instruction-boundary validation, emulation, single-step setup/resume, and reentry.

Control flow: registration rejects alternative-text ranges, validates the target is an instruction boundary inside a symbol, skips exception/CFI-sensitive instructions, allocates an executable instruction slot, copies the original instruction, adjusts RIP-relative displacement, chooses emulation or out-of-line stepping, and stores the original first byte. Arming patches one byte of int3 into text and reports a perf text-poke event. Trap handling ignores user mode, looks up a kprobe at `ip - 1`, runs the pre-handler, either emulates or redirects IP to copied instruction, then catches the second int3 from the slot to resume original IP and invoke the post-handler.

State and persistence: state persists in registered `struct kprobe` objects, executable instruction slots, patched kernel text, and per-CPU current-probe control blocks. Boostable probes add a relative jump in the copied instruction slot when preemption is off and no post-handler is needed.

Dependencies and integration points: depends on kprobes core, x86 instruction decoder, kallsyms, exception tables, CFI trap metadata, ftrace and optprobe instruction recovery, KGDB breakpoint detection, text-poking, perf text-poke events, objtool no-probe annotations, and executable-memory slot allocators.

Risks: instruction decoding and RIP-relative displacement relocation are correctness-critical. Probing exception-fixup, CFI decode, alternative, ftrace, or KGDB-modified code can corrupt execution and is explicitly guarded. Reentered probes skip user handlers and can BUG on unrecoverable nested states. Faults during copied instruction execution must reset IP back to the original address.

Test signals: kprobe selftests should cover normal pre/post handlers, handler-modified IP, ret/call/jmp/jcc/loop/IF-emulated instructions, RIP-relative instructions, nested probes, optprobe recovery interaction, KGDB conflict, faulting copied instructions, blacklist coverage for entry text, and arm/disarm text-poke events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/ftrace.c

Purpose: Implements the x86 backend for kprobes-on-ftrace, letting probes at ftrace locations run from the ftrace callback path instead of patching an int3 breakpoint.

Important APIs/types/functions: defines `kprobe_ftrace_handler()` and `arch_prepare_kprobe_ftrace()`. It uses `ftrace_get_regs()`, `ftrace_test_recursion_trylock()`, `get_kprobe()`, per-CPU `current_kprobe`, and `struct kprobe_ctlblk`.

Control flow: the ftrace callback returns immediately when globally disabled or recursion lock acquisition fails. It looks up a kprobe at the ftrace IP and ignores missing or disabled probes. If another kprobe is already running, it increments missed count. Otherwise it sets `regs->ip` to `ip + INT3_INSN_SIZE` to mimic normal int3 entry, records the current probe, runs the pre-handler, optionally emulates a post-handler by advancing to `ip + MCOUNT_INSN_SIZE`, then restores the original IP and clears current-probe state.

State and persistence: no private persistent state. It uses the same registered `struct kprobe` objects and per-CPU kprobe state as core kprobes. `arch_prepare_kprobe_ftrace()` marks the architecture instruction slot as absent and non-boostable.

Dependencies and integration points: depends on dynamic ftrace with register saving, kprobes core, ftrace recursion protection, x86 int3 size and ftrace mcount instruction size conventions, and `common.h` declarations.

Risks: the fake int3 IP convention must match kprobe handlers that expect the breakpoint address plus one. Post-handler emulation assumes a 5-byte ftrace NOP/mcount site. Recursion handling is necessary because ftrace callbacks can run in sensitive contexts with preemption disabled.

Test signals: kprobes-on-ftrace selftests should place probes on ftrace-capable functions, verify pre/post handler register IP values, nested probe missed counts, global disable behavior, and equivalence with int3 probes for handler return semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/opt.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/opt.c

Purpose: Adds x86 optimized kprobes by replacing an int3 with a 5-byte relative jump to a generated detour buffer. The detour saves registers, calls the optimized callback, executes copied original instructions, and jumps back after the optimized range.

Important APIs/types/functions: defines `__recover_optprobed_insn()`, `arch_prepare_optimized_kprobe()`, `arch_check_optimized_kprobe()`, `arch_optimize_kprobes()`, `arch_unoptimize_kprobe()`, `arch_unoptimize_kprobes()`, `arch_remove_optimized_kprobe()`, `arch_within_optimized_kprobe()`, and `setup_detour_execution()`. Internal helpers include the assembly `optprobe_template_*` labels, `optimized_callback()`, `copy_optimized_instructions()`, and `can_optimize()`.

Control flow: preparation decodes the whole containing function to ensure no instruction jumps into the bytes that will be replaced, avoids entry text and exception-table code, allocates an optinsn slot, copies the trampoline template, copies enough boostable original instructions to cover 5 bytes, patches the template argument and callback call, appends a jump back, and writes it to RO executable memory. Optimization backs up the four bytes after int3 and atomically patches a relative jump. Unoptimization writes int3 first, synchronizes CPUs, restores the following bytes, and records perf text-poke events.

State and persistence: optimized state lives in `struct optimized_kprobe`: generated detour slot, copied original bytes, optimized size, and list state. Kernel text is modified from int3 to a relative jump while optimized.

Dependencies and integration points: depends on core kprobe instruction copying/recovery, text-poking, perf events, ftrace/alternatives/jump-label/static-call reservation checks, kallsyms, exception tables, KGDB breakpoint detection, nospec/SMAP CLAC handling, and `common.h` register-save templates.

Risks: relative jump reach must fit within 2 GB. Any branch into the overwritten range would execute corrupted code, so full-function decode is required. Retpoline/IBT assumptions affect indirect jump-table safety. Unoptimization order is critical to avoid CPUs executing mixed bytes. The detour register frame must match normal kprobe handler expectations.

Test signals: optprobe tests should verify optimization/unoptimization under load, probes near function starts and short functions, functions with direct and indirect branches, reserved text conflicts, KGDB breakpoint conflicts, SMAP-enabled CLAC patching, post-unopt instruction recovery, and perf text-poke notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/opt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ksysfs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ksysfs.c

Purpose: Exposes x86 boot parameters and setup-data records under `/sys/kernel/boot_params` using sysfs attributes and binary attributes.

Important APIs/types/functions: init entry is `boot_params_ksysfs_init()` via `arch_initcall`. Important helpers include `version_show()`, `boot_params_data_read()`, `get_setup_data_paddr()`, `get_setup_data_size()`, `type_show()`, `setup_data_data_read()`, `create_setup_data_node()`, `create_setup_data_nodes()`, and cleanup helpers. Attributes include `version`, binary `data`, and per-setup-data `type`/`data`.

Control flow: init creates the `boot_params` kobject under `kernel_kobj`, adds a group for the boot protocol version and full binary bootparams, then enumerates setup-data nodes from `boot_params.hdr.setup_data`. For each numbered node it computes the effective payload size, creates a kobject, sets the shared binary attribute size, and creates a group. Read paths remap setup-data headers, handle `SETUP_INDIRECT` by switching to the indirect target unless the target is itself invalid indirect, clamp offsets and counts, remap the payload, and copy bytes into sysfs buffers.

State and persistence: sysfs objects persist for the boot lifetime. The data is live kernel memory or physical setup-data content from boot and has no writable path. `data_attr.size` is a static bin attribute updated during node creation, so creation is serialized at init time.

Dependencies and integration points: depends on kobject/sysfs infrastructure, boot protocol structures, `memremap()`, setup-data indirect format, and `kernel_kobj`. It complements debugfs boot-param exposure in `kdebugfs.c` with a stable sysfs location.

Risks: indirect setup-data handling must avoid following recursively invalid indirect records. Shared `data_attr` mutation would be unsafe outside init-time single-threaded creation. Remapping the full setup-data length for partial reads can be heavier than needed but keeps logic simple.

Test signals: verify `/sys/kernel/boot_params/version` and `data` read correctly, numbered setup-data directories are created with correct binary sizes, offset reads clamp at EOF, indirect setup-data exposes the indirect type and payload, and init failures clean up created kobjects/groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ksysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kvm.c

Purpose: Implements the x86 guest-side KVM paravirtual platform. It detects KVM, enables paravirt clock and platform hooks, manages async page faults, steal time, PV EOI, PV IPIs, PV TLB flush, PV spinlocks, SEV migration/shared-page state, reboot/suspend cleanup, and halt-poll control.

Important APIs/types/functions: exports `kvm_para_available()`, `kvm_arch_para_hints()`, `kvm_async_pf_task_wait_schedule()`, `kvm_read_and_reset_apf_flags()`, haltpoll functions, and `x86_hyper_kvm`. Key flows include `kvm_guest_init()`, `kvm_init_platform()`, `kvm_guest_cpu_init()`, `kvm_guest_cpu_offline()`, `__kvm_handle_async_pf()`, `sysvec_kvm_asyncpf_interrupt()`, `kvm_flush_tlb_multi()`, `__send_ipi_mask()`, `kvm_spinlock_init()`, and SEV helpers.

Control flow: CPUID detection finds the KVM signature. Platform init sets SEV page encryption callbacks, resets KVM shared-page state for encrypted guests, initializes kvmclock, APIC post-init, and guest MTRR state. Late guest init installs reboot/syscore hooks, initializes async-PF sleeper hash locks, enables steal-time static calls and PV spinlock preemption tests, installs PV EOI and async-PF interrupt vector, replaces SMP hooks for PV TLB/IPI/yield where supported, and registers CPU hotplug callbacks. Per-CPU init writes KVM MSRs for async PF, PV EOI, steal time, migration control, and clock.

State and persistence: persistent runtime state is per-CPU decrypted `apf_reason`, `steal_time`, `kvm_apic_eoi`, `async_pf_enabled`, hash-table async-PF sleepers, static keys, and paravirt/static-call registrations. State must be disabled before reboot, kexec, CPU offline, suspend, or crash because the host keeps writing registered guest physical addresses.

Dependencies and integration points: depends on KVM CPUID/MSR ABI, x86 paravirt ops, APIC callbacks, SMP ops, CPU hotplug, kvmclock, e820/MTRR, confidential-computing memory encryption APIs, EFI SEV migration variable, syscore suspend/resume, reboot notifiers, qspinlock PV hooks, and haltpoll.

Risks: async PF injected with interrupts disabled or in kernel mode panics because the host violated the ABI. Shared per-CPU structures must be decrypted before exposing physical addresses under SEV. PV TLB flush relies on steal-time preempted flags and must queue flush-on-enter for preempted vCPUs. Reboot/kexec cleanup is required to prevent host writes into freed memory.

Test signals: KVM guest boot should show expected paravirt features, kvmclock, steal time, and PV EOI when advertised. Tests should cover `no-kvmapf`, `no-steal-acc`, CPU hotplug, suspend/resume, kexec/crash shutdown, async PF wait/wake including wake-before-wait dummy entries, SEV/SEV-ES/SNP migration control, PV IPI clusters, PV TLB with preempted vCPUs, and haltpoll enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kvmclock.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/kvmclock.c

Purpose: Provides the KVM paravirtual clocksource, sched clock, wallclock, TSC calibration, and VDSO pvclock time-info setup for x86 guests.

Important APIs/types/functions: main entry is `kvmclock_init()`. Other APIs are `kvm_check_and_clear_guest_paused()`, `kvmclock_disable()`, per-CPU exported `hv_clock_per_cpu`, and early init `kvm_setup_vsyscall_timeinfo()`. Important helpers include `kvm_register_clock()`, `kvm_clock_read()`, `kvm_sched_clock_init()`, `kvm_get_wallclock()`, `kvm_get_tsc_khz()`, and `kvmclock_setup_percpu()`.

Control flow: early parameters can disable kvmclock or VDSO pvclock. Early vsyscall setup allocates extra pvclock pages if more possible CPUs exist than fit in the boot page and marks them decrypted for encrypted guests. Init selects old or new KVM clock MSRs, registers a CPU hotplug prepare callback for per-CPU pvti assignment, writes CPU0 system-time MSR, sets stable TSC flags if advertised, installs sched clock and x86 platform calibration/wallclock hooks, lowers clocksource rating below TSC when invariant TSC is good, and registers the clocksource.

State and persistence: KVM writes time into shared `pvclock_vsyscall_time_info` structures in `hv_clock_boot` or allocated `hvclock_mem`, and wallclock into `wall_clock`. Per-CPU pointers persist for the boot. `kvm_sched_clock_offset` normalizes sched-clock start.

Dependencies and integration points: depends on KVM paravirt feature detection from `kvm.c`, pvclock library, clocksource framework, x86 platform hooks, CPU hotplug, VDSO clock mode registration, memory encryption decryption APIs, and KVM system-time/wall-clock MSRs.

Risks: shared clock memory must be decrypted under guest memory encryption. VDSO pvclock is enabled only when the stable TSC bit is present. CPU hotplug setup must avoid CPU0 pointer duplication from percpu replication. Disabling clock must zero the system-time MSR to stop host writes.

Test signals: KVM guests should register `kvm-clock`, expose stable VDSO pvclock only with stable flags, calibrate TSC and loops-per-jiffy from pvclock, survive CPU hotplug, clear guest-paused flags and touch watchdogs, and allocate/decrypt extra pvclock memory for large CPU counts under SEV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/kvmclock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ldt.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ldt.c

Purpose: Implements x86 `modify_ldt()` and LDT context management for processes, including fork duplication, mm teardown, per-CPU LDTR loading, and page-table-isolation aliases for user-visible LDT mappings.

Important APIs/types/functions: exposes `load_mm_ldt()`, `switch_ldt()`, `ldt_dup_context()`, `destroy_context_ldt()`, `ldt_arch_exit_mmap()`, and `SYSCALL_DEFINE3(modify_ldt)`. Internal helpers manage allocation, PTI mapping/unmapping, segment refresh, `install_ldt()`, read/write operations, and 16-bit segment policy.

Control flow: `modify_ldt` routes reads, default reads, and writes. Writes validate `struct user_desc`, reject invalid entries and disallowed 16-bit segments, allocate a new immutable `ldt_struct`, copy old entries, install the changed descriptor, map it into the alternate PTI slot if needed, publish it with release ordering, IPI all CPUs using the mm to reload LDTR, unmap the old slot, and free the old LDT. Reads copy current entries and zero-fill requested trailing space.

State and persistence: each `mm_struct` may own one `context.ldt`. LDT entries persist until replaced, duplicated on fork, or freed on mm destruction. Under PTI the same LDT content is mapped read-only into one of two fixed alias slots at `LDT_BASE_ADDR`, toggling slots so CPUs can keep using the old mapping until reloaded.

Dependencies and integration points: depends on x86 descriptor loading, mm context locks and semaphores, TLB shootdown, PTI page-table helpers, paravirt LDT allocation/free hooks, Xen PV detection, user-copy helpers, and mm fork/exit hooks.

Risks: lock order is explicitly `ldt_usr_sem`, `mmap_lock`, `context.lock`. LDTR updates rely on IPIs before freeing the old LDT. PTI alias mapping must be read-only, non-global, and synchronized to user page tables. Xen PV disallows 16-bit segments because ESPFIX64 is unavailable. RCU conversion is warned against because IRQ and IPI ordering are subtle.

Test signals: `modify_ldt` ABI tests should read/write/clear descriptors, reject invalid contents and 16-bit segments when disabled, fork with inherited LDT, switch between tasks with and without LDT, run with PTI on/off, CPU hotplug under active LDT users, Xen PV behavior, and stress concurrent LDT updates plus context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ldt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_32.c

Purpose: Handles the 32-bit x86 machine transition for kexec and kexec-jump. It prepares minimal executable control code and page tables, then disables unsafe CPU state and jumps into the relocation routine.

Important APIs/types/functions: defines `machine_kexec_prepare()`, `machine_kexec_cleanup()`, and `machine_kexec()`. Helpers include `load_segments()`, `machine_kexec_alloc_page_tables()`, `machine_kexec_free_page_tables()`, `machine_kexec_page_table_set_one()`, and `machine_kexec_prepare_page_tables()`.

Control flow: prepare marks the control page executable, allocates a PGD plus PTEs and optional PAE PMDs, and maps the control page both at its virtual address and physical identity. Cleanup restores NX and frees page tables. Execution optionally saves processor state for kexec jump, disables ftrace, interrupts, and hardware breakpoints, may reset IOAPIC to boot IRQ mode, copies relocation code to the control page, fills `page_list` with physical control page, virtual control page, PGD, and optional swap page, reloads kernel segments, invalidates IDT/GDT, and calls the relocation code with image head, page list, entry point, PAE flag, and preserve-context flag.

State and persistence: staged page-table pointers live in `image->arch`. Control page permissions are changed for the lifetime of the image. During execution the old kernel is past the point of no return unless preserve-context jump returns.

Dependencies and integration points: depends on generic kexec image layout, x86 page table allocation, relocation assembly symbols, ftrace state save/restore, IOAPIC legacy mode, segment/GDT/IDT management, hardware breakpoint disable, and suspend processor-state helpers.

Risks: `machine_kexec()` must not allocate or fail. Page tables must map the control code exactly as relocation expects. Invalidating GDT/IDT means no normal exception handling is available after that point. Preserve-context paths must restore processor state and ftrace on return.

Test signals: 32-bit kexec tests should cover default kexec, crash/preserve-context where configured, PAE and non-PAE page tables, IOAPIC reset behavior, control page permissions before and after cleanup, and ftrace/hardware-breakpoint state restoration on kexec-jump return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_64.c

Purpose: Handles 64-bit x86 kexec transition setup, relocation execution, purgatory relocations, crash-memory protection, and memory-encryption adjustments for kexec control pages.

Important APIs/types/functions: exports `kexec_file_loaders`, `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_kexec()`, `arch_kexec_apply_relocations_add()`, `arch_kimage_file_post_load_cleanup()`, crash resource protect/unprotect APIs, `arch_kexec_post_alloc_pages()`, and `arch_kexec_pre_free_pages()`. Helpers build identity mappings for RAM, segments, EFI tables, ACPI tables, MMIO serial debug, and transition virtual mapping.

Control flow: prepare rejects CPUs with the TDX partial-write machine-check erratum, creates identity page tables using control pages, maps current RAM and image segments, maps EFI/ACPI/debug ranges, maps the control page at its current virtual address, records global relocation arguments, prepares a debug IDT, copies relocation code into the control page, and marks it ROX. Execution disables ftrace, interrupts, hardware breakpoints, and CET, optionally resets IOAPIC for preserve-context, computes relocation flags including preserve-context and cache-incoherent state, reloads flat segments, and calls the copied relocation routine. Cleanup restores page permissions and frees transition page-table pages.

State and persistence: `image->arch` owns transition page-table pages. Globals such as `kexec_va_control_page`, `kexec_pa_table_page`, and optional swap-page physical address are consumed by relocation code. Crash kernel resources and dm-crypt key pages can be marked read-only or not-present while idle.

Dependencies and integration points: depends on generic kexec, x86 identity mapping helpers, EFI/ACPI resource discovery, memory encryption and confidential-computing attributes, CET disable, ftrace, IOAPIC, purgatory ELF relocation, crash dump resources, and kexec file loader for bzImage64.

Risks: `machine_kexec()` cannot allocate or call functions after GS is reset because percpu state is unavailable. Encryption attributes must match SME/SEV expectations for new-kernel access. Purgatory relocation supports only selected x86_64 relocation types and checks overflow. Crash resource protection must skip the active control page.

Test signals: 64-bit kexec and kdump tests should run with 4-level and 5-level paging, EFI/ACPI tables outside normal RAM, serial debug mapping, SME/SEV/TDX combinations, CET enabled, crash resource protection toggling, dm-crypt key preservation, purgatory relocation overflow failures, and kexec-jump preserve-context return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/mmconf-fam10h_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/mmconf-fam10h_64.c

Purpose: Detects and enables PCI MMCONFIG space on AMD Family 10h systems, especially platforms whose firmware leaves MMCONFIG disabled or needs a safe high-MMIO base selected.

Important APIs/types/functions: exposes `fam10h_check_enable_mmcfg()` and `check_enable_amd_mmconf_dmi()`. Internal state is `fam10h_pci_mmconf_base`. Important helpers are `get_fam10h_pci_mmconf_base()`, `cmp_range()`, and DMI callback `set_check_enable_amd_mmconf()`.

Control flow: DMI can set `PCI_CHECK_ENABLE_AMD_MMCONF` for affected systems. The check function reads `MSR_FAM10H_MMIO_CONF_BASE`; if already enabled and trustworthy, it records or validates the base. Otherwise it probes hostbridge PCI IDs, reads top-of-memory and high-MMIO window registers, chooses a base above TOM2 while avoiding reserved HT ranges near `0xfd-0xff << 32`, searches around existing high-MMIO ranges for a valid window, then programs the MSR for one 256-bus segment.

State and persistence: chosen base persists in `fam10h_pci_mmconf_base` for the running kernel and is written to the CPU MSR. The PCI probe flag may be cleared if no valid base can be found.

Dependencies and integration points: depends on early PCI config access, AMD MSRs, ACPI PCI state, DMI matching, PCI MMCONFIG architecture init, PCI probe flags, high-MMIO resource interpretation, and sort/range helpers.

Risks: base selection must not collide with RAM, HyperTransport reserved ranges, or existing high-MMIO windows. Trust policy differs when ACPI is enabled versus disabled. Programming inconsistent bases across CPUs would break PCI config access, so the first discovered base is reused.

Test signals: test on AMD Family 10h systems with MMCONFIG enabled, disabled, ACPI off, and DMI-triggered Sun systems. Verify programmed MSR base, 256-bus range, no overlap with high-MMIO windows, and successful extended PCI config reads after enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/mmconf-fam10h_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/module.c

Purpose: Implements x86-specific module relocation, runtime relocation clearing for livepatch, and final module text fixups such as alternatives, retpolines, returns, call thunks, FineIBT/CFI, ENDBR sealing, SMP locks, and ORC unwind registration.

Important APIs/types/functions: defines `apply_relocate()` on 32-bit, `apply_relocate_add()` on 64-bit, optional `clear_relocate_add()`, `module_finalize()`, and `module_arch_cleanup()`. Internal helper `__write_relocate_add()` applies or clears ELF64 RELA relocations with either `memcpy` or `text_poke`.

Control flow: 32-bit relocation applies `R_386_32`, `R_386_PC32`, and `R_386_PLT32`. 64-bit relocation computes symbol plus addend, validates relocation type and overflow, verifies the target is zero before applying or matches expected value before clearing, then writes through normal memory for unformed modules or `text_poke` under `text_mutex` for live modules. Finalization scans section names, initializes IBT sealing state, applies FineIBT/CFI and retpolines, finalizes IBT state, applies return-site and call-thunk patches, alternatives, ENDBR sealing, SMP lock alternatives, and ORC unwind metadata.

State and persistence: relocation writes modify loaded module memory. Runtime relocation patching for already formed modules uses synchronized text patching. Module cleanup removes SMP alternatives and frees IBT sealing metadata.

Dependencies and integration points: depends on ELF relocation definitions, module loader state, x86 text patching, alternatives, jump labels/static calls indirectly through module text, retpoline/return thunk/fineibt/callthunk machinery, objtool-generated sections, ORC unwinder, stack protector special clang relocation workaround, and livepatch clearing.

Risks: relocation targets are required to be zero before apply to detect corrupt or reused module text. PC-relative and 32-bit relocations check overflow. Finalization order matters: FineIBT, retpolines, return sites, alternatives, and sealing all mutate code. Runtime patching must hold `text_mutex` and sync CPUs.

Test signals: module load tests should cover 32-bit and 64-bit relocation types, overflow rejection, nonzero relocation target rejection, livepatch clear/apply paths, modules with alternatives, ORC unwind, retpolines, return sites, call thunks, CFI/FineIBT, ENDBR sealing, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/mpparse.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/mpparse.c

Purpose: Parses legacy Intel MultiProcessor Specification tables on x86, registers processors, buses, IOAPICs, and interrupt sources, constructs default MP tables when needed, scans BIOS memory for floating pointers, and optionally updates broken MP IRQ entries.

Important APIs/types/functions: public init hooks include `mpparse_find_mptable()`, `mpparse_parse_early_smp_config()`, `mpparse_parse_smp_config()`, `e820__memblock_alloc_reserved_mpc_new()`, and late `update_mp_table()`. Helpers include `smp_scan_config()`, `smp_read_mpc()`, `smp_check_mpc()`, `check_physptr()`, default table constructors, IRQ replacement helpers, and early params `update_mptable` and `alloc_mptable`.

Control flow: early scanning checks the first 1 KB, top of base RAM, BIOS region, and EBDA for a valid MP floating pointer. It reserves MP structures in memblock. Early parse can register the LAPIC address. Full parse validates MPC signature/checksum/version/LAPIC address, processes entries for CPUs, buses, IOAPICs, interrupt sources, and LINT sources, or constructs default ISA/EISA/PCI tables from floating-pointer feature bytes. If IOAPIC IRQ entries are absent it synthesizes defaults. Optional late update rewrites or copies the MP table and replaces level-low PCI interrupt sources with ACPI/PIRQ-discovered entries.

State and persistence: boot-time state includes `num_procs`, `mpf_base`, `mpf_found`, `irq_used`, spare IRQ entry slots, `enable_update_mptable`, and optional allocated replacement MPC physical memory. Parsed data populates global topology, bus, IOAPIC, and `mp_irqs` state.

Dependencies and integration points: depends on BIOS EBDA access, early memremap, memblock reservation, APIC/topology registration, IOAPIC IRQ domains, ACPI coexistence flags, PCI routing, E820 allocation, MTRR/boot CPU data for default CPU entries, and legacy PIC ELCR registers.

Risks: malformed MP tables can disable SMP or fall back to default IRQ routing. ACPI-provided LAPIC/IOAPIC data suppresses some MPS parsing because MPS lacks hyperthreading detail. In-place MP table update can fail on read-only mappings; allocated replacement must be large enough and checksum-fixed. IRQ rewrite has limited spare slots.

Test signals: legacy BIOS or emulator tests should cover valid MP 1.1/1.4 tables, default configurations, missing IRQ entries, bad checksum/signature/version, ACPI coexistence, EBDA-only floating pointer, `update_mptable`, `alloc_mptable=`, PCI routeirq interaction, ELCR fallback, and memblock reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/mpparse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/msr.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/msr.c

Purpose: Implements the x86 `/dev/cpu/<n>/msr` character device for privileged userspace reads and writes of model-specific registers on online CPUs.

Important APIs/types/functions: module init/exit are `msr_init()` and `msr_exit()`. File operations are `msr_read()`, `msr_write()`, `msr_ioctl()`, and `msr_open()`. CPU hotplug callbacks create and destroy per-CPU devices. Module parameter `allow_writes` is handled by `set_allow_writes()` and `get_allow_writes()`.

Control flow: init registers fixed major `MSR_MAJOR`, creates the `msr` device class, and registers dynamic CPU hotplug state to create `/dev/cpu/%u/msr` devices. Open requires `CAP_SYS_RAWIO`, a valid online CPU, and CPU MSR support. Reads require 8-byte granularity, repeatedly call `rdmsr_safe_on_cpu()` at the file offset register number, and copy two u32 values to userspace. Writes enforce lockdown `LOCKDOWN_MSR`, apply the write policy filter, taint the kernel as CPU-out-of-spec, then call `wrmsr_safe_on_cpu()`. Ioctls provide register-array read/write variants.

State and persistence: persistent module state is CPU hotplug state id, registered char device/class, and `allow_writes` policy. Device nodes follow CPU online state. MSR writes change CPU hardware state and may persist until reset depending on the register.

Dependencies and integration points: depends on x86 MSR safe-on-CPU helpers, Linux device model, CPU hotplug, security lockdown, capability checks, kernel tainting, user-copy helpers, and `/dev/cpu` device-node naming.

Risks: MSR writes are inherently unsafe; default policy logs and taints but allows writes, while `allow_writes=off` blocks them and `on` suppresses warnings. Logging is rate-limited to avoid kmsg floods. CPU offline after open can still make safe MSR helpers fail. Lockdown blocks writes but not reads.

Test signals: tests should open devices only as `CAP_SYS_RAWIO`, reject offline/non-MSR CPUs, enforce 8-byte read/write counts, exercise read and ioctl paths, verify lockdown write denial, check `allow_writes=off/on/default`, CPU hotplug device creation/removal, and taint/warning behavior on writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/msr.c -->
