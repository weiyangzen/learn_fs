# subset-b-000878 Research

Grouped source research for subset B work item `subset-b-000878`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/boot.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/boot.c

## Purpose
`boot.c` is the x86 architecture ACPI boot integration layer. It maps early ACPI tables, interprets MADT/FADT/HPET/BOOT/BGRT/SPCR data, chooses the IRQ routing model, enumerates LAPIC/x2APIC/SAPIC and IOAPIC topology, wires ACPI GSI registration into PIC or IOAPIC backends, and applies old-platform DMI quirks. It is reached from `setup_arch()` through `acpi_boot_table_init()`, `early_acpi_boot_init()`, and `acpi_boot_init()`, so most state here is early boot state that becomes global policy for SMP, interrupt routing, PCI initialization, sleep, and ACPI OS services.

## Important APIs, Types, and Functions
- Global policy/export state: `acpi_disabled`, `acpi_pci_disabled`, `acpi_noirq`, `acpi_lapic`, `acpi_ioapic`, `acpi_strict`, `acpi_disable_cmcff`, `acpi_irq_model`, `acpi_int_src_ovr[]`, `acpi_sci_flags`, `acpi_sci_override_gsi`, `isa_irq_to_gsi[]`, and the function pointers `__acpi_register_gsi`, `__acpi_unregister_gsi`, `acpi_suspend_lowlevel`.
- Table mapping: `__acpi_map_table()` and `__acpi_unmap_table()` wrap `early_memremap()` and `early_memunmap()` for the ACPI core.
- MADT CPU parsing: `acpi_parse_madt()`, `acpi_parse_lapic()`, `acpi_parse_x2apic()`, `acpi_parse_sapic()`, NMI parsers, `acpi_is_processor_usable()`, and `topology_register_apic()` integration.
- MADT IRQ parsing: `acpi_parse_ioapic()`, `acpi_parse_int_src_ovr()`, `acpi_sci_ioapic_setup()`, `mp_override_legacy_irq()`, `mp_register_ioapic_irq()`, and `mp_config_acpi_legacy_irqs()`.
- Public IRQ APIs: `acpi_gsi_to_irq()`, `acpi_isa_irq_to_gsi()`, `acpi_register_gsi()`, `acpi_unregister_gsi()`, `acpi_register_ioapic()`, `acpi_unregister_ioapic()`, and `acpi_ioapic_registered()`.
- CPU hotplug APIs under `CONFIG_ACPI_HOTPLUG_CPU`: `acpi_map_cpu()` and `acpi_unmap_cpu()`.
- Boot sequence APIs: `acpi_boot_table_init()`, `early_acpi_boot_init()`, `acpi_boot_init()`, `acpi_mps_check()`, and command-line parsers for `acpi=`, `pci=`, `acpi_sci=`, `bgrt_disable`, and timer-override knobs.
- Miscellaneous ACPI OS hooks: global-lock helpers `__acpi_acquire_global_lock()`/`__acpi_release_global_lock()`, `arch_reserve_mem_area()`, RSDP getters/setters, Xen PV `acpi_os_ioremap`, and `acpi_get_cpu_uid()`.

## Control Flow
Early flow starts in `acpi_boot_table_init()`, which runs the early DMI blacklist, bails out if ACPI was already disabled, locates initial tables, and reserves them. `early_acpi_boot_init()` completes table initialization, parses the Simple Boot Flag table, checks `acpi_blacklisted()`, parses MADT enough to register the LAPIC base, and applies reduced-hardware initialization. Later, `acpi_boot_init()` reruns SBF parsing, parses FADT for legacy-device and PM-timer state, fully processes MADT CPU and IOAPIC entries, parses optional HPET and BGRT tables, installs `pci_acpi_init` unless ACPI IRQ routing is disabled, and parses SPCR for early console setup.

MADT processing first validates the LAPIC/x2APIC/SAPIC CPU entries and records usable processors even when disabled so hotplug capacity can be sized. It then parses IOAPIC entries, interrupt source overrides, synthetic SCI setup if firmware did not provide an override, legacy ISA mappings, and NMI sources. When both LAPIC and IOAPIC paths succeed, `acpi_set_irq_model_ioapic()` switches `acpi_irq_model` from PIC to IOAPIC and replaces the GSI registration function pointers.

Runtime registration flow is intentionally indirect. `acpi_register_gsi()` dispatches through `__acpi_register_gsi`, which initially points to `acpi_register_gsi_pic()` and later points to `acpi_register_gsi_ioapic()` after IOAPIC discovery. IOAPIC mapping is serialized by `acpi_ioapic_lock` and uses irqdomain allocation metadata derived from ACPI trigger/polarity. CPU and IOAPIC hotplug APIs similarly translate ACPI handles and GSIs into APIC IDs, NUMA nodes, and IOAPIC registrations.

## State and Persistence Behavior
Most variables are boot-time or `__initdata` state, but their effects persist through global exported flags, APIC topology tables, the IRQ model, registered IOAPICs, `isa_irq_to_gsi[]`, platform legacy-device flags, the ACPI PM timer port, HPET resource insertion, and the ACPI suspend low-level function pointer. DMI quirks and command-line options can permanently disable all ACPI, ACPI PCI routing, XSDT use, BGRT parsing, or SCI polarity/trigger defaults for the boot. The ACPI global lock helpers operate on firmware-shared lock words using `try_cmpxchg`.

## Dependencies and Integration Points
This file sits between the ACPICA table parser and x86 subsystems: APIC topology, IOAPIC irqdomains, PCI IRQ routing, HPET, BGRT, SPCR serial console, e820/NVS reservation, Xen PV ioremap behavior, ACPI hotplug CPU/IOAPIC paths, NUMA node assignment, legacy PIC/ELCR, DMI, and platform legacy device descriptors. It calls into `madt_wakeup.c` through `acpi_parse_mp_wake()` when `CONFIG_ACPI_MADT_WAKEUP` is enabled and into `sleep.c` through `x86_acpi_suspend_lowlevel`.

## Risks
- Invalid or inconsistent MADT entries can disable ACPI or leave the system in PIC mode; regressions here affect boot CPU enumeration and interrupt delivery very early.
- IRQ source override handling is quirk-heavy, especially IRQ0 and SCI trigger/polarity. Small changes can break old BIOSes or produce interrupt storms.
- `__acpi_register_gsi` function-pointer switching is global; using it before the IRQ model is finalized or without the IOAPIC lock can produce mismatched IRQ mappings.
- DMI blacklist and command-line parsing decisions override large subsystems; changes require care because the affected hardware is often old and hard to test.
- Hardware-reduced ACPI bypasses legacy PIC/timer setup, so legacy assumptions can fail on those platforms.

