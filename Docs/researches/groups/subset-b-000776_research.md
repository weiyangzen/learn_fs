# Research: subset-b-000776

Grouped research for PowerPC kernel probe, KVM paravirtualization, machine-check, module, firmware/NVRAM, serial, cache, PACA, MSI, ELF-note, and low-level assembly support. Each section is keyed by the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes.c

Purpose: PowerPC architecture backend for generic kprobes, including symbol lookup quirks, probe instruction preparation, breakpoint arming, trap handling, single-step/emulation, nested probe handling, and fault recovery.

Important APIs/types/functions: per-CPU `current_kprobe` and `kprobe_ctlblk`; `kprobe_lookup_name`; `arch_adjust_kprobe_addr`; `arch_prepare_kprobe`; `arch_arm_kprobe`; `arch_disarm_kprobe`; `arch_remove_kprobe`; `kprobe_handler`; `kprobe_post_handler`; `kprobe_fault_handler`; `arch_trampoline_kprobe`; helpers around `emulate_step`, `enable_single_step`, `patch_instruction`, and `search_exception_tables`.

Control flow: registration rejects unaligned addresses, instructions that cannot single-step, and placement on the second word of prefixed instructions. It allocates an executable instruction slot, copies the original instruction there, and replaces the probed address with `BREAKPOINT_INSTRUCTION` when armed. Trap handling ignores user mode and non-translated non-BookE contexts, disables preemption, locates the probe, runs the pre-handler, then either emulates the instruction through `emulate_step` or redirects NIP to the copied instruction for hardware single-step. The post handler verifies that execution returned from the copied instruction, runs the post-handler, restores NIP/MSR, and releases the per-CPU probe state. Recursive hits save and restore the previous `kprobe_ctlblk` state and count missed probes instead of running user handlers.

State and persistence: state is per-CPU and transient: current probe pointer, saved MSR, previous nested probe fields, and per-probe `ainsn` slot plus `boostable` hint. There is no filesystem persistence, but live kernel text is modified until the probe is disarmed or removed.

Dependencies and integration: integrates generic kprobes, kallsyms, ftrace location lookup, PPC64 ELF ABI v1/v2 entry rules, text patching, PowerPC instruction decoding, software single-step, exception tables, and rethook trampoline support.

Risks: incorrect symbol entry adjustment can probe descriptors rather than code; prefixed instruction handling must prevent half-instruction probes; faults while single-stepping must restore MSR and preemption state exactly; probe recursion suppresses handlers and can hide expected callbacks; self-modifying text requires correct cache synchronization through `patch_instruction`.

Test signals: build with `CONFIG_KPROBES` across PPC32/PPC64 ABI variants, register probes by name and address, probe ftrace entry points, exercise prefixed instruction rejection, trigger nested probes and faulting load/store probes, and verify no stuck preemption or incorrect NIP after post handling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm.c

Purpose: boot-time KVM/ePAPR guest optimization for PowerPC kernels running under a paravirtualized host, replacing selected privileged SPR/MSR operations with faster magic-page memory accesses or nearby emulation trampolines.

Important APIs/types/functions: `kvm_guest_init`; `kvm_use_magic_page`; `kvm_map_magic_page`; `kvm_check_ins`; patch helpers `kvm_patch_ins_*`; trampoline builders for `mtmsrd`, `mtmsr`, BookE `wrtee/wrteei`, and Book3S 32-bit `mtsrin`; global `kvm_patching_worked`, `kvm_tmp`, and `kvm_tmp_index`.

Control flow: the postcore initcall exits unless KVM paravirt and ePAPR are enabled. If `KVM_FEATURE_MAGIC_PAGE` is present, every CPU asks the hypervisor to map the magic page at `-4096`, the kernel validates the mapping with `fault_in_readable`, disables local IRQs, scans `_stext` to `_etext`, skips the template range, and rewrites matching instructions. Simple reads/writes of MSR, SPRG, SRR, DAR/DEAR, DSISR, MAS, ESR, PIR, and segment-register state become loads/stores into `struct kvm_vcpu_arch_shared`. Instructions that need conditional interrupt semantics are replaced with branches into copied assembly templates stored in the 64 KiB `kvm_tmp` area.

State and persistence: changes are live kernel text patches and a fixed negative-address magic-page mapping supplied by the hypervisor. `kvm_tmp_index` consumes template space once during boot; `kvm_patching_worked` records failures for logging but does not roll back already-applied patches.

Dependencies and integration: depends on `kvm_para_available`, ePAPR hypercalls, `KVM_MAGIC_FEAT_*`, PowerPC opcode encodings, cache flushes after patching, and assembly labels exported by `kvm_emul.S`.

Risks: branch offsets are only checked against the positive maximum and depend on layout; relocatable Book3S interrupt handlers are intentionally skipped; partial success can leave mixed optimized/unoptimized text; IRQ disabling protects SPRG4-7 synchronization assumptions; scratch registers 30/31 require special magic-page save/restore handling.

