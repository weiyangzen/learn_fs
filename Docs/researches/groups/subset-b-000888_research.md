# subset-b-000888 Research

Grouped research for x86 kernel files under `sources/distributed-fs/ceph-client/arch/x86/kernel`. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/nmi.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/nmi.c

## Purpose
Implements x86 non-maskable interrupt dispatch, accounting, nested-NMI containment, crash shootdown integration, and diagnostic stall reporting. It multiplexes architectural NMI entry events into registered Linux NMI handler chains for local, unknown, PCI SERR, and I/O-check NMIs.

## APIs, Types, And Functions
Key state is `struct nmi_desc`, the `nmi_desc[NMI_MAX]` handler registry, per-CPU `struct nmi_stats`, `ignore_nmis`, `unknown_nmi_panic`, `panic_on_unrecovered_nmi`, `panic_on_io_nmi`, per-CPU nested state `nmi_state`, `nmi_cr2`, and `nmi_dr7`. Public integration points include `__register_nmi_handler()`, `unregister_nmi_handler()`, `set_emergency_nmi_handler()`, `exc_nmi`, KVM's `exc_nmi_kvm_vmx` wrapper, `nmi_backtrace_stall_snap()`, `nmi_backtrace_stall_check()`, `stop_nmi()`, `restart_nmi()`, and `local_touch_nmi()`.

## Control Flow
NMI entry reaches `exc_nmi`, which handles SEV-ES completion, ignores offline CPUs except microcode NMIs, latches nested NMIs via the per-CPU `NMI_NOT_RUNNING/NMI_EXECUTING/NMI_LATCHED` state machine, saves CR2 and debug state, enters irqentry NMI context, and invokes `default_do_nmi()` unless NMIs are globally ignored. `default_do_nmi()` first services microcode NMIs, then local NMI handlers, then external reason-port sources under `nmi_reason_lock`, then unknown NMI handlers. Back-to-back NMI detection uses per-CPU RIP tracking and `swallow_nmi` to suppress some already-handled edge-triggered events. FRED builds use a simpler NMI entry because FRED preserves CR2/DR6 semantics in the event frame.

## State And Persistence
Handler lists are RCU-protected and spinlock-updated; unregister synchronizes before reinitializing list nodes. The emergency handler is a direct pointer intended for crash contexts and is published with a write barrier. Per-CPU counters persist for runtime diagnostics. `nmi_longest_ns` is writable through debugfs and controls slow-handler warnings. Sysctl-exposed panic knobs are registered from setup code, not here.

## Dependencies And Integration
Depends on APIC/NMI vector entry code, `x86_platform.get_nmi_reason()`, machine-check and microcode NMI hooks, SEV-ES IST hooks, irqentry, debug registers, tracepoint `trace_nmi_handler`, KVM exports, crash IPI callback code in `reboot.c`, and debugfs. NMI handlers are consumed by perf, watchdog, kdump, and selftests.

## Risks And Test Signals
Risks center on NMI-context safety: no sleeping locks, careful RCU use, preserving CR2/DR7, preventing list corruption during unregister, and avoiding false unknown-NMI panics. Back-to-back swallowing can hide a real unknown NMI by design. Test signals include `CONFIG_NMI_CHECK_CPU` stall diagnostics, handler duration tracepoints, NMI selftest coverage, crash dump shootdown behavior, and boot/runtime logs for unknown or external NMI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/nmi_selftest.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/nmi_selftest.c

## Purpose
Provides an init-time NMI IPI selftest that checks whether local and remote APIC-delivered NMI vectors reach the registered local NMI handler on online CPUs.

## APIs, Types, And Functions
The file is centered on `nmi_selftest()`. Support state includes `nmi_fail`, `nmi_ipi_mask`, testcase counters, and unexpected unknown/failure counters. It installs `nmi_unk_cb()` on `NMI_UNKNOWN` and `test_nmi_ipi_callback()` on `NMI_LOCAL`.

## Control Flow
`nmi_selftest()` registers an unknown-NMI trap handler, runs `remote_ipi()` and `local_ipi()` through `dotest()`, unregisters the handler, and prints a summary. `remote_ipi()` sends NMIs to all online CPUs except the current CPU; `local_ipi()` sends one to the current CPU. `test_nmi_ipi()` registers the local handler with `NMI_FLAG_FIRST`, issues `__apic_send_IPI_mask(mask, NMI_VECTOR)`, waits up to one second for the callback to clear all CPUs from the mask, and unregisters the handler.

## State And Persistence
All state is `__initdata`, so it disappears after init. The selftest mutates the shared NMI handler registry only during the test window. Its persistent output is only printk diagnostics.

## Dependencies And Integration
Depends on APIC IPI delivery, `register_nmi_handler()`, `unregister_nmi_handler()`, online CPU masks, and `udelay()`. It validates the handler infrastructure implemented in `nmi.c` and the APIC NMI vector path.

## Risks And Test Signals
The test can time out on broken APIC/NMI routing or if CPUs fail to service NMIs. A failure disables debugging according to the printed message. Because it runs at init and uses NMI handler registration, ordering and unregister cleanup matter. Test signals are the printed per-case `ok`, `FAILED`, or `TIMEOUT` lines and the final pass/fail summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/nmi_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt-spinlocks.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt-spinlocks.c

## Purpose
Supplies x86 paravirtual spinlock defaults and feature capability setup. It lets hypervisors replace native queued spinlock unlock and vCPU preemption checks while keeping native fallback behavior.

## APIs, Types, And Functions
Exports `virt_spin_lock_key` as a static key and, under `CONFIG_PARAVIRT_SPINLOCKS`, `pv_ops_lock`. Important functions are `native_pv_lock_init()`, `__native_queued_spin_unlock()`, `pv_is_native_spin_unlock()`, `__native_vcpu_is_preempted()`, `pv_is_native_vcpu_is_preempted()`, and `paravirt_set_cap()`.

## Control Flow
On SMP, `native_pv_lock_init()` enables `virt_spin_lock_key` when the boot CPU advertises a hypervisor. `pv_ops_lock` defaults to native queued spin lock slowpath/unlock, no-op wait/kick hooks, and a native `vcpu_is_preempted` implementation returning false. `paravirt_set_cap()` forces `X86_FEATURE_PVUNLOCK` and `X86_FEATURE_VCPUPREEMPT` only when the paravirt operation pointers have been replaced from the native thunks.