## Test Signals
- Boot logs should report MADT LAPIC/IOAPIC use, HPET base, PM timer port, SCI override behavior, and any DMI quirks.
- Kernel boot tests should cover `acpi=off`, `acpi=force`, `acpi=noirq`, `pci=noacpi`, `acpi=rsdt`, `acpi_sci=edge/level/high/low`, and timer override options.
- x86 ACPI hotplug tests should exercise CPU map/unmap and IOAPIC register/unregister paths.
- Interrupt routing validation should include legacy PIC fallback, IOAPIC systems with interrupt source overrides, and hardware-reduced ACPI systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cppc.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cppc.c

## Purpose
`cppc.c` provides x86-specific ACPI CPPC FFH support and AMD performance-capability helpers. It decides whether CPPC is supported by the current CPU family, implements FFH reads/writes through model-specific registers, initializes scheduler frequency invariance from CPPC performance data, and exports AMD helpers for preferred-core detection and boost-ratio scaling.

## Important APIs, Types, and Functions
- `cpc_supported_by_cpu()` recognizes AMD/Hygon CPPC support by family/model exceptions and `X86_FEATURE_CPPC`.
- `cpc_ffh_supported()` advertises FFH support for x86.
- `cpc_read_ffh()` and `cpc_write_ffh()` access `struct cpc_reg` bitfields through `rdmsrq_safe_on_cpu()` and `wrmsrq_safe_on_cpu()`.
- `acpi_processor_init_invariance_cppc()` initializes frequency invariance if APERF/MPERF and AMD CPPC data are available.
- `amd_get_highest_perf()` reads either `MSR_AMD_CPPC_CAP1` or generic `cppc_get_highest_perf()`.
- `amd_detect_prefcore()` determines whether online CPUs expose different highest-performance values and caches the result in `amd_pref_core_detected`.
- `amd_get_boost_ratio_numerator()` returns the numerator used for boost-ratio scaling, with special handling for preferred cores, Zen4 model `0x70..0x7f`, and heterogeneous AMD core types.

## Control Flow
The ACPI CPPC core calls the `cpc_*` hooks when evaluating FFH register access. Reads mask and right-shift the requested bitfield from the MSR; writes read-modify-write the same bitfield to preserve neighboring fields. Frequency invariance initialization is guarded by `freq_invariance_lock` and a static `init_done`, then obtains CPPC performance caps, derives a midpoint between maximum boost and nominal performance, and calls `freq_invariance_set_perf_ratio()`.

AMD preferred-core detection is lazy. Callers ask `amd_detect_prefcore()`, which returns a cached supported/unsupported state if available, otherwise scans online CPUs until it sees either one highest-performance value or two distinct values. `amd_get_boost_ratio_numerator()` first forces detection, then chooses either the cached non-preferred-core numerator, a Zen4 constant, a performance-core constant, an efficiency-core actual highest-performance value, or the default preferred-core constant.

## State and Persistence Behavior
`amd_pref_core_detected` and `boost_numerator` persist the preferred-core probe result across callers. `freq_invariance_lock` and the static `init_done` prevent repeated scheduler-scale initialization. MSR writes persist in CPU hardware state according to the CPPC register being accessed; the helpers do not maintain rollback state.

## Dependencies and Integration Points
The file integrates ACPI CPPC (`acpi/cppc_acpi.h`), MSR access, x86 CPU feature flags, scheduler capacity scaling, topology core-type classification, and AMD P-state/CPU frequency consumers through exported GPL symbols. It assumes caller-side interpretation of CPPC performance registers and delegates generic ACPI object access to `drivers/acpi/cppc_acpi.c`.

## Risks
- Model-specific CPPC allow-list logic can misclassify AMD/Hygon systems and disable performance control or preferred-core hints.
- `amd_detect_prefcore()` scans only online CPUs and caches the result; CPU topology changes after first use may not alter the cached outcome.
- FFH bitfield masks rely on firmware-provided `bit_offset` and `bit_width`; invalid values could produce bad masks.
- Hardcoded numerator constants are sensitive to CPU family/model errata and heterogeneous-core policy.

## Test Signals
- Validate CPPC FFH reads/writes with ACPI CPPC tables on AMD/Hygon machines and with invalid MSR paths returning errors.
- Compare `amd_detect_prefcore()` results with known preferred-core systems and uniform-core systems.
- Exercise AMD P-state frequency invariance and scheduler capacity reporting across Zen generations, including Zen4 `0x70..0x7f` and AMD heterogeneous-core systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cppc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cstate.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cstate.c

## Purpose
`cstate.c` implements x86-specific ACPI processor C-state support, especially FFH C-state entry through the `MONITOR/MWAIT` instruction pair. It also sets bus-mastering flags that tell the generic ACPI processor idle code whether C3 entry needs cache flushing or ARB_DISABLE handling on different CPU vendors.

## Important APIs, Types, and Functions
- `acpi_processor_power_init_bm_check()` initializes `struct acpi_processor_flags` fields `bm_check` and `bm_control` based on online CPU count, vendor, family/model, and Zen feature state.
- `struct cstate_entry` stores per-CPU MWAIT `eax` and `ecx` hints for ACPI C-state indices.
- `cpu_cstate_entry` is a per-CPU allocation used by C-state probe, idle entry, and offline play-dead.
- `acpi_processor_ffh_cstate_probe()` validates FFH register data, runs the CPU-local CPUID MWAIT probe, stores hints, and marks Intel BM_STS skip behavior.
- `acpi_processor_ffh_cstate_enter()` calls `mwait_idle_with_hints()`.
- `acpi_processor_ffh_play_dead()` calls `mwait_play_dead()` for CPU offline.
- `ffh_cstate_init()` allocates per-CPU storage for Intel, AMD, and Hygon systems at `arch_initcall`.

## Control Flow
The generic ACPI processor driver asks x86 to initialize bus-master behavior after CPUs are online. For FFH C-states, `acpi_processor_ffh_cstate_probe()` rejects unsupported conditions, clears the per-CPU state entry, and uses `call_on_cpu()` so CPUID leaf 5 is evaluated on the target CPU. The CPU-local probe verifies that the ACPI C-state MWAIT hint has a hardware-supported substate and that interrupt-break extensions are present. A successful probe stores the MWAIT hint and interrupt-break ECX flag for later idle entry.

Idle entry is direct: the cpuidle path calls `acpi_processor_ffh_cstate_enter()`, which fetches the current CPU's stored hints and executes the MWAIT idle helper. CPU offline death uses the same stored EAX hint through `acpi_processor_ffh_play_dead()`.

## State and Persistence Behavior
The per-CPU `cpu_cstate_entry` array persists for the lifetime of the module/built-in code and is freed only by the exit callback. `mwait_supported[]` suppresses repeated debug logging per C-state type. The function mutates ACPI processor C-state descriptors (`cx->desc`, `cx->bm_sts_skip`) and stores per-CPU idle hints derived from firmware `_CST` data.