Test signals: boot a PPC KVM guest with magic page enabled, check the "KVM: Live patching for a fast VM" log, verify no fault on `-4096`, compare instruction patch counts under BookE/Book3S configs, and run interrupt-heavy and TLB-heavy guest workloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm_emul.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm_emul.S

Purpose: assembly template library copied and patched by `kvm.c` to emulate selected privileged instructions using KVM's magic page while preserving register state and interrupt semantics.

Important APIs/types/functions: exported template ranges `kvm_template_start/end`, `kvm_emulate_mtmsrd`, `kvm_emulate_mtmsr`, BookE `kvm_emulate_wrtee`, `kvm_emulate_wrteei_0`, Book3S 32-bit `kvm_emulate_mtsrin`, per-template offset symbols such as `*_branch_offs`, `*_reg_offs`, `*_orig_ins_offs`, length symbols, and the `kvm_tmp` 64 KiB allocation area.

Control flow: `SCRATCH_SAVE` marks the magic-page critical section with the current stack pointer and saves r30, r31, and CR fields. Templates read and update the magic-page MSR or segment-register fields, decide whether a real privileged instruction is still required, optionally execute the original instruction patched into the template, restore scratch state, and branch back to the instruction after the patched call site. `mtmsr/mtmsrd/wrtee` paths run the real instruction if critical MSR bits change or a pending interrupt must be delivered; otherwise they update the shared MSR field only.

State and persistence: templates are static text plus `kvm_tmp` scratch text space; runtime guest-visible state is the hypervisor shared page at `KVM_MAGIC_PAGE`, including MSR, interrupt-pending flag, scratch slots, and segment-register array.

Dependencies and integration: consumed by `kvm.c`, depends on `asm-offsets.h` offsets for `struct kvm_vcpu_arch_shared`, PowerPC register conventions, BookE/Book3S configuration guards, and the hypervisor honoring the critical-section field.

Risks: any mismatch between offset labels and C patching corrupts generated trampolines; scratch restore must run on every branch; magic-page critical markers assume r2 is never equal to r1; handling pending interrupts incorrectly can defer or spuriously enter the hypervisor.

Test signals: build all guarded variants, disassemble generated template copies, boot paravirt guests under interrupt load, and verify MSR[EE/RI] transitions, BookE `wrteei`, and Book3S `mtsrin` behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm_emul.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/l2cr_6xx.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/l2cr_6xx.S

Purpose: low-level cache-control routines for 6xx/7xx/74xx PowerPC processors, covering L2/L3 cache configuration, global invalidation, flush-before-disable behavior, and L1 flush/disable or invalidate/enable helpers.

Important APIs/types/functions: `_set_L2CR`; `_get_L2CR`; `_set_L3CR`; `_get_L3CR`; `__flush_disable_L1`; `__inval_enable_L1`; feature fixup sections for `CPU_FTR_L2CR`, `CPU_FTR_L3CR`, `CPU_FTR_ALTIVEC`, and `CPU_FTR_SPEC7450`.

Control flow: `_set_L2CR` rejects unsupported CPUs, stops AltiVec streams, disables interrupts and data relocation, disables HID0 dynamic power management for errata, flushes existing L2 contents by reading and `dcbf`-flushing a conservative memory span, writes L2CR with invalidate/enable bits masked, performs global invalidation, waits for completion, conditionally enables L2, restores prefetch and HID0 state, then restores MSR. `_set_L3CR` performs analogous L3 disable, flush, reserved-bit/clock-enable sequencing, invalidation wait, optional enable, and MSR restore. L1 helpers sweep cache lines and toggle HID0 DCE/ICE/flash-invalidate bits.

State and persistence: persistent state is hardware cache-control SPR state, HID0/MSSCR0 bits, and actual cache contents. No software data persists beyond clobbered registers and processor cache mode.

Dependencies and integration: used by platform CPU setup, sleep/resume, CPU frequency, and board code that must manage external caches before normal C/cache APIs are safe. Depends on exact processor feature bits and SPR semantics.

Risks: wrong cache sizing or sequencing can lose dirty data or hang waiting for invalidate bits; running with MMU/interrupt state assumptions violated is unsafe; comments document errata-sensitive alignment and DPM/prefetch workarounds; 7450 bit layout differs from older L2CR users.

Test signals: only hardware or accurate emulator tests are meaningful: enable/disable L2/L3 on supported CPUs, suspend/resume or cpufreq paths, memory stress before/after toggles, and boot logs confirming feature fixups selected the intended paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/l2cr_6xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/legacy_serial.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/legacy_serial.c

Purpose: discovers Open Firmware-described legacy 8250-compatible serial ports very early on PowerPC, initializes an early firmware console when possible, and later registers platform `serial8250` ports with fixed-up IRQ and I/O resources.

