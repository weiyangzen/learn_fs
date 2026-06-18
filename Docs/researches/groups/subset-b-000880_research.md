# subset-b-000880 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_uv_x.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_uv_x.c

## Purpose
This file implements the SGI/HPE UV x2APIC/APIC driver and UV platform bring-up path. It detects UV hubbed and hubless systems from ACPI MADT OEM IDs and UVsystab data, configures UV hub type and APIC behavior, maps UV MMR/GRU/MMIOH regions, builds socket/pnode/node translation tables, initializes per-CPU/per-hub UV state, and exposes legacy `/proc/sgi_uv` compatibility files.

## Important APIs, Types, and Functions
Core exported state includes `get_uv_system_type()`, `uv_get_hubless_system()`, `uv_get_archtype()`, `is_uv_system()`, `is_uv_hubbed()`, `__uv_hub_info_list`, per-CPU `__uv_cpu_info`, `uv_possible_blades`, and `sn_rtc_cycles_per_second`. Early detection is centered on `uv_acpi_madt_oem_check()`, `uv_set_system_type()`, `early_get_arch_type()`, `early_set_hub_type()`, `early_get_pnodeid()`, and `early_get_apic_socketid_shift()`. Runtime platform setup is split between `uv_system_init()`, `uv_system_init_hub()`, and `uv_system_init_hubless()`.

The APIC integration is the `apic_x2apic_uv_x` descriptor registered with `apic_driver()`. Its IPI methods route through UV global MMR writes in `uv_send_IPI_one()`, mask variants, and `uv_wakeup_secondary()`. Memory and address routing helpers include `decode_uv_systab()`, `decode_gam_params()`, `decode_gam_rng_tbl()`, `build_uv_gr_table()`, `build_socket_tables()`, `map_gru_high()`, `map_mmr_high()`, `map_mmioh_high()`, and `calc_mmioh_map()`.

## Control Flow
During APIC probing, the MADT OEM hook seeds CPU0 hub info and calls `uv_set_system_type()`. Hubbed systems require UV arch strings such as `SGI*`, NUMA enabled, valid hub revision/type, and UV MMR reads. Hubless systems use `NSGI*` arch strings and record hubless generation bits but do not select the UV APIC driver. Later, `uv_system_init()` dispatches to hubbed or hubless initialization. Hubbed initialization maps low MMRs, initializes UV BIOS, decodes UVsystab entries, builds conversion tables, maps high GRU/MMR/MMIOH windows, fills hub structures per blade and node, assigns CPU-to-hub pointers, installs UV NMI handling, registers VGA redirection, and adjusts reboot behavior. Hubless initialization is narrower: NMI, BIOS, UVsystab, block size, proc compatibility, and reboot fallback.

## State and Persistence
Most state is boot-time global or `__initdata` that is discarded after setup. Persistent runtime state includes `uv_system_type`, hubless/hubbed bitmasks, arch/OEM strings, per-node `__uv_hub_info_list`, per-CPU `__uv_cpu_info`, possible blade count, RTC frequency, and selected x86 platform hooks. The file also installs `x86_platform.is_untracked_pat_range` for ISA and GRU PAT exclusions, `x86_platform.nmi_init`, and optional PCI VGA state handling. UVsystab-derived tables and hub structures remain live because UV address translation helpers use them after boot.

## Dependencies and Integration Points
The code depends on ACPI, EFI, APIC/x2APIC, NUMA, memblock/memory hotplug block sizing, PCI, UV BIOS calls, UV MMR definitions, and x86 platform hooks. It integrates with TSC stability marking, PAT range policy, NMI setup, procfs, PCI VGA routing, reboot selection, and per-CPU topology data. It assumes UV firmware tables and MMR layouts match the detected hub generation.

## Risks and Test Signals
Primary risks are firmware table mismatches, incorrect pnode/socket/node translations, bad MMR base/shift values, and edge cases around deconfigured sockets. Incorrect APIC routing or memory mappings can break CPU bring-up, IPIs, MMIO access, or early boot. Test signals include boot logs for UV OEM IDs, hub type, TSC sync state, GAM table output, min/max pnodes, MMR/GRU/MMIOH mappings, `/proc/sgi_uv/*` values, successful secondary CPU startup, NMI delivery, VGA legacy routing, and absence of UVsystab mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_uv_x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apm_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apm_32.c

