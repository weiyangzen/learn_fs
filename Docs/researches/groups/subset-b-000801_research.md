# Research: subset-b-000801

Grouped research for PowerMac SMP/time/early debug console code and PowerNV OPAL, EEH, idle, memtrace, OCXL, firmware dump, and firmware update platform code. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/smp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/smp.c

Purpose: implements SMP bring-up, IPI delivery, timebase synchronization, cache handoff, and CPU hotplug behavior for legacy PowerMac systems. It supports the older PowerSurge multiprocessing hardware and the Core99/G4/G5 generation selected by `pmac_setup_smp()`.

Important APIs/types/functions: exports the platform `smp_ops_t` implementations `psurge_smp_ops` and `core99_smp_ops`. PowerSurge paths include `smp_psurge_probe()`, `smp_psurge_kick_cpu()`, `psurge_secondary_ipi_init()`, `psurge_set_ipi()`, and software timebase exchange via `tb_req`/`timebase`. Core99 paths include `smp_core99_probe()`, `smp_core99_kick_cpu()`, `smp_core99_setup_cpu()`, `smp_core99_give_timebase()`, `smp_core99_take_timebase()`, and several hardware timebase-freeze backends: GPIO on 32-bit G4, I2C Cypress/Pulsar on some G5s, and platform-function `cpu-timebase` on newer machines.

Control flow: `pmac_setup_smp()` detects Core99 by `uni-n`, `u3`, or `u4` device-tree nodes and otherwise falls back to PowerSurge when configured. Probe counts or fabricates CPU presence, installs MPIC or custom IPI handling, initializes I2C/platform-function support, and disables 32-bit NAP where unsafe. CPU kick paths patch or write low-level reset/start vectors, briefly hold interrupts, release the target CPU, then restore the vector. Timebase synchronization freezes hardware timebase when possible and falls back to generic software sync.

State and persistence: state is early-boot global kernel state: mapped hardware registers, `smp_ops`, CPU possible/present masks, `pmac_tb_freeze`, I2C host references, `timebase`, `tb_req`, and hotplug callbacks. No persistent storage is written.

Dependencies and integration points: depends on Open Firmware device tree, MPIC, PowerMac feature calls, low-level text patching, early MMIO mappings, KeyLargo GPIO, PMac low I2C, platform functions, CPU feature flags, and generic PowerPC SMP/hotplug helpers. It integrates directly with `ppc_md`, `smp_ops`, MPIC IPI setup, and CPU hotplug state registration.

Risks: very hardware-specific sequencing around reset vectors, IPI registers, and timebase freeze can hang machines if timing or memory ordering changes. PowerSurge paths rely on undocumented physical registers and fabricated CPU topology. Core99 CPU kick temporarily patches the reset vector at `PAGE_OFFSET+0x100`; correctness depends on interrupt exclusion and restoration. Hotplug offline loops deliberately run with unusual interrupt and MMU assumptions.

Test signals: no unit tests are expected. Useful validation is booting SMP-capable PowerMac variants, secondary CPU call-in, synchronized timebase, MPIC IPI delivery, CPU offline/online, cache register consistency on G4, and negative testing on single-CPU or unsupported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/time.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/time.c

Purpose: supplies PowerMac time initialization, RTC access, and decrementer calibration. It bridges machine-controller-specific RTC implementations and corrects timebase frequency on older 32-bit machines.

Important APIs/functions: `pmac_time_init()` reads GMT offset and DST flags from XPRAM on 32-bit NVRAM-enabled builds. `pmac_get_boot_time()`, `pmac_get_rtc_time()`, and `pmac_set_rtc_time()` dispatch to CUDA, PMU, or SMU RTC functions according to `sys_ctrler`. `pmac_calibrate_decr()` starts with generic Open Firmware calibration and optionally invokes `via_calibrate_decr()`.

Control flow: early init reads timezone metadata and returns a delta. RTC calls switch over `sys_ctrler` and return zero or `-ENODEV` when no controller backend exists. `via_calibrate_decr()` maps a VIA device found in the device tree, configures VIA timer 1 in continuous mode, measures decrementer ticks across a known timer interval, updates `ppc_tb_freq`, and unmaps the device. `pmac_calibrate_decr()` avoids VIA calibration for MacRISC2/3/4 except for the PowerMac3,5 QuickSilver special case.

State and persistence: writes only kernel globals such as `ppc_tb_freq`; reads XPRAM/NVRAM, RTC, and device-tree resources. It does not persist new values.

Dependencies and integration points: depends on CUDA, PMU, SMU, RTC conversion helpers, Open Firmware address translation, early ioremap, PowerMac machine controller selection, and generic PowerPC time/decrementer infrastructure.

Risks: VIA calibration busy-waits on hardware interrupt flags during early boot; missing or inaccurate device-tree resources make it fall back to generic calibration. RTC dispatch depends on `sys_ctrler` being correctly initialized. Older firmware quirks mean removing the QuickSilver override can regress clock accuracy.