## Dependencies and Integration Points
The file integrates ACPI processor idle data, `struct acpi_processor_cx`, CPUID leaf `CPUID_LEAF_MWAIT`, `asm/mwait.h`, SMP CPU-local execution helpers, CPU vendor/family identification, cpuidle annotations, and CPU hotplug play-dead support.

## Risks
- Incorrect BM flag decisions can cause unnecessary `WBINVD`, skipped cache-coherency handling, or wrong ARB_DISABLE behavior on C3 entry.
- Firmware can advertise unsupported MWAIT hints; the probe rejects many cases but relies on CPUID decoding and `_CST` address semantics.
- Per-CPU state must be initialized before idle entry or play-dead; missing allocation causes probe failure.
- C-state entry is CPU-local and low-level; incorrect hints can hang or wake CPUs incorrectly.

## Test Signals
- Boot with ACPI processor idle enabled and check logs for `Monitor-Mwait will be used` messages.
- Validate cpuidle state entry/exit and CPU offline on Intel and AMD/Hygon systems.
- Exercise vendor-specific BM behavior on Intel, Centaur, Zhaoxin, and Zen systems.
- Use firmware with invalid FFH/MWAIT C-state data to verify graceful rejection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_playdead.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_playdead.S

## Purpose
`madt_playdead.S` contains the 64-bit assembly handoff used by ACPI MADT Multiprocessor Wakeup support when a CPU is stopped or offlined and control must be returned to firmware through a reset vector. It is the low-level endpoint called from `madt_wakeup.c`.

## Important APIs, Types, and Functions
- `asm_acpi_mp_play_dead(reset_vector, pgd)` is the sole exported symbol in this file.
- Arguments follow the x86-64 C ABI: `%rdi` carries the physical/identity-mapped reset-vector target and `%rsi` carries the page-global-directory address for an identity mapping.
- The code uses `ANNOTATE_NOENDBR` and `ANNOTATE_RETPOLINE_SAFE` because it intentionally enters from low-level CPU-stop paths and jumps indirectly to firmware.

## Control Flow
The routine clears `X86_CR4_PGE` from CR4 to disable global TLB entries, writes CR3 with the supplied identity-mapping PGD, then performs an indirect jump to the reset vector. There is no return path: firmware takes control of the CPU.

## State and Persistence Behavior
The routine mutates CPU-local CR4 and CR3 state and leaves kernel virtual mappings behind. The CPU is expected not to resume kernel execution through this path. Persistent state needed by the routine, such as the reset vector and identity PGD physical address, is prepared and stored by `madt_wakeup.c`.

## Dependencies and Integration Points
This file depends on x86 processor flag definitions, page alignment, linkage macros, and branch-mitigation annotations. `madt_wakeup.c` maps this exact code page into an identity mapping and sets SMP callbacks to call it from `play_dead`, `stop_this_cpu`, and reset handoff paths.

## Risks
- The code must be identity-mapped at the same virtual location before and after CR3 switch; otherwise the CPU can fault after switching page tables.
- Clearing PGE and replacing CR3 in a CPU teardown path is irreversible for this flow.
- The reset vector target comes from ACPI firmware; invalid firmware data can strand the CPU.

## Test Signals
- Exercise ACPI MADT MP wakeup v1 CPU offlining on capable systems.
- Confirm `madt_wakeup.c` identity mapping includes the page containing `asm_acpi_mp_play_dead`.
- Validate kexec/offline paths do not attempt to return from this function.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_playdead.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_wakeup.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_wakeup.c

## Purpose
`madt_wakeup.c` implements x86 support for the ACPI MADT Multiprocessor Wakeup structure. It allows secondary CPU startup through a firmware mailbox instead of legacy INIT/SIPI, and, for version 1 wakeup structures, configures CPU offlining handoff through an ACPI reset vector.

## Important APIs, Types, and Functions
- Persistent addresses: `acpi_mp_wake_mailbox_paddr`, `acpi_mp_wake_mailbox`, `acpi_mp_pgd`, and `acpi_mp_reset_vector_paddr`.
- CPU teardown callbacks: `acpi_mp_stop_this_cpu()`, `acpi_mp_play_dead()`, and `acpi_mp_cpu_die()`.
- Mapping setup: `alloc_pgt_page()`, `free_pgt_page()`, and `acpi_mp_setup_reset()`.
- Startup callback: `acpi_wakeup_cpu()` writes APIC ID, wakeup vector, and command into the ACPI mailbox.
- Policy fallback: `acpi_mp_disable_offlining()` disables CPU offlining and clears the MADT mailbox address for kexec convention.
- Entry point: `acpi_parse_mp_wake()` validates and parses the MADT subtable and updates APIC startup callbacks.

## Control Flow
`boot.c` parses the MADT MP Wake subtable and calls `acpi_parse_mp_wake()`. The parser validates the minimum v0 structure, records the mailbox physical address, and, when v1 reset-vector data is present, calls `acpi_mp_setup_reset()`. Reset setup builds a new identity page table over all `pfn_mapped[]` ranges, maps the reset-vector page, maps the `asm_acpi_mp_play_dead()` page at its kernel virtual offset, and then installs SMP callbacks for play-dead, stop-this-CPU, and CPU-die. If reset setup fails or the structure is only v0, CPU offlining is disabled.

Secondary CPU wakeup is serialized by the CPU bringup core. On first use, `acpi_wakeup_cpu()` `memremap()`s the mailbox, writes APIC ID and wake vector, publishes the wake command with `smp_store_release()`, and spins until firmware clears the command. CPU die confirmation uses a test command and a one-second timeout to verify firmware has taken control.

## State and Persistence Behavior
Mailbox physical address and reset-vector identity mapping state are initialized once and marked read-mostly/after-init where applicable. The mailbox remains mapped after first use. `acpi_mp_disable_offlining()` mutates the in-memory MADT wakeup structure by zeroing `mailbox_address` to prevent a kexec kernel from using an invalid inherited mailbox; this is a Linux convention rather than ACPI-defined persistence.

## Dependencies and Integration Points
This file integrates ACPI MADT parsing, x86 APIC secondary wakeup callbacks, SMP hotplug callbacks, memblock page-table allocation, kernel identity mappings, CPU hotplug policy, kexec safety, NMI/APIC/processor headers, and the assembly routine in `madt_playdead.S`.

## Risks
- Firmware mailbox command ordering is critical; APIC ID and wake vector must be visible before the command.
- The wake loop intentionally waits indefinitely to avoid TDX/VMM delayed-wakeup attacks; a broken firmware path can hang bringup.
- Identity-map construction failures disable offlining and can limit kexec secondary CPU use.
- Clearing the MADT mailbox for kexec is Linux-specific and assumes the running kernel has already cached the mailbox address.

