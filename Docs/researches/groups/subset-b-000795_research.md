# Research: subset-b-000795

Grouped research for `subset-b-000795`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-pmu.c

Purpose: registers the POWER8 core PMU with Linux perf, translating generic perf events, cache events, branch-history filters, raw event encodings, and POWER8-specific alternate event codes into the shared PowerISA v2.07 PMU backend.

Important APIs/types/functions: `power8_get_alternatives()` delegates to `isa207_get_alternatives()` with the local alternate-event table; `power8_bhrb_filter_map()` accepts only branch-any or any-call branch history filters; `power8_config_bhrb()` writes the IFM bits into `SPRN_MMCRA`; `power8_cache_events` maps `PERF_COUNT_HW_CACHE_*` tuples; `power8_pmu` is the exported `struct power_pmu`; `init_power8_pmu()` gates registration on `PVR_POWER8E`, `PVR_POWER8NVL`, or `PVR_POWER8`.

Control flow: boot-time PMU probing reads PVR, registers `power8_pmu`, advertises EBB support through `cur_cpu_spec->cpu_user_features2`, and logs the PMAO workaround when active. Runtime perf setup enters through generic powerpc perf code, which uses this file's generic/cache tables, `isa207_compute_mmcr()`, `isa207_get_constraint()`, and BHRB callbacks to program MMCR/MMCRA/MMCRC fields described in the header comment.

State and persistence: all state is static tables plus the registered `power_pmu`; hardware-visible state is in MMCRA and PMU registers programmed by the common ISA207 backend. No allocation or persistent per-event state is created here beyond perf core state.

Dependencies and integration: depends on `isa207-common.h`, `power8-events-list.h`, perf sysfs attribute macros, PVR/cpu feature definitions, and special-register accessors. It integrates with perf event creation, sysfs `events`, `format`, and `caps` groups, EBB exposure, BHRB sampling, memory data source decoding, and generic cache/generic event aliases.

Risks and test signals: event-code or alternate-table mistakes silently count the wrong hardware source; BHRB filter rejection must match hardware limits; raw-event bit fields are dense and SoC-specific. Test with `perf list`, generic events, cache events, marked events, BHRB call filtering, raw events using threshold/cache/sample bits, and POWER8 variant boot detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-events-list.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-events-list.h

Purpose: centralizes POWER9 event mnemonic-to-raw-code definitions consumed by `power9-pmu.c` through the caller-defined `EVENT()` macro.

Important APIs/types/functions: this header has no standalone declarations; its API is the `EVENT(name, code)` expansion contract. It defines generic aliases such as `PM_CYC`, `PM_INST_CMPL`, cache/TLB/branch events, alternate codes such as `PM_RUN_CYC_ALT`, POWER9 DD2.1/DD2.2 blacklisted event identifiers, and synthetic memory profiling encodings `MEM_LOADS` and `MEM_STORES`.

Control flow: inclusion inside an enum in `power9-pmu.c` turns every `EVENT()` row into an enum constant. The same constants are then used in sysfs attributes, generic/cache mapping arrays, alternate-event lookup tables, blacklist arrays, and raw memory-profiling event aliases.

State and persistence: no runtime state. The file persists a compile-time event catalog and therefore affects the ABI values shown under perf PMU sysfs events.

Dependencies and integration: depends on its includer defining `EVENT()`. It is tightly coupled to POWER9 PMU raw encoding, `power9_check_attr_config()`, and perf's exposed event names.

Risks and test signals: a wrong constant produces plausible but incorrect counts; blacklist constants must match DD-level errata; memory event encodings combine base event and MMCRA sampling/threshold bits. Test by building POWER9 perf support, checking `perf list`, verifying blacklist behavior on DD2.1/DD2.2, and comparing memory load/store sampling against architecture documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-events-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-pmu.c

Purpose: registers the POWER9 core PMU with Linux perf, including POWER9 raw-format fields, generic/cache event aliases, branch-history filtering, MMCR programming via the ISA207 backend, DD-level event blacklists, and extended register capture support.

Important APIs/types/functions: `power9_get_alternatives()` provides alternate raw event encodings; `power9_check_attr_config()` rejects unsupported sample-mode value `0xC` and delegates ISA3xx checks; `power9_bhrb_filter_map()` and `power9_config_bhrb()` handle BHRB IFM bits; `power9_cache_events` and `power9_generic_events` map generic perf requests; `power9_pmu` is the registered `struct power_pmu`; `init_power9_pmu()` performs PVR gating and DD blacklist selection.

Control flow: initialization accepts only `PVR_POWER9`, chooses blacklist arrays for non-Cumulus DD2.1 or DD2.2 PVRs, sets `PERF_REG_EXTENDED_MASK` to `PERF_REG_PMU_MASK_300`, registers the PMU, and advertises EBB. During event setup, perf uses the file's format group for raw config bits, validates attributes, maps generic/cache events, computes MMCRs with `isa207_compute_mmcr()`, and applies the cache PMC4 group constraint.

State and persistence: persistent state is static tables plus mutable fields in `power9_pmu` for blacklist pointer/count during init. Hardware state is programmed through the common backend and the BHRB callback writes MMCRA. No heap allocation occurs here.

Dependencies and integration: depends on `isa207-common.h`, `power9-events-list.h`, perf sysfs macros, PVR helpers, CPU feature flags, and the shared Power PMU registration layer. It integrates with perf sysfs `events`, POWER9-specific `format`, cache/generic events, BHRB, EBB, extended sample registers, and memory data source/weight helpers.

