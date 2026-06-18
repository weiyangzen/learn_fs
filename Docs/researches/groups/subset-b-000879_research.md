# subset-b-000879 APIC Source Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic.c

## Purpose
This is the central local APIC implementation for x86. It initializes and tears down the LAPIC, selects interrupt delivery mode, configures BSP/AP setup, calibrates and registers the LAPIC clockevent, handles local APIC timer/spurious/error vectors, manages x2APIC enablement, composes x86 MSI messages, and preserves LAPIC state across suspend/resume. It is the coordinating layer between APIC driver callbacks, IO-APIC routing, IRQ remapping, timer infrastructure, CPU topology, and platform firmware.

## Important APIs, Types, And Functions
Global state includes `boot_cpu_physical_apicid`, `boot_cpu_apic_version`, `apic_is_disabled`, `apic_intr_mode`, `x2apic_mode`, `lapic_timer_period`, `apic_mmio_base`, `pic_mode`, and `smp_found_config`. Public or cross-file functions include `lapic_get_maxlvt()`, `setup_APIC_eilvt()`, `setup_boot_APIC_clock()`, `setup_secondary_APIC_clock()`, `clear_local_APIC()`, `apic_soft_disable()`, `disable_local_APIC()`, `lapic_shutdown()`, `apic_intr_mode_select()`, `apic_intr_mode_init()`, `apic_ap_setup()`, `x2apic_setup()`, `enable_IR_x2apic()`, `init_apic_mappings()`, `register_lapic_address()`, `disconnect_bsp_APIC()`, `__irq_msi_compose_msg()`, and `x86_msi_msg_get_destid()`. The file also declares IDT entries for timer, spurious, and error vectors.

## Control Flow
Boot begins with command-line parsing (`lapic`, `nolapic`, `noapictimer`, `nox2apic`, `apic_extnmi`, verbosity knobs), APIC mapping via `init_apic_mappings()`/`register_lapic_address()`, and interrupt mode selection through `apic_intr_mode_select()`. `apic_intr_mode_init()` probes the active APIC backend, runs platform post-init hooks, then calls `apic_bsp_setup()`, which connects the BSP APIC, optionally forces UP topology, initializes the local APIC, enables/sets up IO-APIC, enables IRQ remapping fault handling, and updates legacy vectors. APs call `apic_ap_setup()`.

Timer setup uses `apic_validate_deadline_timer()`, `calibrate_APIC_clock()`, and `setup_APIC_timer()`. Non-deadline mode calibrates the LAPIC bus timer against jiffies/TSC and optionally PM timer, then registers a per-CPU `clock_event_device`; deadline mode uses `MSR_IA32_TSC_DEADLINE` and TSC frequency. Runtime interrupts enter `sysvec_apic_timer_interrupt()`, `sysvec_spurious_apic_interrupt()`, `spurious_interrupt()`, or `sysvec_error_interrupt()`.

## State And Persistence
Most boot configuration is `__ro_after_init`; timer calibration writes `lapic_timer_period`; x2APIC mode uses `x2apic_state` and `x2apic_mode`; EILVT reservations are tracked in atomic `eilvt_offsets`. Suspend/resume persists LAPIC register values in `apic_pm_state`, masks IO-APIC/PIC paths while restoring, and reenables IRQ remapping. Resource state is published via the `lapic_resource` late initcall.

## Dependencies And Integration Points
This file depends on `struct apic` callbacks, IO-APIC helpers (`enable_IO_APIC()`, `setup_IO_APIC()`, `mask_ioapic_entries()`), irq-remapping APIs, x86 topology registration, clockevents, ACPI PM timer, PIT/HPET availability, MCE/perf hooks, DMI quirks, syscore PM, and hypervisor hooks for x2APIC/MSI extended destination IDs. `__irq_msi_compose_msg()` is consumed by MSI, IO-APIC, DMAR, and vector-domain code.

## Risks
The highest-risk areas are hardware errata workarounds: TSC-deadline microcode filtering, LAPIC timer shutdown with counter zeroing, ISR cleanup after crash kernels, 82489DX/old APIC behavior, x2APIC disable restrictions for large APIC IDs or locked hardware, and suspend/resume ordering. Mistakes can cause lost interrupts, stuck level IRQs, bad CPU affinity, boot hangs, or unusable timers. Command-line parsing also changes global hardware policy very early.

## Test Signals
Useful signals include boot logs for APIC mode selection, `TSC deadline timer available`, LAPIC timer calibration messages, x2APIC enable/disable logs, IRQ remapping logs, spurious/error APIC counters, suspend/resume interrupt delivery, CPU hotplug AP startup, timer tick stability, MSI routing to high APIC IDs, and boot combinations with `nolapic`, `noapictimer`, `nox2apic`, `apic=verbose/debug`, and `apic_extnmi=`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_common.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_common.c

## Purpose
This file contains small common helpers shared by APIC driver implementations. It abstracts basic APIC ID calculation and logical destination register initialization so 32-bit, xAPIC, x2APIC, flat, physical, and specialized backends can reuse consistent mappings.

## Important APIs, Types, And Functions
`apic_default_calc_apicid(cpu)` returns `per_cpu(x86_cpu_to_apicid, cpu)` for physical destination mode. `apic_flat_calc_apicid(cpu)` returns `1U << cpu` for classic flat logical mode. `default_cpu_present_to_apicid(mps_cpu)` exports a KVM-visible helper that maps a present Linux CPU number to the recorded APIC ID or `BAD_APICID`. `default_init_apic_ldr()` programs `APIC_DFR` to flat mode and writes a per-CPU logical APIC ID into `APIC_LDR`.