## State And Persistence
State is mostly static-call/jump-label configuration and the global paravirt lock ops table. Once capabilities are forced during boot, they persist as CPU feature bits.

## Dependencies And Integration
Depends on qspinlock, static keys, paravirt call thunks, and CPU feature setup. Hypervisor-specific code can patch `pv_ops_lock`; lock slowpaths and scheduler preemption heuristics consume the resulting operations.

## Risks And Test Signals
Wrong native-vs-paravirt detection can advertise PV unlock/preemption capabilities incorrectly. Because this touches lock primitives, regressions show as hangs or poor performance under virtualization. Test signals include boot feature flags, lock stress under KVM/Xen/Hyper-V, and tracing that confirms PV wait/kick hooks are active only when intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt-spinlocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt.c

## Purpose
Defines the default x86 paravirtualization operation table for bare hardware and provides native fallback functions that paravirtual backends can override or patch.

## APIs, Types, And Functions
Exports `pv_info` and `pv_ops`. Important functions and stubs include `paravirt_ret0`, `default_banner()`, native IRQ flag helpers (`pv_native_save_fl`, `pv_native_irq_disable`, `pv_native_irq_enable`), CR2/CR3/debug register wrappers, `pv_native_safe_halt()`, and paravirt page-table operation defaults.

## Control Flow
At boot, `pv_info` identifies the environment as bare hardware unless a hypervisor overwrites it. `default_banner()` prints the chosen paravirt provider. `pv_ops` is initialized with native CPU, IRQ, halt, TLB, page-table, lazy-MMU, and fixmap operations, with XXL-only entries populated when configured. Paravirt patching machinery later rewrites call sites to these entries or hypervisor replacements.

## State And Persistence
The central persistent state is the global `pv_ops` template and `pv_info`. Some entries are callee-save asm thunks, and identity PTE conversion helpers are encoded as paravirt callee-save patch targets. These values persist after init and influence core low-level operations.

## Dependencies And Integration
Integrates with `asm/paravirt.h`, descriptor loading, TLB flushing, CR/MSR access, I/O bitmap operations from `process.c`, APIC and delay code, and static/paravirt patch infrastructure. Hypervisor code such as Xen or KVM paravirt paths replace fields before or during alternatives/paravirt patching.

## Risks And Test Signals
Incorrect defaults can break boot on bare metal or hypervisors because these hooks sit under interrupt, MMU, and CPU control paths. The functions marked `noinstr`/`NOKPROBE_SYMBOL` are sensitive to tracing and kprobe recursion. Test signals include successful boot across bare metal and paravirt guests, paravirt patch validation, TLB/MMU stress, and interrupt flag/halt behavior under tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pci-dma.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/pci-dma.c

## Purpose
Coordinates x86 PCI DMA/IOMMU initialization, command-line IOMMU options, SWIOTLB fallback, Xen DMA bounce buffering, and a VIA DAC workaround.

## APIs, Types, And Functions
Exports `dma_ops`; global knobs include `panic_on_overflow`, `force_iommu`, `iommu_merge`, `no_iommu`, `iommu_detected`, `x86_swiotlb_enable`, and `disable_dac_quirk`. Main functions are `pci_iommu_alloc()`, `iommu_setup()`, `pci_iommu_init()`, Xen/SWIOTLB helpers, and VIA PCI fixup callbacks.

## Control Flow
`iommu_setup()` parses `iommu=` early parameters such as `off`, `force`, `noforce`, `merge`, `nomerge`, `panic`, `soft`, `pt`, and `nopt`, while warning for ignored DAC-related options. `pci_iommu_alloc()` chooses Xen SWIOTLB for Xen PV domains, otherwise detects SWIOTLB need, GART, AMD IOMMU, Intel IOMMU, and initializes SWIOTLB. `pci_iommu_init()` later runs `x86_init.iommu.iommu_init()` and either prints SWIOTLB info or exits SWIOTLB if disabled.

## State And Persistence
Boot parameters set global policy for the rest of the system. SWIOTLB allocation and DMA ops persist after rootfs init. The VIA fixup sets `bus_dma_limit` on subordinate devices to 32-bit unless `iommu=usedac` disables that quirk.

## Dependencies And Integration
Depends on memblock PFN sizing, confidential-computing attributes, Xen SWIOTLB, AMD/Intel/GART IOMMU detection, generic DMA map ops, PCI fixup infrastructure, and x86 init hooks.

## Risks And Test Signals
The main risks are broken DMA on encrypted-memory guests, too-small DMA address limits, unexpected passthrough defaults, or SWIOTLB being disabled when needed. Test signals include boot logs showing detected IOMMU/SWIOTLB mode, DMA stress on >4G memory systems, Xen PV PCI tests, encrypted guest I/O, and VIA bridge regression coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pci-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pcspeaker.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/pcspeaker.c

## Purpose
Registers the legacy PC speaker platform device so the generic `pcspkr` driver can bind on systems that still expose the PIT/speaker interface.

## APIs, Types, And Functions
The only function is `add_pcspkr()`, registered with `device_initcall()`. It creates a platform device named `pcspkr` with id `-1` and no resources.

## Control Flow
During device init, `platform_device_register_simple()` publishes the device. The function returns `PTR_ERR_OR_ZERO(pd)` so initcall failure is propagated only if allocation/registration fails.

## State And Persistence
Persistent state is the registered platform device in the driver core. This file has no private mutable state.

## Dependencies And Integration
Depends on Linux platform device registration and the separate PC speaker driver. It is part of x86 legacy device bring-up and assumes the actual driver handles hardware probing or absence.

## Risks And Test Signals
Risk is small: registering an unconditional legacy device can create noise on platforms without speaker hardware, but driver binding should handle it. Test signals are platform-device registration logs, presence of the `pcspkr` device, and successful beep/input driver behavior when hardware exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pcspeaker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/perf_regs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/perf_regs.c