Test signals: boot logs showing XPRAM GMT delta and stable decrementer frequency, RTC read/set on CUDA/PMU/SMU systems, suspend/resume RTC access, and time drift checks on older non-MacRISC2 PowerMacs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_adb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_adb.c

Purpose: layers ADB keyboard input and optional BootX framebuffer text output onto the early `udbg` console used by xmon and early debugging on PowerMac.

Important APIs/functions/state: `udbg_adb_init_early()` can install BootX text output before full ADB probing. `udbg_adb_init()` captures existing `udbg_putc`, `udbg_getc`, and `udbg_getc_poll`, then replaces them with ADB-aware wrappers. `udbg_adb_getc_poll()` calls `pmu_poll_adb()` or `cuda_poll()` before delegating. With `CONFIG_BOOTX_TEXT`, `udbg_adb_local_getc()` waits for ADB keyboard keycodes, tracks shift state, maps keycodes through local tables, and draws a cursor via `btext`.

Control flow: initialization preserves the previous console implementation and uses this file as a final wrapper. It verifies a device-tree `keyboard` node whose parent is type `adb`, selects PMU or CUDA input by probing VIA controller helpers, and leaves BootX output active even if keyboard input is unavailable. Reads poll ADB and then either consume local xmon keycodes or delegate to the old console. Writes draw to BootX text and then delegate.

State and persistence: global callback pointers retain previous console state. `input_type`, `udbg_adb_use_btext`, `xmon_wants_key`, `xmon_adb_keycode`, and shift state are volatile early-debug state only.

Dependencies and integration points: integrates with global `udbg_*` callbacks, xmon ADB globals, BootX btext drawing, PMU/CUDA ADB polling, device-tree keyboard discovery, and PowerMac controller probes.

Risks: callback wrapping order is important because this implementation expects to be initialized last. Local keymap coverage is limited and ignores key-up transitions except for shift. Polling loops can spin indefinitely while waiting for input. Failure to find ADB input returns `-ENODEV` but may still change output callbacks.

Test signals: early xmon input from ADB keyboards, BootX text output, delegation to preexisting serial/other udbg console, PMU and CUDA keyboard polling, and no regressions when no ADB keyboard exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_adb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_scc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_scc.c

Purpose: provides early `udbg` console support for Apple Zilog SCC serial ports on PowerMac, including a real-mode PPC64 path.

Important APIs/functions: `udbg_scc_init(int force_scc)` locates the ESCC device, selects the Open Firmware stdout channel or channel A when forced, maps SCC control/data registers, initializes the serial port, and installs `udbg_scc_putc`, `udbg_scc_getc`, and `udbg_scc_getc_poll`. `udbg_init_pmac_realmode()` hardwires real-mode SCC addresses on PPC64 and installs a real-mode putc callback using `real_readb`/`real_writeb`.

Control flow: normal init finds `escc`, parent `mac-io`, and the `linux,stdout-path` chosen node. It computes physical MMIO from `reg` and `assigned-addresses`, enables/locks the SCC through `pmac_call_feature(PMAC_FTR_SCC_ENABLE)`, maps one page, resets the selected side, preserves baud rate from OF when SCC was stdout, otherwise chooses 57600 for Xserve/G5 or 38400 for older machines, writes the init table, and prints a test string.

State and persistence: global `sccc` and `sccd` hold mapped control/data register addresses. No persistent state is written.

Dependencies and integration points: depends on Open Firmware nodes, mac-io assigned addresses, PMac feature control, raw MMIO accessors, `udbg` global callbacks, and PPC64 real-mode access helpers.

Risks: busy-wait getc/putc can hang if hardware is absent after partial initialization. The forced fallback to channel A can conflict with firmware or another user if the port is not intended for debugging. Real-mode fixed addresses are platform-specific.

Test signals: early serial output and input on OF-selected SCC, forced channel-A debug on supported machines, newline CR handling, PPC64 real-mode output before virtual mappings, and clean no-op behavior when ESCC is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/udbg_scc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Kconfig

Purpose: defines build-time configuration for the IBM PowerNV non-virtualized PowerPC platform and selected platform features.

Important symbols: `PPC_POWERNV` requires `PPC64 && PPC_BOOK3S`, defaults to enabled, and selects platform MMU, interrupt, PCI, MSI, CPU frequency, doorbell, SMP, radix TLBIE, and debug-console capabilities. `OPAL_PRD` enables the OPAL PRD driver for processor recovery diagnostics. `PPC_MEMTRACE` enables runtime allocation of RAM for hardware tracing and depends on PowerNV, memory hotplug, and contiguous allocation. `SCOM_DEBUGFS` exposes SCOM controllers through debugfs when `DEBUG_FS` is enabled.

Control flow and state: this file has no runtime control flow. It shapes compile-time inclusion, dependency solving, and implied architecture capabilities for the PowerNV platform.

Dependencies and integration points: integrates with top-level PowerPC Kconfig, OPAL firmware-facing drivers, PCI/interrupt subsystems, memory hotplug, debugfs, and platform files selected in the sibling Makefile.