## Control Flow
APIC driver structs install these helpers in their callback tables. During local APIC setup, `setup_local_APIC()` calls `apic->init_apic_ldr()` when present, which for logical flat drivers routes here. Vector and MSI code calls `apic->calc_dest_apicid()` to convert a target CPU into the destination ID encoded into an interrupt message or route entry.

## State And Persistence
The file does not own persistent structures. It reads per-CPU `x86_cpu_to_apicid`, `cpu_present()`, and `nr_cpu_ids`, and it mutates APIC hardware registers `APIC_DFR` and `APIC_LDR` through the active APIC accessors.

## Dependencies And Integration Points
It depends on `asm/apic.h`, per-CPU topology state, and local APIC register read/write callbacks. It integrates with APIC backend definitions in `probe_32.c`, `apic_flat_64.c`, `x2apic_*`, and platform-specific drivers such as Numachip.

## Risks
The logic is small, but the destination ID calculation must match the backend's destination mode. Using flat logical IDs on a physical-mode APIC, or vice versa, would route IPIs/MSIs incorrectly. `default_init_apic_ldr()` assumes classic flat xAPIC semantics and is unsuitable for x2APIC cluster/physical drivers.

## Test Signals
Confirm APIC driver selection logs, successful SMP boot, IPI delivery, and correct `/proc/interrupts` distribution. For flat logical mode, inspect APIC debug dumps for expected DFR/LDR values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_flat_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_flat_64.c

## Purpose
This is the default 64-bit physical-flat xAPIC driver. It provides a `struct apic` backend for systems using memory-mapped APIC registers and physical destination mode, and it is the initial global `apic` pointer on x86-64 before probing may switch to another driver.

## Important APIs, Types, And Functions
`physflat_get_apic_id()` extracts the 8-bit APIC ID from the APIC ID register. `physflat_probe()` and `physflat_acpi_madt_oem_check()` always accept, making this a safe fallback. The `apic_physflat` driver sets physical destination mode, `max_apic_id = 0xFE`, physical IPI helpers, native MMIO read/write/EOI, native ICR access, and memory-mode ICR wait functions. `apic_driver(apic_physflat)` registers it, and `struct apic *apic` is initialized to it.

## Control Flow
During `x86_64_probe_apic()`, this driver can be selected if no more specific x2APIC or platform driver wins. Once installed, generic APIC calls are static-call patched by `init.c`, so IPI, register access, and EOI operations dispatch to the physical-flat callbacks.

## State And Persistence
The file owns no dynamic state except the global `apic` pointer default. The driver struct is `__ro_after_init`, so callback configuration becomes read-only after initialization.

## Dependencies And Integration Points
It depends on shared helpers from `apic_common.c` and `ipi.c`, native APIC MMIO accessors from the architecture APIC layer, and the APIC driver linker section. It integrates with local APIC setup, vector allocation, MSI composition, and SMP IPI delivery through `struct apic`.

## Risks
Because `probe()` always succeeds, driver ordering matters: this fallback must not preempt more specific drivers. Its 8-bit destination limit means it is unsuitable for systems requiring x2APIC extended IDs unless another driver replaces it. Incorrect fallback use could cap CPU enumeration or misroute interrupts on large systems.

## Test Signals
Boot logs should show `Switched APIC routing to: physical flat` when this driver is selected. SMP bring-up, IPIs, timer interrupts, and MSI affinity changes validate the callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_flat_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_noop.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_noop.c

## Purpose
This file defines the no-op APIC backend used when APIC support is disabled or unavailable. It lets generic APIC call sites continue to invoke callbacks without scattering APIC-disabled conditionals through low-level interrupt code.

## Important APIs, Types, And Functions
The file provides empty IPI senders, an ICR writer that drops writes, an ICR reader returning zero, `noop_get_apic_id()`, `noop_apic_eoi()`, and a secondary CPU wakeup function returning failure. `noop_apic_read()` and `noop_apic_write()` warn if hardware APIC support appears present and APIC is not explicitly disabled. `apic_noop` is a full `struct apic` instance using logical destination defaults and shared CPU-to-APIC helpers.

## Control Flow
`apic.c` calls `apic_disable()` to install `apic_noop` when APIC facilities are disabled during early mapping/detection. After installation, static calls are updated by `apic_install_driver()` so later APIC operations become harmless no-ops.

## State And Persistence
The driver has no mutable runtime state. Its warning behavior depends on `boot_cpu_has(X86_FEATURE_APIC)` and `apic_is_disabled`.

## Dependencies And Integration Points
It integrates with the APIC driver switch mechanism in `init.c` and provides the fallback implementation for APIC read/write, EOI, IPI, ICR, and CPU wakeup callbacks. It depends on common APIC ID helpers and x86 feature flags.

## Risks
The no-op backend hides APIC hardware access, so accidental installation on systems that require APIC can leave interrupts, timers, IPIs, CPU bring-up, and MSI routing nonfunctional. The read/write warnings are useful but only catch some incorrect call paths. Wakeup always fails, so SMP boot must not depend on this driver.

## Test Signals
Boot with `nolapic` or configurations without APIC should not crash due to APIC call sites. Logs should show APIC-disabled mode, no unexpected `WARN_ON_ONCE` from noop reads/writes, and expected loss or fallback of APIC-dependent capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_noop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_numachip.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_numachip.c