Important APIs/types/functions: `legacy_serial_ports`; `legacy_serial_infos`; `find_legacy_serial_ports`; `add_legacy_port`; `add_legacy_soc_port`; `add_legacy_isa_port`; `add_legacy_pci_port`; `setup_legacy_serial_console`; `ioremap_legacy_serial_console`; `serial_dev_init`; `check_legacy_serial_console`; TSI-specific `tsi_serial_in/out`.

Control flow: early discovery checks `/chosen` stdout path, scans `ns16550` children under known SoC/simple-bus parents, ISA/LPC serial nodes, and PCI serial nodes. Each accepted node records clock, current speed, register shift, translated address, and provisional port data in an array of up to eight entries. If the firmware stdout matches a discovered node, the file maps or uses PIO for the port and initializes `udbg` for early console output. Later init remaps the early console to normal `ioremap`, resolves IRQs with `irq_of_parse_and_map`, adjusts PCI/PIO offsets, maps MMIO, applies Freescale IRQ workaround hooks when available, and registers the platform 8250 device.

State and persistence: static arrays preserve discovered device nodes and port metadata from early boot to device init. The only persistent effects are OF node references, early/normal mappings, preferred console selection, and registered platform devices.

Dependencies and integration: depends on device tree properties (`clock-frequency`, `current-speed`, `reg-shift`, `linux,stdout-path`, `stdout-path`), OF address/IRQ translation, PCI host bridges, `udbg`, `serial8250`, `fsl8250_handle_irq`, and early ioremap.

Risks: array slot replacement can reorder ports; early address translation is incomplete for some LPC/PIO cases; clock-frequency is mandatory for SoC/PCI early use; stale OF properties can choose the wrong default console; device-node references are retained for boot lifetime.

Test signals: boot boards with SoC, ISA/LPC, and PCI serial devices; verify early console before normal driver probe; check `ttyS` numbering and preferred console; confirm IRQ fixups and Freescale workaround activation in logs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/legacy_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce.c

Purpose: common PowerPC machine-check and hypervisor-maintenance interrupt support: event capture, per-CPU queues, notification, deferred memory-failure processing, printing, HMI special-trigger handling, and MCE data allocation.

Important APIs/types/functions: `mce_register_notifier`; `save_mce_event`; `get_mce_event`; `release_mce_event`; `machine_check_queue_event`; `mce_common_process_ue`; `mce_run_irq_context_handlers`; `machine_check_print_event_info`; `machine_check_early`; `hmi_handle_debugtrig`; `hmi_exception_realmode`; `mce_init`; per-PACA `mce_info`, queue counters, and `mce_pending_irq_work`.

Control flow: early machine-check handlers call platform-specific real-mode decode, which eventually saves an event into the current CPU's PACA `mce_info`. Unrecovered events schedule irq work. UE events with physical addresses are copied to a UE queue for later notifier and `memory_failure` handling. `machine_check_queue_event` releases the current nested event into a print/log queue. IRQ-context processing calls platform log hooks, prints queued events, schedules UE work, and clears pending status. Printing decodes severity, initiator, class, subtype, effective address, physical address, guest/user context, and SLB dumps. HMI handling detects POWER9 debug trigger functions from device tree or PVR and either handles vector CI emulation or falls back to platform HMI code.

State and persistence: transient event state lives per CPU in PACA-allocated `struct mce_info` buffers, counters, and pending flags. Events can lead to tainting, notifier callbacks, memory failure isolation, and platform/NVRAM logging through `ppc_md.machine_check_log_err`, but this file itself does not persist records.

Dependencies and integration: relies on PACA allocation, NMI interrupt wrappers, `ppc_md` machine hooks, exception tables, device tree CPU properties, `memory_failure`, notifier chains, and platform HMI synchronization helpers.

Risks: queue overflow silently drops events; real-mode paths must avoid unsafe operations; nested count handling must match release calls; ignored UE events depend on exception-table fixups; HMI debug-trigger interpretation differs by CPU revision and firmware properties.

Test signals: inject recoverable and unrecoverable MCEs, verify event printing and taint, exercise UE memory failure with and without physical address, test KVM guest MCE pass-through, and validate POWER9 HMI debug-trigger paths on affected revisions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce_power.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce_power.c

Purpose: POWER7/8/9/10 CPU-side real-mode machine-check decoder and recovery logic, translating SRR1/DSISR signatures into structured MCE information and attempting SLB/ERAT/TLB recovery or UE fixups.

Important APIs/types/functions: `addr_to_pfn`; `flush_and_reload_slb`; `flush_erat`; `mce_flush`; P7/P8/P9/P10 instruction and data error tables; `mce_handle_ierror`; `mce_handle_derror`; `mce_find_instr_ea_and_phys`; `mce_handle_ue_error`; `mce_handle_error`; exported real-mode entry helpers `__machine_check_early_realmode_p7/p8/p9/p10`.