## Purpose
This 32-bit x86 driver implements the legacy APM BIOS interface. It provides BIOS power management calls, a kernel APM daemon, `/proc/apm`, `/dev/apm_bios`, optional cpuidle integration, display blanking, power-off support, suspend/standby handling, and a large DMI quirk table for known broken firmware.

## Important APIs, Types, and Functions
The key per-open structure is `struct apm_user`, which tracks reader/writer privilege, event queue positions, pending suspend/standby acknowledgements, and wait state. BIOS calls use `struct apm_bios_call`, `apm_bios_call()`, `apm_bios_call_simple()`, and CPU0 helpers around the assembly entry points. Power operations include `apm_driver_version()`, `apm_get_event()`, `set_power_state()`, `set_system_power_state()`, `apm_get_power_status()`, `apm_engage_power_management()`, `suspend()`, `standby()`, and `apm_power_off()`.

User interfaces are `do_open()`, `do_read()`, `do_poll()`, `do_ioctl()`, `do_release()`, `proc_apm_show()`, and `apm_bios_fops`. Boot and module policy comes from `apm_setup()`, module parameters, `apm_init()`, and `apm_exit()`. Idle integration is implemented by `apm_cpu_idle()` and the `apm_idle_driver`.

## Control Flow
`apm_init()` applies DMI quirks, validates BIOS presence and 32-bit support, rejects unsafe ACPI/SMP combinations unless configured, sets GDT descriptors for BIOS segments on CPU0, creates `/proc/apm`, starts `kapmd`, registers the misc device, and optionally registers cpuidle. The `kapmd` thread pins itself to CPU0, negotiates APM version, enables/engages power management, installs `pm_power_off`, optionally hooks console blanking, then polls the BIOS once per second through `apm_mainloop()`. Events are pulled with `apm_get_event()`, decoded in `check_events()`, queued to interested users, and may drive `standby()` or `suspend()`.

Suspend saves device and syscore state, calls the BIOS, restores processor/syscore/device state, queues a normal resume event, and wakes user waiters. User ioctl paths either acknowledge pending BIOS events or generate user standby/suspend events, with privileged writers participating in vetoable suspend coordination.

## State and Persistence
Persistent driver state includes APM BIOS info in `apm_info`, global pending suspend/standby counters, waitqueues, the user linked list protected by `user_list_lock`, `apm_mutex`, idle thresholds, flags from boot/module parameters, and the `kapmd_task`. Each file descriptor owns a bounded circular event queue. Power management state also persists through global hooks such as `pm_power_off`, `console_blank_hook`, procfs, miscdevice registration, and cpuidle registration. The driver mutates firmware-facing state by enabling/engaging APM and may disengage on module exit.

## Dependencies and Integration Points
The file depends on 32-bit protected-mode APM assembly, GDT descriptor manipulation, CPU0 work execution, syscore and device PM, freezer-safe kthreads, procfs, miscdevice, poll/ioctl/read file operations, cpuidle, DMI, ACPI disable policy, reboot paths, branch speculation restriction, and IBT save/restore around firmware calls.

## Risks and Test Signals
The main risks are firmware hangs, long interrupt-off BIOS calls, unsafe SMP behavior, broken battery reporting, event queue overflow, suspend veto races, and stale global hooks on partial init/exit. Test signals include `/proc/apm` output, `/dev/apm_bios` reads and ioctls, boot messages for DMI quirks and connection version, successful CPU0-pinned BIOS calls, suspend/resume event delivery, power-off behavior, cpuidle registration when enabled, and clean unregister on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apm_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets.c

## Purpose
This generator emits C-derived constants for x86 assembly code. It is not normal runtime code; it is compiled by kbuild so `OFFSET()` and `DEFINE()` output struct offsets, sizes, and masks consumed by low-level assembly.

## Important APIs, Types, and Functions
`common()` emits offsets for `cpuinfo_x86`, `task_struct`, suspend `pbe`, IA32 signal frames, Xen vcpu fields, TDX module arguments, boot parameters, `pt_regs`, TLB state, CPU entry area, entry stack, TSS fields, optional ARIA crypto context fields, `struct alt_instr`, and exception table entries. It includes `asm-offsets_32.c` or `asm-offsets_64.c` depending on target architecture.