## Purpose
This file implements APIC backends for Numascale NumaConnect and NumaConnect2 systems. These systems need nonstandard APIC ID extraction and remote IPI delivery through Numachip local CSR registers when targets are outside the local APIC ID segment.

## Important APIs, Types, And Functions
Global `numachip_system` records detected generation. `numachip1_get_apic_id()` and `numachip2_get_apic_id()` derive extended APIC IDs from AMD node/MMIO configuration MSRs. `numachip1_apic_icr_write()` and `numachip2_apic_icr_write()` write generation-specific CSR interrupt generation registers. `numachip_wakeup_secondary()` sends INIT/SIPI through the CSR path. IPI helpers choose local APIC delivery when the target is local to the Numachip segment and CSR delivery otherwise. Two `struct apic` drivers, `apic_numachip1` and `apic_numachip2`, register with OEM MADT checks.

## Control Flow
ACPI MADT OEM matching sets `numachip_system`. The early initcall `numachip_system_init()` maps LCSR space, selects the CSR writer, installs CPU topology fixups, and overrides PCI arch initialization. APIC probing then selects the matching driver. During IPI delivery, `numachip_send_IPI_one()` compares local and destination APIC IDs; local targets use standard physical ICR writes, remote targets use the Numachip CSR generator.

## State And Persistence
The persistent state is the generation flag and the selected `numachip_apic_icr_write` function pointer. CPU topology is adjusted through `x86_cpuinit.fixup_cpu_id`, setting LLC and package IDs based on node topology. LCSR mappings persist for the kernel lifetime.

## Dependencies And Integration Points
It depends on Numachip CSR/MSR definitions, AMD topology MSRs, early extra UC mappings, APIC common helpers, native APIC MMIO accessors, and x86 PCI init hooks. It integrates with APIC driver selection through MADT OEM IDs `NUMASC/NCONNECT` and `NUMASC/NCONECT2`.

## Risks
Wrong generation detection or CSR formatting would break remote IPIs and AP startup. Topology fixups influence scheduler/cache/package decisions. The local-vs-remote decision depends on `NUMACHIP_LAPIC_BITS`; mismatch with hardware APIC ID layout can route interrupts incorrectly. The driver assumes CSR space is mapped before remote IPI use.

## Test Signals
Boot logs should identify NumaConnect generation and APIC routing. Validate AP startup, remote IPI delivery, NMI delivery, CPU topology/package IDs, PCI init behavior, and interrupt distribution across remote nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_numachip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/hw_nmi.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/hw_nmi.c

## Purpose
This file provides APIC-backed hardware NMI watchdog support and architecture backtrace triggering. It bridges generic NMI watchdog/backtrace code to x86 APIC NMI IPI delivery.

## Important APIs, Types, And Functions
When `CONFIG_HARDLOCKUP_DETECTOR_PERF` is enabled, `hw_nmi_get_sample_period(watchdog_thresh)` computes a perf NMI sample period from `cpu_khz`. When architecture backtrace triggering is enabled, `arch_trigger_cpumask_backtrace(mask, exclude_cpu)` invokes `nmi_trigger_cpumask_backtrace()` using `nmi_raise_cpu_backtrace()`, which sends `NMI_VECTOR` to the requested CPUs via `__apic_send_IPI_mask()`. `nmi_cpu_backtrace_handler()` delegates to `nmi_cpu_backtrace()` and is registered as an `NMI_LOCAL` handler at early init.

## Control Flow
Backtrace requests from generic NMI code enter `arch_trigger_cpumask_backtrace()`, which supplies the APIC NMI raiser callback. Incoming local NMIs run the registered handler and either report a CPU backtrace or return `NMI_DONE`.

## State And Persistence
This file owns no persistent state beyond NMI handler registration. It reads `cpu_khz` and uses the APIC IPI path for delivery.

## Dependencies And Integration Points
It depends on generic NMI watchdog APIs, notifier/NMI registration, APIC IPI helpers, kprobe safety annotations, and CPU masks. It integrates with hard-lockup detection, sysrq-style CPU backtraces, panic diagnostics, and APIC NMI delivery policy.

## Risks
NMI delivery is non-maskable and can run in fragile contexts. Incorrect cpumask handling can target wrong CPUs or miss backtraces. The sample-period calculation depends on a valid `cpu_khz`; stale or inaccurate CPU frequency affects watchdog cadence.

## Test Signals
Use hardlockup watchdog enablement, triggered CPU backtraces, panic-time NMI backtraces, and logs from `nmi_cpu_backtrace()` as signals. Validate that excluded CPUs are not targeted and that APIC NMI IPIs reach all requested online CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/hw_nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/init.c

## Purpose
This file initializes and updates APIC static calls. It lets the kernel route hot APIC operations through patched direct-call trampolines while still supporting runtime APIC driver installation and callback overrides from platform/hypervisor code.

## Important APIs, Types, And Functions
`DEFINE_APIC_CALL()` creates static-call slots for APIC callbacks such as `eoi`, `native_eoi`, `icr_read`, `icr_write`, `read`, IPI senders, `wait_icr_idle`, CPU wakeup, and `write`. `__x86_apic_override` holds optional callback overrides. `restore_override_callbacks()` reapplies overrides after driver switches. `update_static_calls()` patches static-call targets. `apic_setup_apic_calls()` initializes the default APIC static calls, and `apic_install_driver(driver)` switches the global APIC driver, handles `native_eoi`, applies overrides, updates static calls, and logs the selected backend.