Control flow: the platform-specific entry chooses a CPU generation table and passes SRR1/DSISR into `mce_handle_error`. Load/store errors use DSISR table matches; instruction errors use SRR1 masks. For recoverable SLB/ERAT/TLB events outside guests, the handler flushes or reloads the relevant translation structures. It fills `mce_error_info` with type, subtype, class, severity, initiator, and sync flag, derives effective and physical addresses where valid, and for UE may analyze the faulting instruction or consult exception-table/platform recovery hooks. Finally it calls `save_mce_event` with the handled decision.

State and persistence: no durable storage; state changes are translation-cache flushes, possible NIP fixup, PACA MCE event creation, and later memory-failure side effects from common code.

Dependencies and integration: depends on PowerPC real-mode page-table walking, hash/radix MMU distinction, SLB shadow routines, `analyse_instr`, KVM guest state in PACA, CPU-specific SRR1/DSISR definitions, and `ppc_md.mce_check_early_recovery`.

Risks: page-table lookup in real mode can race with updates; guest context intentionally avoids recovery and address lookup; table order matters because multiple DSISR bits may be set and UE entries must win; async store/link errors on P9/P10 need special SRR1 routing; wrong severity/class causes panic or missed isolation.

Test signals: inject SLB/ERAT/TLB parity or multihit errors, UE instruction and load/store faults, POWER9 paste spurious MCE, async real-address store errors, guest MCEs, and SCOM/OPAL early recovery paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/mce_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc.S

Purpose: common low-level PowerPC assembly helpers shared across 32-bit and 64-bit builds for early relocation math, nonlocal jump state save/restore, and current stack-frame inspection.

Important APIs/types/functions: `reloc_offset`; `add_reloc_offset`; `setjmp`; `longjmp`; `current_stack_frame`; exported `current_stack_frame`; `_ASM_NOKPROBE_SYMBOL` annotations for relocation helpers.

Control flow: `reloc_offset` returns zero via the fall-through into `add_reloc_offset`, while `add_reloc_offset(x)` uses a link-register branch trick to compare the current executing address against a linked address constant and add that runtime relocation delta to the input. `setjmp` saves LR, SP, TOC/r2, CR, and callee-saved GPRs into the caller-supplied buffer and returns 0. `longjmp` restores that state, sets LR, and returns the supplied nonzero value or 1 if the supplied value is zero. `current_stack_frame` loads the caller's backchain from the current stack pointer.

State and persistence: all state is caller-provided memory for jump buffers or CPU registers; no kernel global state is retained.

Dependencies and integration: used by early boot/relocation and exception-like control transfers before normal C runtime assumptions fully apply. Depends on ABI register layout, `SZL`, and offsets selected by 32-bit versus 64-bit configuration.

Risks: jump buffer layout must match callers and architecture width; restoring stale r2/TOC or CR can corrupt subsequent C execution; relocation helper must remain unprobeable because it is used in delicate early contexts.

Test signals: boot relocatable kernels, run paths using kernel `setjmp/longjmp`, inspect stack unwinding users of `current_stack_frame`, and build PPC32/PPC64 variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_32.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_32.S

Purpose: 32-bit PowerPC assembly support for early GOT relocation, CPU setup dispatch, PMac CPU-frequency register switching, optimized page copying, compiler helper routines for 64-bit arithmetic, byte swap, and secondary CPU resume.

Important APIs/types/functions: `reloc_got2`; `call_setup_cpu`; `low_choose_750fx_pll`; `low_choose_7447a_dfs`; `copy_page`; `__ashrdi3`; `__ashldi3`; `__lshrdi3`; `__cmpdi2`; `__ucmpdi2`; `__bswapdi2`; `start_secondary_resume`.

Control flow: `reloc_got2` walks the `.got2` range and adds a relocation offset to each word. `call_setup_cpu` finds `cur_cpu_spec->cpu_setup` using the data offset and branches through CTR when present. PMac frequency helpers disable interrupts, update HID registers and saved HID images, then restore MSR. `copy_page` warns on unaligned destinations, prefetches, uses `dcbz` on destination lines, and unrolls cache-line-sized copies. Arithmetic helpers implement compiler runtime operations on 64-bit values represented in register pairs. SMP resume resets the stack, zeroes the frame pointer, calls `start_secondary`, and spins if it returns.

State and persistence: mutates early GOT entries, CPU HID/HID1 registers, `nap_save_hid1`, destination page memory, and secondary CPU stack/register state.

Dependencies and integration: depends on boot relocation symbols, CPU spec layout, cache-line constants, PMac cpufreq code, compiler-generated helper calls, SMP startup, and feature-fixup headers.

Risks: page copy assumes cacheable aligned destination and correct `L1_CACHE_BYTES`; HID programming is CPU-specific and runs with interrupts disabled; GOT relocation must run before virtual addressing expectations; arithmetic helpers are ABI-visible and must preserve exact return conventions.

