# Research Group subset-b-000867

This grouped report covers Intel perf event source files under `sources/distributed-fs/ceph-client/arch/x86/events/intel/`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.c

## Purpose

`pt.c` implements the Intel Processor Trace perf PMU named `intel_pt`. It exposes Intel PT CPUID capabilities through sysfs, validates perf event configuration, allocates and programs AUX buffers using ToPA or single-range output, starts/stops tracing through RTIT MSRs, handles PT PMIs, integrates with perf address filters, and coordinates with VMX/LBR exclusivity. The file is CPU-affine and keeps one `struct pt` context per CPU plus one global `struct pt_pmu`.

## Important APIs, Types, And Functions

The public/exported entry points are `intel_pt_validate_cap()`, `intel_pt_validate_hw_cap()`, `intel_pt_interrupt()`, `intel_pt_handle_vmx()`, `cpu_emergency_stop_pt()`, and `is_intel_pt_event()`. `pt_init()` is the `arch_initcall` that registers the perf PMU.

Important internal groups are:

- Capability/sysfs setup: `pt_caps`, `pt_cap_show()`, `pt_pmu_hw_init()`, `pt_attr_groups`.
- Event validation/configuration: `pt_event_valid()`, `pt_config_filters()`, `pt_config()`, `pt_config_start()`, `pt_config_stop()`.
- AUX buffer/ToPA management: `struct topa`, `struct topa_page`, `topa_alloc()`, `topa_insert_table()`, `topa_insert_pages()`, `pt_buffer_setup_aux()`, `pt_buffer_free_aux()`.
- Runtime pointer/accounting paths: `pt_config_buffer()`, `pt_read_offset()`, `pt_handle_status()`, `pt_update_head()`, `pt_buffer_reset_offsets()`, `pt_buffer_reset_markers()`.
- Perf callbacks: `pt_event_init()`, `pt_event_add()`, `pt_event_start()`, `pt_event_stop()`, `pt_event_del()`, `pt_event_snapshot_aux()`, `pt_event_destroy()`.

## Control Flow

Initialization rejects CPUs without `X86_FEATURE_INTEL_PT`, refuses to load if PT was already enabled at boot, reads platform timing data and CPUID leaf 20 capability bits, builds sysfs cap attributes, checks ToPA support, sets PMU capabilities, and calls `perf_pmu_register("intel_pt")`.

Event creation flows through `pt_event_init()`: type match, `pt_event_valid()` config bit/capability checks, LBR exclusivity acquisition, and address-filter context allocation. Adding an event ensures only one active PT event per CPU context. Starting an event begins a perf AUX transaction, maps `aux_head` into the ToPA/current output region, places STOP/INT markers for non-snapshot mode, programs output base/mask MSRs, writes RTIT filter/control MSRs, and sets tracing enabled unless VMX blocks it. Stopping clears NMI/pause/resume gates, disables TraceEn, reads final hardware offsets/status, updates AUX head/data size, and ends the AUX transaction.

On a PT PMI, `intel_pt_interrupt()` disables tracing, translates hardware output registers into buffer offsets, handles RTIT status/error/STOP conditions, advances ToPA regions when required, updates perf AUX accounting, ends the current AUX output, and starts another AUX output transaction if the event is still active.

## State And Persistence Behavior

Persistent runtime state is in per-CPU `pt_ctx`, global `pt_pmu`, perf event `hw` fields, and per-event AUX `struct pt_buffer`. The driver does not persist trace data itself; PT data is written by hardware into perf AUX pages and exposed through perf ring-buffer semantics. `pt_buffer` tracks ToPA tables, current entry, offsets, logical head, collected data size, snapshot/single-range mode, wrap state, and STOP/INT marker positions. `pt->output_base` and `pt->output_mask` cache MSR values to avoid redundant writes. `pause_allowed`, `resume_allowed`, and `handle_nmi` are explicit race gates between PMU callbacks and PMIs.

## Dependencies And Integration Points

The file depends on x86 CPUID/MSR helpers, Intel RTIT MSR definitions from `<asm/intel_pt.h>`, perf AUX APIs, perf address filters, CPU hot/VMX coordination hooks, KVM-exported PT capability helpers, and x86 LBR exclusivity. Userspace integration is through `/sys/bus/event_source/devices/intel_pt/{caps,format}` and perf AUX trace collection.