## Control Flow
Early boot starts with a default `apic` pointer from the architecture probe file. `apic_setup_apic_calls()` initializes static calls once the default is usable. Later, APIC probe or forced disable paths call `apic_install_driver()`, which updates the global callback table and repatches all static calls so wrapper macros dispatch to the new backend.

## State And Persistence
The central state is the global `apic` pointer, the `__x86_apic_override` initdata object, and static-call patch state. Driver structs become read-only after init; overrides are applied before initdata goes away.

## Dependencies And Integration Points
It depends on Linux static calls and the APIC driver registry. Hypervisors or platform code can populate `__x86_apic_override`. All APIC users benefit indirectly because `apic_read()`, `apic_write()`, `apic_eoi()`, and IPI wrappers route through these patched callbacks.

## Risks
Static calls must be initialized before APIC wrappers are used in paths that assume non-null callbacks. Missing callbacks in a driver can become immediate crashes because wrappers intentionally avoid conditional calls for many operations. Preserving `native_eoi` is important for KVM/Hyper-V style EOI overrides.

## Test Signals
Boot should log `Static calls initialized` and `Switched APIC routing to: ...`. Validate APIC driver switches, hypervisor EOI overrides, IPI delivery, AP startup, and no null static-call faults during early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/io_apic.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/io_apic.c

## Purpose
This is the main IO-APIC implementation. It discovers/registers IO-APICs, maps their MMIO windows, saves/restores redirection entries, maps GSIs and MP/ACPI interrupt source records to Linux IRQs, creates hierarchical irqdomains, configures route entries, handles masking/unmasking/EOI/affinity, probes timer routing, and supports hotplug registration/unregistration.

## Important APIs, Types, And Functions
Core state includes `ioapics[]`, `nr_ioapics`, `gsi_top`, `mp_irqs[]`, `mp_irq_entries`, `ioapic_is_disabled`, `io_apic_irqs`, and `ioapic_dynirq_base`. Key structures are `irq_pin_list`, `mp_chip_data`, `mp_ioapic_gsi`, and per-IOAPIC `struct ioapic`. Externally relevant functions include `disable_ioapic_support()`, `mp_save_irq()`, `arch_early_ioapic_init()`, `native_io_apic_read()`, `clear_IO_APIC()`, `save_ioapic_entries()`, `mask_ioapic_entries()`, `restore_ioapic_entries()`, `acpi_get_override_irq()`, `ioapic_set_alloc_attr()`, `mp_map_gsi_to_irq()`, `mp_unmap_irq()`, `IO_APIC_get_PCI_irq_vector()`, `enable_IO_APIC()`, `restore_boot_irq_mode()`, `setup_IO_APIC()`, `io_apic_init_mappings()`, `ioapic_insert_resources()`, `mp_find_ioapic()`, `mp_find_ioapic_pin()`, `mp_register_ioapic()`, `mp_unregister_ioapic()`, and `mp_irqdomain_*`.

## Control Flow
Firmware parsers call `mp_register_ioapic()` and `mp_save_irq()` during enumeration. Early IRQ init allocates saved RTE storage. Mapping code creates fixmaps and resources. `enable_IO_APIC()` detects any ExtINT pin and clears all non-SMI RTEs. `setup_IO_APIC()` creates irqdomains, fixes IDs, syncs arbitration IDs, maps MP interrupt source pins, initializes traps, and verifies timer IRQ routing via `check_timer()`.

Runtime allocation maps GSIs through `mp_map_gsi_to_irq()`, which locates IO-APIC/pin, derives polarity/trigger attributes, allocates from the IO-APIC irqdomain, and configures `mp_chip_data`. Activation calls `ioapic_configure_entry()`, which asks the parent MSI/vector domain to compose a message and copies the resulting fields into the RTE. Affinity changes call the parent chip then rewrite the RTE. Level EOI handling uses local APIC TMR state and IO-APIC EOI or mask/edge/level simulation to clear remote IRR.

## State And Persistence
The file persists firmware routing records, IO-APIC hardware metadata, saved RTE snapshots for suspend/resume and IRQ remapping transitions, IRQ-to-pin lists for shared mappings, and per-IRQ route attributes. Syscore suspend/resume saves/restores RTEs and IO-APIC IDs. Hotplug registration updates `gsi_top`, fixmaps, resources, and irqdomains.

## Dependencies And Integration Points
It integrates with MP table/ACPI parsing, irqdomain hierarchy, vector domain, interrupt remapping, legacy PIC, LAPIC setup, PCI routing, HPET/timer code, syscore PM, memblock/fixmap/resource management, and confidential-computing MMIO encryption decisions.

## Risks
Risks concentrate around firmware quirks and interrupt races: broken MP tables, duplicate IO-APIC IDs, overlapping GSI ranges, remote-IRR not clearing, timer IRQ misrouting, non-atomic RTE updates, shared ISA pins, interrupt remapping transitions, and CPU affinity moves. Incorrect lock ordering around `ioapic_lock`/`ioapic_mutex` or route-entry write order can produce lost or stuck interrupts.

## Test Signals
Inspect `apic=debug` IO-APIC dumps, GSI-to-IRQ mappings, timer boot probes, `/proc/interrupts`, PCI MSI/MSI-X routing with and without IRQ remapping, suspend/resume, CPU hotplug, `noapic`, ACPI override behavior, and hotplug IO-APIC register/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/io_apic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/ipi.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/ipi.c