## Control Flow
The build compiles this file with `COMPILE_OFFSETS` and post-processes assembly output. `common()` is marked `__used` so the compiler emits its offset macros. Architecture-specific includes contribute additional definitions before `common()`.

## State and Persistence
No runtime state exists. The persistent artifact is generated header-style offset data used to keep assembly synchronized with C layout.

## Dependencies and Integration Points
The file depends on many layout-defining headers, including scheduler, thread info, signal frames, boot params, TLB flush, suspend, TDX, Xen, and optional crypto ARIA types. Any layout change in those structures can change generated constants and therefore entry, suspend, Xen, TDX, or crypto assembly behavior.

## Risks and Test Signals
Risk is stale or missing offset output causing assembly to address wrong fields. Test signals are successful `asm-offsets.s` generation, clean architecture build, and boot/runtime coverage of entry paths, suspend/resume, TDX calls, Xen paths, and optional ARIA assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_32.c

## Purpose
This file contributes 32-bit x86-specific generated offsets to `asm-offsets.c`. It is included by the main generator and explicitly rejects direct builds.

## Important APIs, Types, and Functions
The only function, `foo()`, emits offsets for 32-bit `pt_regs` fields, `saved_context.gdt_desc`, the `TSS_entry2task_stack` delta from CPU entry stack to task stack, and the EFI runtime `set_virtual_address_map` offset.

## Control Flow
When `CONFIG_X86_32` is selected, `asm-offsets.c` includes this file. The generator emits constants from the `OFFSET()` and `DEFINE()` macros and kbuild post-processing turns them into assembly-visible definitions.

## State and Persistence
No runtime state exists. The generated constants persist as build artifacts used by 32-bit entry, resume, and EFI assembly.

## Dependencies and Integration Points
It depends on `linux/efi.h`, `asm/ucontext.h`, `pt_regs`, `saved_context`, `cpu_entry_area`, `tss_struct`, and EFI runtime service layouts. The TSS delta is tightly coupled to entry-stack switching code.

## Risks and Test Signals
Layout drift can break trap/syscall entry, resume, or EFI runtime transitions on 32-bit builds. Test signals are successful 32-bit build, correct generated offset names, and boot tests covering entry stack and EFI runtime paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_64.c

## Purpose
This file contributes 64-bit x86-specific generated offsets to `asm-offsets.c`.

## Important APIs, Types, and Functions
`main()` emits paravirt patch offsets when configured, KVM steal-time `preempted`, selected `pt_regs` register offsets, and `saved_context` control-register/GDT descriptor offsets.

## Control Flow
For non-`CONFIG_X86_32` builds, `asm-offsets.c` includes this file. The function body is compiled only for its offset-emitting side effects in generated assembly.

## State and Persistence
No runtime state exists. Generated definitions persist into headers consumed by 64-bit assembly and low-level paravirt/KVM code.

## Dependencies and Integration Points
The file depends on IA32 emulation headers, optional KVM paravirt structures, paravirt patch templates, `pt_regs`, and `saved_context`. It integrates with entry code, KVM steal-time checks, paravirt patching, and suspend/resume save areas.

## Risks and Test Signals
Wrong offsets can corrupt register save/restore, paravirt patching, KVM steal-time logic, or resume. Test signals are successful 64-bit build and runtime coverage of entry, KVM guest, paravirt, and suspend paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/audit_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/audit_64.c

## Purpose
This file provides x86-64 audit syscall classification and audit class registration, including IA32 emulation support when enabled.

## Important APIs, Types, and Functions
It defines native audit class arrays for directory writes, reads, writes, attribute changes, and signals. `audit_classify_arch()` recognizes IA32 audit architecture under `CONFIG_IA32_EMULATION`. `audit_classify_syscall()` maps native syscalls such as `open`, `openat`, `openat2`, `execve`, and `execveat` to audit syscall classes and delegates IA32 classification to `ia32_classify_syscall()`. `audit_classes_init()` registers native and optional 32-bit classes.

## Control Flow
At initcall time, audit class arrays are registered. At audit decision time, syscall classification switches on ABI and syscall number to return audit categories.

## State and Persistence
The static arrays persist for audit class lookup after registration. There is no mutable runtime state in this file beyond audit subsystem registration effects.