## Test Signals
- Boot on systems advertising `ACPI_MADT_TYPE_MULTIPROC_WAKEUP`; verify secondary CPU startup uses `acpi_wakeup_cpu`.
- Test CPU hotplug/offline on v1 structures and verify offlining is disabled on v0 or failed reset setup.
- Test kexec after MP wakeup parsing to ensure the second kernel does not misuse an invalid mailbox.
- Validate TDX or delayed-vCPU environments do not prematurely abort wakeup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/madt_wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.c

## Purpose
`sleep.c` provides x86-specific ACPI sleep and wakeup preparation, primarily for S3 suspend. It fills the real-mode wakeup header with protected-mode restoration data, sets the firmware wake vector address, bridges assembly low-level suspend code to `acpi_enter_sleep_state()`, and parses `acpi_sleep=` command-line options.

## Important APIs, Types, and Functions
- `acpi_get_wakeup_address()` returns the physical address of `real_mode_header->wakeup_start`.
- `x86_acpi_enter_sleep_state()` is an assembly-callable wrapper around `acpi_enter_sleep_state()`.
- `x86_acpi_suspend_lowlevel()` validates the wakeup header, stores video mode and protected-mode CPU state, sets magic values and wake targets, pauses graph tracing, and calls `do_suspend_lowlevel()`.
- `acpi_sleep_setup()` parses `s3_bios`, `s3_mode`, `s3_beep`, S4 hardware-signature options, NVS save options, old ordering, and blacklist bypass.
- `init_s4_sigcheck()` sets hypervisor guest hibernation signature checking defaults when configured.

## Control Flow
The generic ACPI sleep path calls the function pointer initialized in `boot.c` to `x86_acpi_suspend_lowlevel()`. The function validates the real-mode wakeup header signature, records video and real-mode flags, saves CR0/CR4 and selected MSRs into the wakeup header, sets protected-mode entry state differently for 32-bit and 64-bit builds, sets `saved_magic`, and then calls the architecture assembly `do_suspend_lowlevel()`. Assembly saves processor/register state, invokes `x86_acpi_enter_sleep_state(3)`, and resumes through architecture-specific wakeup code.

Command-line parsing occurs through `__setup("acpi_sleep=", ...)` and mutates global ACPI sleep policy before suspend. Hypervisor S4 signature behavior is initialized as an arch initcall before ACPI subsystem initialization.

## State and Persistence Behavior
The file writes persistent suspend-resume handoff state into the real-mode wakeup header, `saved_magic`, `initial_code`, `current->thread.sp` for 64-bit SMP resume, and `smpboot_control` for non-parallel startup. `acpi_realmode_flags` persists command-line S3 behavior. S4 hardware-signature and ACPI NVS policy changes persist for the boot.

## Dependencies and Integration Points
This code depends on real-mode trampoline data under `arch/x86/realmode`, low-level assembly in `wakeup_32.S` and `wakeup_64.S`, saved processor-state helpers, MSR access, ftrace graph tracing, SMP startup controls, ACPI core sleep entry, hibernation policy, and hypervisor detection.

## Risks
- Wakeup header corruption or signature mismatch aborts suspend.
- Saved MSR/CR state is CPU- and mode-specific; incorrect restoration can fail resume.
- 64-bit SMP temporarily abuses `current->thread.sp` so unwinders and startup code must tolerate the value while suspended.
- Low-level suspend has unusual call/return behavior, hence graph tracing is paused around it.

## Test Signals
- Run S3 suspend/resume on 32-bit and 64-bit x86 configurations.
- Validate `acpi_sleep=s3_bios,s3_mode,s3_beep,nonvs,old_ordering,nobl` parsing changes expected behavior.
- Test hibernation on hypervisor guests and bare metal for S4 hardware-signature policy.
- Confirm resume logs do not show wakeup header mismatch and CPU state restores cleanly.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.h -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.h

## Purpose
`sleep.h` is the small private header shared by x86 ACPI sleep C and assembly code. It declares the cross-language variables and entry points used to transfer control between `sleep.c`, `wakeup_32.S`, and `wakeup_64.S`.

## Important APIs, Types, and Functions
- Shared state declarations: `saved_video_mode`, `saved_magic`, and `wake_sleep_flags`.
- 32-bit resume symbol: `wakeup_pmode_return`.
- 64-bit wake entry: `wakeup_long64()`.
- Low-level suspend entry: `do_suspend_lowlevel()`.
- C low-level suspend function: `x86_acpi_suspend_lowlevel()`.
- Assembly-callable ACPI sleep bridge: `x86_acpi_enter_sleep_state(u8 state)`.

## Control Flow
`sleep.c` includes this header to call `do_suspend_lowlevel()` and to set or reference symbols defined in assembly. The assembly files include or match these declarations so they can call `x86_acpi_enter_sleep_state()` and publish resume symbols.

## State and Persistence Behavior
The declared variables are part of the suspend/resume handoff. `saved_magic` is used by wakeup assembly as an integrity/sanity marker; `saved_video_mode` is written into the real-mode wakeup header; `wake_sleep_flags` is shared with wakeup paths.

## Dependencies and Integration Points
The header depends only on kernel linkage declarations and ACPI status typing supplied by includers. Its integration point is the private ACPI sleep implementation under `arch/x86/kernel/acpi`.

## Risks
- Type or symbol mismatches between C and assembly can break low-level suspend or resume.
- Because these are low-level externs, missing configuration guards can expose symbols not defined in a given build mode.

## Test Signals
- Build both 32-bit and 64-bit ACPI sleep configurations.
- Use `nm`/link checks for `saved_magic`, `do_suspend_lowlevel`, `wakeup_long64`, and `wakeup_pmode_return` in the corresponding builds.
- Run S3 suspend/resume smoke tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/sleep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_32.S

## Purpose
`wakeup_32.S` implements the 32-bit protected-mode return path and low-level suspend entry for x86 ACPI S3. It saves CPU register context before sleep, calls into ACPI sleep state entry, and restores state after firmware wakes the system.

## Important APIs, Types, and Functions
- `wakeup_pmode_return` is the protected-mode resume entry programmed into the real-mode wakeup header by `sleep.c`.
- `do_suspend_lowlevel` saves processor/register state and calls `x86_acpi_enter_sleep_state(3)`.
- Local helpers `save_registers` and `restore_registers` save IDT/LDT/TSS, stack, callee-saved registers, flags, and the resume EIP.
- Data symbols include `saved_magic`, `saved_eip`, `saved_idt`, `saved_ldt`, and `saved_tss`.

## Control Flow
Before entering S3, `do_suspend_lowlevel()` calls `save_processor_state()`, saves registers, pushes state `3`, and calls `x86_acpi_enter_sleep_state()`. If entry fails or after wakeup, control reaches `ret_point`, restores registers and processor state, and returns to C. On a successful resume through firmware, `wakeup_pmode_return` reloads segment registers and descriptor tables, flushes CR3, executes `wbinvd`, restores the saved stack, checks `saved_magic == 0x12345678`, and jumps to `saved_eip`.