## Purpose
Maps x86 `pt_regs` and optional XMM register state into perf sample register values, validates user-requested perf register masks, and supplies user register snapshots for perf, including NMI-safe 64-bit handling.

## APIs, Types, And Functions
Core data is `pt_regs_offset[PERF_REG_X86_MAX]`. Public functions are `perf_reg_value()`, `perf_reg_validate()`, `perf_reg_abi()`, and `perf_get_regs_user()`. On 64-bit, per-CPU `nmi_user_regs` stores a partial NMI-safe copy.

## Control Flow
`perf_reg_value()` returns XMM values from `struct x86_perf_regs` when requested or otherwise reads from `pt_regs` using the offset table. `perf_reg_validate()` rejects empty masks, unsupported architecture-specific register bits, and reserved bits. `perf_reg_abi()` reports 32-bit or 64-bit ABI based on task mode. `perf_get_regs_user()` normally points perf at `task_pt_regs(current)`; in NMI context on 64-bit it first checks whether the NMI interrupted `task_pt_regs` setup and otherwise copies only reliably saved user registers into per-CPU storage.

## State And Persistence
The offset table is static. The per-CPU NMI copy is transient sample state and overwritten on each NMI sampling path. No persistent storage is created.

## Dependencies And Integration
Depends on perf event sampling, `asm/perf_regs.h`, ptrace register layout, task stack layout, user mode detection, and x86 FPU/XMM perf extensions.

## Risks And Test Signals
Register layout drift can corrupt perf samples. NMI sampling is especially fragile because it may interrupt syscall or interrupt entry while user regs are being constructed. Test signals include perf record/report register samples on 32-bit, 64-bit, and compat tasks, validation of rejected masks, and NMI PMU sampling under syscall-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/platform-quirks.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/platform-quirks.c

## Purpose
Initializes broad x86 legacy platform feature expectations before later boot code probes devices. It distinguishes PC, Xen, Intel MID, and CE4100 subarchitectures.

## APIs, Types, And Functions
Exports no symbols. Main functions are `x86_early_init_platform_quirks()`, `x86_pnpbios_disabled()`, and, under `CONFIG_PNPBIOS`, `arch_pnpbios_disabled()`.

## Control Flow
`x86_early_init_platform_quirks()` sets conservative defaults: i8042 expected, RTC present, warm reset supported, BIOS region reservation disabled, and PNPBIOS enabled. It then switches on `boot_params.hdr.hardware_subarch`: PC enables BIOS region reservation; Xen disables PNPBIOS and RTC; Intel MID and CE4100 disable PNPBIOS, RTC, and i8042. A platform override hook may then adjust the features.

## State And Persistence
State persists in the global `x86_platform.legacy` feature structure, which later init paths consult for RTC registration, PNPBIOS availability, keyboard controller expectations, warm reset, and BIOS reservation behavior.

## Dependencies And Integration
Depends on boot parameters, `x86_platform`, BIOS EBDA setup, and PNPBIOS. It feeds `setup.c`, `rtc.c`, and platform-specific x86 init logic.

## Risks And Test Signals
Incorrect subarch classification can probe nonexistent legacy devices or skip real ones. Test signals are boot behavior on PC, Xen PV/HVM, Intel MID, and CE4100 platforms, plus absence of spurious RTC/i8042/PNPBIOS probes where disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/platform-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pmem.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/pmem.c

## Purpose
Registers an `e820_pmem` platform device when the x86 I/O memory resource tree contains legacy persistent-memory ranges, triggering the NVDIMM e820 driver to load.

## APIs, Types, And Functions
The file defines `found()` as a resource-walk callback and `register_e820_pmem()` as a `device_initcall()`.

## Control Flow
At device init, `register_e820_pmem()` calls `walk_iomem_res_desc()` for `IORES_DESC_PERSISTENT_MEMORY_LEGACY`. If no matching memory resource exists, it exits successfully without registering anything. If found, it allocates a platform device named `e820_pmem` and adds it; failed add releases the device.

## State And Persistence
Persistent state is only the platform device registered with the driver core. The actual persistent-memory resource ownership and NVDIMM behavior live elsewhere.

## Dependencies And Integration
Depends on the iomem resource tree built from E820 data and `drivers/nvdimm/e820.c` for the implementation that binds to the platform device.

## Risks And Test Signals
Risk is mainly missed or duplicate device registration if E820 resource descriptors are wrong. Test signals include the presence of `e820_pmem`, successful nvdimm/e820 driver binding, and namespace discovery on platforms exposing legacy persistent memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/probe_roms.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/probe_roms.c

## Purpose
Discovers and reserves legacy BIOS, video, extension, and adapter option ROM memory regions, and provides PCI helpers to map a discovered BIOS option ROM that matches a device.

## APIs, Types, And Functions
Key resources are `system_rom_resource`, `extension_rom_resource`, `adapter_rom_resources[]`, and `video_rom_resource`. Exported APIs are `pci_map_biosrom()`, `pci_unmap_biosrom()`, and `pci_biosrom_size()`. Helpers include `match_id()`, `probe_list()`, `find_oprom()`, `romsignature()`, `romchecksum()`, and `probe_roms()`.

## Control Flow
`probe_roms()` scans the video ROM window in 2 KiB increments, validates the `0xaa55` signature and checksum-derived length, then requests the video ROM resource. It always requests the system ROM range, optionally requests the extension ROM if signature and checksum match, and scans adapter ROMs below the next reserved upper boundary. PCI mapping helpers search the recorded adapter resources, parse PCI data structures in ROM images using fault-tolerant reads, match vendor/device IDs or device lists, and map the resource with `ioremap()`.

## State And Persistence
Discovered ROMs persist as busy, read-only iomem resources. Mapping calls create transient ioremap mappings owned by callers until `pci_unmap_biosrom()`.

## Dependencies And Integration
Depends on ISA bus virtual mapping, `iomem_resource`, PCI driver/device IDs, fault-safe kernel reads, E820/setup memory reservations, and `setup.c` calling `x86_init.resources.probe_roms()`.