Risks: `PPC_POWERNV` selects many foundational features, so dependency changes can alter architecture-wide builds. Feature symbols such as `PPC_MEMTRACE` expose privileged runtime interfaces and must remain gated by required memory-management support.

Test signals: `olddefconfig`/`allyesconfig`/PowerNV defconfig resolution, successful PowerNV kernel builds, expected object inclusion from the Makefile, and no impossible dependency cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Makefile

Purpose: selects PowerNV platform object files and sanitizer exclusions for low-level real-mode code.

Important entries: disables KASAN instrumentation for `idle.o`, `pci-ioda.o`, `pci-ioda-tce.o`, and `setup.o` because real-mode paths and early machine-check handling are unsafe to instrument. Always builds OPAL setup/call/wrapper/core platform files, RTC/NVRAM/LPC/flash/log/dump/sysparam/sensor/message/HMI/power/irq/kmsg/powercap/PSR/sensor-group/ultravisor support. Conditional objects include SMP/subcore, FADump, OPAL core, PCI/IODA, EEH, memory errors, OPAL PRD, IMC, memtrace, VAS, OCXL, XSCOM, and secure variables.

Control flow and state: build-only declarative control. It maps Kconfig symbols to object inclusion and sanitizer behavior.

Dependencies and integration points: depends on symbols from PowerPC and PowerNV Kconfig. It is the link point that ties the source files in this subset into the kernel image.

Risks: enabling KASAN on real-mode code can break runtime behavior. Conditional duplication of `opal-fadump.o` under both `CONFIG_FA_DUMP` and `CONFIG_PRESERVE_FA_DUMP` must remain consistent with the file's compile-time branches. Object ordering matters for some initcall-visible platform symbols.

Test signals: PowerNV allmod/allyes/defconfig builds, KASAN PowerNV builds, and link checks for each conditional feature combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/copy-paste.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/copy-paste.h

Purpose: exposes inline wrappers for PowerPC VAS copy/paste instructions used by PowerNV accelerator code.

Important APIs: `vas_copy(void *crb, int offset)` emits the `copy` instruction using the command/request block pointer and offset. `vas_paste(void *paste_address, int offset)` emits the `paste` instruction, reads CR0 through `mfocrf`, and returns the condition-code bits after masking out summary overflow.

Control flow and state: both helpers are single inline assembly operations with `memory` clobbers. `vas_paste()` returns hardware status encoded in CR0; no memory or global state is maintained by the wrapper itself.

Dependencies and integration points: depends on opcode macros from `asm/ppc-opcode.h` and CR field constants from `asm/reg.h`. Included by PowerNV VAS code that submits accelerator requests.

Risks: register constraints and CR0 handling must match instruction semantics exactly. Callers must provide valid MMIO/architected addresses and interpret nonzero paste status correctly. The helpers provide no retry, ordering beyond the assembly memory clobber, or validation.

Test signals: successful VAS accelerator submission paths, paste error handling, compiler build coverage across supported PowerPC toolchains, and hardware tests that verify CR0 status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/copy-paste.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/eeh-powernv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/eeh-powernv.c

Purpose: implements PowerNV-specific EEH operations for PCI error detection, isolation, diagnostics, reset, config-space mediation, error injection, and OPAL event handling.

Important APIs/types/functions: registers `pnv_eeh_ops` through `eeh_init()`. Key functions include `pnv_eeh_probe()`, `pnv_eeh_post_init()`, `pnv_eeh_set_option()`, `pnv_eeh_get_state()`, `pnv_eeh_reset()`, `pnv_eeh_next_error()`, `pnv_eeh_read_config()`, `pnv_eeh_write_config()`, `pnv_eeh_restore_config()`, and exported reset helper `pnv_pci_reset_secondary_bus()`. Debugfs includes error injection and raw PHB register accessors when enabled.

Control flow: init verifies OPAL firmware, sets EEH probe mode, sizes PE aux diagnostic buffers, hooks `ppc_md.pcibios_bus_add_device`, and registers the backend. Post-init requests the OPAL PCI error event IRQ, creates debugfs files per PHB, and toggles PHB EEH flags. Device probe records PCI capabilities, builds PE trees, caches primary buses, saves BARs, and enables global EEH on first device. OPAL event IRQ disables itself and queues EEH core recovery. `pnv_eeh_next_error()` drains pending events, walks PHBs, asks OPAL for next errors, classifies IOC/PHB/PE conditions, freezes compound PEs, dumps diagnostics, and unmasks the IRQ when no actionable error remains.

State and persistence: persistent kernel state includes `eeh_event_irq`, PE trees, PE state flags such as isolated/config-blocked/reset, PHB flags, saved BARs, diagnostic buffers, and debugfs files. It does not write disk state.

Dependencies and integration points: integrates with OPAL PCI calls, PowerNV PHB/IODA structures, generic EEH core, PCI config accessors, MSI/IRQ domain code, debugfs, firmware feature flags, and PCI bus/device add hooks.