Test signals: boot PPC32 relocatable kernels, run memory/page-copy stress, exercise PMac cpufreq transitions, build code that emits 64-bit helper calls, and online secondary CPUs after resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_64.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_64.S

Purpose: 64-bit PowerPC assembly helpers for byte swapping, real-mode I/O and SCOM access on selected platforms, and kexec handoff/sequencing for SMP and Book3E/Book3S systems.

Important APIs/types/functions: `__bswapdi2`; BootX `rmci_on/off`; PMac `real_readb/real_writeb`; PA Semi `real_205_readb/real_205_writeb`; 970 `scom970_read/write`; `kexec_wait`; `kexec_smp_wait`; local `real_mode`; `kexec_sequence`; Book3E `kexec_create_tlb`; local text `kexec_flag`.

Control flow: platform real-mode I/O helpers temporarily disable data relocation or adjust HID4/SLB state, perform byte access or SCOM SPR operations, and restore MSR/HID state. `kexec_wait` loops at low thread priority until `kexec_flag` changes, then branches to the next kernel's secondary entry in real mode or via a Book3E identity TLB. `kexec_smp_wait` records real-mode kexec state in PACA and joins that loop. `kexec_sequence` switches to the kexec stack, saves arguments, disables interrupts, optionally enters real mode, copies/flushed image pages, copies the new entry stub to address zero, releases secondary CPUs, clears hash page tables if requested, and jumps to the new kernel entry with physical CPU id.

State and persistence: mutates MSR, HID4, SCOM SPRs, TLB entries, PACA kexec state, `kexec_flag`, memory at physical zero, and copied kexec image pages. This is terminal handoff state, not normal runtime persistence.

Dependencies and integration: tied to kexec core, PACA hardware CPU ids, Book3S/Book3E MMU mechanisms, `kexec_copy_flush`, `copy_and_flush`, platform CPU-frequency/early-debug configs, and ABI function descriptor handling.

Risks: terminal code has little recovery; incorrect real-mode or TLB setup can strand secondary CPUs; copying to address zero must happen after kernel data is no longer needed; endian/MSR handling matters during handoff; SCOM helpers explicitly do not check status bits.

Test signals: kexec/kdump boot cycles on Book3S and Book3E, SMP secondary release, PMac/PA Semi real-mode I/O smoke tests, 970 SCOM read/write validation, and disassembly checks under guarded configs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/module.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/module.c

Purpose: common PowerPC module finalization after architecture-specific relocation, applying CPU/MMU/firmware/speculation fixups and recording ABI v1 OPD bounds.

Important APIs/types/functions: `find_section`; `module_finalize`; `module_finalize_ftrace`; `do_feature_fixups`; `do_barrier_nospec_fixups_range`; `do_lwsync_fixups`; module architecture fields `start_opd` and `end_opd`.

Control flow: `module_finalize` first delegates ftrace finalization. It then locates optional special sections by name: `__ftr_fixup`, `__mmu_ftr_fixup`, PPC64 `__fw_ftr_fixup`, ABI v1 `.opd`, `__spec_barrier_fixup`, and `__lwsync_fixup`. Existing sections are patched in-place according to current CPU features, MMU features, firmware features, speculation barrier enablement, and lwsync capability.

State and persistence: mutates loaded module text/data before use and stores OPD address bounds in `me->arch` for later function-descriptor dereferencing. Effects persist for the lifetime of the module.

Dependencies and integration: sits between generic module loader and PowerPC-specific 32/64 relocation files; depends on section names emitted by build tooling and runtime feature masks in `cur_cpu_spec` and `powerpc_firmware_features`.

Risks: missing or malformed fixup sections leave code unpatched for the active CPU; ftrace finalization failure aborts module load; ABI v1 OPD bounds are required to distinguish descriptors from code pointers.

Test signals: load modules with feature-fixup sections on CPUs with differing features, test ftrace-enabled modules, ABI v1 function descriptors, speculation barrier toggles, and lwsync fixups.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_32.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_32.c

Purpose: 32-bit PowerPC module loader backend for sizing PLT trampoline sections, applying ELF RELA relocations, and creating ftrace trampolines for out-of-range calls.

Important APIs/types/functions: `module_frob_arch_sections`; `get_plt_size`; `count_relocs`; `relacmp`; `do_plt_call`; `apply_relocate_add`; `module_trampoline_target`; `module_finalize_ftrace`; module fields `core_plt_section`, `init_plt_section`, `tramp`, and `tramp_regs`.

Control flow: before allocation, relocation sections are sorted by symbol/addend and scanned for unique `R_PPC_REL24` entries, adding PLT space for core/init sections and ftrace callers. During relocation, absolute 32-bit and 16-bit HI/HA/LO writes are patched, REL24 branches are checked for +/-32 MiB range, and out-of-range calls allocate or reuse a four-instruction PLT entry (`lis/addi/mtctr/bctr`) before patching the branch displacement. REL32 writes a 32-bit relative value. Ftrace finalization reserves PLT entries for `ftrace_caller` and optionally `ftrace_regs_caller`.