## Risks And Test Signals
Legacy ROM memory may contain malformed data, so fault-safe reads and checksum checks are important. Bad resource bounds could reserve usable memory or expose the wrong ROM to PCI drivers. Test signals include `/proc/iomem` ROM resources, PCI ROM consumers successfully mapping expected images, and booting systems with old VGA/option ROM layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/probe_roms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/process.c

## Purpose
Implements architecture-common x86 task lifecycle, clone/fork register setup, thread teardown, TLS and I/O bitmap handling, CPUID/TSC prctl modes, speculation mitigation context switch work, CPU idle selection, CPU stop behavior, stack/brk randomization, and `arch_prctl` dispatch.

## APIs, Types, And Functions
Important state includes per-CPU `cpu_tss_rw`, `__tss_limit_invalid`, `cache_state_incoherent`, `msr_misc_features_shadow`, per-CPU `ssb_state`, `boot_option_idle_override`, and `cpus_stop_mask`. Core functions include `arch_dup_task_struct()`, `arch_release_task_struct()`, `exit_thread()`, `copy_thread()`, `ret_from_fork()`, `flush_thread()`, `set_tsc_mode()`, CPUID faulting helpers, `arch_setup_new_exec()`, `native_tss_update_io_bitmap()`, `__switch_to_xtra()`, idle functions, `stop_this_cpu()`, `select_idle_routine()`, `arch_post_acpi_subsys_init()`, `arch_align_stack()`, `arch_randomize_brk()`, `__get_wchan()`, and syscall handlers for `arch_prctl`/`ni_syscall`.

## Control Flow
Fork setup builds a `fork_frame`, copies user registers, handles kernel-thread vs user-thread paths, allocates shadow stack state, clones FPU state, applies `CLONE_SETTLS`, and shares I/O bitmaps when needed. Exec cleanup re-enables CPUID if disabled, clears no-exec SSBD state, and resets tagged-address masks. Context switches call `__switch_to_xtra()` only when thread flags require extra work; it invalidates/copies I/O bitmaps, propagates return notifiers, toggles blockstep, TSC disable, CPUID faulting, and speculation MSRs. Idle setup chooses polling, MWAIT, TDX-aware halt, or safe halt based on command line and CPU quirks.

## State And Persistence
Per-task thread fields preserve TLS, PKRU, I/O bitmap, debug breakpoints, CPUID/TSC flags, and speculation flags. Per-CPU TSS and SSBD sibling state persist across context switches and CPU hotplug. Boot parameters such as `idle=` and prctl calls persist as global or per-task policy.

## Dependencies And Integration
Integrates with scheduler, entry code, FPU/xstate, shadow stacks, ptrace breakpoints, TSS/descriptor handling, APIC/tick idle, machine check, TDX, seccomp/prctl speculation controls, unwind/proc, and process_32/process_64 switch implementations.

## Risks And Test Signals
Risks are high because this code touches context switch correctness, security mitigations, user ABI, idle behavior, and CPU shutdown. Watch for stale I/O bitmaps, wrong PKRU/FPU/shstk state, CPUID/TSC policy mismatch, speculation MSR races across HT siblings, and idle regressions. Test signals include fork/clone/exec suites, prctl tests, ptrace/hw-breakpoint tests, kexec/cache-incoherent paths, idle boot options, CPU hotplug, and speculation mitigation selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/process.h

## Purpose
Provides shared inline context-switch glue for 32-bit and 64-bit x86 process code, keeping the common fast path cheap while deferring uncommon work to `__switch_to_xtra()`.

## APIs, Types, And Functions
Declares `__switch_to_xtra(struct task_struct *prev_p, struct task_struct *next_p)` and defines `switch_to_extra(struct task_struct *prev, struct task_struct *next)`.

## Control Flow
`switch_to_extra()` reads previous and next thread flags, optionally masks `_TIF_SPEC_IB` from both when conditional STIBP is disabled, and calls `__switch_to_xtra()` only if either task has context-switch work bits in `_TIF_WORK_CTXSW_NEXT` or `_TIF_WORK_CTXSW_PREV`.

## State And Persistence
No private state. It interprets per-task thread flags and static branch state from speculation-control code.

## Dependencies And Integration
Included by `process.c`, `process_32.c`, and `process_64.c`. Depends on task thread flag APIs and `switch_to_cond_stibp` from speculation-control support.

## Risks And Test Signals
The main risk is missing required extra work on context switch or calling it too often. Missing calls can leak debug, I/O bitmap, TSC, CPUID, or speculation state; excessive calls hurt scheduler performance. Test signals include context-switch microbenchmarks plus targeted tests for blockstep, I/O permission, CPUID/TSC prctl, and STIBP/SSBD transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/process_32.c

## Purpose
Implements 32-bit x86-specific register display, thread release, user-mode start frame setup, and task context switching.

## APIs, Types, And Functions
Key functions are `__show_regs()`, `release_thread()`, `start_thread()`, and `__switch_to()`. It exports `start_thread()`.

## Control Flow
`__show_regs()` prints general registers, segment selectors, EFLAGS, and optionally CR/debug registers. `release_thread()` asserts the task has no `mm` and releases vm86 IRQs. `start_thread()` clears GS, initializes user DS/ES/SS/CS, sets IP/SP, and enables interrupts in EFLAGS. `__switch_to()` saves FPU state, saves outgoing GS, loads next TLS, performs extra switch work, ends paravirt lazy mode, updates kernel stack and SYSENTER state, restores GS, writes `current_task`, and schedules Intel resctrl state.

## State And Persistence
Persists user segment and GS state in `thread_struct`, stack-top/TSS state per CPU, and resctrl scheduling state. No standalone storage is introduced.

## Dependencies And Integration
Depends on scheduler switch assembly, FPU context switching, TLS/GDT loading, vm86, paravirt `arch_end_context_switch()`, SYSENTER refresh, `process.h`, and resctrl.

## Risks And Test Signals
Risks include stale segment selectors, bad SYSENTER CS after vm86 transitions, FPU state loss, and incorrect current stack tracking. Test signals include 32-bit userspace boot, vm86 coverage, TLS/threading tests, ptrace register dumps, context-switch stress, and resctrl scheduling tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/process_64.c

## Purpose
Implements 64-bit x86-specific register display, FS/GS base management, PKRU loading, context switching, personality transitions, VDSO mapping prctls, Linear Address Masking prctls, and 64-bit `arch_prctl` operations.