Risks: recovery sequencing is sensitive: frozen state is intentionally kept until BAR restore, config access may be blocked for problematic adapters, and parent PE migration affects which device gets recovered. Debugfs error injection can deliberately fault hardware. OPAL return-code mapping must not hide fatal PHB/IOC states. IRQ masking/unmasking prevents event storms but can lose progress if `next_error` is not called.

Test signals: EEH injection via debugfs, OPAL PCI error events, frozen PE recovery, PHB reset/fenced PHB recovery, VF FLR/AF FLR, Broadcom restricted-config behavior, diagnostic log dumps, and PCI config access behavior while isolated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/eeh-powernv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/idle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/idle.c

Purpose: provides PowerNV CPU idle, stop/nap/sleep/winkle entry and wakeup handling, deep-state register save/restore, CPU hotplug offline idle, and device-tree parsing of OPAL idle states.

Important APIs/functions/state: exports `pnv_get_supported_cpuidle_states()`, `pnv_power9_force_smt4_catch()`, `pnv_power9_force_smt4_release()`, `pnv_program_cpu_hotplug_lpcr()`, and `pnv_cpu_offline()`. Core paths are `power7_idle_insn()`, `power9_idle_stop()`, `power10_idle_stop()`, `arch300_idle_type()`, `validate_psscr_val_mask()`, `pnv_arch300_idle_init()`, `pnv_parse_cpuidle_dt()`, and `pnv_init_idle_states()`. Global state includes discovered `pnv_idle_states`, supported flags, default/deepest PSSCR values, TB and SPR loss thresholds, and Power7 fastsleep workaround flags.

Control flow: subsystem init initializes PACA idle state fields, parses `/ibm,opal/power-mgt`, validates properties, calculates supported states, selects platform `ppc_md.power_save`, and programs OPAL stop-api SPR restoration for deep states. Power7/8 paths save per-core/subcore/thread SPRs for winkle, manage fastsleep workaround apply/undo, track idle threads via PACA bit fields, resync timebase after loss, and restore SLB/SPR state. POWER9/10 paths construct PSSCR, enter ISA 3.0 stop, use PLS to detect SPR/TB loss, restore core/thread registers, handle HMI wakeups, and coordinate KVM stop avoidance for SMT4 workarounds.

State and persistence: runtime state lives in PACA fields, global idle-state arrays, sysfs attribute `fastsleep_workaround_applyonce`, and OPAL stop-api register programming. No filesystem persistence exists.

Dependencies and integration points: depends on OPAL idle state DT properties, stop-api calls, PowerPC idle assembly helpers, PACA, cpuidle disable policy, KVM HV fields, subcore sibling masks, runlatch, doorbells, HMI real-mode handling, SLB restore, and CPU hotplug.

Risks: real-mode idle code has strict MMU/interrupt assumptions. Incorrect state-loss thresholds can skip required SPR or timebase restoration. POWER10 deep loss handling is intentionally incomplete and deep context-loss states are skipped. Fast sleep workaround sysfs changes affect all cores. KVM `dont_stop` ordering is security-critical because a thread may be switched to a guest context.

Test signals: DT parsing on POWER8/9/10/11, platform idle entry/exit under interrupt load, timebase continuity, CPU offline/online, KVM HV guest coexistence, fastsleep workaround sysfs, HMI wake handling, and suspend-like deep state stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/memtrace.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/memtrace.c

Purpose: implements PowerNV debugfs-controlled runtime reservation of contiguous per-NUMA-node RAM for hardware tracing, exposing reserved memory as noncached trace buffers.

Important APIs/types/functions: `struct memtrace_entry` tracks each reserved region. `memtrace_enable_set()` is the debugfs control write path. `memtrace_alloc_node()` allocates contiguous pages, flushes cache, marks pages offline, and removes the linear mapping. `memtrace_init_debugfs()` maps each region with `ioremap()` and creates per-node debugfs files `trace`, `start`, and `size`. `memtrace_free_regions()` reverses mappings and returns pages through `arch_create_linear_mapping()` and `free_contig_range()`.

Control flow: machine device init creates `arch_debugfs_dir/memtrace/enable`. Writing a nonzero aligned size frees any previous reservation, allocates one region per online node, creates debugfs entries, and records the active size. Writing zero frees all reservations. Reads and mmap of per-node `trace` expose the reserved memory buffer.

State and persistence: global state is protected by `memtrace_mutex`: `memtrace_size`, `memtrace_array`, and `memtrace_array_nr`. Reserved pages are marked `PageOffline` and removed from normal linear mapping until freed. Debugfs entries are ephemeral runtime state.

Dependencies and integration points: depends on PowerNV machine init, memory hotplug, contiguous page allocation, architecture linear mapping hooks, cache flushes, NUMA online node iteration, debugfs, ioremap, and remap_pfn_range.