## Dependencies and Integration Points
It depends on generic audit syscall class include fragments, x86 syscall numbers, `asm/audit.h`, and IA32 emulation audit tables. The audit subsystem consumes the registered class IDs and classification functions.

## Risks and Test Signals
Incorrect classification can under-audit or over-audit file access, exec, signal, or chmod-like operations. Test signals include audit rule tests for native and IA32 syscalls, registration during boot, and expected class matches for `openat2` and `execveat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/audit_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/bootflag.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/bootflag.c

## Purpose
This file implements the Simple Boot Flag 2.0 CMOS update used during boot.

## Important APIs, Types, and Functions
`sbf_port` is set earlier by ACPI boot code. `sbf_read()` and `sbf_write()` serialize CMOS access with `rtc_lock`. `sbf_value_valid()` checks reserved bits and parity. `sbf_init()` validates and rewrites the flag, clearing BOOTING and DIAG and optionally setting PNPOS for ISA PnP.

## Control Flow
At `arch_initcall`, `sbf_init()` exits if no port was found, reads the CMOS byte, logs invalid values, masks reserved/status bits, sets policy bits, recalculates parity in `sbf_write()`, and writes back.

## State and Persistence
The only kernel variable is init-only `sbf_port`. The persistent state is the CMOS boot flag byte, which survives reboots and communicates boot status to firmware or other OS components.

## Dependencies and Integration Points
The file depends on ACPI discovery of the SBF CMOS port, RTC CMOS helpers, parity helpers, and optional ISA PnP configuration. It integrates with early architecture init and firmware boot status conventions.

## Risks and Test Signals
Risks include writing the wrong CMOS location, parity mistakes, or racing RTC access. Test signals include boot log messages, valid CMOS parity after boot, correct BOOTING/DIAG clearing, and no RTC/CMOS regressions on systems without SBF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/bootflag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/callthunks.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/callthunks.c

## Purpose
This file implements x86 call thunk patching for call depth tracking mitigation. It rewrites compiler-recorded direct call sites so calls land on per-target padding containing the call-depth accounting template before reaching the original function.

## Important APIs, Types, and Functions
Important public entry points are `callthunks_patch_builtin_calls()`, `callthunks_translate_call_dest()`, module hook `callthunks_patch_module_calls()`, and BPF helper `x86_call_depth_emit_accounting()` when BPF JIT is enabled. Internals include `call_get_dest()`, `skip_addr()`, `patch_dest()`, `patch_call()`, `patch_call_sites()`, and `callthunks_setup()`. Debug builds export per-CPU call/return/stuff/context-switch counters and may create debugfs files.

## Control Flow
On boot, `callthunks_patch_builtin_calls()` checks `X86_FEATURE_CALL_DEPTH`, locks `text_mutex`, walks `__call_sites`, decodes each direct call, skips special entry/kexec/ftrace/switch targets, verifies source and target text ownership, installs the accounting template into target padding, and rewrites the call displacement to the padding. Module and live translation paths repeat this under `text_mutex`. BPF JIT can either detect an existing thunk or emit accounting bytes inline.

## State and Persistence
`thunks_initialized` records whether builtin patching completed. Patched kernel/module text and function padding are persistent until reboot or module unload. Debug counters are per-CPU runtime state. The `debug-callthunks` boot parameter enables verbose logging.

## Dependencies and Integration Points
The code depends on alternatives/text patching, instruction decoding, kallsyms/module text ranges, ftrace, kexec relocation ranges, Xen hypercall entry symbols, nospec branch mitigation definitions, BPF JIT, debugfs, and `text_mutex` synchronization.

## Risks and Test Signals
Risks include decoding non-call bytes, patching insufficient or non-NOP padding, targeting text outside validated ranges, racing text modification, or missing special entry points that already manage call depth. Test signals include boot log `Setting up call depth tracking`, absence of invalid padding warnings, module load tests with call thunk patching, BPF JIT execution, debugfs counter movement, and mitigation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/callthunks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cet.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cet.c

## Purpose
This file handles x86 Control-flow Enforcement Technology control-protection exceptions (`#CP`) for user shadow stack and kernel IBT.