## APIs, Types, And Functions
Important functions include `__show_regs()`, `release_thread()`, inactive GS base helpers, `current_save_fsgs()`, `x86_fsgsbase_read_task()`, `x86_fsbase_read_task()`, `x86_gsbase_read_task()`, `x86_fsbase_write_task()`, `x86_gsbase_write_task()`, `start_thread()`, `compat_start_thread()`, `__switch_to()`, `set_personality_64bit()`, `set_personality_ia32()`, and `do_arch_prctl_64()`.

## Control Flow
Context switch saves FPU state, saves FS/GS selectors and bases before TLS changes, loads TLS, exits paravirt lazy mode, restores DS/ES and FS/GS using FSGSBASE or legacy MSR/selector paths, loads PKRU if needed, updates per-CPU current task/stack/TSS, runs extra switch work, applies SYSRET SS workaround, schedules resctrl state, and clears AMD workload history. `start_thread_common()` resets thread features and builds the user return frame, with FRED-specific NMI/single-step bits. `do_arch_prctl_64()` implements FS/GS base set/get, checkpoint-restore VDSO mapping, LAM/tagged-address operations, and shadow-stack prctls.

## State And Persistence
Per-task `thread_struct` stores FS/GS selectors/bases, DS/ES, PKRU, and personality flags. LAM state persists in `mm->context` masks and flags. FRED, Xen PV, FSGSBASE, and CPU erratum feature bits change which hardware registers are touched.

## Dependencies And Integration
Depends on scheduler, FPU, descriptors/TLS, FSGSBASE, FRED, Xen PV, PKRU, resctrl, syscall/personality ABI, VDSO images, address masking, shadow stacks, and KVM export of `current_save_fsgs()`.

## Risks And Test Signals
FS/GS handling is ABI-critical and security-sensitive; mistakes can corrupt TLS, percpu GS, or ptrace-visible bases. Other risks include PKRU leaks, SYSRET SS erratum regressions, LAM enabling while multithreaded, and VDSO remap misuse. Test signals include glibc TLS/thread tests, ptrace FS/GS tests, compat and x32 exec, PKU tests, LAM prctl selftests, shadow-stack tests, KVM use of `current_save_fsgs()`, and context-switch stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/process_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/ptrace.c

## Purpose
Implements x86 ptrace register access, debug register emulation via perf hardware breakpoints, compat/x32 ptrace ABI handling, user regset views, xstate sizing, and SIGTRAP reporting helpers.

## APIs, Types, And Functions
Defines 32-bit and 64-bit regset enums, `struct pt_regs_offset`, register offset/name query APIs, general register get/set functions, debug register helpers, I/O permission regset access, `ptrace_disable()`, `arch_ptrace()`, `compat_arch_ptrace()`, `update_regset_xstate_info()`, `task_user_regset_view()`, `send_sigtrap()`, and `user_single_step_report()`. Regset tables include general, FP, XFP, XSTATE, TLS, IOPERM, and shadow-stack SSP where configured.

## Control Flow
Native `arch_ptrace()` handles USER-area peek/poke, full general/FP register transfers, 32-bit TLS area requests, and 64-bit `PTRACE_ARCH_PRCTL`; unknown requests fall back to generic ptrace. Register writes validate segment selectors, mask user-writable EFLAGS, and keep FS/GS base semantics aligned with architecture mode. Debug register writes create or modify perf hardware breakpoints, emulate DR6/DR7, and roll back DR7 changes on failure. Compat code translates IA32 and x32 layouts to native `pt_regs` and thread fields. Regset view selection uses current task code segment mode.

## State And Persistence
Ptrace-visible state lives in stopped tasks' `pt_regs`, `thread_struct` segment/base fields, `virtual_dr6`, `ptrace_dr7`, `ptrace_bps[]`, TLS descriptors, I/O bitmap, and FPU/xstate buffers. `xstate_fx_sw_bytes` and regset XSTATE sizes are initialized once after xstate enumeration.

## Dependencies And Integration
Depends on generic ptrace, perf hardware breakpoints, FPU regset code, LDT/TLS code, syscall ABI helpers, security/seccomp/audit layers, task stacks, nospec array indexing, shadow-stack regset support, and `process_64.c` FS/GS arch-prctl helpers.

## Risks And Test Signals
This is a user ABI boundary. Risks include accepting invalid selectors, exposing wrong ABI register layouts, debug breakpoint leaks, incompatible xstate sizes, or incorrect compat sign/zero extension. Test signals include ptrace selftests, GDB on 32/64/x32 tasks, hardware breakpoint tests, core dump regset validation, xstate/AMX changes, IOPERM dump tests, and single-step/SIGTRAP behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pvclock.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/pvclock.c

## Purpose
Provides common x86 paravirtual clock helpers used by KVM and Xen to convert hypervisor-provided pvclock structures into monotonic clocksource and wall-clock values.

## APIs, Types, And Functions
Key state is `valid_flags`, global atomic `last_value`, and `pvti_cpu0_va`. Public functions include `pvclock_set_flags()`, `pvclock_tsc_khz()`, `pvclock_touch_watchdogs()`, `pvclock_resume()`, `pvclock_read_flags()`, `pvclock_clocksource_read()`, `pvclock_clocksource_read_nowd()`, `pvclock_read_wallclock()`, `pvclock_set_pvti_cpu0_va()`, and exported `pvclock_get_pvti_cpu0_va()`.

## Control Flow
Readers use pvclock version retry loops to read consistent vCPU time or wall-clock structures. Clocksource reads calculate nanoseconds from ordered TSC, optionally clear `PVCLOCK_GUEST_STOPPED` and touch watchdogs, return directly when stable-TSC is valid, or otherwise enforce monotonicity through `last_value` compare-exchange. Wall-clock reads combine boot wall time with pvclock elapsed time.

## State And Persistence
`valid_flags` filters trusted hypervisor flags. `last_value` persists as a global monotonic floor and is reset on resume. `pvti_cpu0_va` stores the CPU0 pvclock vsyscall mapping pointer and must be set before VDSO pvclock use.