## State and Persistence Behavior
The assembly stores resume-critical CPU state in static data symbols and relies on `sleep.c` setting `saved_magic`. A magic mismatch loops forever at `bogus_magic`, preventing return into a corrupted context.

## Dependencies and Integration Points
This file integrates with `sleep.c`, `sleep.h`, `save_processor_state()`, `restore_processor_state()`, real-mode wakeup trampoline setup, x86 segment constants, and ACPI sleep state entry.

## Risks
- Resume correctness depends on exact descriptor, stack, CR3, and magic state.
- The infinite `bogus_magic` loop is deliberate but produces a hard hang when resume state is wrong.
- Assembly/C symbol and calling-convention mismatches can break S3 only on 32-bit builds, making coverage easy to miss.

## Test Signals
- Build `CONFIG_X86_32` with ACPI sleep enabled.
- Run S3 suspend/resume and verify return from `do_suspend_lowlevel()` without magic mismatch.
- Fault-injection or instrumentation can validate the failure path by corrupting `saved_magic` in a controlled debug build.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_64.S

## Purpose
`wakeup_64.S` implements the 64-bit x86 ACPI S3 low-level suspend entry and long-mode wakeup return. It saves general-purpose and control-register state, enters ACPI sleep state S3, and restores enough state after wake to jump back to the saved kernel instruction pointer.

## Important APIs, Types, and Functions
- `wakeup_long64` is the 64-bit wakeup entry set through `initial_code` by `sleep.c`.
- `do_suspend_lowlevel` saves processor state and register context, calls `x86_acpi_enter_sleep_state(3)`, and restores state at `.Lresume_point`.
- Data symbols include saved callee-saved registers, saved RIP/RSP, `saved_magic`, and `saved_context` fields populated through `asm-offsets.h`.
- The function is marked `STACK_FRAME_NON_STANDARD` because it has non-standard suspend/resume control flow.

## Control Flow
`do_suspend_lowlevel()` creates a small frame, calls `save_processor_state`, stores a `pt_regs`-like context plus resume RIP/RSP and callee-saved registers, calls `x86_acpi_enter_sleep_state(3)`, and jumps to `.Lresume_point` if sleep entry returns. On wake, `wakeup_long64` checks `saved_magic == 0x123456789abcdef0`, reloads segment registers, restores saved stack and callee-saved registers, then jumps to the saved RIP. `.Lresume_point` restores CR4/CR3/CR2/CR0, flags, general registers, optionally unpoisons the task stack for KASAN stack mode, clears `eax`, and jumps to `restore_processor_state`.

## State and Persistence Behavior
The file persists resume state in static data and in the `saved_context` structure. `saved_magic` is a guard against jumping into stale or corrupted resume data; mismatch enters an infinite diagnostic loop with a marker in `rcx`.

## Dependencies and Integration Points
It depends on `sleep.c`, `sleep.h`, saved processor-state helpers, x86 segment constants, MSR/page-table definitions, retpoline annotations, frame macros, KASAN stack unpoisoning, and ACPI sleep entry.

## Risks
- Control register restoration order and saved context layout must match `asm-offsets.h`; drift can crash resume.
- The path intentionally bypasses normal C call/return expectations, so tracing, unwinding, and sanitizers need special handling.
- Magic mismatch or wrong wake vector produces a hard hang during resume.

## Test Signals
- Run S3 suspend/resume on `CONFIG_X86_64`, including SMP systems.
- Build with KASAN stack mode to exercise the unpoison call.
- Check objtool warnings for the non-standard stack frame annotation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/wakeup_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/alternative.c

## Purpose
`alternative.c` is the central x86 runtime and boot-time text patching engine. It applies CPU-feature alternatives, retpoline/return thunk rewrites, ENDBR sealing, FineIBT/CFI transformations, SMP lock-prefix alternatives, and live text pokes using safe temporary mappings and INT3-based synchronization. It is performance- and security-critical because it rewrites executable kernel and module text based on the actual CPU, mitigation policy, and module lifecycle.

## Important APIs, Types, and Functions
- Global state: `alternatives_patched`, `debug_alternative`, `noreplace_smp`, `x86_nops[]`, `x86_nops[]` pointer table, CFI mode state, ITS thunk page state, SMP alternative module list, `text_poke_mm`, `text_poke_mm_addr`, `text_poke_array`, and per-CPU `text_poke_array_refs`.
- Alternative patching: `apply_alternatives()`, `analyze_patch_site()`, `prep_patch_site()`, `patch_site()`, `text_poke_apply_relocation()`, `add_nop()`, `optimize_nops()`, relocation helpers, and `alt_replace_call()`.
- Spectre/return mitigation patching: `apply_retpolines()`, `patch_retpoline()`, `emit_indirect()`, `emit_call_track_retpoline()`, `apply_returns()`, `patch_return()`, and `cpu_wants_rethunk*()`.
- ITS thunk support: `its_init_mod()`, `its_fini_mod()`, `its_free_mod()`, `its_allocate_thunk()`, and `its_static_thunk()`.
- IBT/FineIBT/CFI support: `apply_seal_endbr()`, `apply_fineibt()`, `decode_fineibt_insn()`, CFI rehash/rewrite helpers, ENDBR poisoning, and hash/arity decoders.
- SMP alternatives: `alternatives_smp_module_add()`, `alternatives_smp_module_del()`, `alternatives_enable_smp()`, and `alternatives_text_reserved()`.
- Boot orchestration: `alternative_instructions()` runs INT3 selftest, disables NMI, applies paravirt caps, saves/disables IBT, rewrites CFI/retpolines/returns/call thunks/alternatives/ENDBR, optionally patches SMP locks to UP, restores IBT/NMI, sets `alternatives_patched`, and runs relocation selftest.
- Text poking: `text_poke_early()`, `text_poke()`, `text_poke_kgdb()`, `text_poke_copy_locked()`, `text_poke_copy()`, `text_poke_set()`, `smp_text_poke_batch_add()`, `smp_text_poke_batch_finish()`, `smp_text_poke_single()`, and `smp_text_poke_int3_handler()`.

## Control Flow
Boot-time patching is staged. `alternative_instructions()` first verifies INT3 call emulation, stops NMIs, sets paravirtual feature caps, disables IBT around the rewrite, applies CFI/FineIBT transformations, rewrites retpoline and return sites, finalizes ITS pages, patches call thunks, applies CPU-feature alternative instruction entries, seals ENDBR sites, restores IBT, applies UP-vs-SMP lock alternatives if only one CPU is present or allowed, restarts NMIs, and marks alternatives complete.

