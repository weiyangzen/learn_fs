# Research: subset-b-000869

This grouped report covers x86 perf-event, Hyper-V, IA32 audit, ACPI/platform, and AMD helper sources under `sources/distributed-fs/ceph-client`. Each section is delimited for reconciliation into the requested source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/perf_event.h -->
## `sources/distributed-fs/ceph-client/arch/x86/events/perf_event.h`

Purpose: central private contract for the x86 perf-event subsystem. It defines the data structures, event flags, scheduling constraints, PMU operation table, per-CPU PMU state, Intel PEBS/LBR/Topdown support, AMD BRS/LBR hooks, and vendor init entry points used by the x86 perf backends.

Important APIs, types, and functions: `struct event_constraint` and the `EVENT_CONSTRAINT*` macros describe legal counter placement; `struct extra_reg` and `struct intel_shared_regs` manage event-specific shared MSRs; `struct cpu_hw_events` is the per-CPU active-event state; `struct x86_pmu` is the main backend vtable; `struct x86_hybrid_pmu` holds hybrid-core PMU overrides. Inline helpers include `is_topdown_event()`, `x86_pmu_config_addr()`, `__x86_pmu_enable_event()`, `x86_pmu_disable_event()`, `kernel_ip()`, and `set_linear_ip()`.

Control flow and integration: generic perf code calls into the `x86_pmu` callbacks for add/delete/start/stop/read/IRQ and hardware configuration. Model-specific backends populate `x86_pmu`, constraints, cache-event maps, PEBS constraints, LBR methods, and sysfs format/event attributes. Static calls wrap hot paths such as period setting, counter update, PEBS draining, and PEBS enable/disable. Hybrid support transparently resolves global fields to per-PMU fields through `hybrid()`, `hybrid_var()`, and `hybrid_bit()`.

State and persistence: most state is per-CPU (`cpu_hw_events`, `pmc_prev_left`) or global read-mostly backend metadata (`x86_pmu`, capability masks, constraint arrays). Hardware state is persistent in PMU MSRs until explicitly disabled or overwritten. Extra-register references use locking and atomic refs because sibling threads or events can share MSRs.

Dependencies and integration points: depends on Linux perf core, x86 MSR accessors, Intel debug store, XSAVE/LBR definitions, APIC/NMI perf interrupts, KVM guest/host masks, CPU feature config, and vendor backends (`intel_pmu_init()`, `amd_pmu_init()`, `zhaoxin_pmu_init()`). The header also exposes sysfs event formatting helpers and branch classification constants consumed by `utils.c`.

Risks: constraint macros are scheduler-critical; bad masks can silently mis-schedule events or cause factorial retry costs for overlap constraints. MSR writes must respect virtualization masks and counter-pair state. Compile-time feature guards must keep stubs behaviorally compatible. PEBS/LBR and hybrid fields are highly coupled to CPU model detection.

Test signals: successful kernel build across Intel/AMD/Zhaoxin and feature-disabled configs; perf selftests for raw events, fixed counters, topdown, PEBS/LBR, and hybrid PMUs; boot logs showing PMU init; `perf stat`, `perf record`, and NMI overflow behavior on supported hardware and virtualized guests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/perf_event_flags.h -->
## `sources/distributed-fs/ceph-client/arch/x86/events/perf_event_flags.h`

Purpose: single-source list of x86 architecture-specific `hw_perf_event.flags` bits. It is intentionally included twice by `perf_event.h`: once to generate enum constants and once to validate that each value stays inside `PERF_EVENT_FLAG_ARCH`.

Important APIs and types: each line is a `PERF_ARCH(name, value)` macro expansion. The flags describe PEBS latency/store/load modes, exclusive counter accounting, dynamic constraints, PEBS counter snapshots, auto-reload, large PEBS, PEBS via Intel PT, counter pairs, LBR select save/restore, Topdown events, AMD BRS, branch counters, ACR, and unprivileged events.

Control flow and integration: no runtime control flow. Backends set these bits during event configuration or constraint matching; generic x86 perf code reads them through helpers such as `is_counter_pair()`, `has_amd_brs()`, `is_topdown_count()`, and group leader checks.

State and persistence: values are ABI-like within the x86 perf implementation because they are embedded in in-kernel event state. They are not direct userspace ABI but must remain unique and non-overlapping.

Dependencies and integration points: included only in `perf_event.h`; depends on `PERF_ARCH` being defined by the includer. Flags are consumed by Intel PEBS, AMD BRS, branch stack, ACR, and scheduling code.

Risks: duplicate bits or bits outside the arch flag range would corrupt event interpretation. Adding a flag without updating relevant scheduling, PEBS, or read paths can create events that configure successfully but behave incorrectly.

Test signals: compile-time static assertions in `perf_event.h`, build coverage with all vendor PMU configs, and perf tests for the feature paths associated with any changed flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/perf_event_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/probe.c -->
## `sources/distributed-fs/ceph-client/arch/x86/events/probe.c`

Purpose: probes arrays of perf MSR descriptors and controls sysfs visibility for event groups whose backing MSRs are unavailable or zero.

Important APIs and functions: `perf_msr_probe(struct perf_msr *msr, int cnt, bool zero, void *data)` iterates a descriptor array, applies optional per-entry `test()` filtering, safely reads the MSR with `rdmsrq_safe()`, optionally rejects zero-valued counters, and returns an availability bitmask. `not_visible()` is assigned to an attribute group to hide unsupported sysfs entries.

Control flow: the probe rejects overly large arrays (`cnt >= BITS_PER_LONG`), hides each checked group by default, skips empty descriptors, applies the descriptor-specific predicate, verifies MSR readability, checks the masked value when zero counters are disallowed, and restores default visibility for entries that pass.

State and persistence: mutates `struct attribute_group.is_visible` for the groups referenced by descriptors; returns transient bit state to the caller. It does not retain private state.

Dependencies and integration points: exported GPL symbol used by RAPL and similar PMU drivers. Depends on `struct perf_msr` from `probe.h`, x86 MSR helpers, sysfs attribute groups, and descriptor masks.

Risks: changing group visibility has global sysfs consequences. A descriptor with `no_check` bypasses all validation and always sets availability, so callers must only use it when the MSR is known present. Virtualization may make read-only MSR presence ambiguous; the code deliberately treats read failures as absence.