State and persistence: mutates module sections, PLT entries, and ftrace architecture fields. Sorted relocation arrays are also modified in memory during sizing.

Dependencies and integration: depends on generic module loader section callbacks, PowerPC text patching, `struct ppc_plt_entry`, dynamic ftrace, and module core/init memory boundary helpers.

Risks: PLT sizing depends on sorted relocation identity and must match later allocation; range checks must be exact for REL24; 16-bit patching aligns down to a full instruction; ftrace trampoline decoding assumes exact PLT instruction patterns.

Test signals: load modules with near and far calls, init/core section calls, unknown relocation rejection, ftrace and ftrace-with-regs enabled, and `module_trampoline_target` on generated PLT entries.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_64.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_64.c

Purpose: 64-bit PowerPC module loader backend for ABI validation, TOC/GOT/stub sizing, symbol name normalization, relocation application, ftrace stub setup, and trampoline target discovery.

Important APIs/types/functions: `module_elf_check_arch`; `module_frob_arch_sections`; `module_init_section`; `apply_relocate_add`; `stub_for_addr`; `create_stub`; `create_ftrace_stub`; `got_for_addr`; `restore_r2`; `module_trampoline_target`; `module_finalize_ftrace`; helper types `ppc64_stub_entry`, `ppc64_got_entry`, `func_desc_t`.

Control flow: ELF flags are checked against configured ABI. Section preparation finds `.stubs`, `.toc` or PCREL `.mygot`, `.data..percpu`, symtab, and version sections; ABI v1/v2 non-PCREL builds remove leading dots from undefined symbols and version names and synthesize `.TOC.`. Stub size is computed from unique REL24/REL24_NOTOC relocations plus ftrace and out-of-line ftrace needs; PCREL builds also size GOT entries for `R_PPC64_GOT_PCREL34` and moved percpu references. Relocation then handles absolute, TOC, REL24, REL64/REL32, PCREL34, GOT_PCREL34, ENTRY, REL16, and TOCSAVE cases. External or livepatch REL24 calls route through stubs that load target/TOC data; non-external calls may use ELFv2 local-entry offsets. Non-PCREL link calls get a following `ld r2,...` restore if the ABI requires it.

State and persistence: mutates loaded module relocation targets, stub section, GOT section, ftrace fields, `.TOC.` symbol value, arch stub counters, OPD-aware function descriptors, and optional out-of-line ftrace storage. Effects persist until module unload.

Dependencies and integration: heavily coupled to PPC64 ELF ABI v1/v2, PC-relative kernel mode, ftrace/mprofile, livepatch symbol states, PowerPC prefixed instruction patching, module memory layout, and `paca_struct` kernel TOC/base fields.

Risks: relocation range checks are architecture-critical; stub alignment must be 8 bytes for prefixed instructions; dedotifying symbols can break if string tables are malformed; PCREL percpu conversion changes instruction form from `pla` to `pld`; `restore_r2` expects a nop after link branches; duplicate stub matching by function address can conflate names with same address.

Test signals: load modules for ABI v1, ABI v2, and PCREL builds; exercise external calls beyond REL24 range, percpu references, ftrace/mprofile and out-of-line ftrace, livepatch relocations, function descriptor dereference, and bad relocation/range failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/module_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/msi.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/msi.c

Purpose: architecture MSI/MSI-X delegation layer that routes PCI MSI setup and teardown through the owning PowerPC PCI host bridge controller operations.

Important APIs/types/functions: `arch_setup_msi_irqs`; `arch_teardown_msi_irqs`; `pci_bus_to_host`; `pci_controller->controller_ops.setup_msi_irqs`; `teardown_msi_irqs`.

Control flow: setup maps the device's bus to its host bridge, rejects setup with `-ENOSYS` if either setup or teardown callback is absent, rejects multiple vector classic MSI requests by returning 1, and otherwise calls the controller setup hook. Teardown repeats the host lookup and calls teardown if present because teardown can be invoked even after `-ENOSYS` setup.

State and persistence: this file holds no state; MSI state is owned by PCI core and platform controller callbacks.

Dependencies and integration: integrates generic PCI/MSI code with platform-specific PowerPC PHB MSI backends.

Risks: multiple MSI vectors are unsupported for classic MSI in this architecture layer; missing controller callbacks leave devices without MSI; teardown must be null-safe for failed setup.

Test signals: PCI device MSI and MSI-X enable/disable on each PHB backend, no-callback fallback to INTx, multi-vector MSI rejection, and teardown after failed setup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/note.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/note.S

Purpose: emits a PowerPC-specific ELF note advertising kernel binary capabilities to bootloaders and userland, currently the ultravisor-capable bit for PowerNV builds.