## Important APIs, Types, and Functions
`enum cp_error_code` names architectural #CP subcodes. `cp_err_string()` formats error codes. User faults are handled by `do_user_cp_fault()`, kernel faults by `do_kernel_cp_fault()`, unexpected cases by `do_unexpected_cp()`, and the IDT entry is `exc_control_protection`. The `ibt=` boot parameter can disable IBT or change missing-ENDBR behavior from fatal to warning.

## Control Flow
The exception entry checks user mode first. User faults require `X86_FEATURE_USER_SHSTK`; the handler reads `MSR_IA32_PL3_SSP`, enables interrupts conditionally, records trap metadata, rate-limits diagnostics, sends `SIGSEGV` with `SEGV_CPERR`, and disables interrupts before return. Kernel faults require `X86_FEATURE_IBT`; ENDBR faults at the IBT selftest site are allowed to continue, other missing ENDBR faults either warn and continue when `ibt=warn` or call `BUG()`.

## State and Persistence
Persistent state is minimal: `ibt_fatal` after init and the ratelimit state. Fault handling mutates the current task's trap metadata and may clear FRED WFE state in `pt_regs`.

## Dependencies and Integration Points
The file depends on trap/IDT infrastructure, CET feature bits, MSR access, signal delivery, ratelimit logging, FRED-aware `pt_regs`, IBT selftests, and global CPU capability setup from boot parameters.

## Risks and Test Signals
Risks include mishandling interrupt state, failing to clear FRED WFE during deliberate or warning-mode ENDBR faults, over-reporting user faults, or treating unsupported #CP causes as normal. Test signals include CET selftests, user shadow-stack SIGSEGV behavior, kernel IBT no-ENDBR test, `ibt=off` and `ibt=warn` boot behavior, and ratelimited fault logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cfi.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cfi.c

## Purpose
This file decodes and reports Clang kernel CFI failures on x86 for KCFI and FineIBT modes.

## Important APIs, Types, and Functions
`decode_cfi_insn()` decodes the compiler-generated KCFI trap sequence near `regs->ip`, extracts the expected type ID and target register value, and returns them to the caller. `handle_cfi_failure()` chooses KCFI or FineIBT decoding based on `cfi_mode`, validates the trap, and reports through `report_cfi_failure()` or `report_cfi_failure_noaddr()`. `__ADDRESSABLE(__memcpy)` forces a KCFI type symbol for memcpy.

## Control Flow
When a `ud2`/bug trap is being classified, `handle_cfi_failure()` checks the configured CFI mode. KCFI requires `is_cfi_trap()` and local instruction decoding from the preceding `movl/addl/je/ud2` sequence. FineIBT delegates to `decode_fineibt_insn()`. Successful decoding reports the target and expected type; unsupported cases return `BUG_TRAP_TYPE_NONE`.

## State and Persistence
The file has no mutable state. It reads kernel text and register state and delegates persistent reporting policy to the generic CFI subsystem.

## Dependencies and Integration Points
It depends on x86 instruction decoding, nofault kernel text reads, register offset evaluation, generic Linux CFI helpers, FineIBT decoding, and bug trap classification.

## Risks and Test Signals
Risks include compiler sequence drift, instruction decoder failures, wrong ModRM register extraction, and false positives for unrelated `ud2`. Test signals include KCFI/FineIBT selftests, deliberate CFI mismatch reporting with target/type, and non-CFI `ud2` traps still following normal bug handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/check.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/check.c

## Purpose
This file reserves and periodically scans low physical memory to detect BIOS or firmware corruption.

## Important APIs, Types, and Functions
Boot parameters are parsed by `set_corruption_check()`, `set_corruption_check_period()`, and `set_corruption_check_size()`. `setup_bios_corruption_check()` reserves free low-memory scan areas and zeros them. `check_for_bios_corruption()` scans and clears nonzero words. `check_corruption()` reschedules delayed work, and `start_periodic_check_for_corruption()` starts the periodic scanner.

## Control Flow
Early setup decides whether the feature is enabled by boot parameter or config default. It rounds the scan size, walks free memblock ranges below the configured size, reserves up to eight aligned scan areas, zeros their direct mappings, and logs coverage. At device init, if areas exist and the period is nonzero, delayed work runs immediately and then every configured interval.