## Risks And Edge Cases

Risk is concentrated in hardware programming and concurrent control paths. Incorrect capability validation can cause #GP MSR writes. ToPA marker placement must not overwrite unread AUX data. Single-entry ToPA has special truncation and PMI-margin handling. Snapshot mode changes accounting and disables PMI use. VMX can clear TraceEn on systems where PT cannot trace post-VMXON, so `intel_pt_handle_vmx()` deliberately flags partial traces and suppresses writes while VMX is active. Address filters must clamp non-canonical virtual ranges safely. Memory barriers around TraceEn disable and AUX head publication are important for consumer visibility.

## Test Signals

Useful signals include successful boot registration of `intel_pt`, correct sysfs caps/format files, `perf record -e intel_pt// --per-thread` and snapshot AUX tests, address-filter acceptance/rejection tests, VMX/KVM tracing gap tests, stress with small AUX buffers to exercise STOP/INT marker handling, CPU-specific validation for unsupported MTC/CYC/PSB/PTWRITE bits, and lockdep/KASAN coverage for buffer allocation/free and PMI races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.h -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.h

## Purpose

`pt.h` defines the private data structures shared by the Intel Processor Trace perf PMU implementation. It models hardware ToPA entries, the global PT PMU capability cache, per-event AUX buffer bookkeeping, IP filter state, and per-CPU PT runtime context.

## Important APIs, Types, And Fields

`TOPA_PMI_MARGIN`, `TOPA_SHIFT`, and `sizes()` encode ToPA region sizing rules. `struct topa_entry` is the hardware table-entry layout with `end`, `intr`, `stop`, `size`, and physical `base` fields. `struct pt_pmu` wraps `struct pmu` and caches PT CPUID leaves, VMX compatibility, the Broadwell branch-enable quirk, and timing ratio data exported to userspace.

`struct pt_buffer` is the AUX-private buffer object used by `pt.c`: it owns the ToPA table list, first/last/current table pointers, current entry index, output offset, page count, logical head, data-size accumulator, snapshot/single/wrapped mode flags, STOP/INT marker state, and perf-provided data pages. `struct pt_filter` and `struct pt_filters` hold up to four address ranges mapped to RTIT address MSRs. `struct pt` is per-CPU state containing the perf output handle, the cached filters, NMI/pause/resume/VMX flags, and cached output MSR values.

## Control Flow

This header has no executable control flow beyond `sizes()`. Its fields are consumed by `pt.c` during PMU registration, event initialization, AUX setup, runtime trace start/stop, PMI handling, and address-filter synchronization.

## State And Persistence Behavior

The structures describe volatile kernel/perf state. `pt_buffer` persists for the lifetime of a perf AUX buffer and is freed through the PMU `free_aux` callback. `pt` persists per CPU while the driver is loaded. None of these structures write durable state; trace bytes live in perf AUX pages owned by perf core.

## Dependencies And Integration Points

The header depends on perf core types such as `struct pmu`, `struct perf_output_handle`, `local_t`, `local64_t`, `list_head`, and Intel PT capability constants. It is intentionally private to the Intel PT PMU driver and is included by `pt.c`.

## Risks And Edge Cases

Bitfield layout in `struct topa_entry` must match the Intel PT hardware format on the target compiler/ABI. Marker and pointer fields in `pt_buffer` are sensitive to wraparound and snapshot semantics. `PT_FILTERS_NUM` must remain aligned with hardware address-range capability handling in `pt.c`.

## Test Signals

Compile coverage for `pt.c`, perf PT AUX buffer tests, sysfs capability enumeration, and tracing on systems with and without multiple-entry ToPA are the main validation signals. Static checks should also catch structure-size assumptions such as the ToPA metadata fitting in a page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.c

## Purpose

`uncore.c` is the central Intel uncore perf PMU framework. It registers model-specific and discovery-derived uncore PMUs, handles PCI/MSR/MMIO box lifetime, schedules perf events onto limited counters with constraints, polls counters with hrtimers, manages CPU hotplug migration of package/die collection CPUs, and dispatches platform initialization selected from Intel CPU model tables.