Important APIs/types/functions: `PPCCAP_ULTRAVISOR_BIT`; `PPC_CAPABILITIES_BITMAP`; `ELFNOTE(PowerPC, PPC_ELFNOTE_CAPABILITIES, ...)`.

Control flow: at assembly time, the ultravisor capability bit is set only when `CONFIG_PPC_POWERNV` is enabled; otherwise the bitmap is zero. The `ELFNOTE` macro places the capability bitmap into the kernel image's note section.

State and persistence: persistent build artifact metadata in the kernel ELF image; no runtime mutable state.

Dependencies and integration: consumed by bootloaders, tooling, or userland that inspect PowerPC ELF notes; tied to ultravisor-aware PowerNV boot requirements and `asm/elfnote.h` constants.

Risks: if the capability bit is missing on an ultravisor-capable kernel, a bootloader may refuse or warn; if set incorrectly, early boot may crash when ultravisor-controlled resources are accessed unsafely.

Test signals: inspect built kernel notes with `readelf -n`, compare PowerNV and non-PowerNV configs, and boot on ultravisor-enabled firmware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/nvram_64.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/nvram_64.c

Purpose: PPC64 NVRAM partition manager plus crash/error persistence backend for RTAS, oops/panic logs, pstore records, Open Firmware config, common, and skiboot partitions.

Important APIs/types/functions: `nvram_write_os_partition`; `nvram_read_partition`; `nvram_init_os_partition`; `nvram_init_oops_partition`; `oops_to_nvram`; `nvram_pstore_open/read/write`; `nvram_scan_partitions`; `nvram_create_partition`; `nvram_remove_partition`; `nvram_find_partition`; `nvram_get_partition_size`; `nvram_checksum`; global partition descriptors such as `rtas_log_partition`, `oops_log_partition`, `skiboot_partition`, `of_config_partition`, and `common_partition`.

Control flow: boot scans raw NVRAM headers into a linked list, validating checksums and lengths. OS partitions are found, resized, created from free space, or recovered by deleting obsolete OS partitions. Oops setup allocates buffers, tries to register pstore, and falls back to a kmsg dumper with zlib compression. On oops/panic/emergency dump, the dumper avoids clobbering unread RTAS events, try-locks, captures recent printk text, compresses when possible, builds an `oops_log_info` header, and writes the error header plus payload to the NVRAM partition. Pstore read iterates through configured partition types, reads OS or firmware partitions, decodes old/new oops headers, and returns records to pstore.

State and persistence: maintains an in-memory partition list and partition metadata, plus durable NVRAM contents containing headers, OS error-log metadata, sequence numbers, compressed or raw panic text, and platform firmware data. Partition creation/removal mutates NVRAM headers and merges free partitions.

Dependencies and integration: depends on `ppc_md.nvram_read/write/size`, RTAS/OPAL platform state, pstore, kmsg_dump, zlib, endian conversions, and PowerPC NVRAM signature conventions.

Risks: NVRAM is small and partition fragmentation can prevent allocation; checksum or zero-length corruption terminates scan; crash paths cannot allocate except preallocated buffers; compression failure falls back to shorter raw capture; pstore and kmsg_dump must avoid overwriting unread RTAS events; partition clearing loop bounds are delicate.

Test signals: scan real or emulated NVRAM partition tables, create/remove/merge partitions, trigger panic/oops pstore writes and reads across reboot, test compressed and uncompressed records, RTAS unread-event protection, and corrupted checksum handling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/nvram_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes.c

Purpose: PowerPC optimized kprobe backend that replaces an armed breakpoint with a direct branch to a generated detour buffer when the probed instruction can be safely emulated and the branch ranges permit it.

Important APIs/types/functions: `alloc_optinsn_page`; `free_optinsn_page`; `can_optimize`; `optimized_callback`; `arch_prepare_optimized_kprobe`; `arch_optimize_kprobes`; `arch_unoptimize_kprobe`; `arch_unoptimize_kprobes`; `arch_remove_optimized_kprobe`; `arch_within_optimized_kprobe`; patch helpers for immediate loads; assembly template labels from `optprobes_head.S`.

Control flow: only one static optinsn page is exposed. Optimization rejects non-kernel addresses, module addresses, conditional branches, and instructions that `analyse_instr` cannot predict/emulate with dummy regs; the rethook trampoline is a special accepted case. Preparation allocates a detour slot, checks branch reach from probe to detour and detour back to post-emulation NIP, copies the assembly template, patches in the `optimized_kprobe` pointer, branches to `optimized_callback` and `emulate_step`, patches the original instruction immediate, and installs a return branch. Optimization later backs up the original instruction and patches the probed address to branch to the detour.

State and persistence: static `insn_page_in_use`; per-optimized-probe detour slot and copied instruction bytes; live kernel text patched from breakpoint to branch and back. No durable storage.

Dependencies and integration: integrates generic optimized kprobes, PowerPC text patching/cache flushing, `analyse_instr`, `emulate_step`, kallsyms lookup for internal helper addresses, and the fixed near-text `optinsn_slot`.