## Dependencies And Integration
Depends on pvclock structure definitions, TSC ordering, clocksource/watchdog APIs, RCU stall and hung-task watchdog resets, VDSO clock mode, fixmap/vgtod integration, and hypervisor-specific KVM/Xen setup.

## Risks And Test Signals
Risks include time going backwards, stale guest-stopped flags, incorrect TSC frequency calculation, and the 32-bit seconds limit in `pvclock_wall_clock`. Test signals include KVM/Xen guest clocksource tests, suspend/resume time continuity, watchdog behavior after guest stop, VDSO pvclock smoke tests, and monotonic clock stress across vCPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/pvclock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/quirks.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/quirks.c

## Purpose
Collects PCI/DMI-driven x86 platform workarounds for chipset IRQ balancing, HPET discovery/resume, HPET MSI disable, AMD NUMA node tagging, AMD scrub errata, Intel RAS copy-machine-check behavior, and Apple machine detection.

## APIs, Types, And Functions
Exports `x86_apple_machine`; defines `force_hpet_address` and HPET resume state. Important functions include Intel IRQ balance quirk, multiple HPET force-enable/resume helpers for Intel ICH, VIA VT8237, ATI, NVIDIA, Intel e6xx, `force_hpet_resume()`, AMD NB NUMA quirk, AMD scrub workaround, Intel RAS capability quirks, and `early_platform_quirks()`.

## Control Flow
PCI fixup macros attach quirk functions to chipset IDs at header, early, or final phases. HPET helpers inspect chipset config registers, optionally require `hpet=force`, set `force_hpet_address`, cache devices for resume, and later reprogram registers in `force_hpet_resume()`. IRQ balancing quirk disables irqdebug/affinity on affected Intel MCH revisions. NUMA quirk derives device node from AMD northbridge config. RAS quirks enable fragile machine-check copy behavior based on server capability bits.

## State And Persistence
Quirk decisions persist in globals such as `force_hpet_address`, `force_hpet_resume_type`, cached PCI device, `hpet_msi_disable`, device NUMA nodes, machine-check copy mode, and `x86_apple_machine`.

## Dependencies And Integration
Depends on PCI fixup infrastructure, HPET timer setup, DMI, IRQ affinity/debug code, NUMA node APIs, machine-check recovery, platform data for Apple machines, and chipset-specific config registers.

## Risks And Test Signals
Quirk code writes undocumented or chipset-specific registers, so false positives can break timers or platform behavior. Resume paths depend on cached devices remaining valid. Test signals include HPET boot/resume logs, timer stability, irq affinity behavior on old Intel platforms, NUMA placement on AMD NB devices, machine-check copy recovery tests, and DMI detection on Apple hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/reboot.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/reboot.c

## Purpose
Implements x86 machine restart, shutdown, halt, power-off, real-mode reboot, DMI reboot-method quirks, emergency virtualization shutdown, and crash NMI CPU shootdown.

## APIs, Types, And Functions
Exports `pm_power_off` and provides `machine_power_off()`, `machine_shutdown()`, `machine_emergency_restart()`, `machine_restart()`, `machine_halt()`, `machine_crash_shutdown()`, `machine_real_restart()`, `nmi_shootdown_cpus()`, `run_crash_ipi_callback()`, and `nmi_panic_self_stop()`. State includes `reboot_emergency`, `port_cf9_safe`, `machine_ops`, `crashing_cpu`, shootdown callback, waiting counter, and `crash_ipi_issued`.

## Control Flow
`reboot_init()` applies DMI quirks unless command line reboot type was overridden, with EFI fallback for hardware-reduced ACPI. `native_machine_restart()` optionally performs clean shutdown, runs restart notifiers, then enters emergency restart. `native_machine_emergency_restart()` disables virtualization when needed, writes CMOS warm/cold reboot marker, honors EFI capsule reboot, and loops through ACPI, keyboard controller, EFI, BIOS real-mode, CF9, and triple-fault reset methods until one succeeds. `native_machine_shutdown()` stops I/O APIC, other CPUs, LAPIC, HPET, IOMMU, and guest encryption hooks. SMP crash shootdown installs an emergency local NMI handler, sends NMI to all other CPUs, runs optional callbacks, disables virtualization, and halts remote CPUs.

## State And Persistence
Reboot type/mode are global boot/runtime policy. `machine_ops` is `__ro_after_init` and can be overridden by platform code before lockdown. Crash shootdown is deliberately one-shot and leaves the emergency NMI handler installed to handle late arrivals.

## Dependencies And Integration
Depends on ACPI, EFI runtime, DMI, real-mode trampoline, CMOS/RTC lock, APIC/IO-APIC/HPET, KVM virtualization disable hooks, tboot, IOMMU shutdown, reboot fixups, panic/crash dump infrastructure, and NMI dispatch in `nmi.c`.

## Risks And Test Signals
Reboot paths run in inconsistent system states, so locking and ordering are constrained. Risks include hanging with VMX/SVM active, wrong DMI reboot method, late NMI list corruption, or shutdown ordering issues with IO-APIC/LAPIC/HPET/IOMMU. Test signals include reboot across DMI-quirked machines, kdump/crash shootdown, sysrq-B, EFI capsule reboot, virtualization host reboot, and panic NMI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/reboot_fixups_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/reboot_fixups_32.c

## Purpose
Provides 32-bit board/chipset-specific warm reset fixups for hardware that does not reliably reboot through the generic keyboard-controller path.

## APIs, Types, And Functions
Implements weak override `mach_reboot_fixups()` for 32-bit builds. Fixup functions include `cs5530a_warm_reset()`, `cs5536_warm_reset()`, `rdc321x_reset()`, and `ce4100_reset()`, selected through `struct device_fixup fixups_table`.

## Control Flow
When generic reboot code reaches the keyboard-controller method, it calls `mach_reboot_fixups()`. This function returns immediately in interrupt context, otherwise iterates known PCI vendor/device IDs, obtains a matching device with `pci_get_device()`, runs the fixup, and drops the reference. Fixups perform chipset-specific reset writes via PCI config, MSR, port CF8/CFC/0x92, or CF9.