## Important APIs, Types, And Functions

Global state includes `uncore_msr_uncores`, `uncore_pci_uncores`, `uncore_mmio_uncores`, `uncore_pci_driver`, `uncore_pci_sub_driver`, `pci2phy_map_head`, `uncore_extra_pci_dev`, `__uncore_max_dies`, and the package collection `uncore_cpu_mask`.

Exported/shared helpers include `uncore_pcibus_to_dieid()`, `uncore_die_to_segment()`, `uncore_device_to_die()`, `__find_pci2phy_map()`, `uncore_event_show()`, `uncore_pmu_to_box()`, `uncore_msr_read_counter()`, `uncore_mmio_exit_box()`, `uncore_mmio_read_counter()`, `uncore_get_constraint()`, `uncore_put_constraint()`, `uncore_shared_reg_config()`, event lifecycle callbacks (`uncore_pmu_event_*()`), `uncore_perf_event_update()`, and `uncore_get_alias_name()`.

Core internal functions are `uncore_assign_hw_event()`, `uncore_collect_events()`, `uncore_get_event_constraint()`, `uncore_assign_events()`, `uncore_validate_group()`, `uncore_pmu_event_init()`, `uncore_pmu_register()`, `uncore_type_init()`, PCI probe/remove/notify paths, CPU hotplug functions, and `intel_uncore_init()`/`intel_uncore_exit()`.

## Control Flow

Module initialization rejects hypervisors, computes max logical dies, matches the boot CPU against `intel_uncore_match`, optionally runs discovery, and then invokes platform `pci_init`, `cpu_init`, and `mmio_init` callbacks. Each selected uncore type is expanded into PMU instances and per-die box arrays. PCI PMUs are registered when matching devices probe or are discovered; MSR/MMIO PMUs are registered during init and receive per-die boxes from CPU hotplug callbacks.

Event initialization validates type, registration, no sampling, valid target CPU, fixed/free-running/generic config rules, optional hardware config hooks, and group schedulability. Adding a non-free-running event collects currently active events, assigns counter indexes using constraints and `perf_assign_events()`, stops/reprograms moved events, then starts new ones if requested. Free-running events are mapped directly to their read-only counter and tracked on `active_list`.

Counters are polled by per-box hrtimers because uncore overflow interrupts are unavailable or unreliable on important platforms. The hrtimer updates active-list free-running events and bitmask-tracked programmable counters, then forwards itself while active.

## State And Persistence Behavior

State is in dynamically allocated `intel_uncore_pmu` arrays, per-die `intel_uncore_box` objects, shared extra-register refcounts/configs, PCI bus-to-die maps, PMU registration flags, event `hw` fields, and hrtimer state. Counts accumulate in `perf_event.count`; raw hardware state lives in MSR, PCI config, or MMIO registers. No durable state is written. CPU hotplug migrates PMU contexts from an outgoing die collection CPU to another CPU in the same die mask and cancels hrtimers before migration.

## Dependencies And Integration Points

This file integrates with Linux perf PMU registration, PCI driver/probe/notifier APIs, x86 CPU model matching, topology and NUMA helpers, hrtimers, raw spinlocks, Intel uncore platform files, and `uncore_discovery.c`. Sysfs integration is via PMU names, `cpumask`, `format`, and `events` attribute groups. Platform descriptions in `uncore_snb.c`, `uncore_nhmex.c`, and other uncore files fill in `intel_uncore_type` arrays consumed here.

## Risks And Edge Cases

Counter scheduling must honor fixed, free-running, and shared-register constraints or perf groups can produce incorrect counts. PCI-to-die mapping depends on platform data and NUMA/topology availability. Hotplug migration can race with hrtimer updates if box CPU ownership is mishandled. Generic discovery PMUs may be absent or partially discovered, so init treats PCI, CPU/MSR, and MMIO paths independently and succeeds if at least one path works. Free-running counters are read-only and must never be programmed like normal counters.

## Test Signals