Alternative patching walks `.altinstructions` in order. Consecutive entries for the same instruction address are treated as a patch site; the selected replacement is the last entry whose feature predicate matches. Replacement bytes are copied into a fixed buffer, optionally direct-call adjusted, padded, relocated for relative branches/RIP-relative operands, NOP-optimized, and written with `text_poke_early()`.

Live patching after boot uses `__text_poke()` to map target text pages into a preallocated temporary mm with writable kernel permissions, copy or set bytes under disabled local IRQs, verify writes, clear PTEs, flush TLBs, and restore the previous mm. SMP multi-byte patching uses an INT3-first protocol: install breakpoints, sync cores, patch instruction tails, emit perf text-poke events, replace first bytes, sync again, and wait for all INT3 handlers to drop references. The handler emulates the old or new control-flow instruction so CPUs encountering a patch in progress continue safely.

FineIBT/CFI flow can first disable kCFI callers, optionally randomize hashes, then either re-enable kCFI or rewrite callee preambles and indirect callers for FineIBT. Decoder helpers interpret traps from FineIBT, BHI, and paranoid caller sequences so CFI violations can be reported or recovered according to policy.

## State and Persistence Behavior
Patching mutates kernel and module executable text permanently for the boot or module lifetime. `alternatives_patched` gates later consumers. ITS thunk pages are allocated, populated, then restored read/execute. SMP alternative module metadata persists while modules are loaded so lock-prefix patching can be toggled if SMP is enabled after UP patching. `text_poke_mm` is preallocated global infrastructure for later live patches. CFI mode, random seed, and BHI/paranoid flags are `__ro_after_init` policy.

## Dependencies and Integration Points
The file is tightly coupled to linker-generated sections (`__alt_instructions`, `__retpoline_sites`, `__return_sites`, `__ibt_endbr_seal`, `__cfi_sites`, `__smp_locks`), objtool output, x86 instruction decoder/evaluator, text mutex locking, module loader hooks, static calls, call thunks, CET-IBT helpers, perf text-poke events, KGDB, ftrace/static-key users of text poking, KASAN, temporary-mm code, LASS access control, NMI control, and CPU feature flags.

## Risks
- Incorrect relocation or instruction decoding can corrupt executable text and crash during boot or module load.
- Patching order matters: retpolines must be rewritten before alternatives that may alter thunks; IBT must be disabled while caller/callee contracts are inconsistent.
- Live text poking is concurrency-sensitive; missing `text_mutex`, wrong INT3 emulation, or unordered patch addresses can expose partially patched instructions.
- FineIBT/CFI transformations are byte-layout dependent and interact with ITS, BHI, retpoline, and compiler-generated CFI sequences.
- SMP lock-prefix alternatives must not patch freed init text or module ranges incorrectly.

## Test Signals
- Boot with `debug-alternative` masks to inspect alternative, return, retpoline, ENDBR, and SMP patch logs.
- Exercise module load/unload with alternatives, ITS, and SMP lock sections.
- Run the built-in INT3 and relocation selftests triggered by `alternative_instructions()`.
- Validate ftrace/static-call/jump-label/livepatch users that rely on `text_poke` and SMP batch poking.
- Test CFI modes via `cfi=off,kcfi,fineibt,debug,norand,paranoid,bhi` on supported hardware and check CFI trap decoding.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/alternative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/amd_gart_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/amd_gart_64.c

## Purpose
`amd_gart_64.c` implements the legacy AMD64 GART aperture as a DMA remapping IOMMU for PCI devices, mainly to support devices with limited DMA masks on systems with memory above 4 GiB. It allocates/remaps aperture pages, manages the GART allocation bitmap, installs DMA map operations, flushes GART TLBs through AMD northbridge helpers, and restores hardware state on resume.

## Important APIs, Types, and Functions
- Global remap state: `iommu_bus_base`, `iommu_size`, `iommu_pages`, `iommu_gatt_base`, `iommu_gart_bitmap`, `next_bit`, `need_flush`, `gart_unmapped_entry`, and `iommu_fullflush`.
- Allocation/flush helpers: `alloc_iommu()`, `free_iommu()`, `flush_gart()`, `iommu_full()`, `need_iommu()`, and `nonforced_iommu()`.
- DMA ops: `gart_map_phys()`, `gart_unmap_phys()`, `gart_map_sg()`, `gart_unmap_sg()`, `gart_alloc_coherent()`, and `gart_free_coherent()`.
- Scatter-gather helpers: `dma_map_area()`, `dma_map_sg_nonforce()`, `__dma_map_cont()`, and `dma_map_cont()`.
- Aperture/GATT setup: `check_iommu_size()`, `read_aperture()`, `enable_gart_translations()`, `init_amd_gatt()`, and `gart_iommu_init()`.
- Resume/shutdown: `set_up_gart_resume()`, `gart_fixup_northbridges()`, `gart_resume()`, `gart_syscore_ops`, and `gart_iommu_shutdown()`.
- Option parsing: `gart_parse_options()` handles size, fullflush, noagp, noaperture, force/allowed, and `memaper`.

## Control Flow
`gart_iommu_init()` runs when `aperture_64.c` detected a usable GART aperture and set `x86_init.iommu.iommu_init`. It checks AMD northbridge GART support, negotiates with the AGP AMD64 driver or creates a private GATT, rejects no-IOMMU/low-memory/no-aperture cases, maps the aperture into kernel page tables if needed, sizes the IOMMU portion, allocates the bitmap, reserves the AGP aperture tail for DMA remapping, marks those virtual pages not-present, flushes CPU caches, enables GART translations, creates a scratch unmapped entry, installs `gart_dma_ops`, disables SWIOTLB, and registers shutdown handling.

DMA mapping flow checks whether direct DMA is possible. If not, it allocates GART pages from the bitmap, fills GATT entries with encoded physical addresses, sets the global `need_flush` flag when wrapping or fullflush policy applies, flushes the GART, and returns a bus address in the aperture. Unmap clears GATT entries to the scratch page and releases bitmap bits. SG mapping coalesces compatible page-aligned entries when `iommu_merge` allows it and falls back to per-entry non-forced mappings if the merged path overflows.

## State and Persistence Behavior
The GATT table and bitmap persist for the boot. Hardware GART aperture registers are programmed in each AMD northbridge and restored during syscore resume if `set_up_gart_resume()` was called by aperture setup. DMA mappings persist until explicit unmap. `need_flush` is shared global state protected by `iommu_bitmap_lock`. `dma_ops` is globally redirected to GART ops once initialized.

## Dependencies and Integration Points
The file depends on AGP AMD64 support, AMD northbridge helpers (`amd_nb_has_feature()`, `node_to_amd_nb()`, `amd_flush_garts()`), aperture setup in `aperture_64.c`, DMA mapping core, scatterlist APIs, MTRR/cache attribute helpers, syscore resume, PCI config access, SWIOTLB policy, and x86 platform IOMMU shutdown hooks.