## State And Persistence
No persistent private state. Effects are immediate chipset reset requests; if reset succeeds, the function never returns.

## Dependencies And Integration
Depends on PCI enumeration, chipset constants, MSR access, I/O ports, and `reboot.c` weak fixup hook.

## Risks And Test Signals
Because reset writes are hardware-specific, false matches or running in unsafe context could wedge the system. Test signals are successful reboot on Geode/Cyrix/NS/RDC/CE4100 class systems and no regression on systems without matching PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/reboot_fixups_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_32.S

## Purpose
Implements 32-bit kexec relocation code that runs from the control page, copies/swaps pages into the target kernel image locations, and either jumps to the new kernel or returns for preserve-context kexec jump.

## APIs, Types, And Functions
Exports assembly entry `relocate_kernel` and symbol `kexec_control_code_size`. Local routines are `identity_mapped`, `virtual_mapped`, and `swap_pages`. Data offsets in the control page save ESP, CR0, CR3, CR4, virtual/physical control data, page table, swap page, and backup map.

## Control Flow
`relocate_kernel` saves callee state and flags, records CPU control registers and stack in the control page, reads page list/start/PAE/preserve-context arguments, disables flags/interrupts, stores jump-back data, switches to the kexec page table, moves to the physical control-page stack, and returns into identity-mapped code. `identity_mapped` normalizes CR0/CR4, flushes TLB, calls `swap_pages()`, clears registers and returns to the new start address for normal kexec, or calls the peer kernel and later swaps pages back for kexec jump. `virtual_mapped` restores original CRs, stack, flags, and registers before returning.

## State And Persistence
Temporary state is stored in the high part of the control page. Page contents are permanently moved/swapped according to the indirection list. Preserve-context mode restores the original kernel mappings/state after the peer returns.

## Dependencies And Integration
Depends on kexec indirection page format, page-size constants, control-page allocation, identity mapping, x86 CR semantics, and retpoline/unret annotations.

## Risks And Test Signals
This code runs with minimal runtime services and wrong state can brick kexec. Risks include corrupt CR state, incorrect page copy order, preserve-context swap bugs, and non-relocatable code. Test signals are `kexec -e`, crashkernel boot, kexec jump where supported, objtool/annotation checks, and testing on PAE/non-PAE 32-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_64.S

## Purpose
Implements 64-bit kexec relocation, including identity-mapped control-page execution, page copying/swapping, preserve-context return, cache-incoherent handling, and optional low-level serial/MMIO exception debugging.

## APIs, Types, And Functions
Exports `relocate_kernel`, `kexec_va_control_page`, `kexec_pa_table_page`, `kexec_pa_swap_page`, debug port/MMIO data, `kexec_debug_idt`, `kexec_debug_exc_vectors`, and `kexec_control_code_size`. Local routines include `identity_mapped`, `virtual_mapped`, `swap_pages`, 8250 print helpers, nybble/qword printers, and exception handler stubs.

## Control Flow
`relocate_kernel` saves GPRs/flags, invalidates old GDT/IDT, switches to kexec page tables, saves CR state, disables PGE/LASS, records backup map, moves to the physical control-page stack, and jumps into identity-mapped code. `identity_mapped` loads a debug GDT/IDT, normalizes CR0/CR4 including CET clearing and LA57/TDX MCE preservation, optionally executes `wbinvd`, calls `swap_pages()`, then either clears registers and returns to the target start address or calls the peer kernel and swaps pages back for preserve-context. `virtual_mapped` restores saved CRs, optional kexec-jump GDT, flags, and GPRs. `swap_pages()` interprets destination, indirection, done, and source entries and copies or swaps via the swap page depending on flags.

## State And Persistence
Relocation state is in `.data..relocate_kernel`, copied with the control page. Normal kexec permanently overwrites destination pages; preserve-context swaps them back. Debug output state persists only through configured serial/MMIO addresses.

## Dependencies And Integration
Depends on kexec page-table/control-page setup, CR0/CR3/CR4 feature constraints, TDX/SME cache-incoherent flags, CET/LASS handling, objtool unwind hints, retpoline annotations, and optional kexec jump state.

## Risks And Test Signals
This is among the most fragile boot-path assembly: bad CR4 bits, LA57 mismatch, CET/LASS handling, cache flush omission under memory encryption, or page-list corruption can fail kexec silently. Test signals include normal kexec, crashkernel, preserve-context kexec jump, encrypted-memory platforms, 5-level paging, TDX guests, and serial debug exception output when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/resource.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/resource.c

## Purpose
Filters candidate x86 memory resources so PCI/resource allocation avoids BIOS ROM and, optionally, E820-reserved ranges.

## APIs, Types, And Functions
Public function is `arch_remove_reservations(struct resource *avail)`. Helpers are `resource_clip()` and `remove_e820_regions()`.

## Control Flow
For memory resources, `arch_remove_reservations()` clips out the high BIOS ROM window, then `remove_e820_regions()` iterates E820 entries if `pci_use_e820` is set. Each overlap shrinks `avail` to keep the larger non-conflicting side, logging the avoided E820 range and remaining range when it changes.

## State And Persistence
This code mutates the caller-provided `struct resource` in place. It does not own persistent state; it reads global E820 and PCI policy.

## Dependencies And Integration
Depends on `e820_table`, BIOS ROM constants, `pci_use_e820`, and generic resource allocation. It protects PCI resource assignment from firmware/BIOS memory conflicts.

## Risks And Test Signals
Clipping keeps only one side of a conflict, so it can discard usable subranges in complex overlaps. Wrong E820 data can overly constrain PCI BAR placement. Test signals include PCI resource allocation logs, absence of allocations inside BIOS/E820 reserved regions, and device enumeration on systems with fragmented firmware memory maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/resource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/rethook.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/rethook.c

## Purpose
Implements the x86 architecture backend for generic rethook, replacing a probed function's return address with a trampoline that saves registers, invokes rethook handlers, and resumes at the original return address.

## APIs, Types, And Functions
Provides assembly `arch_rethook_trampoline`, callback `arch_rethook_trampoline_callback()`, `arch_rethook_fixup_return()`, and `arch_rethook_prepare()`. Functions are marked `NOKPROBE_SYMBOL` where recursion would be unsafe.