Signals include module init on supported and unsupported CPUs, sysfs PMU/event/format/cpumask visibility, perf group validation with constrained events, fixed and free-running counter reads, CPU hotplug migration tests, PCI device add/remove tests, lockdep for shared registers, and comparing memory-controller bandwidth events against known traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.h -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.h

## Purpose

`uncore.h` is the shared private interface for Intel uncore perf support. It defines uncore PMU type descriptors, PMU instances, physical boxes, operation callbacks, event descriptors, topology helpers, free-running counter encoding, register-address helpers for MSR/PCI/MMIO backends, and prototypes used by platform-specific uncore files and generic discovery.

## Important APIs, Types, And Fields

Key structures are `intel_uncore_type`, `intel_uncore_ops`, `intel_uncore_pmu`, `intel_uncore_box`, `intel_uncore_extra_reg`, `uncore_event_desc`, `freerunning_counters`, `intel_uncore_topology`, and `pci2phy_map`. `intel_uncore_type` is the main static or discovery-generated PMU contract: name, counter counts/widths, register offsets, masks, constraints, callbacks, attributes, topology mapping, and PMU arrays. `intel_uncore_box` is the live per-die/per-PMU hardware instance with active events, constraints, PCI/MMIO handles, hrtimer, and shared extra registers.

Important inline helpers classify counter indexes (`uncore_pmc_fixed()`, `uncore_pmc_freerunning()`), validate MMIO offsets, compute box/control/counter addresses for PCI and MSR backends, decode free-running event config, select backend-specific register helpers, call type operations, initialize/exit boxes, and convert perf events/devices to uncore objects.

Macros such as `DEFINE_UNCORE_FORMAT_ATTR`, `INTEL_UNCORE_EVENT_DESC`, `UNCORE_PCI_DEV_DATA`, and constraint helpers support concise platform tables.

## Control Flow

The header provides inline dispatch used by `uncore.c`: PMU callbacks call into `uncore_enable_event()`, `uncore_disable_event()`, and `uncore_read_counter()`, which dispatch through `intel_uncore_ops`. Register address calculation selects PCI/MMIO paths when `box->pci_dev` or `box->io_addr` is present, otherwise MSR paths are used. Free-running config helpers validate and map `event=0xff,umask>=0x10` encodings into hardware offsets.

## State And Persistence Behavior

The header defines the state containers but does not allocate durable data. Runtime state spans PMU arrays, box arrays, event slots, active masks, per-counter tags, extra-register refcounts, topology mappings, PCI maps, and global uncore arrays declared as externs. All persistence is in memory or hardware registers for the lifetime of the module and perf events.

## Dependencies And Integration Points

It depends on Linux perf, PCI, slab, APIC/topology, Intel family IDs, and non-atomic 64-bit I/O helpers. It links platform files (`uncore_snb.c`, `uncore_nhmex.c`, server uncore files) to `uncore.c` by declaring init hooks and global arrays. It also exports discovery support hooks and ignore-list externs.

## Risks And Edge Cases

Register-offset helpers embed platform assumptions such as paired counter/control spacing, Coffee Lake 8th CBOX special MSR offsets, fixed-counter sharing, and MMIO map sizes. A wrong `intel_uncore_type` field can program the wrong register. Free-running event encoding has a special `0xff` event code shared with fixed counters, so validation must distinguish umask ranges. MMIO offset validation warns once but returns zero counts on invalid offsets.

## Test Signals

High-signal tests are build coverage across all Intel uncore platform files, sysfs `format` correctness, fixed/free-running event validation, register address calculations for representative MSR/PCI/MMIO types, and hotplug/perf group tests that exercise inline dispatch through each backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.c

## Purpose

`uncore_discovery.c` implements Intel uncore PerfMon discovery. It parses discovery tables exposed through PCI DVSEC BARs or MSRs, records discovered uncore unit types and boxes in red-black trees, and synthesizes generic `intel_uncore_type` arrays for MSR, PCI, and MMIO access backends.

## Important APIs, Types, And Functions