Risks: branch reach is limited to 32 MiB; module probes are not optimized; conditional branch NIP cannot be predicted; only one page of detour slots is available; disabled probes under delayed unoptimization must be ignored by callback; generated immediate-load instruction counts differ PPC32/PPC64.

Test signals: optimize probes on simple emulatable kernel instructions, reject module and conditional branch probes, fill/free optinsn slots, enable/disable delayed unoptimization, and verify post-probe NIP and pre-handler callbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes_head.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes_head.S

Purpose: executable slot reservation and detour-buffer template used by `optprobes.c` to build optimized kprobe trampolines close enough to kernel text for relative branches.

Important APIs/types/functions: exported `optinsn_slot`; `optprobe_template_entry`; `optprobe_template_op_address`; `optprobe_template_call_handler`; `optprobe_template_insn`; `optprobe_template_call_emulate`; `optprobe_template_ret`; `optprobe_template_end`; `SAVE_30GPRS/REST_30GPRS`; `TEMPLATE_FOR_IMM_LOAD_INSNS`.

Control flow: the file reserves a 64 KiB aligned text area for detour slots. The template allocates an interrupt-frame-sized `pt_regs` image on the stack, saves GPRs and SPR-derived state, records trap/MSR/CTR/LR/XER/CR and PPC64 soft-mask state, loads kernel TOC on PPC64, loads a patched `optimized_kprobe` pointer into r3, passes the `pt_regs` pointer in r4 to `optimized_callback`, then calls `emulate_step` with the same regs and a patched original instruction. It restores saved state, releases the stack frame, and executes a patched return branch.

State and persistence: `optinsn_slot` is static executable storage; copied templates contain patched immediates and branches. Runtime stack state is temporary per probe hit.

Dependencies and integration: depends on pt_regs offsets from `asm-offsets.h`, PowerPC calling convention, PPC32/PPC64 save/restore differences, PACA TOC loading, and C-side template index calculations.

Risks: stack frame layout must exactly match `struct pt_regs`; failing to restore MSR/CR/LR/CTR/XER/GPRs corrupts interrupted code; template size/index changes must stay synchronized with `optprobes.c`; slot locality is required for relative branch reach.

Test signals: disassemble generated detour buffers, run optimized probes on PPC32/PPC64, verify register preservation with stress probes, and confirm template index constants match labels.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes_head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/paca.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/paca.c

Purpose: allocation and initialization of per-CPU PACA structures and related hypervisor/MMU companion data used by low-level PowerPC exception, KVM, kexec, machine-check, and scheduler paths.

Important APIs/types/functions: `alloc_paca_data`; pSeries `alloc_shared_lppaca`, `init_lppaca`, `new_lppaca`; hash-MMU `new_slb_shadow`; exported `paca_ptrs`; `initialise_paca`; `setup_paca`; `allocate_paca_ptrs`; `allocate_paca`; `free_unused_pacas`; `copy_mm_to_paca`.

Control flow: early boot allocates the PACA pointer array with memblock, then allocates each CPU's `struct paca_struct` below the real-mode/bolted mapping limit. Boot CPU allocations use bottom-up memblock so node placement is suitable before NUMA mapping is reliable. `initialise_paca` fills default fields such as lock token, paca index, kernel TOC/base/MSR, hardware CPU id, kexec state, current task, and architecture pointers. pSeries guests allocate LPPACA unless in HV mode; secure guests allocate a shared page-aligned LPPACA pool and call `uv_share_page`. Hash MMU builds allocate SLB shadows when radix is not active. `setup_paca` installs the PACA pointer into r13 and SPRG PACA registers. After CPU count is finalized, unused pointer memory and radix-only boot SLB shadow allocations are freed.

State and persistence: PACA structures are long-lived per-CPU kernel state, referenced from SPRG/r13 and by many real-mode paths. LPPACA may be shared with hypervisor/ultravisor; SLB shadow holds persistent bolted SLB metadata; `copy_mm_to_paca` caches current mm slice page-size arrays in PACA.

Dependencies and integration: depends on memblock, NUMA early node mapping, pSeries LPPACA ABI, secure guest ultravisor sharing, Book3E TLB exception frames, hash/radix MMU selection, kexec state, and scheduler `init_task`.

Risks: PACA must be real-mode accessible, cache-line aligned, and allocated below required limits; boot CPU allocation happens before final feature parsing; shared LPPACA pool sizing assumes `nr_cpu_ids`; incorrect SPRG setup breaks low-level exceptions; freeing boot SLB shadow under radix is a special-case fixup.

Test signals: boot with varying `nr_cpu_ids`, NUMA and secure guest configs, pSeries/HV/non-HV modes, hash versus radix MMU, CPU hotplug/SMP startup, kexec, and machine-check paths that access PACA in real mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/paca.c -->