## State and Persistence
Persistent state includes `memory_corruption_check`, scan size and period, `scan_areas[]`, `num_scan_areas`, and the delayed work item. Reserved memblock regions remain unavailable for normal allocation so writes into them indicate corruption.

## Dependencies and Integration Points
The file depends on early boot params, memblock free range iteration and reservation, low-memory direct mapping via `__va`, workqueues, jiffies/HZ timing, and kernel warning/logging.

## Risks and Test Signals
Risks include reserving too much low memory, missing corruption outside the selected range, false positives from legitimate firmware reservations not excluded early enough, and repeated warning noise. Test signals include boot logs for reserved scan areas, periodic scan logs, injected low-memory writes causing a single warning, and disabled behavior with size zero or period zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/Makefile

## Purpose
This Makefile selects and configures x86 CPU feature, topology, vendor, hypervisor, mitigation, and generated capability-name objects.

## Important APIs, Types, and Functions
The core object list includes cache info, topology, common CPU identification, RDRAND, matching, CPU bug handling, APERF/MPERF, CPUID dependencies, UMWAIT, and generated `capflags.o`/`powerflags.o`. Conditional objects add local APIC topology, procfs, Intel/AMD/Hygon and other vendor files, MCE, MTRR, microcode, resctrl, SGX, perf watchdog, hypervisor guests, debugfs, bus lock detection, and generated `capflags.c`.

## Control Flow
kbuild expands `obj-y` and `obj-$(CONFIG_*)` based on configuration. It also removes tracing from early secondary CPU boot-sensitive objects and disables KCOV/KMSAN/KCSAN instrumentation for code paths that can hang when instrumented. The `mkcapflags` rule regenerates `capflags.c` from `cpufeatures.h`, `vmxfeatures.h`, and `mkcapflags.sh`.

## State and Persistence
There is no runtime state. Persistent outputs are selected built objects and generated `capflags.c`.

## Dependencies and Integration Points
It integrates with architecture Kconfig, kbuild, tracing and sanitizer instrumentation policy, CPU vendor support files, hypervisor detection files, and generated feature string tables.

## Risks and Test Signals
Risks include missing object selection for a configured CPU vendor or hypervisor, unsafe instrumentation on early CPU boot code, and stale generated capability strings. Test signals include config matrix builds, generated `capflags.c` updates when feature headers change, and boot tests with tracing/sanitizers enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/acrn.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/acrn.c

## Purpose
This file implements ACRN hypervisor detection and guest callback interrupt setup.

## Important APIs, Types, and Functions
`acrn_detect()` returns the ACRN CPUID base. `acrn_init_platform()` installs `sysvec_acrn_hv_callback` on `HYPERVISOR_CALLBACK_VECTOR` and routes TSC calibration to `acrn_get_tsc_khz`. `acrn_x2apic_available()` reports x2APIC availability from the boot CPU feature. `acrn_setup_intr_handler()` and `acrn_remove_intr_handler()` export registration for a single callback handler. `x86_hyper_acrn` registers the hypervisor descriptor.

## Control Flow
During hypervisor detection, the descriptor's detect callback identifies ACRN. Platform init installs the system vector and calibration hooks. On callback interrupt, the IDT entry saves old irq regs, sends APIC EOI as required by ACRN, increments hypervisor callback stats, calls the optional registered handler, and restores irq regs.

## State and Persistence
Persistent state is the global function pointer `acrn_intr_handler`, installed IDT vector, and modified `x86_platform` calibration hooks.

## Dependencies and Integration Points
The file depends on ACRN CPUID helpers, APIC EOI, IDT system vectors, irq register tracking, hypervisor framework registration, TSC calibration hooks, and exported symbols for ACRN device code.

## Risks and Test Signals
Risks include missing EOI causing lower-priority interrupts to be blocked, races around handler registration/removal, and incorrect TSC calibration. Test signals include ACRN guest boot detection, callback interrupt count increments, registered handler invocation, and stable TSC/cpu calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/acrn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd.c

## Purpose
This file implements AMD CPU identification, early feature setup, family/model-specific errata workarounds, topology/NUMA fixups, security mitigation feature adjustments, cache/TLB reporting, debug register address mask support, and late platform diagnostics.