## Purpose
This file provides generic IPI delivery helpers for xAPIC-style APIC drivers and SMP call sites. It manages the optional IPI shorthand optimization and implements physical/logical APIC ICR writes for single, mask, all, all-but-self, and self IPIs.

## Important APIs, Types, And Functions
`apic_use_ipi_shorthand` is a static key controlling broadcast shorthand use. Boot option `no_ipi_broadcast=` sets `apic_ipi_shorthand_off`. SMP-facing functions include `apic_smt_update()`, `apic_send_IPI_allbutself()`, `native_smp_send_reschedule()`, `native_send_call_func_single_ipi()`, `native_send_call_func_ipi()`, and `apic_send_nmi_to_offline_cpu()`. Low-level helpers include `apic_mem_wait_icr_idle_timeout()`, `apic_mem_wait_icr_idle()`, `__default_send_IPI_dest_field()`, physical and logical mask senders, and shorthand senders.

## Control Flow
CPU topology changes call `apic_smt_update()` to enable shorthand only after all present CPUs have booted once and more than one CPU is online. Generic SMP reschedule/call-function paths invoke native send helpers, which choose APIC shorthand when safe or fall back to mask delivery. Driver structs in other files point their IPI callbacks at these helpers. Low-level send functions wait for ICR idle, write ICR2 for explicit destinations, then write ICR.

## State And Persistence
The persistent runtime state is the static key plus the boot option flag. Delivery uses per-CPU APIC IDs, online/present/booted-once masks, and APIC hardware ICR state.

## Dependencies And Integration Points
It depends on SMP CPU masks, `x86_cpu_to_apicid`, local APIC MMIO accessors, vector constants, and string-choice logging. It integrates with scheduler reschedule IPIs, generic call-function IPIs, NMI backtraces, APIC driver callback tables, and CPU hotplug state.

## Risks
IPI broadcast shorthand is unsafe before all present CPUs have initialized APIC state, especially for NMIs. ICR2 plus ICR writes must be protected from interruption for explicit destinations; the code uses IRQ save where needed. NMI sends use timeout waiting to avoid panic/kdump hangs.

## Test Signals
Signals include SMP boot, CPU hotplug toggling shorthand logs, scheduler reschedule IPIs, smp-call-function stress, NMI backtraces, panic stop-CPU behavior, and `no_ipi_broadcast=` boot variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/local.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/local.h

## Purpose
This private APIC header declares shared helpers used across the APIC subdirectory. It centralizes x2APIC helper declarations, IPI helper prototypes, local APIC logical initialization, and ICR preparation logic.

## Important APIs, Types, And Functions
It declares x2APIC functions (`x2apic_get_apic_id()`, `x2apic_send_IPI_all()`, `x2apic_send_IPI_allbutself()`, `x2apic_send_IPI_self()`), `x2apic_max_apicid`, and the `apic_use_ipi_shorthand` static key. `__prepare_ICR(shortcut, vector, dest)` constructs the APIC ICR low word, selecting fixed delivery by default and NMI delivery for `NMI_VECTOR`. Under `CONFIG_X86_X2APIC`, `__x2apic_send_IPI_dest()` writes x2APIC ICR MSRs. It also declares the common APIC LDR and default IPI helper functions.

## Control Flow
Driver files include this header to populate `struct apic` callbacks. IPI helpers call `__prepare_ICR()` before writing xAPIC or x2APIC ICRs. x2APIC drivers use `__x2apic_send_IPI_dest()` as their final send primitive.

## State And Persistence
The header owns no storage except declarations. Its inline helpers encode assumptions about ICR bit layout and delivery modes.

## Dependencies And Integration Points
It depends on `asm/irq_vectors.h`, `asm/apic.h`, and jump labels. It integrates `ipi.c`, `apic_common.c`, `x2apic_*`, `probe_32.c`, `apic_flat_64.c`, Numachip, and Secure AVIC driver code.

## Risks
Because `__prepare_ICR()` is shared by many send paths, a bug affects fixed and NMI IPI delivery broadly. The x2APIC inline write assumes callers apply any required WRMSR fences, which the x2APIC implementations do before calling it.

## Test Signals
Compile coverage across xAPIC/x2APIC and 32/64-bit configurations, IPI delivery tests, NMI sends, and APIC driver selection exercise this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/msi.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/msi.c

## Purpose
This file implements x86 APIC-backed MSI domain support for PCI MSI/MSI-X, DMAR/IOMMU MSI, and Xen MSI restore integration. It connects MSI allocation and affinity changes to the x86 vector domain and APIC message composition.

## Important APIs, Types, And Functions
`x86_pci_msi_default_domain` stores the default PCI MSI parent domain. `irq_msi_update_msg()` composes and writes an MSI message. `msi_set_affinity()` migrates MSI targets safely. `pci_dev_has_default_msi_parent_domain()` checks whether a PCI device uses the vector domain. `x86_msi_prepare()` initializes x86 allocation info for MSI/MSI-X. `x86_init_dev_msi_info()` configures child MSI domain info based on the real parent. `native_create_pci_msi_domain()` marks `x86_vector_domain` as an MSI parent, and `x86_create_pci_msi_domain()` invokes platform creation. Legacy exported `pci_msi_prepare()` remains for Hyper-V. DMAR support defines `dmar_msi_controller`, domain ops, `dmar_alloc_hwirq()`, and `dmar_free_hwirq()`.