Risks: allocation failure can leave partial per-node reservations that later control writes must clean up. Mapping and page-offline manipulation are privileged and memory-management sensitive. Debugfs `trace` exposes raw physical trace buffers. Size must align with memory block size or memory hotplug assumptions break.

Test signals: enable/disable cycles, partial allocation failure recovery, mmap/read of trace buffers, NUMA-node coverage, page offline status, memory hotplug interactions, and debugfs cleanup after free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/memtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ocxl.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ocxl.c

Purpose: supplies PowerNV OpenCAPI/OCXL platform services for actag allocation, PASID sizing, transaction-layer configuration, XSL register mapping, SPA setup, LPAR mapping, and ATSD TLB invalidation.

Important APIs/functions: exported functions include `pnv_ocxl_get_actag()`, `pnv_ocxl_get_pasid_count()`, `pnv_ocxl_get_tl_cap()`, `pnv_ocxl_set_tl_conf()`, `pnv_ocxl_get_xsl_irq()`, `pnv_ocxl_map_xsl_regs()`, `pnv_ocxl_unmap_xsl_regs()`, `pnv_ocxl_spa_setup()`, `pnv_ocxl_spa_release()`, `pnv_ocxl_spa_remove_pe_from_cache()`, `pnv_ocxl_map_lpar()`, `pnv_ocxl_unmap_lpar()`, and `pnv_ocxl_tlb_invalidate()`. `pnv_ocxl_fixup_actag()` is a PCI fixup that gathers desired actag counts during enumeration.

Control flow: a PCI header fixup identifies NPU OCAPI PHBs, reads IBM DVSEC AFU metadata, accumulates desired actags per function in shared `npu_link` entries, and later `assign_actags()` prorates the 64 Power9 actags across functions. Driver-facing calls return actag/PASID values, hard-coded TL capabilities, configure TL via OPAL, map DT-described XSL MMIO registers, set up SPA through OPAL, map LPAR ATSD registers, and issue ATSD invalidations by programming MMIO and polling status.

State and persistence: `links_list` stores per-link actag accounting protected by `links_list_lock`; SPA setup stores PHB OPAL ID and BDFN in caller-owned platform data. No persistent storage.

Dependencies and integration points: depends on PCI DVSEC config space, `struct pnv_phb`, OPAL NPU calls, OpenCAPI config definitions, device-tree properties such as `ibm,opal-xsl-irq`, `ibm,opal-xsl-mmio`, and PHB `ibm,mmio-atsd`, plus exported OCXL base-driver interfaces.

Risks: actag fairness depends on fixups having seen all functions before drivers query. Only one AFU-carrying function is effectively supported for PASID count. ATSD invalidation uses polling with timeout and direct MMIO bitfield programming. Hard-coded Power9 TL capabilities are not generic to future NPUs.

Test signals: multi-function OpenCAPI adapter enumeration, actag allocation under overcommit, PASID query, TL setup OPAL call success, XSL IRQ/MMIO DT parsing, SPA setup/release, LPAR mapping, and ATSD invalidation timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/ocxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-async.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-async.c

Purpose: manages OPAL asynchronous operation tokens and completion delivery through OPAL message notifiers.

Important APIs/types/functions: `enum opal_async_token_state` tracks unallocated, allocated, dispatched, abandoned, and completed tokens. Exported APIs are `opal_async_get_token_interruptible()`, `opal_async_release_token()`, `opal_async_wait_response()`, and `opal_async_wait_response_interruptible()`. `opal_async_comp_event()` handles `OPAL_MSG_ASYNC_COMP` messages, and `opal_async_comp_init()` initializes token count from device tree.

Control flow: init reads `/ibm,opal` property `opal-msg-async-num`, allocates the token array, registers a notifier, and initializes a semaphore to the token count. Token allocation waits on the semaphore then marks a free token allocated under spinlock. Callers issuing an OPAL async call must wait at least once after `OPAL_ASYNC_COMPLETION`; interruptible wait marks an allocated token dispatched so signal-aborted callers can safely release it. Completion messages mark tokens completed, copy the response, wake waiters, or free abandoned tokens.

State and persistence: state is an in-memory token array, semaphore, waitqueue, and completion spinlock. No persistent state.

Dependencies and integration points: depends on OPAL message infrastructure, `opal_wake_poller()`, device tree, waitqueues, semaphores, and clients of async OPAL calls.

Risks: completion handler trusts firmware token values and indexes the token array after parsing the message. Caller ordering is strict: if an async OPAL call completes asynchronously, the caller must wait before further async token operations. Abandoned-token handling prevents leaks after interruptible waits but is sensitive to state transitions.

Test signals: concurrent token exhaustion, signal-interrupted waits, abandoned completion freeing, notifier registration failure, invalid token argument checks, and OPAL async clients receiving response payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-call.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-call.c

Purpose: central low-level wrapper layer for OPAL firmware calls, including interrupt masking, real-mode handling, and optional tracepoints.