## Important APIs, Types, and Functions
The CPU vendor descriptor `amd_cpu_dev` registers `early_init_amd()`, `cpu_detect_tlb_amd()`, `bsp_init_amd()`, and `init_amd()`. Family-specific helpers cover K5/K6/K7/K8/F10h/F12h/F15h/F16h and Zen generations. Security and correctness helpers include `early_detect_mem_encrypt()`, `bsp_determine_snp()`, `tsa_init()`, `fix_erratum_1386()`, `init_spectral_chicken()`, `zen2_zenbleed_check()`, `clear_rdrand_cpuid_bit()`, and Zen RDSEED handling. Exported/debugger-facing functions include `amd_set_dr_addr_mask()`, `amd_get_dr_addr_mask()`, and `amd_check_microcode()`.

## Control Flow
Early init sets K8/common capability bits, records microcode, derives constant/nonstop TSC, RAPL/accumulated power, extended APIC IDs, VMMCALL, memory encryption exposure, and branch prediction capabilities. BSP init checks TSC semantics, Fam15h VA alignment randomization, MWAITX delay, SSBD fallback, resctrl, Zen generation classification, SNP host support, TSA mitigation, and CPUID faulting. Full init applies family errata, Zen common setup, Zen-generation-specific mitigations, cache/TLB detection, NUMA node repair, SVM disabling detection, LFENCE serialization, ARAT, PREFETCHW, SYSRET bug, IRPERF, AUTOIBRS, APIC MSR fence clearing, and TCE enabling.

## State and Persistence
Persistent state includes CPU capability and bug bits, global `invlpgb_count_max`, `x86_amd_ls_cfg_*` mitigation state, randomized `va_align` bits, per-CPU debug register address masks, and cache/TLB global descriptors. Late init reads and clears FCH S5 reset status and logs AGESA strings from DMI additional info.

## Dependencies and Integration Points
The file integrates with x86 CPU vendor registration, CPUID/MSR helpers, NUMA/APIC topology, PCI config access, SME/SEV/SNP confidential-computing platform state, scheduler clock/delay, randomization, resctrl, cacheinfo, KVM exported symbols, microcode update paths, DMI, MMIO, and speculation mitigation infrastructure.

## Risks and Test Signals
Risks include over- or under-exposing CPU capabilities, unsafe MSR writes on guests, stale microcode tables, incorrect Zen family classification, NUMA node misassignment, breaking SVM or SME/SEV detection, and mitigation regressions. Test signals include boot CPU feature flags, dmesg errata notices, microcode update rechecks, kvm/debug register tests, NUMA topology validation, suspend/resume RDRAND behavior, SME/SEV/SNP boot tests, and late reset/AGESA logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd_cache_disable.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd_cache_disable.c

## Purpose
This file exposes AMD L3 cache index disable and subcache partitioning controls through private cache sysfs attributes.

## Important APIs, Types, and Functions
`amd_init_l3_cache()` attaches an AMD northbridge object to L3 cacheinfo and computes L3 indices via `amd_calc_l3_indices()`. `cache_get_priv_group()` returns the private attribute group for eligible L3 caches. Attribute handlers include `cache_disable_0/1_show`, `cache_disable_0/1_store`, `subcaches_show()`, and `subcaches_store()`. Hardware programming is done through `amd_get_l3_disable_slot()`, `amd_set_l3_disable_slot()`, and `amd_l3_disable_index()`.

## Control Flow
For L3 cacheinfo entries, initialization finds the northbridge for the current AMD node and lazily calculates subcache geometry from PCI config. Sysfs visibility depends on `ci->priv` and AMD northbridge feature bits. Writes require `CAP_SYS_ADMIN`, parse an index or mask, select a CPU from the shared cache map, validate slot/index state, program PCI config registers, run `wbinvd_on_cpu()` on a CPU in the owning node, and activate the disable slot.

## State and Persistence
Persistent state lives mostly in hardware PCI config registers and the northbridge `l3_cache` descriptor. The attribute array is allocated once and stored in the static `cache_private_group`.

## Dependencies and Integration Points
The file depends on cacheinfo sysfs, AMD northbridge discovery/features, PCI config access, topology node mapping, shared CPU maps, capability checks, and cache flush helpers.