Test signals: RAPL PMU sysfs event visibility on systems with partial domains, virtualized boots without RAPL MSRs, and build/load tests for modules using `perf_msr_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/probe.h -->
## `sources/distributed-fs/ceph-client/arch/x86/events/probe.h`

Purpose: declares the perf MSR probing descriptor and helper macros for simple PMU event sysfs groups.

Important APIs and types: `struct perf_msr` contains the MSR number, optional attribute group, optional predicate, `no_check` bypass, and value mask. `perf_msr_probe()` is declared for users such as RAPL. `PMU_EVENT_GROUP()` builds a one-attribute sysfs event group around an existing `attr_*` symbol.

Control flow: no runtime logic in the header; it provides the data contract consumed by `probe.c`.

State and persistence: descriptor arrays are normally static model tables. The pointed `attribute_group` objects may be mutated by `perf_msr_probe()` to hide or reveal events.

Dependencies and integration points: depends on `<linux/sysfs.h>` and x86 perf-event users. RAPL uses this contract to map hardware domain MSRs to perf event groups.

Risks: descriptor arrays with missing groups or wrong masks can hide valid events or expose unsupported ones. The `PMU_EVENT_GROUP` macro assumes naming conventions (`attr_<name>`) and should be used only where that generated symbol exists.

Test signals: compile coverage of descriptor arrays; sysfs event files appear only for present MSRs; probing returns correct bitmasks on platforms with known domain support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/probe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/rapl.c -->
## `sources/distributed-fs/ceph-client/arch/x86/events/rapl.c`

Purpose: implements the Intel/AMD RAPL perf PMUs for read-only energy counters. It exposes package/die scoped `power` events and, on AMD/Hygon, per-core `power_core` energy events.

Important APIs, types, and functions: `struct rapl_pmu` tracks one topology-scoped PMU instance, active events, and overflow-prevention hrtimer. `struct rapl_pmus` owns the perf `pmu`, counter mask, and indexed PMU instances. `struct rapl_model` maps CPU models to MSR tables and energy domains. Core operations are `rapl_pmu_event_init()`, `add()`, `start()`, `stop()`, `read()`, `rapl_event_update()`, `rapl_check_hw_unit()`, `init_rapl_pmus()`, and module init/exit.

Control flow: module init matches CPU model/feature, reads the energy unit MSR, computes a conservative timer interval, allocates per-package/die/core PMU objects, probes domain MSRs with `perf_msr_probe()`, registers PMUs, and advertises units. Event init validates type, system-wide CPU binding, no sampling, config bits, supported domain bit, topology index, and assigns `pmu_private`. Active events are list-managed under a raw spinlock. The hrtimer periodically updates software counts so 32-bit hardware counters do not wrap unnoticed.

State and persistence: energy MSRs are free-running hardware counters shared with other tools. Software state includes global model pointer, hardware unit arrays, `rapl_pmus_pkg/core`, per-PMU active lists, and event `prev_count`/`count`. No persistent storage beyond kernel lifetime.

Dependencies and integration points: Linux perf core, hrtimers, topology package/die/core IDs, x86 CPU model matching, MSR reads, `probe.c`, and sysfs event/format groups. Event counts are fixed-point 32.32 Joules and userspace scales using the exposed `.scale` files.

Risks: unit quirks are model-specific; wrong unit means wrong energy reporting. Topology index failures disable events on unusual CPU maps. The core-scope branch validates against the package-domain maximum, which warrants regression attention. Hrtimer/list locking must prevent update-vs-stop races.

Test signals: `perf list | grep power`, sysfs `events/*.{unit,scale}`, `perf stat -a -e power/energy-pkg/ sleep 1`, wrap behavior under long runs, model-specific domain visibility, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/rapl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/utils.c -->
## `sources/distributed-fs/ceph-client/arch/x86/events/utils.c`

Purpose: decodes x86 control-flow instructions around LBR/perf branch samples and maps x86-internal branch classifications to generic perf branch types.

Important APIs and functions: `branch_type()`, `branch_type_fused()`, and `common_branch_type()` are exported through `perf_event.h`. Internally, `decode_branch_type()` classifies decoded opcodes, and `get_branch_type()` safely fetches instruction bytes from user or kernel text, handles transaction aborts, optional fused-branch scanning, privilege-level tagging, and IRQ/fault inference.

Control flow: for user addresses the code uses `copy_from_user_nmi()` and requires a current mm; for kernel addresses it checks `kernel_text_address()` and rejects gate areas. It initializes the x86 instruction decoder with ABI mode, decodes one instruction, optionally scans forward up to `MAX_INSN_SIZE` for fused branches, then combines branch kind with target user/kernel bits.

State and persistence: no persistent state. It reads current task/register mode and text mappings at classification time.

Dependencies and integration points: `asm/insn.h`, NMI-safe user copying, kernel text validation, perf branch enum values, and branch constants from `perf_event.h`. Intel and AMD LBR/BRS paths use these helpers to enrich branch stack samples.

Risks: instruction fetch occurs in perf/NMI-sensitive paths, so it must avoid unsafe kernel reads from attacker-controlled addresses. Misclassification affects profiling quality rather than normal execution, but unsafe fetches would be serious. Fused scanning must not run past the copied byte window.

Test signals: perf LBR branch stack samples for syscalls, returns, indirect calls, conditional branches, interrupts, and fused branches; fault-injection with unmapped user text; KASAN/lockdep/NMI safety coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/Makefile -->
## `sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/Makefile`

Purpose: builds the Zhaoxin x86 PMU backend object.

Important APIs and build rules: `obj-y += core.o` unconditionally includes `core.o` when the parent Kbuild selects this directory.

Control flow: no runtime control flow. Build selection happens in the parent perf-event Makefile and CPU vendor config; this file only contributes the implementation object.

State and persistence: no runtime state.

Dependencies and integration points: the object depends on `core.c`, shared x86 perf symbols, and config paths that include the Zhaoxin events directory.

Risks: because the file is minimal, risks are selection-related: a wrong parent Kbuild condition could omit or include the backend unexpectedly.

Test signals: kernel build with `CONFIG_CPU_SUP_ZHAOXIN` or related vendor support; link succeeds and `zhaoxin_pmu_init()` is available when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/core.c -->
## `sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/core.c`

Purpose: implements the Zhaoxin PMU backend, modeled after Intel Architectural PerfMon v2 but with ZXC/ZXD/ZXE-specific event maps, fixed-counter constraints, overflow acknowledgement, and cache-event tables.

Important APIs and functions: `zhaoxin_pmu_init()` detects supported CPUID version/family/model and populates global `x86_pmu`. Runtime callbacks include `zhaoxin_pmu_handle_irq()`, `zhaoxin_pmu_enable_all()`, `disable_all()`, `enable_event()`, `disable_event()`, `event_map()`, and `get_event_constraints()`. Static maps define generic perf events and cache event encodings for ZXD/ZXE.

Control flow: init requires architectural perfmon CPUID leaf 10, version 2, and known Zhaoxin family/model. ZXC disables several generic events and uses special status-clear behavior requiring global control to be enabled. ZXD/ZXE install cache maps and branch event encodings. IRQ handling disables all counters, reads global overflow status, acknowledges status, ignores condition-changed bit 63, updates and reloads each active overflowing event, invokes `perf_event_overflow()`, loops while status remains, then reenables counters.

State and persistence: global `x86_pmu` and shared `hw_cache_event_ids` are initialized at boot. Hardware state lives in Zhaoxin performance MSRs, global control/status/overflow-control registers, fixed counter control, and per-event `hw_perf_event` state.

Dependencies and integration points: depends on shared x86 perf scheduling and counter update code, APIC perf NMIs, CPUID model data, MSR helpers, and sysfs format/event display from `perf_event.h`.

Risks: event encodings and constraints are model-specific; wrong tables produce misleading counts or unusable fixed counters. ZXC acknowledgement ordering is special. IRQ loops must avoid losing overflow bits while preventing repeated false handling of bit 63.

Test signals: boot on ZXC/ZXD/ZXE reports the selected event family; `perf stat` for cycles/instructions/cache/branch events; overflow sampling; fixed counter use; CPUID-unavailable events hidden through the quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/zhaoxin/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/Makefile -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/Makefile`

Purpose: selects x86 Hyper-V integration objects and generated assembly-offset headers.

Important build rules: base objects are `hv_init.o`, `mmu.o`, `nested.o`, `irqdomain.o`, and `ivm.o`. x86-64 adds `hv_apic.o`; VTL mode adds `hv_vtl.o` and `mshv_vtl_asm.o`; paravirt spinlocks add `hv_spinlock.o`; root crash dump support adds `hv_crash.o` and `hv_trampoline.o`. `mshv_vtl_asm.o` depends on generated `mshv-asm-offsets.h`, produced from `mshv-asm-offsets.s` via `filechk`.

Control flow: build-time only. It also removes profiling and stack protector from `hv_trampoline.o` for crash-path assembly safety.

State and persistence: no runtime state, but generated offset headers are build artifacts and cleaned by `clean-files`.

Dependencies and integration points: x86 Hyper-V Kconfig symbols, kbuild offset generation, crash dump, VTL, paravirt spinlock, and x86-64 build constraints.

Risks: missing offset dependency would break VTL assembly when context layout changes. Incorrect instrumentation flags on crash trampoline code could make devirtualization entry unsafe.

Test signals: clean incremental builds across combinations of `CONFIG_HYPERV_VTL_MODE`, `CONFIG_PARAVIRT_SPINLOCKS`, `CONFIG_MSHV_ROOT`, and `CONFIG_CRASH_DUMP`; generated `mshv-asm-offsets.h` updates when `struct mshv_vtl_cpu_context` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_apic.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_apic.c`

Purpose: installs Hyper-V enlightened APIC operations for EOI/TPR/ICR access and IPI delivery.

Important APIs and functions: `hv_apic_init()` patches the global APIC callbacks. `hv_enable_coco_interrupt()` updates vector injection state. `hv_apic_read/write/icr_read/icr_write/eoi_write()` route selected APIC accesses through synthetic Hyper-V MSRs. `__send_ipi_one()`, `__send_ipi_mask()`, and `__send_ipi_mask_ex()` implement fast and extended IPI hypercalls.

Control flow: initialization checks Hyper-V recommendation hints. Cluster IPI support replaces APIC IPI callbacks while retaining `orig_apic` fallback. APIC access recommendation replaces EOI and, in xAPIC mode, read/write/ICR accessors. IPI senders validate vectors, translate Linux CPUs to Hyper-V VP numbers, use the fast 64-bit mask hypercall when possible, fall back to extended VP sets for larger VP indexes, and finally fall back to original APIC operations on unsupported cases.

State and persistence: `orig_apic` snapshots previous APIC methods. VP assist pages can suppress EOI MSR writes via lazy EOI. Per-CPU hypercall input pages are used transiently with interrupts disabled.

Dependencies and integration points: `ms_hyperv` hints/features, Hyper-V hypercall helpers, APIC callback patching, CPU-to-VP mapping, tracing, confidential-computing isolation checks, and VP assist pages allocated in `hv_init.c`.

Risks: wrong fallback behavior can lose IPIs. VP set construction must handle sparse/high VP indexes. Lazy EOI cannot be used under some confidential VM modes. IPI paths run with tight interrupt and ordering constraints.

Test signals: SMP boot and CPU hotplug under Hyper-V, high CPU-count guests requiring extended masks, interrupt delivery tests, APIC timer operation, and tracepoints for IPI calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_apic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_crash.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_crash.c`

Purpose: root-partition Hyper-V crash/kdump support. It coordinates Linux and hypervisor crash handling, devirtualizes the root partition through a disable-hypervisor hypercall, and allows hypervisor RAM to be captured in vmcore.

Important APIs and functions: `hv_root_crash_init()` registers NMI handling, locates the hypervisor crash dump area, sets up trampoline/page tables, and overrides crash stop handling. `hv_crash_nmi_local()`, `hv_crash_stop_other_cpus()`, and `crash_nmi_callback()` synchronize CPUs and invoke `HVCALL_DISABLE_HYP_EX`. `hv_crash_c_entry()` restores long-mode kernel CPU state after the assembly trampoline returns. Helper setup functions build low-4G trampoline data and temporary page tables.

Control flow: on hypervisor crash, NMIs arrive and the shared crash dump area marks the condition. On Linux crash, the panic CPU sends NMIs to others. Non-BSP CPUs save state and spin; BSP waits for quorum, optionally notifies Hyper-V of root crash, saves CPU context, fixes TSS/page tables, issues the disable hypercall, and resumes via `hv_trampoline.S` into `hv_crash_c_entry()`, which restores registers and calls crash kexec.

State and persistence: global crash context, crash dump area pointer `hv_cda`, low-memory trampoline physical address, temporary page tables, CPU wait count, and booleans tracking hypervisor/Linux crash. Enables `crash_kexec_post_notifiers` and `hv_crash_enabled`.

Dependencies and integration points: Hyper-V root partition hypercalls, NMI subsystem, crash/kexec, APIC NMI delivery, page table primitives, GDT/IDT/TSS manipulation, Intel PT emergency stop, and the matching trampoline assembly.

Risks: this is panic/NMI/devirtualization code with little recovery latitude. Low-4G allocation, 5-level paging exclusion, exact struct offsets, TSS busy-bit handling, and interrupt-free hypercall buffers are critical. Wrong context restore can hang before vmcore capture.

Test signals: root partition kdump with loaded crash kernel, hypervisor crash simulation, Linux panic on BSP and non-BSP CPUs, no 5-level paging path, vmcore contains hypervisor RAM, and boot log says both Linux and hypervisor kdump support enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_init.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_init.c`

Purpose: main x86 Hyper-V initialization, CPU lifecycle, hypercall page setup, VP assist pages, reenlightenment, hibernation syscore operations, panic reporting, PCI quirks, and initialization status helpers.

Important APIs and functions: exported state includes `hv_hypercall_pg`, `hv_ghcb_pg`, and `hv_vp_assist_page`. Key functions are `hyperv_init()`, `hyperv_cleanup()`, `hv_cpu_init()`, `hv_cpu_die()`, `set_hv_tscchange_cb()`, `clear_hv_tscchange_cb()`, `hyperv_stop_tsc_emulation()`, `hyperv_report_panic()`, `hv_is_hyperv_initialized()`, and `hv_apicid_to_vp_index()`. x86-64 uses a static call for `hv_std_hypercall()`.

Control flow: `hyperv_init()` verifies the Hyper-V hypervisor, runs common init, allocates VP assist/GHCB state, registers CPU hotplug callbacks, writes guest OS ID, initializes or skips the hypercall page depending on isolation/paravisor mode, calls root crash init when appropriate, hooks timers/APIC/PCI/MSI domains, queries capabilities, records VTL, and optionally starts VTL early init. CPU online allocates/maps VP assist pages, enables the VP assist MSR, maps GHCB pages for SNP paravisor, and enables stimer vector injection. Suspend disables hypercalls and CPU0 state; resume reinitializes and restores.

State and persistence: global hypercall page pointer and static-call target, saved hypercall pointer across hibernation, per-CPU GHCB mappings, per-CPU VP assist pages, reenlightenment callback, and Hyper-V MSR-programmed guest ID/hypercall state.

Dependencies and integration points: Hyper-V common code, APIC and timer setup, syscore, cpuhotplug, GHCB/SNP/TDX isolation helpers, root crash support, PCI/MSI IRQ domain, VMBus hypercall pages, and x86 initialization hooks.

Risks: early boot order is delicate: LAPIC timers, hypercall page permissions, confidential VM page encryption, and static-call updates must occur in the right context. Panic cleanup avoids `static_call_update()` after CPUs stop. VP assist page zeroing prevents lazy-EOI offline hangs.

Test signals: Hyper-V guest boot, root partition boot, TDX/SNP paravisor and no-paravisor paths, CPU hotplug, hibernation, reenlightenment/TSC frequency changes, panic MSR reporting, and `hv_is_hyperv_initialized()` consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_spinlock.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_spinlock.c`

Purpose: installs Hyper-V paravirtual queued spinlock waiting/kicking operations so vCPUs can enter a hypervisor idle state while spinning.

Important APIs and functions: `hv_init_spinlocks()` patches `pv_ops_lock`; `hv_qlock_wait()` waits via `HV_X64_MSR_GUEST_IDLE`; `hv_qlock_kick()` sends an IPI to wake a waiting CPU; `hv_vcpu_is_preempted()` is a stub returning false; `hv_parse_nopvspin()` handles `hv_nopvspin`.

Control flow: initialization requires the command-line feature not disabled, APIC availability, Hyper-V cluster IPI recommendation, and guest-idle MSR support. Wait disables interrupts, rechecks the lock byte against the expected value to avoid missed wakeups, reads the guest-idle MSR, and restores interrupts. Kick sends `X86_PLATFORM_IPI_VECTOR`.

State and persistence: `hv_pvspin` is boot-time state. Runtime state is in global paravirt lock ops; no private per-lock state is stored here.

Dependencies and integration points: paravirt queued spinlock core, APIC IPI send, Hyper-V feature/hint bits, and MSR access.

Risks: the race between unlock IPI and entering guest idle is the central hazard; interrupt disabling and lock-byte recheck are required. NMI context cannot safely idle and returns immediately.

Test signals: boot logs for enabled/disabled PV spinlocks, lock stress under Hyper-V, command-line `hv_nopvspin`, and no CPU offline or spinlock hang under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_trampoline.S -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_trampoline.S`

Purpose: low-level trampoline used after Hyper-V root devirtualization. Hyper-V calls this copied low-4G code in 32-bit protected mode; it restores paging and long mode, switches to kernel page tables, and jumps to the C crash entry.

Important APIs and labels: `hv_crash_asm32`, `hv_crash_asm64`, and `hv_crash_asm_end` are consumed by `hv_crash.c`. The `HV_CRASHDATA_OFFS_*` constants define exact offsets into `struct hv_crash_tramp_data` and must match build-time checks in C.

Control flow: 32-bit entry enables PAE, loads temporary CR3, sets EFER.LME, enables paging, loads a temporary GDT, and far-jumps to a 64-bit code selector. The 64-bit entry loads the kernel CR3 and jumps indirectly to the saved C entry address.

State and persistence: no persistent state; it consumes the trampoline data block at the physical address passed in `EDI`. It temporarily changes CR0/CR3/CR4/EFER/GDT/CS during crash recovery.

Dependencies and integration points: `hv_crash.c` copies this code to a DMA32 page and builds the matching data and page tables. Uses x86 processor flag definitions and ENDBR/retpoline annotations.

Risks: no stack is available and compile/link-time addresses are invalid after copying, so only offset-based addressing is safe. Offset drift, instrumentation, stack protector, or profiling would break the path.

Test signals: root crash devirtualization reaches `hv_crash_c_entry()` and kexecs; build validates C/assembly offsets; objtool accepts intentional nonstandard control flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_trampoline.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_vtl.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_vtl.c`

Purpose: supports Linux running in a non-default Hyper-V Virtual Trust Level, especially VTL2. It disables firmware assumptions, implements AP bring-up through Hyper-V VTL hypercalls, and provides VTL return-call support.

Important APIs and functions: `hv_vtl_init_platform()` rewrites x86 platform hooks for VTL mode; `hv_vtl_early_init()` installs restart and AP wakeup overrides; `hv_vtl_wakeup_secondary_cpu()` maps APIC ID to VP index; `hv_vtl_bringup_vcpu()` builds 64-bit CPU context and issues `HVCALL_ENABLE_VP_VTL`/`HVCALL_START_VP`; `mshv_vtl_return_call_init()` and `mshv_vtl_return_call()` wrap the VTL return hypercall.

Control flow: early init rejects XSAVE, installs a dummy real-mode header, and patches AP startup. Platform init disables BIOS/real-mode/legacy device paths and uses triple fault for restart. AP bring-up obtains idle stack and current GDT/IDT/TSS/LDT state, fills the Hyper-V VP context with long-mode descriptors/control registers, enables the target VTL, and starts the VP at `hv_vtl_ap_entry()`.

State and persistence: stores VTL state in `ms_hyperv.vtl`, a static real-mode header, and a static call for VTL return. `mshv_vtl_return_call()` temporarily uses VP assist return registers and FPU save/restore around the transition.

Dependencies and integration points: Hyper-V hypercalls, APIC callback replacement, x86 platform init hooks, GDT/IDT/TSS descriptors, FPU state management, and `mshv_vtl_asm.S`.

Risks: AP context values are architectural and exact; wrong descriptors or control registers prevent secondary CPU startup. XSAVE is explicitly unsupported. FPU handling and VTL transition assembly must remain noinstr-safe.

Test signals: VTL2 boot, secondary CPU bring-up, restart via triple fault, VTL return hypercall round trips, and boot failure when XSAVE is not disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_vtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/irqdomain.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/irqdomain.c`

Purpose: implements IRQ and MSI mapping for Linux running as the Hyper-V root partition, translating Linux IRQ affinity/vector choices into Microsoft Hypervisor device-interrupt mappings.

Important APIs and functions: `hv_map_interrupt()` and `hv_unmap_interrupt()` issue core map/unmap hypercalls. Exported wrappers include `hv_map_msi_interrupt()`, `hv_map_ioapic_interrupt()`, and `hv_unmap_ioapic_interrupt()`. PCI MSI support includes `hv_build_pci_dev_id()`, `hv_irq_compose_msi_msg()`, `hv_teardown_msi_irq()`, `hv_create_pci_msi_domain()`, and MSI parent/domain ops.

Control flow: mapping builds a device ID, fixed interrupt descriptor, target vector, trigger mode, and sparse VP set for the target CPU, then performs `HVCALL_MAP_DEVICE_INTERRUPT`. MSI compose unmaps any previous entry because retargeting cannot change vector or outside-VP set, maps a fresh entry, stores it in `irq_data.chip_data`, and converts the returned Hyper-V entry to `struct msi_msg`. Free tears down stored mappings.

State and persistence: per-IRQ `chip_data` stores the Hyper-V interrupt entry needed for unmap. The created MSI domain persists for the root partition. Hypervisor mapping state persists until explicitly unmapped.

Dependencies and integration points: PCI/MSI core, x86 vector domain, Hyper-V current partition ID, per-CPU hypercall buffers, VP-set helpers, IRQ affinity, and IOAPIC routing.

Risks: stale `chip_data` or missed unmap leaks hypervisor mappings. PCI alias/PCI-X bridge shadow bus range handling is required for correct device IDs. Domain free currently gets irq data using `virq` in the loop, a detail worth regression scrutiny for multi-IRQ frees.

Test signals: PCI MSI/MSI-X devices in root partition, IRQ affinity changes, device remove/reprobe, IOAPIC interrupt mapping, and hypercall error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/irqdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/ivm.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/ivm.c`

Purpose: Hyper-V isolated VM support for AMD SEV-SNP, Intel TDX, paravisor-mediated MSR/hypercalls, AP startup, and vTOM shared/private memory visibility.

Important APIs and functions: SNP/paravisor functions include `hv_ghcb_hypercall()`, `hv_ghcb_negotiate_protocol()`, `hv_ghcb_terminate()`, GHCB MSR read/write helpers, `hv_snp_boot_ap()`, and `hv_snp_hypercall()`. TDX functions include `hv_tdx_msr_read/write()` and `hv_tdx_hypercall()`. Shared wrappers are `hv_ivm_msr_read/write()`, `hv_vtom_init()`, `hv_get_isolation_type()`, `hv_is_isolation_supported()`, `hv_isolation_type_snp()`, and `hv_isolation_type_tdx()`.

Control flow: SNP paravisor paths use a per-CPU GHCB page, fill Hyper-V-specific hypercall fields, and execute `VMGEXIT`. Fully enlightened SNP AP boot constructs a VMSA, marks it as VMSA with `RMPADJUST`, and starts the VP. TDX paths use GHCI hypercalls for MSR and Hyper-V calls. vTOM initialization sets confidential-computing masks, adjusts physical address mask, installs encryption-status-change hooks, and forces WB MTRR state.

State and persistence: tracks GHCB protocol version, per-CPU VMSA pages, a global list of PFN regions made host-visible, static keys for isolation type, and platform encryption hooks. Hypervisor host-visibility state persists until reversed, especially around kexec/kdump.

Dependencies and integration points: AMD SEV/SNP GHCB, RMPADJUST, Intel TDX module calls, Hyper-V isolation fields, memory encryption APIs, x86 platform guest hooks, VMBus shared pages, IOAPIC/vTPM private MMIO, and kexec conversion stop hooks.

Risks: host visibility accounting must stay consistent on hypercall failures. Clearing PTE present bits avoids paravisor #VC/#VE issues during transitions but must always restore them. AP VMSA allocation has a potential leak path if VP index lookup fails after allocation. NMI use of GHCB hypercalls is warned against.

Test signals: SNP and TDX Hyper-V isolated boots, paravisor/no-paravisor hypercalls, AP startup, memory share/unshare with VMBus, kexec/kdump clearing host visibility, and static-key detection of isolation type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/ivm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/mmu.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/mmu.c`

Purpose: replaces remote TLB shootdowns with Hyper-V hypercalls when the hypervisor recommends enlightened remote TLB flushes.

Important APIs and functions: `hyperv_setup_mmu_ops()` installs `hyperv_flush_tlb_multi()` into `pv_ops.mmu.flush_tlb_multi`. `fill_gva_list()` encodes page ranges into Hyper-V GVA list entries. `hyperv_flush_tlb_others_ex()` handles extended VP-set hypercalls.

Control flow: flush builds an address-space identifier from CR3 without PCID bits or requests all address spaces, converts CPU masks to VP masks or extended VP sets, skips lazy CPUs unless freed page tables require flushing, chooses address-space vs address-list hypercalls based on `TLB_FLUSH_ALL` and GVA capacity, and falls back to `native_flush_tlb_multi()` on unsupported status or missing hypercall page.

State and persistence: no persistent private state beyond the installed paravirt op. It uses per-CPU hypercall input pages while interrupts are disabled.

Dependencies and integration points: Hyper-V hints, x86 TLB state, per-CPU `cpu_tlbstate_shared.is_lazy`, CR3/address-space semantics, tracepoints, VP-set helpers, and native TLB fallback.

Risks: incorrect lazy CPU skipping can leave stale translations. GVA encoding packs page counts in low address bits and must respect maximum rep count. Extended hypercall variable headers must compute `max_gvas` correctly.

Test signals: memory-management stress under Hyper-V, high CPU-count guests, lazy TLB workloads, page table free paths, tracepoints, and fallback behavior when hypercalls fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv-asm-offsets.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv-asm-offsets.c`

Purpose: generates assembly offset definitions for `struct mshv_vtl_cpu_context` fields used by VTL transition assembly.

Important APIs and functions: `common()` emits `OFFSET()` records for general-purpose registers and `cr2` when `CONFIG_HYPERV_VTL_MODE` is enabled. The output is post-processed by kbuild into `mshv-asm-offsets.h`.

Control flow: build-time only; no runtime code is intended. `COMPILE_OFFSETS` selects offset-generation behavior.

State and persistence: generated header is a build artifact; no runtime state.

Dependencies and integration points: `<linux/kbuild.h>`, `asm/mshyperv.h`, the Hyper-V Makefile dependency for `mshv_vtl_asm.o`, and `mshv_vtl_asm.S` symbolic offsets.

Risks: missing a field used in assembly or stale generated headers would corrupt register save/restore during VTL return. The config guard must align with assembly inclusion.

Test signals: rebuild after changing `struct mshv_vtl_cpu_context`, generated header contains all referenced offsets, and VTL transition tests preserve registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv-asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv_vtl_asm.S -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv_vtl_asm.S`

Purpose: implements the noinstr assembly context switch for returning from the current VTL to VTL0 through a Hyper-V static-call trampoline.

Important APIs and labels: `__mshv_vtl_return_call(struct mshv_vtl_cpu_context *vtl0)` is called by `hv_vtl.c`. It uses generated `MSHV_VTL_CPU_CONTEXT_*` offsets. A discard-addressable record keeps the static-call key symbol reachable.

Control flow: the function saves host callee-saved registers, loads guest/VTL0 registers from the context, restores guest CR2, pushes host `rax/rcx`, calls the configured `__mshv_vtl_return_hypercall`, then saves returned guest registers and CR2 back into the context before restoring host callee-saved registers and returning.

State and persistence: mutates the caller-provided `mshv_vtl_cpu_context`. Uses stack for temporary host register storage. Does not maintain global state itself; the static-call target is initialized by C.

Dependencies and integration points: `mshv-asm-offsets.h`, static call infrastructure, Hyper-V VTL return hypercall page offset, and C-side FPU save/restore around the call.

Risks: this runs in `.noinstr.text`, so instrumentation must not be introduced. Register clobber assumptions are strict: the VTL switch preserves only `rax/rcx` by contract, and CR2 handling protects fault state.

Test signals: VTL transitions preserve all saved registers and CR2, objtool/noinstr validation, and static-call target initialization before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv_vtl_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/nested.c -->
## `sources/distributed-fs/ceph-client/arch/x86/hyperv/nested.c`

Purpose: provides Hyper-V nested virtualization helpers to flush guest physical mappings by address space or ranges.

Important APIs and functions: exported functions are `hyperv_flush_guest_mapping()`, `hyperv_fill_flush_guest_mapping_list()`, and `hyperv_flush_guest_mapping_range()`. The range helper accepts a callback of type `hyperv_fill_flush_list_func`.

Control flow: whole-address-space flush validates the hypercall page and per-CPU input buffer, fills `address_space`, and issues `HVCALL_FLUSH_GUEST_PHYSICAL_ADDRESS_SPACE`. Range flush invokes the caller-provided fill callback, then issues `HVCALL_FLUSH_GUEST_PHYSICAL_ADDRESS_LIST` as a rep hypercall. The list filler compresses contiguous GFNs into Hyper-V entries with `additional_pages`, bounded by `HV_MAX_FLUSH_REP_COUNT` and `HV_MAX_FLUSH_PAGES`.

State and persistence: no private persistent state. Uses per-CPU hypercall input pages with interrupts disabled. Traces return status.

Dependencies and integration points: exported for nested Hyper-V/KVM integration, Hyper-V hypercall helpers, TLB flushing definitions, and tracepoints.

Risks: missing hypercall page returns `-ENOTSUPP`; callers need fallback. Range list overflow returns `-ENOSPC`, and callers should switch to broader flushes. Input buffers are per-CPU and require interrupts disabled.

Test signals: nested virtualization workloads with guest mapping invalidations, large range flushes forcing fallback, hypercall failure tracepoints, and module users resolving GPL exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/hyperv/nested.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ia32/Makefile -->
## `sources/distributed-fs/ceph-client/arch/x86/ia32/Makefile`

Purpose: builds IA32 emulation support objects for x86, currently the audit syscall classification object when audit is enabled.

Important build rules: `audit-class-$(CONFIG_AUDIT) := audit.o` and `obj-$(CONFIG_IA32_EMULATION) += $(audit-class-y)` include `audit.o` only when both IA32 emulation and audit are enabled.

Control flow: build-time only.

State and persistence: no runtime state in the Makefile.

Dependencies and integration points: Kconfig symbols `CONFIG_IA32_EMULATION` and `CONFIG_AUDIT`, and `audit.c`.

Risks: incorrect gating could either omit IA32 audit classification or build audit code without audit support.

Test signals: build matrix for IA32 emulation with/without audit; compat syscall audit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ia32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ia32/audit.c -->
## `sources/distributed-fs/ceph-client/arch/x86/ia32/audit.c`

Purpose: provides audit syscall classes and classification for 32-bit compatibility syscalls on x86.

Important APIs and data: arrays `ia32_dir_class`, `ia32_chattr_class`, `ia32_write_class`, `ia32_read_class`, and `ia32_signal_class` are populated from generic audit syscall class include files and terminated by `~0U`. `ia32_classify_syscall()` maps specific 32-bit syscall numbers to audit categories.

Control flow: classification switches on syscall number and returns specialized classes for `open`, `openat`, `socketcall`, `execve`, `execveat`, and `openat2`; all others return `AUDITSC_COMPAT`.

State and persistence: static read-mostly class arrays; no mutable runtime state.

Dependencies and integration points: Linux audit core, `asm/unistd_32.h` syscall numbers, and `asm/audit.h`. Used when auditing compat tasks on x86-64 or IA32 emulation paths.

Risks: missing new compat syscalls in classification can reduce audit specificity. The include-generated arrays must align with 32-bit syscall numbering.

Test signals: audit records for 32-bit compat open/exec/socket syscalls, build with `CONFIG_IA32_EMULATION` and `CONFIG_AUDIT`, and syscall-table updates checked against audit mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ia32/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/GEN-for-each-reg.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/GEN-for-each-reg.h`

Purpose: macro include that enumerates general-purpose registers in architectural machine order for 64-bit or 32-bit x86.

Important APIs and content: the includer defines `GEN(name)`, then includes this file to expand over `rax..r15` on 64-bit or `eax..edi` on 32-bit. The order intentionally matches machine encoding/order and is relied upon by generated register tables.

Control flow: no runtime logic; preprocessor generation only.

State and persistence: no state.

Dependencies and integration points: depends on `CONFIG_64BIT` and the includer-provided `GEN` macro. Likely used by register save/restore, ptrace, unwind, or generated asm metadata where ordering matters.

Risks: changing order or names breaks ABI-like assumptions in generated code and register arrays. Adding separators in this file would break macro includers.

Test signals: build all x86 configs, generated register metadata diff, ptrace/perf register indexing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/GEN-for-each-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/Kbuild -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/Kbuild`

Purpose: declares generated x86 UAPI/internal headers and generic asm header fallbacks for kbuild.

Important build rules: generated headers include ORC hash, syscall tables for 32/64/x32, IA32/x32 unistd compatibility, Xen hypercalls, and CPU feature masks. Generic fallbacks include `early_ioremap.h`, `fprobe.h`, `mcs_spinlock.h`, and `mmzone.h`.

Control flow: build-time only; kbuild uses these lists to generate or export headers.

State and persistence: generated headers are build artifacts.

Dependencies and integration points: syscall generation, ORC unwinder tooling, Xen, CPU feature mask generation, and generic asm-generic headers.

Risks: omitting a generated header breaks include dependencies; wrongly using a generic fallback may hide missing x86-specific behavior.

Test signals: clean allmodconfig/defconfig builds, header install checks, syscall table generation, and ORC tooling builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/acenv.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/acenv.h`

Purpose: x86 ACPICA environment hooks for cache flush, global lock operations, and integer math helpers.

Important APIs and macros: `ACPI_FLUSH_CPU_CACHE()` flushes CPU caches with `wbinvd()` except under a hypervisor. `__acpi_acquire_global_lock()` and `__acpi_release_global_lock()` back ACPICA global lock macros. `ACPI_DIV_64_BY_32()` and `ACPI_SHIFT_RIGHT_64()` provide inline x86 assembly arithmetic helpers for ACPICA.

Control flow: sleep-state cache flushing checks `X86_FEATURE_HYPERVISOR` to avoid unnecessary host-impacting flushes in VMs. Global lock macros pass the FACS global lock field address to arch functions.

State and persistence: global lock state lives in ACPI FACS memory; this header does not store state.

Dependencies and integration points: ACPICA core, x86 special instructions, CPU feature detection, and ACPI sleep/global-lock code.

Risks: cache flush bypass in guests assumes VM sleep state cannot cause host data loss. Inline asm constraints must be correct for ACPICA arithmetic users. Global lock functions must implement ACPI locking semantics.

Test signals: ACPI suspend/resume on bare metal and VMs, ACPICA build, and global-lock firmware interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/acenv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/acpi.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/acpi.h`

Purpose: x86 ACPI integration header for global ACPI knobs, GSI registration, suspend wakeup, processor capability reporting, NUMA, APEI, Xen PV remapping, and non-ACPI stubs.

Important APIs and functions: declares ACPI enable/disable flags, SCI override state, `__acpi_register_gsi`, `acpi_gsi_to_irq()`, `disable_acpi()`, `acpi_disable_pci()`, `acpi_get_wakeup_address()`, `acpi_parse_mp_wake()`, `asm_acpi_mp_play_dead()`, `acpi_processor_cstate_check()`, `arch_acpi_set_proc_cap_bits()`, root-pointer accessors, APEI memory attribute/error-report hooks, and NUMA init.

Control flow: inline helpers gate ACPI/PCI IRQ use, adjust max C-state for AMD errata/APIC C1E, advertise processor power-management capabilities based on CPU features, sanitize capabilities in Xen dom0, skip wake address setup under Xen PV, and provide stubs when `CONFIG_ACPI` is off.

State and persistence: ACPI global flags persist for boot lifetime; FADT/MADT-derived state affects IRQ routing, CPU discovery, and power management. This header mainly exposes state owned elsewhere.

Dependencies and integration points: ACPICA, x86 init hooks, NUMA, CPU feature detection, Xen, APEI/CPER, EFI memory attributes, IRQ vectors, and ACPI processor/power code.

Risks: global ACPI flags are boot-critical and affect PCI/IRQ discovery. Processor capability bits must match CPU and hypervisor behavior or firmware may choose unsafe power states. APEI mapping attributes are conservative but SME/no-encryption assumptions matter.

Test signals: ACPI boot on bare metal, ACPI-off boot, Xen PV/dom0, suspend/resume, CPU C-state exposure, ACPI NUMA, APEI error injection/reporting, and GSI registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/acrn.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/acrn.h`

Purpose: x86 ACRN hypervisor guest interface definitions and inline hypercall helpers.

Important APIs and macros: defines ACRN CPUID leaves for features and timing info, privileged VM feature bit, interrupt handler registration functions, `acrn_cpuid_base()`, `acrn_get_tsc_khz()`, and `acrn_hypercall0/1/2()`.

Control flow: CPUID base detection checks the generic hypervisor CPU feature and searches for the ACRN signature. Hypercall helpers move the hypercall ID into `r8d`, pass up to two arguments in `rdi/rsi`, execute `vmcall`, and return `rax`.

State and persistence: no private state. Registered interrupt handlers are managed by implementation code elsewhere.

Dependencies and integration points: x86 CPUID helpers, ACRN platform drivers, interrupt handling, and ACRN hypercall ABI.

Risks: inline asm ABI is strict; wrong clobbers or argument registers break all ACRN hypercalls. `acrn_get_tsc_khz()` assumes the timing CPUID leaf is valid after ACRN detection.

Test signals: ACRN guest boot, CPUID feature detection, interrupt handler registration/removal, and hypercall smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/acrn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/agp.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/agp.h`

Purpose: x86 AGP/GART cache-coherency helpers for pages mapped into the AGP aperture.

Important APIs and macros: `map_page_into_agp(page)` sets the page uncacheable with `set_pages_uc()`, `unmap_page_from_agp(page)` restores write-back with `set_pages_wb()`, and `flush_agp_cache()` uses `wbinvd()`.

Control flow: no function bodies beyond macro expansion; AGP users call these at mapping/unmapping or flush points.

State and persistence: mutates page cacheability attributes in the kernel page tables and CPU cache state. No private state.

Dependencies and integration points: agpgart/GART drivers, x86 cacheflush/page attribute APIs, and memory aliasing rules.

Risks: conflicting cacheability aliases can corrupt data on some CPUs. `wbinvd()` is heavy and global, so misuse has performance impact. Forgetting to restore write-back affects later page use.

Test signals: AGP/GART driver tests on supported hardware, PAT/cache attribute debug warnings, graphics stability, and page attribute restore checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/agp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/alternative.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/alternative.h`

Purpose: declares and implements x86 alternatives infrastructure macros for runtime instruction patching based on CPU features, SMP state, retpoline/return/call-thunk mitigation sites, and assembly/C inline alternatives.

Important APIs and types: `struct alt_instr` describes original and replacement instruction offsets, feature/flags, and lengths. Public patching entry points include `alternative_instructions()`, `apply_alternatives()`, `apply_retpolines()`, `apply_returns()`, `apply_seal_endbr()`, `apply_fineibt()`, call thunk patchers, ITS helpers, SMP alternatives, and text reservation checks. Macros include `ALTERNATIVE`, `ALTERNATIVE_2/3`, `ALTERNATIVE_TERNARY`, `alternative()`, `alternative_input()`, `alternative_io()`, and `alternative_call()`.

Control flow: compile-time macros emit original instructions, `.altinstructions` metadata, and `.altinstr_replacement` code. Early boot or module load patching walks metadata and overwrites instruction sites according to CPU feature bits and flags such as `ALT_NOT` or `ALT_DIRECT_CALL`. SMP lock prefix sites can be patched for UP/SMP behavior.

State and persistence: patched kernel text persists for runtime. Metadata sections persist as needed for modules/SMP switching. `alternatives_patched` reports patch state.

Dependencies and integration points: objtool annotations, static CPU features, module loader, retpoline/return thunk/CFI/IBT mitigations, SMP lock patching, and assembly users.

Risks: instruction length mismatches, unsafe direct-call patching, missing memory clobbers, or incorrect metadata can corrupt executable text. This is security-sensitive because it underpins speculation mitigations and call thunks.

Test signals: boot alternatives patch logs, objtool validation, module load/unload with alternatives, CPU mitigation selftests, SMP hotplug, and disassembly checks of patched sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/hsmp.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/hsmp.h`

Purpose: exposes the AMD HSMP message-sending kernel API, with a stub when the driver is disabled.

Important APIs and types: includes UAPI `asm/amd_hsmp.h` for `struct hsmp_message`; declares `hsmp_send_message()` when `CONFIG_AMD_HSMP` is enabled, otherwise provides an inline `-ENODEV` stub.

Control flow: no runtime logic in enabled builds; disabled builds immediately fail calls.

State and persistence: HSMP state is owned by the implementation driver, not this header.

Dependencies and integration points: AMD HSMP platform driver and any kernel subsystem sending HSMP mailbox messages.

Risks: callers must handle `-ENODEV` because the helper may compile out. UAPI structure layout must remain compatible with HSMP firmware expectations.

Test signals: builds with and without `CONFIG_AMD_HSMP`, HSMP message success on supported AMD servers, and caller fallback on `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/hsmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/ibs.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/ibs.h`

Purpose: defines AMD Instruction-Based Sampling MSR bitfield layouts, data source constants, and the perf IBS data buffer contract.

Important APIs and types: unions `ibs_fetch_ctl`, `ibs_op_ctl`, `ibs_op_data`, `ibs_op_data2`, `ibs_op_data3`, and `ic_ibs_extd_ctl` map IBS MSRs into named bitfields. Constants describe IBS data source and extended data source encodings. `struct perf_ibs_data` contains size/caps and captured IBS MSR values.

Control flow: no runtime logic; used by IBS perf driver code to program, decode, and export sampled fetch/op records.

State and persistence: structures mirror hardware MSR state at sample time. No state is stored by this header.

Dependencies and integration points: AMD IBS MSR indexes, perf sampling, CPU family documentation, and userspace perf decoding of IBS records.

Risks: bitfield layouts must match AMD PPR definitions exactly. Compiler bitfield ordering assumptions are tied to target ABI. Incorrect data-source constants mislabel memory hierarchy samples.

Test signals: IBS perf sampling on supported AMD CPUs, decode checks for fetch/op latency, branch/data source samples, and build tests across compilers/configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/ibs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/nb.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/nb.h`

Purpose: declares AMD northbridge discovery, GART, L3 cache partitioning, MMCONFIG, and NUMA helper interfaces.

Important APIs and types: `struct amd_nb_bus_dev_range`, `struct amd_l3_cache`, `struct amd_northbridge`, and `struct amd_northbridge_info` model AMD NB PCI devices and feature state. Functions include `early_is_amd_nb()`, `amd_get_mmconfig_range()`, `amd_flush_garts()`, `amd_numa_init()`, subcache get/set helpers, `amd_nb_num()`, `amd_nb_has_feature()`, and `node_to_amd_nb()`.

Control flow: enabled builds provide real functions from AMD NB code. Disabled builds return safe defaults. `amd_gart_present()` checks CPU vendor/family/model for legacy GART availability.

State and persistence: implementation owns discovered northbridge arrays and feature flags; this header exposes the contract. L3 cache/subcache settings may persist in hardware registers.

Dependencies and integration points: PCI, resources, AMD node helpers, NUMA init, GART/IOMMU, EDAC/cache drivers, and CPU model data.

Risks: disabled stub macros have inconsistent function-like usage in this snapshot (`amd_nb_num(x)`), so call-site expectations matter. Wrong family/model checks can expose unsupported GART paths.

Test signals: AMD platform boot, NUMA discovery, GART flush paths, L3 subcache controls, and builds without `CONFIG_AMD_NB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/nb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/node.h -->
## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/node.h`

Purpose: central AMD node/SMN helper contract for code that accesses per-node PCI functions or System Management Network registers.

Important APIs and macros: defines `MAX_AMD_NUM_NODES`, `AMD_NODE0_PCI_SLOT`, `amd_node_get_func()`, `amd_num_nodes()`, `amd_smn_read()`, `amd_smn_write()`, `amd_smn_hsmp_rdwr()`, and `smn_read_register()`.

Control flow: `amd_num_nodes()` derives total nodes from topology. Enabled builds use implementation functions; disabled builds return `-ENODEV`. `smn_read_register()` reads node 0 and returns either an error code or register data for polling helpers.

State and persistence: implementation owns PCI/SMN access state. SMN writes can mutate hardware configuration persistently until reset or further writes.

Dependencies and integration points: PCI, topology helpers, AMD HSMP, hardware monitoring, RAS, EDAC, and platform drivers accessing SMN registers.

Risks: SMN reads/writes are low-level hardware operations; wrong node/address can affect platform behavior. `smn_read_register()` conflates negative error values and data in an `int`, so callers must use it only where that convention is expected.

Test signals: AMD node discovery on multi-socket systems, SMN read/write users, disabled-config stubs, and polling helpers with error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/node.h -->