The main exported functions are `uncore_discovery()`, `intel_uncore_clear_discovery_tables()`, generic backend box/event operations (`intel_generic_uncore_*`), `intel_generic_uncore_assign_hw_event()`, `intel_uncore_generic_init_uncores()`, `intel_uncore_generic_uncore_cpu_init()`, `intel_uncore_generic_uncore_pci_init()`, `intel_uncore_generic_uncore_mmio_init()`, `intel_uncore_find_discovery_unit_id()`, `uncore_find_add_unit()`, and `uncore_get_uncores()`.

Internal state includes `discovery_tables`, keyed by box type, and `num_discovered_types[]` by access type. Each discovered type owns a unit tree keyed by PMU index and die. Parsing helpers include `__parse_discovery_table()`, `parse_discovery_table()`, `uncore_discovery_pci()`, `uncore_discovery_msr()`, `uncore_insert_box_info()`, and ignore-list filtering.

## Control Flow

`uncore_discovery()` iterates configured discovery domains from `struct uncore_plat_init`. MSR domains read one discovery-table base per logical die from online CPUs. PCI domains find Intel discovery-table devices, scan DVSEC capabilities for PMON discovery entries, derive the table BAR, compute die ID, and parse the mapped table.

Parsing first reads the global discovery record, validates it, maps the full table based on stride and max-unit count, optionally runs a platform global-init callback, then iterates unit records. Valid, non-ignored units become `intel_uncore_discovery_unit` nodes attached to a type record. Later, generic init converts discovered records into `intel_uncore_type` objects with common format groups, event masks, counter width/offsets, unit trees, and backend-specific ops.

## State And Persistence Behavior

Discovery data is held in kernel memory until module exit or init failure, when `intel_uncore_clear_discovery_tables()` frees all type and unit nodes. It does not persist across boots. Generic PMUs reference discovery unit trees through `intel_uncore_type.boxes`; live boxes use those records to compute control addresses and MMIO mappings.

## Dependencies And Integration Points

The file integrates with `uncore.c` platform init, PCI config/DVSEC access, MSR reads on specific CPUs, `ioremap()` discovery-table reads, red-black tree helpers, and generic uncore perf callbacks. It is used both as a fallback for unknown CPUs with discovery support and as a supplement for newer known platforms.

## Risks And Edge Cases

Invalid discovery records are common enough to be explicitly filtered: missing table/control fields, all-ones sentinel values, unsupported access types, ignored platform unit IDs, absent DVSEC entries, disabled/invalid BARs, and unavailable NUMA die info. Generic MMIO mapping uses a default map size unless platform code overrides a type through `uncore_get_uncores()`. Discovery state is global, so cleanup must release nested unit trees reliably.

## Test Signals

Useful checks include booting discovery-capable platforms with and without `uncore_no_discover`, verifying generic PMU names and aliases, validating discovered box counts and counter widths against hardware documentation, PCI DVSEC parsing tests, MSR-domain parsing on multi-die systems, and exercising generic MSR/PCI/MMIO event reads through perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.h -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.h

## Purpose

`uncore_discovery.h` defines constants, packed discovery-table record layouts, generic PMON bit masks, access-type identifiers, discovered-unit/type records, and function prototypes for Intel uncore PerfMon discovery and generic uncore backends.

## Important APIs, Types, And Fields

Important constants identify discovery sources (`UNCORE_DISCOVERY_MSR`, `CBB_UNCORE_DISCOVERY_MSR`, `PACKAGE_UNCORE_DISCOVERY_MSR`), PCI discovery table devices, DVSEC offsets/IDs, global map size, and fields for PCI-domain/bus/devfn/box-control extraction. `uncore_discovery_invalid_unit()` centralizes validation of empty or all-ones discovery records.

`enum uncore_access_type` distinguishes MSR, MMIO, and PCI units. `struct uncore_global_discovery` describes table type, stride, unit count, access type, global control address, and status layout. `struct uncore_unit_discovery` describes unit counter count, control/counter offsets, bit width, access type, control address, box type, and box ID. `intel_uncore_discovery_unit` and `intel_uncore_discovery_type` are the in-memory normalized records used by `uncore_discovery.c`.

The prototypes expose discovery execution, cleanup, generic CPU/PCI/MMIO init, generic backend operations, discovered-unit lookup, and `uncore_get_uncores()` platform override merging.

## Control Flow