## Control Flow
During initialization, the vector domain becomes an MSI parent and platform code creates the default PCI MSI domain. Device MSI allocation calls `x86_msi_prepare()` to set allocation type, then parent vector allocation assigns vectors and destination APIC IDs. Affinity changes call `msi_set_affinity()`, which asks the parent vector chip for a new target and rewrites MSI messages. For non-maskable non-remapped MSI moves with changed vector and CPU, it temporarily redirects to the new vector on the current CPU under `vector_lock`, then moves to the final CPU and retriggers if the local LAPIC IRR shows a raced interrupt.

## State And Persistence
The file persists the default MSI domain pointer and lazily creates a singleton DMAR MSI domain protected by a mutex. Per-interrupt state lives in parent `irq_cfg` and generic MSI descriptors.

## Dependencies And Integration Points
It depends on the vector domain, `__irq_msi_compose_msg()` from `apic.c`, IRQ remapping parent domains, PCI/MSI core, DMAR APIs, Xen initdom restore, and vector move helpers. DMAR composition uses high destination APIC ID bits specially.

## Risks
MSI address/data updates are not always atomic, so affinity migration can create rare stray interrupts; the local temporary-vector path mitigates this. Incorrect feature flag filtering can expose unsupported MSI domain capabilities. DMAR high-address destination encoding must not be used for ordinary MSI devices.

## Test Signals
Validate PCI MSI/MSI-X allocation, affinity changes under load, vector migration races, interrupt remapping on/off, DMAR fault interrupt allocation, Xen initial-domain MSI restore, and devices with/without maskable MSI support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_32.c

## Purpose
This file provides the generic 32-bit APIC driver and APIC probe layer. It supplies a default logical-flat APIC backend for up to classic xAPIC-era systems and handles the `apic=` command-line driver override.

## Important APIs, Types, And Functions
`default_get_apic_id()` extracts a 4-bit or 8-bit APIC ID depending on xAPIC/extended APIC ID support. `probe_default()` always succeeds as the fallback. `apic_default` is a logical-destination `struct apic` using `default_init_apic_ldr()`, flat APIC ID calculation, logical IPI mask helpers, native MMIO accessors, and ICR wait functions. The global `apic` pointer is initialized to `apic_default`. `parse_apic()` scans the APIC driver linker section for a named driver and installs it. `x86_32_probe_apic()` probes registered drivers unless the command line already selected one.

## Control Flow
Early `apic=` parsing can select a specific driver by name. Later, `x86_32_probe_apic()` iterates `__apicdrivers` and installs the first driver whose `probe()` succeeds. If no driver is found, it panics because APIC-enabled operation cannot proceed without callbacks.

## State And Persistence
`cmdline_apic` records whether a user-selected driver was installed. The `apic` pointer and driver struct become stable after probing and static-call update.

## Dependencies And Integration Points
It depends on APIC driver section ordering, native APIC MMIO helpers, shared logical-flat helpers, Xen/ACPI/IO-APIC headers, and the static-call update path in `init.c`. It integrates with early command-line parsing and 32-bit APIC setup.

## Risks
The default driver always succeeds, so ordering with more specialized 32-bit drivers matters. Command-line driver names must match exactly. Wrong APIC ID width selection could break systems with extended APIC IDs or old non-xAPIC hardware.

## Test Signals
Boot 32-bit kernels with default APIC selection and with explicit `apic=<driver>`. Validate APIC ID extraction, logical IPIs, SMP bring-up, and early panic absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_64.c

## Purpose
This file implements the 64-bit APIC probe layer. It enables interrupt remapping/x2APIC preparation, selects the best registered APIC backend, and supports ACPI MADT OEM-driven driver selection.

## Important APIs, Types, And Functions
`x86_64_probe_apic()` calls `enable_IR_x2apic()` and then iterates the APIC driver linker section, installing the first driver whose `probe()` callback succeeds. `default_acpi_madt_oem_check(oem_id, oem_table_id)` iterates drivers and installs the first whose OEM check matches.

## Control Flow
During APIC mode initialization, 64-bit setup invokes `x86_64_probe_apic()`. IRQ remapping and x2APIC state are prepared before driver probing so x2APIC drivers can observe `x2apic_mode`. Firmware parsing can call `default_acpi_madt_oem_check()` earlier to select platform-specific drivers such as Numachip or Secure AVIC.

## State And Persistence
The file owns no state directly. It mutates the global `apic` driver through `apic_install_driver()` and relies on global x2APIC/IRQ-remapping state from `apic.c`.

## Dependencies And Integration Points
It integrates APIC driver registration, ACPI MADT OEM matching, IRQ remapping setup, x2APIC enablement, and the static-call APIC dispatch path. Driver ordering determines fallback behavior.

## Risks
If `enable_IR_x2apic()` fails or changes mode unexpectedly, x2APIC-capable drivers may not probe. If no driver probe succeeds, the code silently leaves the existing default driver rather than explicitly panicking, so correctness relies on the default initialized in `apic_flat_64.c`.

## Test Signals
Boot logs for IRQ remapping/x2APIC enablement and `Switched APIC routing to:` identify selection. Test MADT OEM platform drivers, x2APIC physical/cluster modes, IRQ remapping failure fallback, and default physical-flat fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/probe_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/vector.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/vector.c

## Purpose
This file owns x86 local APIC interrupt vector allocation and the root vector irqdomain. It assigns vectors to IRQs, composes APIC MSI messages, manages vector migration and cleanup during affinity changes, reserves legacy/system vectors, handles CPU online/offline vector state, and provides APIC/PIC debug dumps.