## Risks and Test Signals
Risks include disabling an invalid cache index, programming the wrong node, missing flush ordering, exposing controls on unsupported hardware, and concurrent sysfs writes racing through hardware slots. Test signals include presence/absence of sysfs attributes by feature bit, correct `FREE` or index reads, rejection of duplicate/out-of-range writes, visible subcache masks, and hardware-specific cache disable validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd_cache_disable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/aperfmperf.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/aperfmperf.c

## Purpose
This file samples APERF/MPERF MSRs to report current CPU frequency and support scheduler frequency/capacity invariance on x86.

## Important APIs, Types, and Functions
Per-CPU samples use `struct aperfmperf` with a seqcount, timestamps, counter deltas, and last raw values. Public functions include `arch_set_max_freq_ratio()`, `freq_invariance_set_perf_ratio()`, `arch_enable_hybrid_capacity_scale()`, `arch_set_cpu_capacity()`, `arch_scale_cpu_capacity()`, `arch_scale_freq_tick()`, `arch_freq_get_on_cpu()`, `bp_init_aperfmperf()`, and `ap_init_aperfmperf()`. Intel ratio discovery uses `slv_set_max_freq_ratio()`, `knl_set_max_freq_ratio()`, `skx_set_max_freq_ratio()`, `core_set_max_freq_ratio()`, and `intel_set_max_freq_ratio()`.

## Control Flow
Early boot initializes APERF/MPERF references on the boot CPU and, on Intel SMP x86-64, derives a max turbo/base ratio and enables the static key for scheduler frequency invariance. AP startup initializes local counter references. Each scheduler tick reads APERF/MPERF, computes deltas, publishes them under a seqcount, and updates `arch_freq_scale` if invariance is active. Frequency queries read recent deltas if fresh enough, otherwise fall back to cpufreq or `cpu_khz`. Hybrid capacity scaling allocates per-CPU capacity/frequency-ratio data and enables a separate static key.

## State and Persistence
Persistent state includes per-CPU APERF/MPERF samples, per-CPU `arch_freq_scale`, static keys for frequency and hybrid capacity scaling, global turbo/max ratios, optional per-CPU hybrid scaling data, syscore resume hooks, and a work item that disables invariance on arithmetic failure.

## Dependencies and Integration Points
The file depends on APERF/MPERF MSRs, Intel family/model matching, cpufreq, scheduler topology and capacity scaling, syscore resume, CPU hotplug init paths, static keys, seqcounts, overflow-safe math, and SMP/IPI-safe per-CPU access.

## Risks and Test Signals
Risks include stale samples on idle/NOHZ CPUs, hypervisors returning zero MSRs, bad turbo ratio heuristics, overflow in scale math, hybrid capacity misuse before enablement, and resume losing counter references. Test signals include scaling_cur_freq behavior, scheduler frequency invariance enabled logs, fallback behavior on old samples, syscore resume reinitialization, hybrid capacity tests, and warning-triggered invariance disable path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/aperfmperf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bhyve.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bhyve.c

## Purpose
This file implements FreeBSD bhyve hypervisor detection and guest enlightenments.

## Important APIs, Types, and Functions
`bhyve_detect()` verifies the hypervisor CPUID feature, finds the `"bhyve bhyve "` CPUID base, and records the max leaf. `bhyve_features()` reads feature leaf `0x40000001`. `bhyve_ext_dest_id()` reports MSI extended destination ID support. `bhyve_x2apic_available()` always returns true. `x86_hyper_bhyve` registers the hypervisor descriptor.

## Control Flow
During hypervisor probing, detection stores CPUID base/max values. Feature callbacks later validate that the feature leaf is present before reading feature bits. Platform init is a noop, but x2APIC is advertised as available and MSI extended destination ID is conditional on CPUID.

## State and Persistence
Persistent state is limited to `bhyve_cpuid_base` and `bhyve_cpuid_max` after detection.

## Dependencies and Integration Points
The file depends on x86 hypervisor CPUID helpers, CPU feature detection, and the generic `hypervisor_x86` registration framework. It integrates with APIC/x2APIC and MSI destination-ID policy through descriptor callbacks.

## Risks and Test Signals
Risks include false detection if the signature or CPUID ranges are mishandled, or advertising x2APIC/MSI capabilities not supported by the host. Test signals include bhyve guest boot detection, CPUID feature leaf behavior, x2APIC availability decisions, and MSI routing tests with extended destination IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bhyve.c -->