## Control Flow
`arch_rethook_prepare()` saves the original stack return address in `rethook_node`, records the frame pointer, and writes `arch_rethook_trampoline` to the return slot. On return, the trampoline pushes a fake return address for unwinding, saves pt_regs-compatible state, calls `arch_rethook_trampoline_callback()`, restores registers/flags, and returns. The callback normalizes pt_regs fields, passes the frame pointer to `rethook_trampoline_handler()`, and stores FLAGS into the pt_regs SS slot so trampoline stack fixup can pop correctly. `arch_rethook_fixup_return()` replaces the fake frame return address with the real one.

## State And Persistence
Per-hook state lives in `struct rethook_node` and the target stack's patched return address. No global mutable state is maintained.

## Dependencies And Integration
Depends on generic rethook, kprobes register save/restore macros, objtool unwind hints, frame-pointer unwinding conventions, and x86 pt_regs layout.

## Risks And Test Signals
Risks include corrupting the target stack, bad unwind metadata, recursion through probes, and incorrect 32/64-bit stack adjustment. Test signals include kretprobe/rethook selftests, stack unwinding through hooked functions, ftrace/kprobe coexistence, and stress with nested hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/rethook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/rtc.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/rtc.c

## Purpose
Implements x86 CMOS RTC access, persistent clock read/write hooks, and fallback `rtc_cmos` platform-device registration.

## APIs, Types, And Functions
Exports `rtc_lock`, and on 32-bit exports `cmos_lock`. Public functions include `mach_set_cmos_time()`, `mach_get_cmos_time()`, `rtc_cmos_read()`, `rtc_cmos_write()`, `update_persistent_clock64()`, and `read_persistent_clock64()`. `add_rtc_cmos()` is a device initcall.

## Control Flow
`mach_set_cmos_time()` converts a timespec to `rtc_time`, validates it, then writes the MC146818 clock. `mach_get_cmos_time()` rejects RTC values used by pm_trace, reads the RTC with a timeout, and converts to timespec. CMOS byte access uses `lock_cmos_prefix/suffix` around port index/data I/O. Persistent clock hooks delegate to `x86_platform.set_wallclock` and `x86_platform.get_wallclock`. `add_rtc_cmos()` registers a fallback platform device unless another CMOS device exists or the platform marked legacy RTC absent.

## State And Persistence
CMOS RTC contents are persistent hardware state. Kernel state includes exported locks and the platform device. The file does not cache wall time.

## Dependencies And Integration
Depends on MC146818 RTC helpers, I/O ports, ACPI/pm_trace validation, `x86_platform` wallclock hooks, platform device core, and legacy platform quirks.

## Risks And Test Signals
Risks include invalid RTC writes, NMI/CMOS locking mistakes, pm_trace misinterpreted as real time, and duplicate RTC platform devices. Test signals include read/write persistent clock tests, suspend/resume timekeeping, `/dev/rtc` binding, 32-bit NMI-safe CMOS access, and boot logs for fallback registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/setup.c

## Purpose
Contains `setup_arch()`, the central x86 boot initialization sequence. It translates boot parameters into kernel state, reserves early memory, processes firmware setup data, initializes CPU/platform subsystems, builds resource maps, configures paging/memblock, and hands off to later architecture init.

## APIs, Types, And Functions
Important globals include `max_low_pfn_mapped`, `max_pfn_mapped`, `_brk_start/_brk_end`, `boot_params`, kernel code/data/bss resources, `boot_cpu_data`, `mmu_cr4_features`, bootloader IDs, `sysfb_primary_display`, `saved_video_mode`, and `command_line`. Public helpers include `extend_brk()`, `ima_free_kexec_buffer()`, `ima_get_kexec_buffer()`, `reserve_standard_io_resources()`, `x86_configure_nx()`, `setup_arch()`, `i386_reserve_resources()`, and `arch_cpu_is_hotpluggable()`.

## Control Flow
`setup_arch()` starts with 32/64-bit page-table and command-line setup, detects OLPC/FW state, installs early traps, initializes CPU/static calls/ioremap, parses boot parameters, runs OEM setup, reserves kernel/initrd/setup_data/BIOS/SNB memory, builds E820/memblock state, processes setup_data entries for E820 extensions, DTB, EFI, IMA, KHO, and RNG seeds, configures NX, parses early params, initializes EFI/DMI/hypervisor/ROM resources, trims BIOS/kernel ranges, computes PFNs, randomizes memory layout, allocates page-table buffers, reserves brk, initializes memory encryption, reserves EFI boot services, real-mode trampoline, direct mapping, log buffer, initrd, ACPI tables, NUMA, crashkernel, KASAN, APIC/IOAPIC/topology, PCI gap/resources, timers, MCE, jiffies, EFI quirks, and unwinder state.

## State And Persistence
Boot parameters are copied into stable globals. Memblock/E820 reservations persist into the resource tree and allocator setup. RNG setup_data is zeroed after ingestion. IMA/KHO buffers are reserved for later consumers. Kernel resources and sysctls persist after boot.

## Dependencies And Integration
Integrates with nearly every x86 boot subsystem: E820, memblock, EFI, ACPI, DMI, hypervisor detection, APIC/MPTABLE/IOAPIC, NUMA, KASLR, memory encryption, KASAN, MTRR/cache, initrd, IMA, kexec handover, sysfb, vgacon, PCI resources, thermal/MCE, timers, and sysctl registration for NMI/reboot/io-delay knobs.

## Risks And Test Signals
Boot ordering is the main risk: memory must be reserved before allocators reuse it, EFI/DMI/hypervisor detection must happen before dependent cache/MTRR work, and setup_data must be mapped/unmapped safely. Other risks include wrong E820 trimming, crashkernel reservation in hotpluggable memory, initrd relocation failure, RNG seed reuse, and APIC/ACPI ordering regressions. Test signals are boot logs across BIOS/EFI/Xen/TDX/SEV/32-bit, memblock debug, `/proc/iomem`, initrd boot, kexec/IMA/KHO paths, NUMA topology, crashkernel reservation, KASAN boot, and APIC/IOAPIC initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/setup.c -->