## Important APIs, Types, And Functions
`struct apic_chip_data` stores per-IRQ vector, previous vector, target CPU, previous CPU, IRQ number, cleanup linkage, and reservation/managed flags. Global state includes `x86_vector_domain`, `vector_lock`, `vector_searchmask`, `vector_matrix`, and per-CPU cleanup timers. Important functions include `lock_vector_lock()`, `unlock_vector_lock()`, `init_irq_alloc_info()`, `copy_irq_alloc_info()`, `irqd_cfg()`, `irq_cfg()`, `lapic_assign_legacy_vector()`, `lapic_update_legacy_vectors()`, `lapic_assign_system_vectors()`, `arch_early_irq_init()`, `lapic_online()`, `lapic_offline()`, `vector_schedule_cleanup()`, `irq_complete_move()`, `lapic_can_unplug_cpu()`, and the `x86_vector_domain_ops`.

## Control Flow
`arch_early_irq_init()` creates the `VECTOR` irqdomain, makes it default, allocates the vector matrix, and initializes IO-APIC early state. Allocation through `x86_vector_alloc_irqs()` creates `apic_chip_data`, sets the APIC irq chip, handles legacy vectors specially, and either assigns or reserves vectors according to managed/reservation policy. Activation assigns real vectors for reserved or managed IRQs. Affinity changes allocate a new vector under `vector_lock`, update per-CPU `vector_irq`, and mark the old vector for deferred cleanup. The first interrupt on the new vector calls `irq_complete_move()`, scheduling cleanup on the previous CPU; a timer frees the old vector after checking IRR.

## State And Persistence
The vector matrix tracks available, reserved, managed, legacy, and system vectors. Per-IRQ chip data persists until IRQ free. Per-CPU `vector_irq[]` maps vectors to descriptors or sentinel states. Cleanup state persists in per-CPU hlist/timer objects. System and legacy vector reservations are established at boot and CPU-online time.

## Dependencies And Integration Points
It depends on generic irqdomain/irq_matrix APIs, local APIC register access, IO-APIC state (`io_apic_irqs`, `gsi_top`), interrupt remapping selection, legacy PIC, MSI message composition, CPU hotplug, SMP vector cleanup, debugfs, and APIC tracepoints. IO-APIC and MSI code use `irqd_cfg()` and vector-domain parent allocation.

## Risks
Vector migration is race-prone: stale vectors must not be freed until the new vector receives an interrupt or cleanup proves no pending IRR. CPU hotplug fixups can leave stale vectors if move completion is mishandled. Exhaustion of vector space affects IRQ affinity and CPU unplug safety. Incorrect legacy vector handling can break timer/PIC fallback.

## Test Signals
Use IRQ allocation/free stress, MSI affinity changes under interrupt load, CPU hotplug, managed IRQs with isolated CPUs, vector exhaustion scenarios, `/proc/interrupts`, debugfs irqdomain output, APIC tracepoints, and boot APIC/PIC dumps with `show_lapic=`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/vector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_cluster.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_cluster.c

## Purpose
This file implements the logical cluster x2APIC driver. It groups CPUs by x2APIC cluster, builds logical destination masks, and sends one IPI per cluster when possible for efficient large-system delivery.

## Important APIs, Types, And Functions
`apic_cluster(apicid)` derives the cluster from the APIC ID. `x86_cpu_to_logical_apicid` maps Linux CPU to logical x2APIC ID. Per-CPU `ipi_mask` is a scratch mask, and per-CPU `cluster_masks` points to the shared mask for that CPU's cluster. Key functions are `x2apic_send_IPI()`, `__x2apic_send_IPI_mask()`, `x2apic_calc_apicid()`, `init_x2apic_ldr()`, `prefill_clustermask()`, `alloc_clustermask()`, `x2apic_prepare_cpu()`, `x2apic_dead_cpu()`, and `x2apic_cluster_probe()`. The `apic_x2apic_cluster` driver uses logical destination mode and MSR APIC accessors.

## Control Flow
The driver probes only when `x2apic_mode` is active. Probe allocates the logical APIC ID array, registers a CPU hotplug prepare state, initializes the current CPU LDR state, and returns success. CPU prepare computes `(cluster << 16) | bit-within-cluster`, allocates or reuses a shared cluster mask, and allocates per-CPU scratch space. Mask IPI delivery copies the target mask, optionally removes self, collapses targets by shared cluster mask, ORs logical destination bits, and sends one x2APIC ICR per cluster.

## State And Persistence
The logical APIC ID array persists after probe. Cluster masks are dynamically allocated per cluster and reused across CPUs in the same cluster. CPU death clears the CPU from its cluster mask and frees scratch masks.

## Dependencies And Integration Points
It depends on CPU hotplug, cpumask allocation, x2APIC MSR ICR helper from `local.h`, `default_cpu_present_to_apicid()`, native x2APIC read/write/EOI callbacks, and APIC driver probing. It integrates with large-system IPI delivery and vector/MSI destination calculations through `calc_dest_apicid`.

## Risks
Cluster mask lifetime and sharing must be correct across boot and hotplug. Logical destination computation assumes 16 APIC IDs per cluster. Missing `weak_wrmsr_fence()` would violate x2APIC MSR ordering, but the send paths include it. Allocation failure during probe or CPU prepare disables or blocks this backend.