Important APIs/functions: `opal_call()` wraps the assembly `__opal_call()`. The `OPAL_CALL(name, opcode)` macro generates a large set of typed eight-argument firmware call entry points such as console, RTC, PCI/EEH, dump, elog, flash, HMI, NPU, XIVE, sensor, MPIPL, secure variable, and powercap calls. With tracepoints enabled, `opal_tracepoint_regfunc()`, `opal_tracepoint_unregfunc()`, `__trace_opal_entry()`, and `__trace_opal_exit()` manage a static key and recursion guard.

Control flow: `opal_call()` records SRR register clobbering, disables external interrupts in the MSR, calls firmware directly when already running with MMU off, otherwise saves local flags, hard-disables interrupts, optionally emits tracepoint entry/exit around `__opal_call()`, then restores flags. Generated wrappers only bind a function name to an OPAL opcode.

State and persistence: per-CPU `opal_trace_depth` prevents recursive trace emission. A static branch controls tracing overhead. No persistent data is written.

Dependencies and integration points: depends on OPAL ABI opcode definitions, assembly prototypes, interrupt/MSR helpers, tracepoint definitions, and every PowerNV subsystem that invokes OPAL.

Risks: this is a critical firmware ABI boundary. Interrupt and MMU state handling must match OPAL requirements. Tracepoints can themselves cause OPAL calls, so recursion protection is required. A wrong opcode mapping misroutes firmware operations globally.

Test signals: boot-time OPAL calls, ftrace/tracepoint enable-disable, no recursion warnings, OPAL consumers across PCI/RTC/console/dump paths, and real-mode callers that skip virtual-mode interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-core.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-core.c

Purpose: exports preserved OPAL firmware memory and CPU state from MPIPL as an ELF core file under sysfs.

Important APIs/types/functions: `struct opalcore_config` tracks CPU count, crashing PIR, CPU state buffer, PT_LOAD regions, ELF buffer, and file size. `create_opalcore()` builds ELF headers, PT_NOTE, and PT_LOAD descriptors. `read_opalcore()` serves the bin attribute. `opalcore_config_init()` discovers OPAL/CPU metadata via MPIPL tags. `release_core_store()` lets userspace release the exported core.

Control flow: `opalcore_init()` runs as an fs initcall, queries `/ibm,opal/dump` for MPIPL boot, retrieves OPAL and CPU metadata tags, parses region lists, validates CPU state layout, allocates a header buffer, builds ELF notes from HDAT register entries using `opal_fadump_read_regs()`, appends AUXV with OPAL entry point, creates `/sys/firmware/opal/mpipl/core`, and adds a compatibility symlink from the old location. Reads copy the header/note buffer first and then preserved OPAL memory via `__va()`.

State and persistence: global `oc_conf`, `opalcore_list`, OPAL metadata pointers, `mpipl_kobj`, and `kernel_initiated` persist until release or exit cleanup. Userspace can free memory by writing `1` to `release_core`.

Dependencies and integration points: integrates with OPAL MPIPL tags, sysfs/kobjects, ELF core note formats, FADump register parsing helpers, device-tree OPAL properties, and `/sys/firmware/opal`.

Risks: file correctness depends on firmware metadata versions, endian conversions, region counts capped by `MAX_PT_LOAD_CNT`, and preserved memory still being mapped. Cleanup has to remove sysfs files before freeing buffers. GDB interpretation relies on first `NT_PRSTATUS` representing the crashing CPU.

Test signals: MPIPL boot with OPAL metadata, valid ELF headers from sysfs `core`, GDB/core parsing, `release_core` cleanup, metadata version mismatch warnings, and behavior when CPU metadata is invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-dump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-dump.c

Purpose: exposes OPAL platform dumps through `/sys/firmware/opal/dump`, including dump initiation, retrieval, and acknowledgement.

Important APIs/types/functions: `struct dump_obj` backs each dump kobject and binary `dump` file. `dump_read_info()` queries dump ID/size/type, preferring `opal_dump_info2()`. `dump_read_data()` allocates a vmalloc buffer, builds an OPAL scatter-gather list, and calls `opal_dump_read()`. `process_dump()` is the threaded IRQ handler. `opal_platform_dump_init()` creates sysfs and requests the OPAL dump event IRQ.

Control flow: init checks firmware token `OPAL_DUMP_READ`, creates the `dump` kset, adds an `initiate_dump` attribute, requests `OPAL_EVENT_DUMP_AVAIL`, and asks firmware to resend pending notifications when supported. On event, the handler reads dump metadata, deduplicates by name, and creates a kobject named by type and ID. Userspace reads the binary dump file; data is fetched lazily on first read and retained until acknowledge. Writing acknowledge removes the attribute, sends `opal_dump_ack()`, and drops the kobject.

State and persistence: each dump object holds ID/type/size and an in-memory buffer until acknowledged. The firmware dump remains pending until ack. Kernel state is sysfs/kobject based.

Dependencies and integration points: depends on OPAL dump calls, OPAL event IRQ mapping, ksets/sysfs binary attributes, vmalloc SG helpers, and userspace dump daemons.