## Risks
- GART supports only physical addresses below 1 TiB; higher mappings fail.
- Running out of aperture space can produce DMA failures or, in legacy fallback comments, possible garbage DMA if callers cannot recover.
- Cache aliasing around the aperture is delicate; the code marks pages not-present and performs `wbinvd()` before enabling translations.
- Lazy flushing historically triggered device bugs, hence `iommu_fullflush` defaults to true.
- AGP driver coexistence changes aperture ownership and shutdown behavior.

## Test Signals
- Boot AMD64 GART-capable systems with memory above 4 GiB and limited DMA-mask PCI devices.
- Exercise `iommu=fullflush`, `nofullflush`, `noagp`, `noaperture`, `force`, `allowed`, and `memaper` options.
- Run DMA API debug with scatter-gather and coherent allocations through GART.
- Suspend/resume and verify GART aperture registers and translations are restored.
- Kdump/kexec tests should verify aperture handling with `aperture_64.c` reservations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/amd_gart_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/amd_nb.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/amd_nb.c

## Purpose
`amd_nb.c` provides shared AMD/Hygon northbridge discovery and helper functions for older AMD64 northbridge and derivative devices. It caches per-node PCI function devices, exposes northbridge feature flags, supports L3 cache partitioning controls, provides MMCONFIG range discovery, and serializes/flushed GART TLB requests for the GART IOMMU/AGP stack.

## Important APIs, Types, and Functions
- Device tables: `amd_nb_misc_ids[]` and `amd_nb_bus_dev_ranges[]`.
- Cached global state: `amd_northbridges` and `flush_words`.
- Exported helpers: `amd_nb_num()`, `amd_nb_has_feature()`, `node_to_amd_nb()`, `amd_flush_garts()`.
- Discovery: `amd_cache_northbridges()`, `early_is_amd_nb()`, and `init_amd_nbs()`.
- MMCONFIG: `amd_get_mmconfig_range()`.
- L3 controls: `amd_get_subcaches()` and `amd_set_subcaches()`.
- GART flush setup: `amd_cache_gart()` and `amd_flush_garts()`.
- Erratum handling: `fix_erratum_688()` and `__fix_erratum_688()`.

## Control Flow
At `fs_initcall`, `init_amd_nbs()` checks for AMD/Hygon vendor, caches northbridge devices by calling `amd_num_nodes()` and `amd_node_get_func()` for functions 3 and 4, detects GART and L3 feature flags, caches GART flush register values, and applies erratum 688 if needed. Consumers then query the cached state through exported helpers.

GART flushing serializes on a static spinlock, writes each northbridge's cached flush word with bit 0 set, and polls until hardware clears the bit on every node. L3 partitioning reads/writes PCI config registers on the node's link/misc functions and preserves reset/BAN state across changes.

## State and Persistence Behavior
`amd_northbridges` owns a heap-allocated array of `struct amd_northbridge` entries and feature flags for the boot. `flush_words` stores per-node GART flush control values. `amd_set_subcaches()` uses static `reset` and `ban` variables to remember original L3 partitioning/BAN state.

## Dependencies and Integration Points
The file integrates AMD node PCI helpers from `amd_node.c`, CPUID feature/family data, PCI config access, GART IOMMU flushing in `amd_gart_64.c`, aperture detection in `aperture_64.c`, L3 cache partitioning users, and MMCONFIG setup logic.

## Risks
- Discovery assumes each node has a misc function; missing devices clear the cache and disable dependent features.
- `amd_flush_garts()` busy-waits on hardware clear bits and can hang if a northbridge stops responding.
- L3 partitioning writes low-level PCI config registers and can alter cache behavior system-wide.
- Early northbridge detection intentionally excludes Zen because newer systems use data-fabric paths.

## Test Signals
- Boot AMD/Hygon non-Zen systems and verify northbridge count/features.
- Exercise GART DMA mappings and confirm `amd_flush_garts()` completes under load.
- Test L3 subcache get/set on family 0x15 partitioning-capable machines.
- Validate MMCONFIG range discovery on Fam10h+ systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/amd_nb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/amd_node.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/amd_node.c

## Purpose
`amd_node.c` provides AMD node and SMN/HSMP access helpers for Zen-era systems. It maps AMD logical nodes to PCI root devices, reserves PCI configuration space used for SMN index/data access, exposes exported SMN read/write helpers, and optionally provides a dangerous debugfs interface for manual SMN access.

## Important APIs, Types, and Functions
- `amd_node_get_func(node, func)` returns the PCI function for legacy node devices at bus 0 slots `0x18..0x1f`.
- Global root mapping: `amd_roots`, protected by `smn_mutex` during initialization and SMN access.
- SMN access core: `__amd_smn_rw()`, `amd_smn_read()`, `amd_smn_write()`, and `amd_smn_hsmp_rdwr()`.
- Register pairs: SMN index/data at `0x60/0x64`, HSMP index/data at `0xc4/0xc8`.
- Debugfs state and handlers: `debugfs_dir`, `debug_node`, `debug_address`, `smn_node_*`, `smn_address_*`, and `smn_value_*`.
- PCI root discovery: `get_next_root()` and `amd_smn_init()`.
- Command-line gate: `amd_smn_debugfs_enable`.

## Control Flow
`amd_smn_init()` runs at `fs_initcall` only on Zen systems. It reserves full PCI config space on AMD/Hygon host bridge root devices to keep user space from touching SMN-sensitive config pairs, counts root devices, allocates one root pointer per AMD node, assigns roots evenly to nodes, optionally creates debugfs files, and finally sets `smn_exclusive = true`. SMN reads/writes fail until that exclusive setup is complete.

SMN access validates the node, fetches the mapped root, requires exclusive reservation, locks `smn_mutex`, writes the target SMN/HSMP address into the index register, then reads or writes the data register. `amd_smn_read()` treats PCI possible-error responses as `-ENODEV` and clears the output value.

## State and Persistence Behavior
`amd_roots` persists for the boot as the node-to-root mapping. PCI config regions are reserved exclusively and are not released in this file. `smn_exclusive` is the persistent gate that enables exported SMN helpers. Debugfs `debug_node` and `debug_address` persist as mutable global selectors; writes to the debugfs `value` file taint the kernel as out-of-spec.

## Dependencies and Integration Points
The file integrates PCI host bridge discovery, AMD/Hygon vendor IDs, `amd_num_nodes()`, debugfs under `arch_debugfs_dir`, exported SMN helpers used by AMD RAS/HSMP/hardware-management code, and kernel tainting for manual debug writes.

## Risks
- SMN semantics are register-specific; the helper can detect PCI error responses but cannot prove read-as-zero or write-ignored behavior.
- Debugfs writes can modify SoC fabric registers and deliberately taint the kernel.
- Root-to-node assignment assumes roots distribute evenly across nodes; odd firmware enumeration could mis-map SMN access.
- Reserving all config space can conflict with other users if initialization ordering changes.