## Test Signals
Validate x2APIC cluster-mode boot, CPU hotplug, IPI delivery to masks spanning multiple clusters, NMI all-but-self, effective interrupt affinity, and logs showing cluster x2APIC routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_cluster.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_phys.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_phys.c

## Purpose
This file implements physical destination mode for x2APIC. It also owns the global x2APIC maximum APIC ID limit used when interrupt remapping or hypervisor constraints restrict addressable APIC IDs.

## Important APIs, Types, And Functions
`x2apic_phys` records forced physical mode from `x2apic_phys`. `x2apic_max_apicid` defaults to `UINT_MAX`. `x2apic_set_max_apicid(apicid)` updates the global limit and active driver limit when supported. `x2apic_fadt_phys()` checks ACPI FADT physical-mode requirement. IPI helpers send physical x2APIC IPIs to one CPU, masks, all, all-but-self, and self. `x2apic_get_apic_id()` returns the APIC ID unchanged. `apic_x2apic_phys` is the physical x2APIC driver.

## Control Flow
Early boot option `x2apic_phys` forces physical mode. Driver probe succeeds when x2APIC mode is active and either forced, required by FADT, or the active driver pointer already indicates physical x2APIC. Send paths use `weak_wrmsr_fence()` and write x2APIC ICRs with physical destination IDs. Shorthand all/all-but-self IPIs use destination shorthand.

## State And Persistence
Persistent state is the forced physical flag and maximum APIC ID limit. The APIC driver struct is read-only after init and exposes `x2apic_set_max_apicid` support so `apic.c` can clamp APIC IDs in non-remapped modes.

## Dependencies And Integration Points
It depends on ACPI FADT, x2APIC native MSR accessors, per-CPU physical APIC IDs, APIC driver probing, and x2APIC enablement policy in `apic.c`. It integrates with MSI/IO-APIC non-remapped destination limits.

## Risks
Without interrupt remapping, only addressable APIC IDs may receive IO-APIC/MSI interrupts; the limit must match hardware or hypervisor support. Physical mask delivery loops over CPUs and can be less efficient than cluster logical mode on large systems. FADT-forced mode must override cluster preference.

## Test Signals
Boot with `x2apic_phys`, ACPI FADT physical-mode systems, non-remapped x2APIC guests, large APIC ID limits, and IPI/mask delivery. Check selected routing log and interrupt affinity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_phys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_savic.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_savic.c

## Purpose
This file implements the Secure AVIC x2APIC backend for AMD SEV-SNP guests. Secure AVIC accelerates APIC state through per-vCPU backing pages and requires special handling for APIC register access, IPI injection, EOI, and hypervisor GPA registration.

## Important APIs, Types, And Functions
`struct secure_avic_page` defines a page-aligned APIC backing page, and per-CPU `savic_page` stores those pages. Register helpers read/write APIC bitmaps and vectors. `savic_read()` returns backing-page values for accelerated registers and GHCB MSR reads for nonaccelerated timer/LVT registers. `savic_write()` updates backing-page or GHCB state. `savic_icr_write()` emulates ICR delivery to self/all/all-but/destination, updates backing-page ICR state, and notifies the hypervisor when needed. IPI callbacks wrap this path. `savic_eoi()` clears ISR locally for edge interrupts or propagates EOI through GHCB for level interrupts. `savic_setup()` registers the backing page GPA and enables Secure AVIC; `savic_teardown()` disables it and unregisters GPA. `apic_x2apic_savic` is the driver.

## Control Flow
Probe requires `CC_ATTR_SNP_SECURE_AVIC`; if Secure AVIC is present without x2APIC mode, the guest terminates. Probe allocates per-CPU backing pages. Setup initializes APIC ID from the hypervisor-visible APIC MSR, registers the backing page GPA via GHCB, and writes `MSR_AMD64_SAVIC_CONTROL` with enable/allowed-NMI bits. Runtime reads/writes avoid expensive intercepted APIC MSRs by touching the backing page where allowed. IPI sends update target backing-page IRR or NMI request state and use GHCB notification for non-self destinations.

## State And Persistence
Per-CPU APIC backing pages persist while the driver is active and mirror APIC ISR/TMR/IRR/allowed-IRR and control registers. Secure AVIC enablement persists in `MSR_AMD64_SAVIC_CONTROL` until teardown. Vector updates maintain the `SAVIC_ALLOWED_IRR` bitmap through the APIC driver's `update_vector` callback.

## Dependencies And Integration Points
It depends on confidential-computing platform attributes, SEV/GHCB helpers, native x2APIC MSR operations for accelerated self IPI/EOI pieces, APIC bitmap helpers, and the generic APIC driver infrastructure. It integrates with vector allocation via `update_vector`, NMI/IPI delivery, local APIC setup/teardown, and SNP guest termination policy.

## Risks
The register allowlist is security- and correctness-sensitive: unknown or misaligned offsets are rejected/logged. Backing-page GPA registration must succeed before VMRUN or the guest cannot continue. EOI differs for level vs edge interrupts; wrong ISR/TMR handling can lose or repeat interrupts. Directly updating remote per-CPU backing pages assumes online CPU mappings and correct APIC ID-to-CPU association.

## Test Signals
Run under SEV-SNP Secure AVIC with x2APIC enabled. Validate setup GPA registration, local timer/LVT accesses, self and remote IPIs, NMI delivery, level-triggered IO-APIC/MSI behavior requiring propagated EOI, vector allocation updates in allowed IRR, CPU hotplug/teardown, and absence of unknown-register errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_savic.c -->