This header has no executable control flow except macros. It provides the contract used by `uncore.c` to request discovery and by `uncore_discovery.c` to populate generic PMU structures.

## State And Persistence Behavior

The structs describe transient discovery and runtime mapping state. Discovery records are read from hardware tables, normalized into RB-tree nodes, and freed on module exit. No durable state is managed here.

## Dependencies And Integration Points

It depends on `struct uncore_plat_init`, `struct intel_uncore_type`, `struct intel_uncore_box`, and perf event types declared through `uncore.h` and perf headers. Platform init tables in `uncore.c` use its constants to configure discovery domains.

## Risks And Edge Cases

Bitfield definitions must match hardware discovery-table encoding. PCI address extraction uses fixed bit positions and must stay aligned with discovered unit address formats. Generic raw event masks only cover common event/umask/edge/invert/thresh fields, so platform-specific units may still need overrides.

## Test Signals

Build coverage for discovery users, boot discovery on PCI and MSR table platforms, sysfs PMU naming for units without names, and perf reads through all three generic access types validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_nhmex.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_nhmex.c

## Purpose

`uncore_nhmex.c` provides Nehalem-EX and Westmere-EX model-specific uncore PMU descriptions and callbacks. It defines MSR layouts, sysfs format/event attributes, PMU types, event constraints, and shared extra-register handling for Ubox, Cbox, Bbox, Sbox, Mbox, Rbox, and Wbox units.

## Important APIs, Types, And Functions

The only exported init hook is `nhmex_uncore_cpu_init()`, which selects Nehalem-EX versus Westmere-EX Mbox event aliases, clamps Cbox count to cores per package, and assigns `uncore_msr_uncores`.

Important callbacks include common MSR box/event operations (`nhmex_uncore_msr_*()`), Bbox/Sbox config and enable functions, complex Mbox shared-register helpers (`nhmex_mbox_get_shared_reg()`, `nhmex_mbox_get_constraint()`, `nhmex_mbox_hw_config()`, `nhmex_mbox_msr_enable_event()`), and Rbox constraint/config/enable functions. Static `intel_uncore_type` objects describe each box with counter counts, widths, MSR bases/offsets, event masks, constraints, shared-reg counts, format groups, and event aliases.

## Control Flow

The generic uncore framework calls `nhmex_uncore_cpu_init()` from `uncore.c` for EX CPU models. Later, `uncore_type_init()` and perf PMU registration consume `nhmex_msr_uncores`. Event initialization uses each type's `hw_config()` to map perf `config`, `config1`, and `config2` into `hw_perf_event_extra` registers. Counter assignment invokes type-specific `get_constraint()` where needed to reserve shared MSRs before an event can be scheduled. Event enable writes extra match/mask/config MSRs first, then writes the primary event control register with the required enable bit.

## State And Persistence Behavior

State is static platform description plus runtime shared-register state inside each `intel_uncore_box`. Mbox and Rbox shared registers use refcounts and raw spinlocks to allow compatible events to share registers and reject incompatible groupings. `uncore_nhmex` switches behavior for the Nehalem-EX versus Westmere-EX ZDP_CTL_FVC encoding and event aliases. Counts are accumulated by the common uncore polling path.

## Dependencies And Integration Points

The file depends on MSR access, `boot_cpu_data`, topology core count, common uncore helpers, perf extra-reg conventions, and sysfs event/format macros from `uncore.h`. It integrates with `uncore.c` through the `nhmex_uncore_cpu_init()` prototype and `uncore_msr_uncores`.

## Risks And Edge Cases

This file is dense with hardware-specific register encoding. Risks include conflicting shared extra-register users, incorrect alternative field selection for functionally identical Mbox/Rbox events, wrong enable-bit choice for different box families, and platform skew between NHM-EX and WSM-EX. Several event aliases use historical spellings, so changing names can break userspace scripts.

## Test Signals

Signals include PMU registration on Nehalem-EX/Westmere-EX, sysfs presence for all box types and aliases, perf group tests that intentionally collide or share Mbox/Rbox extra registers, validation of `config1`/`config2` match-mask events, and known workload counter sanity for QPI, memory, Bbox/Sbox, and Wbox clockticks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_nhmex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snb.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snb.c

## Purpose