Risks: sysfs object lifetime is explicitly guarded by extra kobject references to avoid read/acknowledge vs uevent races. Partial dump reads return `-EIO` and rely on userspace retry. Large dumps allocate vmalloc memory and retain it.

Test signals: firmware dump notification, duplicate event deduplication, binary read, partial-read retry, acknowledge removal and firmware ack, initiate FSP dump, and uevent ordering under fast userspace consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-elog.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-elog.c

Purpose: exposes OPAL error logs as sysfs kobjects and raw binary files for userspace collection and acknowledgement.

Important APIs/types/functions: `struct elog_obj` stores log ID/type/size and buffer. `elog_event()` handles OPAL error-log event IRQs. `create_elog_obj()` creates a kobject named by log ID and a read-only `raw` bin file. `raw_attr_read()` fetches or retries the log payload using `opal_read_elog()`. `opal_elog_init()` installs the interface.

Control flow: init checks `OPAL_ELOG_READ`, creates `/sys/firmware/opal/elog`, requests `OPAL_EVENT_ERROR_LOG_AVAIL`, and asks firmware to resend pending logs if supported. On an event, it calls `opal_get_elog_size()`, clamps size to 16 KiB, deduplicates by log ID, creates an object, prefetches the payload when possible, and sends a uevent. Userspace reads `raw` and writes `acknowledge`; the store path removes the acknowledge file, calls `opal_send_ack_elog()`, and releases the kobject.

State and persistence: per-log kernel objects and buffers persist until acknowledged. Firmware persistence of logs is released only after ack.

Dependencies and integration points: OPAL elog calls, OPAL event IRQs, sysfs/kobject bin attributes, userspace log daemon behavior, and endian conversion of firmware metadata.

Risks: object lifetime races are handled similarly to dumps with extra references around bin-file creation and uevent. Oversized firmware-reported logs are clamped with a warning. Failed prefetch falls back to lazy read retry, but repeated failures expose `-EIO`.

Test signals: pending log resend at boot, event-driven log creation, duplicate event handling, raw read, ack removal and firmware ack, clamp behavior for oversized logs, and uevent race stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-elog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.c

Purpose: implements OPAL-backed firmware-assisted dump registration, preservation, crash processing, CPU note construction, and MPIPL trigger behavior for PowerNV.

Important APIs/functions: `opal_fadump_dt_scan()` discovers support and active dumps. `opal_fadump_init_mem_struct()`, `opal_fadump_setup_metadata()`, `opal_fadump_register()`, `opal_fadump_unregister()`, `opal_fadump_invalidate()`, `opal_fadump_process()`, `opal_fadump_region_show()`, and `opal_fadump_trigger()` populate `struct fadump_ops`. Under `CONFIG_PRESERVE_FA_DUMP`, `opal_fadump_dt_scan()` only preserves memory above the firmware boot-memory tag.

Control flow: normal build scans `/ibm,opal/dump`, validates firmware load areas against `OPAL_FADUMP_MIN_BOOT_MEM`, sets FADump support and max copy size, detects MPIPL boot, retrieves kernel and CPU metadata tags, validates metadata version/registered regions, marks dump active, and reconstructs boot memory configuration. Registration initializes kernel metadata in reserved dump memory, registers firmware tags, and adds each boot memory range through `opal_mpipl_update(OPAL_MPIPL_ADD_RANGE)`. Processing reads crash header and firmware CPU state, builds ELF notes from HDAT register entries, and updates the vmcore header. Trigger records crashing PIR and requests `OPAL_REBOOT_MPIPL`.

State and persistence: metadata is deliberately placed in reserved memory and registered with OPAL so the capture kernel can retrieve it. Runtime globals track active kernel metadata, CPU metadata, and the writable metadata structure.

Dependencies and integration points: generic FADump internals, OPAL MPIPL APIs, flat device tree scanning, crash dump/vmcore note helpers, `opal-fadump.h` HDAT parsing, and optional OPAL core export via `kernel_initiated`.

Risks: metadata format/version mismatch can corrupt vmcore interpretation. Partial registration is accepted on `OPAL_RESOURCE` but warns about unsaved regions. CPU-state fallback may include only crashing CPU registers. The preserve-only build has different semantics and must not invalidate preserved memory.

Test signals: FADump registration/unregistration, MPIPL crash and capture boot, vmcore CPU notes, preserve mode memory reservation, region display output, firmware load-area rejection, and invalid CPU metadata fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.h

Purpose: defines OPAL FADump metadata and HDAT CPU register parsing helpers shared by OPAL FADump and OPAL core export code.

Important APIs/types: `OPAL_FADUMP_MIN_BOOT_MEM` enforces a minimum boot memory boundary. `struct opal_fadump_mem_struct` is the kernel metadata structure registered with firmware and later consumed by a capture kernel. `struct hdat_fadump_thread_hdr` and `struct hdat_fadump_reg_entry` describe firmware-provided CPU state data. Inline helpers `opal_fadump_set_regval_regnum()` and `opal_fadump_read_regs()` translate HDAT register entries into `struct pt_regs`.