Risks and test signals: blacklist selection relies on precise PVR bit interpretation; raw format differs from POWER8 in threshold compare and `sdar_mode`; unsupported sample modes must be rejected before programming hardware. Test on POWER9 DD2.1/DD2.2/Cumulus, verify blacklisted raw events fail, exercise generic/cache/memory events, BHRB call filtering, extended register sampling, and raw events with `sdar_mode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/ppc970-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/ppc970-pmu.c

Purpose: implements perf PMU support for PPC970/970FX/970GX/970MP processors, including direct and bus-event constraint solving, MMCR0/MMCR1/MMCRA programming, generic/cache event aliases, and marked-instruction sampling enablement.

Important APIs/types/functions: `p970_marked_instr_event()` detects events requiring `MMCRA_SAMPLE_ENABLE`; `p970_get_constraint()` encodes PMC, unit, byte lane, SPCSEL, and group constraints; `p970_get_alternatives()` supplies LSU-empty alternates; `p970_compute_mmcr()` assigns PMCs and multiplexer fields for up to eight events; `p970_disable_pmc()` disables a counter by selecting `0x08`; `ppc970_pmu` is the registered PMU descriptor; `init_ppc970_pmu()` gates on PPC970-family PVRs.

Control flow: perf event grouping first queries constraints, then `p970_compute_mmcr()` performs a resource-use pass to reject conflicting PMCs, bus bytes, TTM selectors, and PMC group overuse. A second pass assigns free counters, sets PMCx selectors and adder bits, enables marked sampling when needed, and returns MMCR values. Initialization only registers for supported PVR versions.

State and persistence: static arrays model adder-bit positions, marked direct events, unit constraints, generic events, and cache events. Runtime state is in perf event hardware fields and MMCR register values; there is no dynamic allocation in this file.

Dependencies and integration: depends on core perf headers, PPC special register definitions, `internal.h`, `register_power_pmu()`, and generic powerpc perf event scheduling. It exposes no sysfs named-event group of its own, unlike newer POWER PMUs.

Risks and test signals: constraint packing is dense; off-by-one PMC numbering or group selection can reject valid groups or program wrong counters. Marked-event detection combines direct, add, decode, and LSU/VPU mask logic. Test with multiple grouped events, direct PMC-pinned events, LSU alternative events, marked sampling, generic perf events, cache aliases, and unsupported groups larger than eight events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/ppc970-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_begin.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_begin.h

Purpose: starts the request-description macro environment used by generated perf request headers under `req-gen`.

Important APIs/types/functions: defines the include guard `POWERPC_PERF_REQ_GEN_H_`, imports `<linux/stringify.h>`, provides `CAT2_STR_()`, `CAT2_STR()`, and `I(...)`, then defines `REQ_GEN_PREFIX`, `REQUEST_BEGIN`, and `REQUEST_END` for sibling include names.

Control flow: request-definition headers include this file before declaring requests. The macros build string include paths such as `req-gen/_request-begin.h` and `req-gen/_request-end.h` for later use by generator-style headers.

State and persistence: no runtime state; it creates preprocessor definitions that persist until `_end.h` or `_clear.h` undefines them.

Dependencies and integration: consumed by powerpc perf request-generation headers, especially `perf.h`, and assumes the preprocessor include path can resolve `req-gen/...` fragments.

Risks and test signals: macro leakage or include-path mistakes can break generated request structures and sysfs events. Test by building hv-gpci/request users with multiple inclusions and by verifying `_end.h` cleans all definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_begin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_clear.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_clear.h

Purpose: resets the request-generation macro layer so the same request file can be included repeatedly with different macro meanings.

Important APIs/types/functions: undefines `__field_`, `__count_`, `__array_`, and `REQUEST_`.

Control flow: generator headers include `_clear.h` before redefining the low-level macros for enum generation, struct generation, offset checks, or perf attribute generation.

State and persistence: only preprocessor state changes. There is no runtime state.

Dependencies and integration: paired with `perf.h`, `_request-begin.h`, and request description files that expand to `REQUEST_` and field macros.

Risks and test signals: missing an undef causes one generation pass to bleed into the next; undefining too much would break the wrapper macros. Test through a full kernel build of request-generated perf PMUs and by checking preprocessed output when adding new request fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_clear.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_end.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_end.h

Purpose: ends the outer request-generation macro environment begun by `_begin.h`.

Important APIs/types/functions: undefines `REQ_GEN_PREFIX`, `REQUEST_BEGIN`, and `REQUEST_END`.

Control flow: included after generated request headers finish using path-construction macros, preventing those names from leaking into later includes.

State and persistence: only preprocessor cleanup.

Dependencies and integration: paired with `_begin.h` and any interface-defining header that uses `REQUEST_BEGIN` or `REQUEST_END`.

Risks and test signals: omitting it can collide with unrelated macros in later includes; including it too early would prevent request include path construction. Test with repeated inclusion and W=1/preprocessor diagnostics for macro redefinition warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_end.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-begin.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-begin.h

Purpose: exposes user-facing request-description macros that stamp each field with the active request name, numeric ID, and starting-index kind.

Important APIs/types/functions: defines `REQUEST(r_contents)`, `__field()`, `__array()`, and `__count()`. These wrap lower-level `REQUEST_`, `__field_`, `__array_`, and `__count_` macros with `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND`.

Control flow: a request description sets request identity macros, includes this header, emits `REQUEST(...)` containing field declarations, then includes `_request-end.h`. Higher-level generators redefine the underscored macros before including the request file.

State and persistence: preprocessor-only state; definitions persist until `_request-end.h` or `_clear.h`.

Dependencies and integration: requires `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND` to be defined by the request file context, and requires a higher-level consumer to define the underscored expansion macros.

Risks and test signals: request identity macros are positional and easy to mismatch, producing wrong sysfs metadata or struct names. Test by adding a request and confirming enum values, struct names, offset assertions, and event attributes all reflect the same request metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-begin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-end.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-end.h

Purpose: cleans up the per-request macro aliases and identity fields established for one request description.

Important APIs/types/functions: undefines `REQUEST`, `__field`, `__array`, `__count`, `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND`.

Control flow: included at the end of each request block so the next request can define a new name, number, and index kind without macro contamination.

State and persistence: preprocessor cleanup only.

Dependencies and integration: used with `_request-begin.h` by request description files included from `perf.h`.

Risks and test signals: missing cleanup can cause subsequent request blocks to reuse stale names or numeric IDs. Test through multi-request generated headers and preprocessed output after editing request definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/_request-end.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/perf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/perf.h

Purpose: turns a declarative request file into enums, packed big-endian request structs, compile-time offset checks, and perf sysfs event attribute arrays for hypervisor/perf request PMUs.

Important APIs/types/functions: requires `REQUEST_FILE`, `NAME_LOWER`, and `NAME_UPPER`; maps byte widths to `__u8`, `__be16`, `__be32`, and `__be64`; generates `enum <NAME_LOWER>_requests`; generates `struct <NAME_LOWER>_<request>`; defines `<NAME_LOWER>_assert_offsets_correct()` with `BUILD_BUG_ON(offsetof(...))`; emits `PMU_EVENT_ATTR_STRING()` entries for `__count()` fields and two arrays, `hv_gpci_event_attrs_v6` and `hv_gpci_event_attrs`.

Control flow: the same `REQUEST_FILE` is included multiple times with a different set of macros after `_clear.h`: once for enum values, once for structs, once for offset assertions, once for event attributes, once for legacy v6 attribute array, and once for current attribute array. `ENABLE_EVENTS_COUNTERINFO_V6` is undefined before generating the current array so request files can suppress deprecated events for newer firmware.

State and persistence: no runtime mutable state, but it defines static attribute arrays and inline assertions in every includer. Struct layout is ABI-sensitive because fields are big-endian and offset-checked against hypervisor request documentation.

Dependencies and integration: depends on `<linux/perf_event.h>`, perf PMU sysfs macros, request files using `_request-begin.h` conventions, `COUNTER_INFO_VERSION_CURRENT`, and the hv-gpci PMU code that consumes the generated attribute arrays.

Risks and test signals: generated code is macro-heavy; bad offsets, byte sizes other than 1/2/4/8, or stale counter-info gating can break firmware requests or userspace event discovery. Test with compile-time offset assertions, `perf list` for generated events, firmware with counter-info versions <=6 and >=8, and request data parsing on big-endian fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/req-gen/perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-dtl.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-dtl.c

Purpose: exposes PowerVM shared-processor Dispatch Trace Log data as a perf AUX-output PMU named `vpa_dtl`, allowing userspace perf tooling to collect raw DTL entries for cede, preempt, fault, or all dispatch-log events.

Important APIs/types/functions: defines event IDs `DTL_CEDE`, `DTL_PREEMPT`, `DTL_FAULT`, and `DTL_ALL`; `struct vpa_dtl` tracks the per-CPU DTL buffer and last index; `struct vpa_pmu_buf` tracks AUX buffer mapping, size, head, and boot timebase metadata; `vpa_dtl_event_init()`, `vpa_dtl_event_add()`, `vpa_dtl_event_del()`, `vpa_dtl_setup_aux()`, and `vpa_dtl_free_aux()` implement the PMU; `vpa_dtl_hrtimer_handle()` polls because hardware does not interrupt on overflow.

Control flow: initialization registers the PMU only on SPLPAR L1 hosts. Event init requires perfmon capability, sampling mode, no branch stack, a valid DTL mask, exclusive `dtl_access_lock` ownership, and a kmem-cache DTL buffer. Add registers the buffer with the hypervisor, clears `lppaca.dtl_idx`, enables the selected DTL mask, and starts a pinned hrtimer. Each timer tick copies new wrapped/non-wrapped DTL entries into the perf AUX area, prepending boot timebase/frequency once. Delete stops the timer, unregisters the DTL buffer, frees memory, and clears the enable mask.

State and persistence: per-CPU `vpa_dtl_cpu` stores active hypervisor buffers; per-CPU `vpa_pmu_ctx` stores output handles; `dtl_global_refc` and `dtl_global_lock` serialize PMU ownership against other DTL readers. AUX-private `vpa_pmu_buf` persists for the mmaped AUX area and tracks ring position and boot-time metadata. Hypervisor-visible state is the registered DTL buffer and lppaca enable/index fields.

Dependencies and integration: depends on `CONFIG_PPC_SPLPAR`, `asm/dtl.h`, `register_dtl()`, `unregister_dtl()`, `lppaca_of()`, `dtl_cache`, `dtl_access_lock`, perf AUX APIs, hrtimers, timebase helpers, and PowerVM firmware feature detection. It integrates with perf record/report/script via raw AUX records rather than normal samples.

Risks and test signals: lock/refcount error paths can leak `dtl_access_lock` or allocated buffers; AUX head accounting and wrap handling can truncate entries; event init allocates before add, so destroy callbacks are important; only L1 shared-processor hosts should load it. Test on SPLPAR L1 with `perf record -e vpa_dtl/dtl_all/ -m,aux`, small AUX buffers, high dispatch churn, concurrent `/proc/powerpc/vcpudispatch_stats`, invalid masks, counting-mode rejection, and event teardown under failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-dtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-pmu.c

Purpose: registers a simple counting PMU named `vpa_pmu` for PowerVM L1 VPA-based virtualization counters: L1-to-L2 context-switch latency, L2-to-L1 latency, and aggregate L2 runtime.

Important APIs/types/functions: `vpa_pmu_events_sysfs_show()` formats sysfs `event=0x..`; `VPA_PMU_EVENT_ATTR()` creates named events; `vpa_pmu_event_init()` validates event type and rejects sampling/branch stacks; `get_counter_data()` chooses per-task/vCPU or global KVM HV counter accessors; `vpa_pmu_add()`, `vpa_pmu_read()`, and `vpa_pmu_del()` implement counting; `pseries_vpa_pmu_init()` and cleanup register/unregister the PMU module.

Control flow: module init only succeeds on PowerVM LPAR L1, not KVM guests. Event add enables L2 counter accumulation for the current CPU and stores a baseline. Reads subtract the previous baseline from the current counter and add the delta to `event->count`. Delete performs a final read and disables accumulation for the CPU.

State and persistence: persistent state is the registered `struct pmu`; per-event state uses `event->hw.prev_count`; hypervisor/KVM HV state is toggled via `kvmhv_set_l2_counters_status()`. There is no local allocation.

Dependencies and integration: depends on KVM Book3S HV counter helpers, firmware feature checks, perf PMU registration, sysfs event macros, and module lifecycle. It uses `perf_sw_context` and declares no interrupts/exclude support.

Risks and test signals: `vpa_pmu_read()` does not update `prev_count`, so repeated reads add deltas from the original baseline; per-task versus CPU attachment changes accessor choice; enabling/disabling by `smp_processor_id()` assumes event CPU affinity semantics. Test counting with repeated `perf stat` reads, task-attached and CPU-wide events, concurrent events on the same CPU, LPAR/KVM/bare-metal load gating, and module unload while counters are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/44x.h

Purpose: provides small shared declarations and GPIO register offsets used by 44x board support code.

Important APIs/types/functions: declares assembly helpers `as1_readb()` and `as1_writeb()` for alternate address-space byte I/O, and defines `GPIO0_OSRH`, `GPIO0_TSRH`, and `GPIO0_ISR1H` offsets used by board-level GPIO mux workarounds.

Control flow: no executable C flow; includers call the AS1 helpers or use offsets in MMIO register arithmetic.

State and persistence: no state.

Dependencies and integration: paired with `misc_44x.S` for AS1 functions and with board files such as `canyonlands.c` for GPIO output/source register programming.

Risks and test signals: wrong offsets or address-space helper prototypes can corrupt board-control registers. Test builds of 44x platforms and board-specific USB/GPIO fixups that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/44x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Kconfig

Purpose: defines the 44x/47x platform, board, CPU-variant, GPIO, PCIe, MSI, and errata configuration menu entries that control which 44x source files and SoC support blocks are built.

Important APIs/types/functions: Kconfig symbols include board selectors such as `EBONY`, `SAM440EP`, `WARP`, `CANYONLANDS`, `ISS4xx`, `CURRITUCK`, `FSP2`, and `AKEBONO`; shared selector `PPC44x_SIMPLE`; driver-like `PPC4xx_GPIO`; CPU feature symbols `440EP`, `440EPX`, `440GRX`, `440GP`, `440GX`, `440SPe`, `460EX`, `460SX`, `476FPE`, `APM821xx`; and errata symbols `476FPE_ERR46` and `IBM440EP_ERR42`.

Control flow: Kconfig selection drives compilation through the 44x Makefile and other architecture Makefiles. Board symbols select CPU variants and subsystem dependencies such as `FORCE_PCI`, `PPC4xx_PCI_EXPRESS`, `PCI_MSI`, `PPC4xx_HSTA_MSI`, `COMMON_CLK`, `I2C`, USB host support, and EMAC PHY helpers.

State and persistence: persistent build-time state only; no runtime state. The selected symbols determine machine descriptors, interrupt controllers, PCI support, idle/CPM behavior, and board quirks.

Dependencies and integration: integrates with architecture `44x` and `PPC_47x` options, PCI, MPIC/UIC, EMAC, USB, I2C, GPIOLIB, SWIOTLB, and linker errata options.

Risks and test signals: incorrect `select` chains can omit mandatory interrupt/PCI/clock drivers or build incompatible board combinations. Test with `olddefconfig`/`randconfig` for representative boards, compile coverage for simple 44x and 47x, and boot logs verifying selected machine descriptors and bus probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Makefile

Purpose: maps 44x Kconfig symbols to the platform object files that implement common SoC setup, board descriptors, PCI/MSI support, power management, GPIO, and interrupt handling.

Important APIs/types/functions: always builds `misc_44x.o`, `machine_check.o`, `uic.o`, and `soc.o`; builds `idle.o` unless CPM is selected; conditionally builds `ppc44x_simple.o`, board files, `pci.o`, `hsta_msi.o`, `cpm.o`, and `gpio.o`.

Control flow: make evaluates Kconfig-driven `obj-*` assignments at build time. The resulting object list determines which `define_machine()`, initcall, and driver registration code enters the kernel.

State and persistence: build-time only.

Dependencies and integration: tied to symbols in `Kconfig`, generic powerpc platform linking, and initcall ordering inside each object.

Risks and test signals: missing object entries can make a selected board unbootable; unconditional common objects must remain safe across all 44x variants. Test per-board builds and confirm no duplicate machine descriptors conflict for enabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/canyonlands.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/canyonlands.c

Purpose: implements AMCC/APM PPC460EX Canyonlands board setup, including OF platform bus population, PCI resource reassignment, UIC interrupt wiring, reset hook, and a USB PHY/GPIO board-control fixup.

Important APIs/types/functions: `ppc460ex_device_probe()` probes `ibm,plb4`, `ibm,opb`, `ibm,ebc`, and `simple-bus`; `ppc460ex_probe()` marks PCI resources for reassignment; `ppc460ex_canyonlands_fixup()` maps the BCSR and PPC4xx GPIO controller, toggles the USB enable/reset bit, and configures GPIO16/GPIO19 alternate output; `define_machine(canyonlands)` supplies platform callbacks.

Control flow: machine probe is selected by compatible `amcc,canyonlands`. Device initcalls populate buses and perform the USB fixup. The fixup disables USB through BCSR7, waits 100 ms, enables USB, then sets OSRH/TSRH mux bits for USB stop signals.

State and persistence: persistent state is board-control and GPIO hardware register configuration. Mappings are temporary and released after init.

Dependencies and integration: depends on OF nodes `amcc,ppc460ex-bcsr` and `ibm,ppc4xx-gpio`, UIC interrupt code, PPC4xx reset, PCI bridge setup, and `44x.h` GPIO offsets.

Risks and test signals: error paths return early without unmapping BCSR if GPIO node lookup fails; hard-coded BCSR/GPIO bits are board-specific. Test Canyonlands boot, USB host/device behavior after reset, PCI enumeration, OF bus devices, and missing-node failure logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/canyonlands.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/cpm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/cpm.c

Purpose: implements PPC4xx Clock and Power Management support for idle wait/doze modes, standby/mem suspend entry, sysfs idle-mode selection, and DCR-based power gating of unused units.

Important APIs/types/functions: `struct cpm` stores mapped DCR host, register offsets, masks, and feature flags; `cpm_set()` sets CPM enable/freeze/status bits; `cpm_idle_wait()`, `cpm_idle_sleep()`, and `cpm_idle_doze()` enter low-power states; `cpm_idle_show()`/`cpm_idle_store()` expose `/sys/devices/system/cpu/cpu0/idle`; `cpm_suspend_valid()` and `cpm_suspend_enter()` implement `platform_suspend_ops`; `cpm_init()` parses the `ibm,cpm` OF node.

Control flow: the `powersave=off` setup parameter disables power-save installation. Late init sets the default `ppc_md.power_save` hook, finds and maps the CPM DCR range, decides register order from `er-offset`, reads masks from OF properties, gates unused units, creates sysfs when doze is available, and registers suspend ops when standby or suspend masks exist. Runtime idle either executes wait or sets CPM masks around wait; suspend disables decrementer interrupts while sleeping.

State and persistence: global `cpm` holds DCR mapping and masks; `idle_mode[]` persists the selected idle policy; hardware CPM registers persist power-gating requests. Sysfs mutates only the idle-mode selection.

Dependencies and integration: depends on OF DCR resources/properties, native DCR access, `ppc_md.power_save`, CPU sysfs, Linux suspend core, MSR wait-enable bits, and decrementer TCR handling.

Risks and test signals: CPM register order detection treats missing `er-offset` as one layout; sysfs string matching uses input length and may accept prefixes; suspend masks are board-provided and can power down necessary units. Test idle wait/doze transitions, `powersave=off`, sysfs mode switching, standby/mem suspend resume, DCR property variants, and unused-unit gating on boards with CPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/cpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ebony.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ebony.c

Purpose: provides IBM Ebony board machine support: OF device population, RTC instantiation, PCI resource reassignment, UIC interrupt setup, and reset/progress hooks.

Important APIs/types/functions: `ebony_device_probe()` probes PLB4/OPB/EBC buses and calls `of_instantiate_rtc()`; `ebony_probe()` enables `PCI_REASSIGN_ALL_RSRC`; `define_machine(ebony)` binds the compatible string `ibm,ebony`.

Control flow: early machine probing accepts the board and sets PCI reassignment. The machine device initcall later registers child platform devices and RTC. Interrupt handling uses `uic_init_tree()`/`uic_get_irq()`.

State and persistence: no local runtime state; persistent effects are registered platform devices, RTC device, PCI flags, and machine callbacks.

Dependencies and integration: depends on OF bus nodes, UIC, PPC4xx reset, generic PCI bridge code, and udbg progress output.

Risks and test signals: simple board file assumes the DT fully describes devices. Test Ebony boot, RTC creation, PCI enumeration, UIC interrupts, and reset path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ebony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.c

Purpose: implements IBM FSP-2 476FPE board support, including bus population, critical hardware error IRQ handlers, early DCR/L2/CMU error setup, UIC initialization, and board reset/progress hooks.

Important APIs/types/functions: diagnostic helpers `l2regs()` and `show_plbopb_regs()` dump L2 and bridge state; IRQ handlers `bus_err_handler()`, `cmu_err_handler()`, `conf_err_handler()`, `opbd_err_handler()`, `mcue_handler()`, and `rst_wrn_handler()` log hardware status and panic; `node_irq_request()` maps compatible error nodes to handlers; `critical_irq_setup()` installs all critical handlers; `fsp2_probe()` performs early hardware programming; `fsp2_irq_init()` chains UIC setup and critical IRQ registration.

Control flow: `fsp2_probe()` first checks flat-DT compatibility `ibm,fsp2`, clears/masks PLB6 errors, ungates/fixes TVSENSE, enables broad L2 machine-check/interrupt reporting, and enables configuration-logic parity errors. Later `fsp2_device_probe()` populates PLB/OPB buses. IRQ setup initializes UICs and registers fatal handlers based on OF compatible names.

State and persistence: persistent state is hardware register configuration in PLB, CMU, L2, DDR, and configuration logic DCRs plus registered IRQ handlers. The handlers intentionally terminate the system on fatal hardware errors.

Dependencies and integration: depends on FSP2 DCR macros in `fsp2.h`, UIC, OF IRQ parsing, PPC4xx reset, and board-specific compatible nodes for critical errors.

Risks and test signals: fatal handlers panic unconditionally; duplicated `P0EARH`/`P1EARH` prints may hide low register values; missing IRQ nodes leave errors unhandled; early DCR magic values are hardware-sensitive. Test FSP2 boot, critical IRQ registration, injected bus/CMU/config/DDR errors, reset-warning path, and OF bus device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.h

Purpose: defines FSP-2 DCR addresses, L2/PLB/DDR/CMU register offsets, reset-status bit masks, and helper macros for indirect CMU and L2 register access.

Important APIs/types/functions: exposes `DCRN_*` constants for PLB4/PLB6 bridges, PLB-OPB bridges, PLB-AHB/AHB-PLB, configuration logic, DDR3/4 controller, core wrapper, and L2 controller; defines CMU register IDs such as `CMUN_CRCS`, `CMUN_TVS1`, and `CMUN_FIR0`; defines `CRCS_STAT_*` reset causes; provides `mtcmu()`, `mfcmu()`, `mtl2()`, and `mfl2()` macros.

Control flow: no standalone execution. Callers write selector DCRs then data DCRs through the macros to access indirect CMU/L2 spaces.

State and persistence: no C state; constants describe persistent hardware state used by `fsp2.c` diagnostics and initialization.

Dependencies and integration: depends on `<asm/dcr.h>` and is used by FSP2 board error handling and early setup.

Risks and test signals: wrong DCR offsets can corrupt unrelated hardware; duplicate `DCRN_DDR34_ECC_CHECK_PORT1/2` value looks suspicious and should be checked against documentation. Test by reading known registers during FSP2 boot and validating error dumps against hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/gpio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/gpio.c

Purpose: implements a gpiolib driver for PPC4xx GPIO controllers with 32 GPIOs per controller, supporting input/output direction, value get/set, and OF platform binding.

Important APIs/types/functions: `struct ppc4xx_gpio` models the big-endian register block; `struct ppc4xx_gpio_chip` wraps `gpio_chip`, MMIO base, and spinlock; `ppc4xx_gpio_get()`, `ppc4xx_gpio_set()`, `ppc4xx_gpio_dir_in()`, and `ppc4xx_gpio_dir_out()` implement gpiolib operations; `ppc4xx_gpio_probe()` maps registers and registers the chip; `ppc4xx_gpio_driver` matches `ibm,ppc4xx-gpio`.

Control flow: arch init registers the platform driver. Probe allocates device-managed chip state, sets dynamic GPIO base and 32 lines, labels from the OF node, maps the first register resource, and calls `devm_gpiochip_add_data()`. Direction functions lock, disable open drain, set or clear TCR, and clear alternate-source/three-state mux bits in low or high source registers.

State and persistence: per-controller driver state is devm-managed; hardware output, direction, open-drain, and mux registers persist until changed. The spinlock serializes read-modify-write register updates.

Dependencies and integration: depends on OF platform bus creation by board files, big-endian MMIO helpers, gpiolib, and consumers such as LEDs or board fixups.

Risks and test signals: GPIO numbering uses MSB-first masks; mux clearing can override alternate functions when requesting GPIO mode; no IRQ support is implemented. Test GPIO input/output via libgpiod/sysfs consumers, concurrent set/direction changes, high GPIO numbers 16-31, and board consumers such as Warp LEDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/hsta_msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/hsta_msi.c

Purpose: provides PCI MSI support for PPC4xx SoCs where High Speed Transfer Assist generates interrupts from writes to 128-bit aligned MMIO addresses.

Important APIs/types/functions: `struct ppc4xx_hsta_msi` stores HSTA MMIO, physical base, MSI bitmap, IRQ map, and count; `hsta_setup_msi_irqs()` allocates bitmap entries, maps each MSI descriptor to a hardware IRQ, and writes MSI messages; `hsta_teardown_msi_irqs()` frees mappings; `hsta_msi_probe()` discovers resources and installs MSI controller ops on all PCI host bridges.

Control flow: subsys init registers a platform driver matching `ibm,hsta-msi`. Probe maps the HSTA memory resource, counts OF IRQs, allocates the MSI bitmap and IRQ map, parses each IRQ, then patches every `pci_controller` in `hose_list` with setup/teardown callbacks. Setup rejects MSI-X, allocates one hwirq per MSI descriptor, computes `address + index * 0x10`, associates the descriptor with the mapped IRQ, and writes an MSI message with zero data.

State and persistence: global singleton `ppc4xx_hsta_msi` persists HSTA state and bitmap allocations. Each MSI descriptor holds its associated Linux IRQ until teardown. HSTA MMIO mapping persists for the platform lifetime.

Dependencies and integration: depends on OF resources/IRQs, `asm/msi_bitmap.h`, PCI host bridge `controller_ops`, Linux MSI descriptors, and platform PCI bridge enumeration occurring before or alongside HSTA probe.

Risks and test signals: partial setup failure after bitmap allocation can leak entries; singleton design assumes one HSTA block; callbacks are assigned only to currently existing hoses; missing IRQ map entries break MSI setup. Test MSI-capable PCI devices on Akebono/compatible hardware, allocation exhaustion, device removal/teardown, MSI-X rejection, and boot ordering with multiple host bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/hsta_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/idle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/idle.c

Purpose: installs a simple PPC44x wait-mode idle loop unless booted with `idle=spin`.

Important APIs/types/functions: `ppc44x_idle()` saves MSR, sets wait-enable plus interrupt/debug/critical enable bits, executes `isync`, then restores MSR; `ppc44x_idle_init()` assigns `ppc_md.power_save`; `idle_param()` handles early `idle=spin`.

Control flow: early parameter parsing can set `mode_spin` and clear `ppc_md.power_save`. At arch init, if spin mode is not requested, the machine power-save hook is set to the wait loop. Runtime idle enters hardware wait and returns on interrupt.

State and persistence: static `mode_spin` stores boot policy; `ppc_md.power_save` persists as the architecture idle hook. Hardware MSR state is temporarily modified and restored each idle entry.

Dependencies and integration: used only when `CONFIG_PPC4xx_CPM` is not selected, because CPM has its own idle support. Depends on PowerPC MSR bits and generic idle paths calling `ppc_md.power_save`.

Risks and test signals: enabling the wrong MSR bits can affect interrupt delivery or debug behavior; CPM and simple idle are mutually exclusive in the Makefile. Test default idle, `idle=spin`, interrupt wakeups, and power-save hook selection on 44x boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/iss4xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/iss4xx.c

Purpose: supports the IBM ISS 4xx simulator platform, including OF device probing, UIC or MPIC interrupt-controller selection, optional 47x SMP spin-table startup, and reset/progress hooks.

Important APIs/types/functions: `iss4xx_device_probe()` registers PLB/OPB/EBC devices and RTC; `iss4xx_init_irq()` discovers the top-level interrupt controller and initializes UIC or MPIC; SMP helpers `smp_iss4xx_setup_cpu()` and `smp_iss4xx_kick_cpu()` program `cpu-release-addr` spin tables; `iss4xx_setup_arch()` installs SMP ops when appropriate; `define_machine(iss4xx)` binds `ibm,iss-4xx`.

Control flow: interrupt init scans interrupt-controller nodes without an `interrupts` property to find the root. If compatible with `ibm,uic`, it initializes UIC and sets `ppc_md.get_irq`; if compatible with `chrp,open-pic`, it allocates/initializes MPIC. For 47x SMP builds, CPU kick writes CPU number and secondary entry physical address into the spin table.

State and persistence: persistent effects are platform devices, RTC, interrupt controller state, `ppc_md.get_irq`, and optional global `smp_ops`. No local heap state is retained except MPIC/UIC allocations in those subsystems.

Dependencies and integration: depends on OF CPU and interrupt nodes, `uic.c`, MPIC, `start_secondary_47x`, MMU feature detection, generic SMP timebase helpers, and PPC4xx reset.

Risks and test signals: missing or unrecognized top-level interrupt controller panics; spin-table mapping assumes linear mapping and valid `cpu-release-addr`; `of_node_put()` is not visible after the root interrupt scan. Test ISS DT variants with UIC and MPIC, SMP secondary start, RTC instantiation, and simulator reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/iss4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/machine_check.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/machine_check.c

Purpose: decodes and logs PPC4xx/440A/47x machine-check causes before returning to generic exception handling.

Important APIs/types/functions: `machine_check_4xx()` distinguishes instruction versus data machine checks using ESR; `machine_check_440A()` decodes MCSR bits for PLB read/write, TLB parity, cache parity, and imprecise checks; `machine_check_47x()` adds 47x GPR/FPR parity and imprecise fields.

Control flow: architecture exception code calls the appropriate function based on CPU family. Instruction synchronous checks clear `ESR_IMCP`. Data checks read MCSR, print set cause bits, flush instruction cache for I-cache parity, clear MCSR by writing it back, and return 0.

State and persistence: hardware ESR/MCSR state is cleared for handled bits; instruction cache may be flushed on parity errors. No software state is stored.

Dependencies and integration: depends on `pt_regs->esr`, special registers `SPRN_ESR`/`SPRN_MCSR`, MCSR bit definitions, cache flush helpers, and CPU-family exception dispatch.

Risks and test signals: functions return 0 after severe errors, leaving policy to higher-level code; logging only in kernel mode may miss user-context nuance; exact MCSR bit meanings differ by CPU. Test injected instruction/data machine checks, cache parity paths, 47x parity bits, and that ESR/MCSR clearing prevents repeated exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/machine_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/misc_44x.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/misc_44x.S

Purpose: implements low-level PPC44x byte I/O helpers that temporarily switch data accesses to address space 1.

Important APIs/types/functions: global symbols `as1_readb` and `as1_writeb` are declared in `44x.h`. Both save MSR, set `MSR_DS`, synchronize, perform `lbz` or `stb`, restore MSR, and return.

Control flow: callers pass an MMIO byte address, the helper switches data-space context only for the single byte load/store, then restores the original MSR with sync/isync barriers around transitions.

State and persistence: temporarily mutates MSR data-space bit; no persistent software state. The write helper has hardware MMIO side effects.

Dependencies and integration: depends on PPC assembly macros, MSR bit definitions, and board code that needs AS1 access.

Risks and test signals: missing barriers or failure to restore MSR would corrupt later memory accesses; arguments follow PowerPC ABI registers. Test AS1 read/write users on 44x hardware and inspect disassembly for correct clobber expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/misc_44x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.c

Purpose: implements PPC4xx PCI, PCI-X, and PCI Express host bridge support, including OF bridge discovery, DMA-window validation, outbound/inbound mapping register programming, PCIe PHY/link initialization for several SoC variants, config-space access, and host-bridge resource fixups.

Important APIs/types/functions: `fixup_ppc4xx_pci_bridge()` hides host bridge BAR resources; `ppc4xx_parse_dma_ranges()` validates global DMA windows and sets `pci_dram_offset`; PCI helpers `ppc4xx_probe_pci_bridge()`, `ppc4xx_configure_pci_PMMs()`, and `ppc4xx_configure_pci_PTMs()` support older PCI; PCI-X helpers `ppc4xx_probe_pcix_bridge()`, `ppc4xx_configure_pcix_POMs()`, and `ppc4xx_configure_pcix_PIMs()` support PCI-X; PCIe uses `struct ppc4xx_pciex_port`, `struct ppc4xx_pciex_hwops`, SoC-specific hwops for 440SPe, 460EX, APM821xx, 460SX, and 476FPE/GTR, `ppc4xx_pciex_read_config()`/`write_config()`, and `ppc4xx_pciex_port_setup_hose()`. `ppc4xx_pci_find_bridges()` is the arch init entry point.

Control flow: arch init enables PCI domain flags, probes `ibm,plb-pciex`, `ibm,plb-pcix`, then `ibm,plb-pci` nodes. Each bridge allocates a `pci_controller`, gets bus ranges and OF ranges, maps registers/config space, disables stale windows, parses `dma-ranges`, programs outbound windows for memory/ISA/IO, programs inbound RAM windows, and configures Linux PCI ops. PCIe first initializes the shared core once, selects SoC hwops by compatible string, initializes each port from the `port`, `device_type`, `sdr-base`, config, UTL, and DCR resources, checks link, maps UTL/config space, and exposes a root complex or endpoint with vendor/device/class IDs.

State and persistence: global `dma_offset_set` enforces one DMA offset across all bridges; `pci_dram_offset` and each hose's DMA fields persist for PCI DMA mapping. PCIe global `ppc4xx_pciex_ports`, `ppc4xx_pciex_port_count`, and selected `ppc4xx_pciex_hwops` persist after init; each port keeps node, DCR mapping, UTL mapping, link state, endpoint mode, and hose pointer. Hardware mapping windows and PHY/link registers persist in bridge/SDR/DCR/config space.

Dependencies and integration: depends on OF address/range parsing, DCR/SDR accessors, generic powerpc PCI controller APIs, `pci_process_bridge_OF_ranges()`, `setup_indirect_pci()`, resource sizing, SoC register definitions from `pci.h`, and board Kconfig selecting PCIe support. It integrates with PCI enumeration, DMA mapping, MSI providers, platform board PCI flags, and host-bridge fixups.

Risks and test signals: DMA ranges must be power-of-two, aligned, cover all memory, and generally fit 32-bit PCI except 460SX/476FPE; wrong OF `port`/`sdr-base`/`device_type` prevents PCIe init; some 460EX PHY waits lack timeout; PCIe config reads suppress machine checks and must restore GPL config; IO window is hard-coded to 64 KiB; endpoint inbound mapping is fixed-size. Test PCI/PCI-X/PCIe enumeration on each supported SoC, invalid/mismatched `dma-ranges`, 64-bit DMA on 460SX/476FPE, no-link PCIe slots, CRS handling, bridge BAR hiding, ISA memory hole, MSI with HSTA, and suspend/reboot after bridge programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.h

Purpose: defines the register offsets, bit masks, and SoC-specific SDR/DCR constants used by PPC4xx PCI, PCI-X, and PCI Express bridge setup code.

Important APIs/types/functions: includes PCI-X register offsets (`PCIX0_*`), older PCI local bridge offsets (`PCIL0_*`), PCIe global DCR offsets (`DCRO_PEGPL_*`), SDR offsets for 440SPe/405EX/460EX/460SX/476FPE style PCIe PHYs, outbound mapping masks such as `GPL_DMER_MASK_DISA`, OMR/PIM constants, UTL/config offsets, lane width and port type fields, and SoC-specific link/status bits consumed by `pci.c`.

Control flow: no executable code. `pci.c` uses these constants to program bridge windows, mask config transaction errors, set up PCIe PHY/link registers, and access internal config/UTL spaces.

State and persistence: no software state; constants describe persistent hardware registers.

Dependencies and integration: tightly coupled to `pci.c`, PPC DCR/SDR accessors, PCI config-space helpers, and 4xx device-tree compatible strings selecting the right hardware path.

Risks and test signals: a wrong register offset can break PCI initialization or corrupt SoC state; this header encodes several subtly different hardware generations. Test by compiling all 44x/47x PCIe variants and boot-enumerating PCI/PCI-X/PCIe on representative hardware or simulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc44x_simple.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc44x_simple.c

Purpose: provides a generic machine descriptor for simple 44x evaluation boards whose differences are fully described by device tree and drivers.

Important APIs/types/functions: `ppc44x_device_probe()` probes PLB4/OPB/EBC/simple-bus children; `board[]` lists compatible strings accepted by the generic machine; `ppc44x_probe()` matches the current machine and enables PCI resource reassignment; `define_machine(ppc44x_simple)` installs UIC, reset, and progress callbacks.

Control flow: early probe iterates compatible strings and returns true on match. The device initcall registers platform devices for standard buses. Interrupts use UIC and reset uses the common PPC4xx DBCR reset path.

State and persistence: no local mutable state. Persistent effects are PCI flags, registered devices, and selected machine callbacks.

Dependencies and integration: depends on OF compatible matching, board DT completeness, UIC, generic PCI bridge code, PPC4xx reset, and udbg.

Risks and test signals: adding a board to `board[]` assumes no custom early setup is needed; `ibm,ebony` appears here despite a dedicated Ebony file, so configuration combinations should avoid ambiguous machine claims. Test all listed compatibles for correct machine selection, bus population, PCI enumeration, and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc44x_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc476.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc476.c

Purpose: supports PPC476FPE/47x boards Akebono and Currituck, including OF bus probing, PCI/USB/I2C board quirks, MPIC interrupt setup, SWIOTLB detection, SMP spin-table startup, board-revision detection, and machine descriptors.

Important APIs/types/functions: `quirk_ppc_currituck_usb_fixup()` forces an NEC USB controller into EHCI mode; AVR I2C helpers `avr_probe()`, `avr_reset_system()`, and `avr_power_off_system()` install Akebono reset/poweroff through an `akebono-avr` client; `ppc47x_device_probe()` registers the AVR driver and buses; `ppc47x_init_irq()` initializes a top-level MPIC; SMP helpers write `cpu-release-addr` spin tables; `ppc47x_setup_arch()` calls `swiotlb_detect_4g()` and SMP setup; `ppc47x_get_board_rev()` reads FPGA board revision; `ppc47x_pci_irq_fixup()` maps USB IRQs based on revision.

Control flow: device init adds AVR I2C support and probes PLB/OPB/EBC buses. IRQ init requires a `chrp,open-pic` root controller. Architecture setup assumes DMA windows cover RAM and enables SWIOTLB for high memory. Board revision init maps board FPGA registers for Currituck/Akebono. Currituck PCI IRQ fixup rewrites NEC USB IRQs for board revisions 0 or 2. Machine descriptors bind `ibm,akebono` and `ibm,currituck`.

State and persistence: global `avr_i2c_client` persists for reset/poweroff; `board_rev` persists for PCI IRQ fixups; `smp_ops`, `ppc_md.restart`, and `pm_power_off` may be reassigned. Hardware state includes USB config writes and FPGA-derived revision handling.

Dependencies and integration: depends on OF bus/CPU/FPGA nodes, MPIC, I2C core, PCI fixup infrastructure, SWIOTLB, 47x secondary entry code, PPC4xx reset, and USB controller IDs.

Risks and test signals: AVR reset spins forever after I2C write and assumes a probed client; spin-table mapping assumes linear addressability; unknown board revisions leave USB IRQ unresolved; MPIC is mandatory. Test Akebono poweroff/reset, Currituck USB enumeration/IRQ routing, SMP secondary start, SWIOTLB on >4G RAM, board revision reads, and missing AVR/FPGA node behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/ppc476.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/sam440ep.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/sam440ep.c

Purpose: implements ACube Sam440ep board support with OF bus probing, PCI resource reassignment, UIC interrupt setup, common reset hook, and static I2C RTC registration.

Important APIs/types/functions: `sam440ep_device_probe()` probes PLB4/OPB/EBC buses; `sam440ep_probe()` enables `PCI_REASSIGN_ALL_RSRC`; `define_machine(sam440ep)` binds `acube,sam440ep`; `sam440ep_setup_rtc()` registers an `m41st85` I2C board device at address `0x68`.

Control flow: machine probe selects the board and sets PCI flags. Device init probes buses and separately registers the RTC board info on I2C bus 0.

State and persistence: persistent effects are registered platform devices, static I2C RTC info, PCI flags, and machine callbacks. No local mutable state remains.

Dependencies and integration: depends on UIC, generic PPC4xx reset, PCI bridge setup, OF buses, and I2C adapter 0 existing for the RTC.

Risks and test signals: static I2C board info assumes bus numbering and RTC address; DT/board mismatch can duplicate RTC representation. Test Sam440ep boot, RTC detection, PCI enumeration, UIC interrupts, and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/sam440ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/soc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/soc.c

Purpose: provides shared PPC4xx SoC support for enabling the on-chip L2 cache, handling L2 parity errors, disabling SRAM windows, configuring snoop regions, and resetting the system through DBCR0.

Important APIs/types/functions: `l2c_diag()` issues L2 diagnostic commands; `l2c_error_handler()` decodes cache/tag parity errors and clears them; `ppc4xx_l2c_probe()` locates `ibm,l2-cache`, maps DCR bases, installs IRQ handler, disables SRAM, configures L2 mode/snoop/ports, clears errors, and enables L2; `ppc4xx_reset_system()` reads optional CPU `reset-type` and writes `SPRN_DBCR0`.

Control flow: arch init probes L2 cache if present. It reads `cache-size` and `dcr-reg`, maps IRQ, registers error handler, disables SRAM blocks, enables L2 mode without CPU ports, clears cache contents and parity/tag errors, programs two 32G snoop windows, then enables ICU/DCU ports and special 460EX/GT behavior. Reset writes core/chip/system reset bits and spins.

State and persistence: global `dcrbase_l2c` holds the L2 DCR base; hardware L2/SRAM/snoop/error registers persist. The IRQ handler clears hardware error state.

Dependencies and integration: depends on OF L2 cache node properties, DCR register definitions, IRQ mapping, PPC4xx reset consumers, and CPU node `reset-type`. Board machine descriptors call `ppc4xx_reset_system()`.

Risks and test signals: L2 enablement is hardware-sensitive and disables SRAM use; DCR properties must have four cells; busy-wait loops have no timeout; reset-type values outside 1-3 are ignored. Test boot with and without L2 cache nodes, parity-error IRQ injection, 460EX/GT L2 compatibility, SRAM users, and core/chip/system reset modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/uic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/uic.c

Purpose: implements the IBM PPC4xx Universal Interrupt Controller irqchip and irq-domain support, including primary and cascaded UIC initialization and top-level interrupt retrieval.

Important APIs/types/functions: `struct uic` stores index, DCR base, lock, and irq domain; irqchip callbacks `uic_unmask_irq()`, `uic_mask_irq()`, `uic_ack_irq()`, `uic_mask_ack_irq()`, and `uic_set_irq_type()` manipulate UIC ER/SR/TR/PR registers; `uic_host_map()` maps hardware IRQs to Linux IRQs; `uic_irq_cascade()` handles secondary UIC interrupts; `uic_init_tree()` initializes primary and cascaded controllers; `uic_get_irq()` returns the mapped pending primary IRQ.

Control flow: initialization finds the top-level `ibm,uic` node by selecting an interrupt-controller without an `interrupts` property, initializes it, sets it as the default domain, then scans for cascaded UIC nodes with `interrupts`, maps their cascade IRQ, and installs chained handlers. Runtime top-level IRQ reads `UIC_MSR`, computes the source with `32 - ffs(msr)`, and finds the virq. Cascades mask/ack the parent, read child MSR, dispatch the child domain IRQ, then ack/unmask parent as appropriate.

State and persistence: global `primary_uic` persists the root controller. Each `struct uic` persists DCR base, lock, and irq domain. Hardware ER/SR/TR/PR/CR registers persist interrupt enable, status, trigger, polarity, and critical configuration.

Dependencies and integration: depends on OF `cell-index` and `dcr-reg`, DCR accessors, Linux irq domains/chained handlers, two-cell interrupt spec translation, and machine descriptors using `uic_init_tree()`/`uic_get_irq()`.

Risks and test signals: `uic_get_irq()` can compute an invalid source when MSR is zero; default `handle_level_irq()` is used for both edge and level; missing properties return NULL and can panic in tree init; level IRQ ack timing is special. Test primary/cascaded UIC boot, edge/level polarity configuration, spurious interrupts, interrupt storms, cascaded device interrupts, and DT property validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/uic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/warp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/warp.c

Purpose: implements PIKA Warp board support, including OF bus probing, machine descriptor, POST reporting, optional digital temperature monitor thread, critical-temperature shutdown handling, fan monitoring, and manual LED GPIO setup.

Important APIs/types/functions: `warp_device_probe()` probes PLB/OPB/EBC buses; `define_machine(warp)` installs UIC and reset hooks; `warp_post_info()` reads FPGA POST words; under `CONFIG_SENSORS_AD7414`, `pika_setup_leds()` acquires green/red LED GPIOs and registers `leds-gpio`, `pika_setup_critical_temp()` programs the AD7414 and IRQ, `temp_isr()` enters emergency LED blink/reset loop, `pika_dtm_thread()` polls temperature and fan status, and `pika_dtm_start()` maps the FPGA and starts the kernel thread.

Control flow: base late init prints POST info if temperature support is absent. With AD7414 support, late init maps the FPGA, prints POST, starts `pika-dtm`, finds the AD7414 I2C client, sets LED ownership, programs high/low temperature thresholds, requests the critical-temp IRQ, then once per second reads temperature, mirrors it to FPGA offset `0x20`, and checks fan error state. Critical temperature disables local IRQs, turns green LED off, logs emergency text, repeatedly pokes an FPGA reset register, toggles red LED, and never returns.

State and persistence: global `dtm_fpga` stores mapped FPGA registers; `warp_gpio_led_pins` hold GPIO descriptors; `warp_gpio_leds` persists as a platform device; the DTM kernel thread persists until stopped; static fan state prevents repeated logs. Hardware state includes FPGA temperature mirror, LED outputs, AD7414 thresholds, and critical IRQ registration.

Dependencies and integration: depends on OF nodes `pika,warp`, `pika,fpga-sd`, `pika,fpga`, `warp-power-leds`, and `adi,ad7414`, UIC, I2C, gpiod, LEDs GPIO platform driver, kthreads, and PPC4xx reset.

Risks and test signals: critical ISR loops forever in interrupt context; LED GPIO acquisition bypasses DT automatic LED registration intentionally; thread startup requires the I2C device to exist; `dtm_fpga` is not unmapped on normal thread lifetime. Test Warp boot with and without AD7414 support, POST logging, LED registration, temperature polling, fan fault log throttling, critical-temp IRQ behavior on hardware, and reset path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/warp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Kconfig

Purpose: defines build-time options for Freescale MPC512x PowerPC Book3S 32-bit platforms and related LocalPlus FIFO and board support.

Important APIs/types/functions: `PPC_MPC512x` selects shared infrastructure such as `COMMON_CLK`, `FSL_SOC`, `IPIC`, `HAVE_PCI`, optional `FSL_PCI`, and EHCI endian quirks. Board/options include `MPC512x_LPBFIFO`, `MPC5121_ADS`, `MPC512x_GENERIC`, and `PDM360NG`.

Control flow: Kconfig selections determine which 512x Makefile objects and platform drivers are compiled. `MPC512x_LPBFIFO` depends on both platform support and `MPC512X_DMA`; board options select `DEFAULT_UIMAGE`.

State and persistence: build-time configuration only.

Dependencies and integration: integrates with common clock, Freescale SoC code, IPIC interrupt controller, PCI, USB EHCI endian settings, DMA, and board-specific platform files in the 512x directory.

Risks and test signals: dependency mistakes can build board code without required clocks/interrupts/PCI or omit endian quirks. Test defconfigs for MPC5121 ADS, generic boards, PDM360NG, and LPBFIFO module/builtin combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Makefile

Purpose: maps MPC512x Kconfig symbols to the platform objects for shared setup, clock support, board files, CPLD support, LocalPlus FIFO, and PDM360NG.

Important APIs/types/functions: builds `clock-commonclk.o` when `COMMON_CLK` is enabled; always builds `mpc512x_shared.o`; conditionally builds `mpc5121_ads.o`, `mpc5121_ads_cpld.o`, `mpc512x_generic.o`, `mpc512x_lpbfifo.o`, and `pdm360ng.o`.

Control flow: make-time object selection follows Kconfig, determining which machine descriptors and platform devices enter the kernel.

State and persistence: build-time only.

Dependencies and integration: paired with `platforms/512x/Kconfig` and the Freescale platform source files not in this work item.

Risks and test signals: missing object mappings can make a selected board unbootable; common shared code is always linked for `PPC_MPC512x`. Test board-specific builds and module/builtin LPBFIFO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/Makefile -->