`uncore_snb.c` supplies client/platform Intel uncore PMU definitions from Nehalem/Sandy Bridge through newer client parts such as Tiger Lake, Alder/Lunar/Panther/Nova Lake. It defines MSR PMUs for CBOX/ARB/clock/cNCU/SANTA-style units, PCI/MMIO memory-controller PMUs, free-running bandwidth counters, PCI ID tables, and init hooks consumed by `uncore.c`.

## Important APIs, Types, And Functions

Exported hooks include `snb_uncore_cpu_init()`, `nhm_uncore_cpu_init()`, `skl_uncore_cpu_init()`, `icl_uncore_cpu_init()`, `tgl_uncore_cpu_init()`, `adl_uncore_cpu_init()`, `mtl_uncore_cpu_init()`, `lnl_uncore_cpu_init()`, `ptl_uncore_cpu_init()`, `nvl_uncore_cpu_init()`, `tgl_uncore_mmio_init()`, `tgl_l_uncore_mmio_init()`, `adl_uncore_mmio_init()`, `lnl_uncore_mmio_init()`, `ptl_uncore_mmio_init()`, `snb_pci2phy_map_init()`, and PCI init wrappers for SNB/IVB/HSW/BDW/SKL.

Key function families are MSR box/event ops (`snb_uncore_msr_*`, SKL/ADL/MTL/LNL variants), IMC PCI/MMIO initialization (`snb_uncore_imc_init_box()`, `snb_uncore_imc_event_init()`, `uncore_get_box_mmio_addr()`), free-running counter setup for SNB/TGL/ADL IMCs, and discovery-merging for PTL through `uncore_get_uncores()`.

Static `intel_uncore_type` objects define event masks, register bases, counter widths, fixed counters, constraints, format groups, event aliases, and per-generation PMU arrays.

## Control Flow

CPU-model init in `uncore.c` calls the matching hook here. Each hook mutates shared static type descriptors as needed for that generation, then assigns `uncore_msr_uncores`, `uncore_pci_uncores`, `uncore_mmio_uncores`, and/or `uncore_pci_driver`. The common uncore framework later initializes types, registers PMUs, and manages boxes.

Desktop IMC PCI init scans known memory-controller PCI IDs, establishes a bus-to-die map, and selects an appropriate PCI driver. SNB IMC events use a custom PMU `event_init()` to preserve old free-running counter encoding while translating to standard uncore free-running `event=0xff,umask=...` config. TGL/ADL/LNL MMIO paths map IMC or SAFBAR-derived MMIO windows and use generic or custom MMIO ops. PTL/NVL combine discovered MMIO uncores with extra static free-running types and override selected discovered type descriptors by type ID.

## State And Persistence Behavior

Most state is static platform description reused across models and sometimes mutated at init time. Runtime state is allocated by `uncore.c` boxes and PMUs. PCI IMC maps one physical bus to die 0 for client systems. MMIO boxes store `io_addr` mappings freed by common exit callbacks. Free-running counters are always active and are polled by the common hrtimer path.

## Dependencies And Integration Points

This file depends on MSR access, PCI device scanning/config reads, memory-controller BAR layout, generic uncore helpers, discovery helpers for newer platforms, and topology core/CBOX count logic. Userspace sees the result as uncore PMUs with generation-specific `format` and `events` sysfs files.

## Risks And Edge Cases

Risk comes from broad platform coverage and mutable shared descriptors. Init hooks change counter counts, register bases, ops pointers, and PMU arrays based on CPU generation; incorrect ordering can affect later model setup. IMC BARs may be disabled or absent, and fallback device lookup may map wrong or no MMIO region. SNB IMC counters are 32-bit and require `readl()` instead of the generic 64-bit MMIO read. Free-running and fixed counters share the `0xff` event code and need careful umask interpretation.

## Test Signals

Strong signals include boot/sysfs PMU coverage for each supported generation, memory bandwidth sanity tests for PCI and MMIO IMC counters, event-format parsing for SNB/NHM/ADL/LNL masks, CBOX count matching hardware, free-running counter wrap polling, CPU hotplug with active uncore events, and discovery override checks for PTL/NVL type IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_snb.c -->