Control flow: `opal_fadump_read_regs()` zeroes a `pt_regs`, walks fixed-size register entries, optionally endian-converts register values, and delegates register assignment. GPR entries fill `gpr[0..31]`; selected SPR IDs fill CTR, LR, XER, DAR, DSISR, NIP, MSR, and CCR.

State and persistence: the header describes persistent reserved-memory metadata but does not allocate or write it by itself.

Dependencies and integration points: depends on OPAL MPIPL region structures, FADump limits, `struct pt_regs`, and SPR number definitions. Used by `opal-fadump.c` and `opal-core.c`.

Risks: only known registers are mapped; unknown firmware entries are ignored. The `cpu_endian` parameter is essential because different consumers pass data with different endian expectations. Metadata layout is packed and firmware ABI-sensitive.

Test signals: vmcore and OPAL core register notes showing correct NIP/MSR/GPRs, mixed GPR/SPR HDAT entries, inactive core skipping by callers, and compatibility with newer metadata versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-fadump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-flash.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-flash.c

Purpose: implements the sysfs firmware update interface for OPAL-managed PowerNV firmware images.

Important APIs/types/functions: global structures track candidate `image_data`, `validate_flash_data`, `manage_flash_data`, and `update_flash_data`. Sysfs files are `image` (binary write), `validate_flash`, `manage_flash`, and `update_flash`. Important functions include `image_data_write()`, `alloc_image_buf()`, `free_image_buf()`, `opal_flash_validate()`, `opal_flash_manage()`, `opal_flash_update()`, `opal_flash_update_print_message()`, and `opal_flash_update_init()`.

Control flow: init checks `OPAL_FLASH_VALIDATE`, allocates a 4 KiB validation buffer, creates sysfs files under `/sys/firmware/opal`, and initializes statuses. Userspace writes the firmware image to `image`; the first write parses the header for total size, allocates a vmalloc buffer, pins pages with `SetPageReserved`, and subsequent writes fill the buffer until ready. `validate_flash` copies the first 4 KiB and invokes OPAL validation. `manage_flash` commits or rejects temporary firmware sides. `update_flash` initiates or cancels update; initiating builds an OPAL SG list and calls `opal_update_flash()`. Reboot path prints warning messages when an update is pending.

State and persistence: candidate image and status values persist in kernel memory until replaced, freed, or rebooted. Firmware update state persists in OPAL once initiated. Mutex `image_data_mutex` serializes image operations.

Dependencies and integration points: depends on OPAL flash calls, sysfs/kobject infrastructure, vmalloc SG helpers, reboot messaging, and userspace firmware update tooling.

Risks: privileged sysfs writes can stage firmware updates. Image size is trusted from header after bounds checks and capped at 1 GiB. Page reservation and SG-list handling must match OPAL expectations. Status fields are reset on some reads, making userspace ordering observable.

Test signals: sysfs file creation, invalid/short/oversized image rejection, chunked image writes, validation status/result text, update cancel/init paths, manage commit/reject, reboot warning output, and memory cleanup on replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-hmi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-hmi.c

Purpose: handles OPAL Hypervisor Maintenance Interrupt event messages, logs detailed checkstop/recovery information, and triggers platform reboot on unrecoverable events.

Important APIs/types/functions: `struct OpalHmiEvtNode` queues copied HMI events. `print_hmi_event_info()` formats severity, disposition, HMER/TFMR, and event detail. `print_core_checkstop_reason()`, `print_nx_checkstop_reason()`, and `print_npu_checkstop_reason()` decode malfunction alert reason fields. `opal_handle_hmi_event()` is the OPAL message notifier. `hmi_event_handler()` processes queued work. `opal_hmi_handler_init()` registers the notifier.

Control flow: init registers for `OPAL_MSG_HMI_EVT` once. The notifier runs in message context, copies event data into a GFP_ATOMIC node, appends it to a spinlock-protected list, and schedules work. The workqueue drains events, prints details, remembers whether any disposition is unrecovered, and if so drains additional HMI messages directly from OPAL before calling `pnv_platform_error_reboot()`.

State and persistence: global queue `opal_hmi_evt_list`, spinlock, work item, and init guard are runtime-only. No persistent state is written.

Dependencies and integration points: depends on OPAL message notifier infrastructure, OPAL HMI event ABI, ratelimited printk, PowerNV platform reboot/error handling, and checkstop reason constants from OPAL headers.

Risks: unrecovered HMI events intentionally lead to platform error reboot. Event copies assume OPAL message parameters contain a complete `struct OpalHMIEvent`. Logging is ratelimited for harmless events but fatal paths drain all queued firmware messages before reboot. Allocation failure drops event detail.

Test signals: notifier registration, recovered and unrecovered HMI injection, checkstop reason decoding for core/NX/NPU, ratelimit behavior for harmless events, workqueue ordering, and reboot path on unrecovered disposition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-hmi.c -->