## Test Signals
- Boot Zen systems and verify root reservation plus node mapping with dynamic debug or PCI debug logs.
- Call `amd_smn_read()` against known valid, read-as-zero, and invalid SMN addresses.
- Exercise HSMP read/write callers.
- Enable `amd_smn_debugfs_enable` only in controlled tests and verify debugfs read/write/taint behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/amd_node.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/aperture_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/aperture_64.c

## Purpose
`aperture_64.c` is early boot firmware-replacement and validation code for the AMD64 GART/AGP aperture. It detects broken or missing BIOS aperture setup, scans AGP bridges and AMD northbridges before the PCI subsystem is fully initialized, reserves or allocates a low-memory aperture hole, fixes northbridge aperture registers, and protects kdump/vmcore from reading RAM remapped as a GART aperture.

## Important APIs, Types, and Functions
- Global aperture policy: `gart_iommu_aperture`, `gart_iommu_aperture_disabled`, `gart_iommu_aperture_allowed`, `fallback_aper_order`, `fallback_aper_force`, and `fix_aperture`.
- Core exclusion state: `aperture_pfn_start`, `aperture_page_count`, `gart_mem_pfn_is_ram()`, `gart_oldmem_pfn_is_ram()`, and `exclude_from_core()`.
- Allocation/discovery helpers: `allocate_aperture()`, `find_cap()`, `read_agp()`, and `search_agp_bridge()`.
- Command-line parser: `gart_fix_e820`.
- Early kexec/kdump guard: `early_gart_iommu_check()`.
- Main aperture setup: `gart_iommu_hole_init()`.

## Control Flow
`early_gart_iommu_check()` runs before normal PCI and verifies any already-enabled GART aperture. It scans AGP bridges, reads AMD northbridge aperture base/order/enable state, detects inconsistent nodes, reserves enabled aperture RAM in e820 when requested, and disables GART on all northbridges if no valid AGP bridge owns the aperture.

`gart_iommu_hole_init()` later performs the main fixup. It skips if no AMD GART is present, aperture fixup is disabled, or early PCI access is unavailable. It optionally reads the AGP bridge aperture, walks AMD northbridge ranges, disables GART translation before reconfiguration, records that GART IOMMU should initialize through `x86_init.iommu.iommu_init = gart_iommu_init`, validates each node's aperture base/size, and decides whether firmware setup is usable. If fixup is needed, it uses the AGP aperture or allocates aligned low memory via memblock, excludes the range from core/vmcore, programs all northbridge aperture registers without enabling translation yet, and calls `set_up_gart_resume()` so `amd_gart_64.c` can restore the settings after suspend.

## State and Persistence Behavior
The file mutates e820 reservations, memblock allocations, nosave ranges, vmcore/kcore PFN filters, northbridge PCI config registers, and `x86_init.iommu.iommu_init`. Allocated aperture memory is intentionally lost to normal RAM use. `fallback_aper_order` and command-line flags persist as boot policy.

## Dependencies and Integration Points
It depends on early PCI config access, AMD northbridge detection (`early_is_amd_nb()` and `amd_nb_bus_dev_ranges`), AGP capability parsing, GART register definitions, e820/memblock, kdump/vmcore/kcore callbacks, suspend nosave regions, IOMMU initialization in `amd_gart_64.c`, and x86 init hooks.

## Risks
- Allocating the aperture over RAM permanently removes that RAM from normal use and must be low enough for 32-bit DMA use.
- Incorrect e820 reservation can cause kexec/kdump memory corruption when the first kernel leaves GART enabled.
- The loops directly program PCI config before full PCI enumeration; bad detection can disable or misconfigure real hardware.
- Aperture size/order must match across all northbridges; inconsistent firmware triggers fixup or panic if allocation fails.

## Test Signals
- Boot affected AMD64 systems with broken/missing aperture firmware and memory above 4 GiB.
- Test `gart_fix_e820=0/1`, `iommu=memaper`, `iommu=noaperture`, and fallback aperture sizing.
- Run kexec/kdump and verify vmcore does not read the GART aperture region.
- Suspend/resume with GART fixup and confirm `amd_gart_64.c` restores aperture registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/aperture_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/Makefile

## Purpose
This Makefile controls which x86 local APIC, IO-APIC, IPI, MSI, NMI, and x2APIC implementation objects are built. It also disables KCOV instrumentation for this directory because APIC timer interrupts introduce nondeterministic coverage unrelated to syscall inputs.

## Important APIs, Types, and Functions
- Build policy: `KCOV_INSTRUMENT := n`.
- Local APIC objects under `CONFIG_X86_LOCAL_APIC`: `apic.o`, `apic_common.o`, `apic_noop.o`, `ipi.o`, `vector.o`, `init.o`, and `probe_$(BITS).o`.
- Always-built object: `hw_nmi.o`.
- IOAPIC/MSI/SMP objects: `io_apic.o`, `msi.o`, and `ipi.o` under their corresponding configs.
- 64-bit x2APIC/probe ordering: `apic_numachip.o`, `x2apic_uv_x.o`, `x2apic_savic.o`, `x2apic_phys.o`, `x2apic_cluster.o`, and `apic_flat_64.o`.

## Control Flow
Kbuild evaluates configuration symbols and appends matching objects to `obj-y` or `obj-*`. The object order is significant: the 64-bit APIC probe depends on listing order, and the 32-bit `probe_$(BITS).o` object is explicitly listed last.

## State and Persistence Behavior
The file has no runtime state, but it persists architecture build composition. Changing object order or config conditions changes which APIC drivers are linked and the order in which probe data is available.

## Dependencies and Integration Points
It integrates x86 APIC source files with Kbuild, KCOV, local APIC configuration, IOAPIC, PCI MSI, SMP IPI support, Numachip, UV, AMD Secure AVIC, and x2APIC physical/cluster modes. The compiled objects are consumed by early APIC probing and interrupt setup used by ACPI/MADT boot code.

## Risks
- Reordering 64-bit APIC objects can change APIC probe selection.
- Instrumenting APIC interrupt code with KCOV would make coverage nondeterministic.
- `ipi.o` appears under both local APIC and SMP conditions; configuration changes must avoid duplicate or missing linkage.
- Moving 32-bit probe earlier can break the explicit "listed last" requirement.

## Test Signals
- Build matrix with `CONFIG_X86_LOCAL_APIC`, `CONFIG_X86_IO_APIC`, `CONFIG_PCI_MSI`, `CONFIG_SMP`, and 64-bit x2APIC platform options.
- Inspect link order in verbose Kbuild output when changing APIC probe objects.
- Run KCOV workloads and confirm APIC timer interrupts do not create random coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/apic/Makefile -->
