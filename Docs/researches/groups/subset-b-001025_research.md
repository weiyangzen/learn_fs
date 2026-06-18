# Research: subset-b-001025

This grouped report covers the requested ACPI/NFIT/NUMA source files. Each file section preserves the source path in the title and is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/core.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/nfit/core.c

## Purpose
`core.c` is the main ACPI NFIT driver. It bridges ACPI NFIT tables and ACPI `_DSM`/`_FIT` methods into the libnvdimm bus, DIMM, namespace, poison, security, and firmware activation interfaces. It discovers NFIT structures, builds persistent in-memory `nfit_*` objects, registers `nvdimm` devices and regions, exposes NFIT sysfs attributes, drives ARS address-range scrubs, and handles ACPI root/DIMM notifications.

## Important APIs, Types, And Functions
- Module parameters shape policy: `force_enable_dimms`, `disable_vendor_specific`, `override_dsm_mask`, `default_dsm_family`, `no_init_ars`, and `force_labels`.
- Global state: `LIST_HEAD(acpi_descs)` plus `acpi_desc_lock` expose active NFIT descriptors to MCE handling; `nfit_wq` serializes ARS work.
- UUID helpers `to_nfit_uuid()` and `to_nfit_bus_uuid()` translate enum/family IDs into GUIDs initialized at module load.
- `acpi_nfit_ctl()` is the central libnvdimm command callback. It validates `ND_CMD_*` or `ND_CMD_CALL`, selects DIMM or bus ACPI handles, builds ACPI package input, calls `_DSM` or `_LSI/_LSR/_LSW`, copies firmware output into libnvdimm buffers, and translates firmware status through `xlat_status()`.
- Table parsers `add_spa()`, `add_memdev()`, `add_dcr()`, `add_bdw()`, `add_idt()`, `add_flush()`, and `add_platform_cap()` validate and store NFIT subtables, preserving unchanged entries across `_FIT` updates via `nfit_table_prev`.
- `nfit_mem_init()` and `__nfit_mem_init()` assemble per-DIMM `struct nfit_mem` associations from SPA, MEMDEV, DCR, IDT, and flush records.
- `acpi_nfit_add_dimm()` detects ACPI child devices, installs DIMM notifications, probes DSM command families, handles label methods, and caches shutdown status.
- `acpi_nfit_register_dimms()` creates libnvdimm DIMM devices with command masks, flush hints, security ops, firmware ops, and NFIT sysfs groups.
- Region registration flows through `acpi_nfit_register_region()`, `acpi_nfit_init_mapping()`, and `acpi_nfit_init_interleave_set()` to create pmem/volatile regions and namespace cookies.
- ARS flows through `ars_get_cap()`, `ars_start()`, `ars_get_status()`, `ars_status_process_records()`, `ars_register()`, `acpi_nfit_scrub()`, and `acpi_nfit_ars_rescan()`.
- Platform entry points are `acpi_nfit_desc_init()`, `acpi_nfit_init()`, `acpi_nfit_probe()`, `__acpi_nfit_notify()`, `acpi_nfit_shutdown()`, `nfit_init()`, and `nfit_exit()`.

## Control Flow
At module init, GUIDs are parsed, the `nfit` workqueue is created, MCE handling is registered, and the ACPI platform driver for `ACPI0012` is registered. Probe installs root notifications, obtains NFIT data from the ACPI NFIT table or `_FIT`, initializes `acpi_nfit_desc`, and calls `acpi_nfit_init()`.

`acpi_nfit_init()` initializes bus DSM support and registers a libnvdimm bus on first entry. It then takes `init_mutex`, moves existing parsed subtables to temporary previous lists, parses incoming NFIT structures through `add_table()`, rejects unsupported deletions, assembles DIMMs, registers DIMMs, and registers regions. Runtime update notifications call `_FIT` again and merge the updated table under the same initialization path after flushing queued ARS work.

Command dispatch is libnvdimm-driven. `acpi_nfit_ctl()` maps libnvdimm commands to DSM function numbers, checks command masks, builds ACPI input, prefers label-specific AML methods where applicable, calls firmware, handles `ND_CMD_CALL` dynamic payloads, copies fixed outputs, and returns both transport status and firmware-derived `cmd_rc`.

ARS control flow starts during region registration. Supported volatile and pmem SPAs are queried for ARS capability, short and optional long ARS requests are queued, status records are processed into libnvdimm badranges, and delayed work continues interrupted or busy scans. User writes to the `scrub` sysfs file or uncorrected memory-error notifications call `acpi_nfit_ars_rescan()`.

## State And Persistence
The driver persists runtime topology in `struct acpi_nfit_desc` lists for SPAs, MEMDEVs, DCRs, BDWs, IDTs, flush hints, DIMMs, ARS status, and firmware activation state. `struct nfit_mem` stores per-DIMM command family, DSM mask, label-method flags, dirty shutdown state, flush resources, ACPI child device pointer, and libnvdimm object pointer. Persistent memory resources may be inserted into `iomem_resource` as `IORES_DESC_PERSISTENT_MEMORY`. ARS bad ranges are pushed to libnvdimm, and scrub counters are exposed through sysfs with `sysfs_notify_dirent()`.

## Dependencies And Integration Points
This file depends heavily on ACPICA table/method services, ACPI device notification handlers, libnvdimm bus/DIMM/region APIs, ndctl command descriptors, kernel resource management, sysfs/kernfs, workqueues, NUMA PXM translation, and the Intel-specific ops from `intel.c`. It exports helper APIs consumed by MCE, tests, and other NVDIMM code, including `acpi_nfit_ctl()`, `acpi_nfit_init()`, `acpi_nfit_shutdown()`, `acpi_nfit_desc_init()`, `__acpi_nfit_notify()`, `__acpi_nvdimm_notify()`, `nfit_get_smbios_id()`, `nfit_spa_type()`, and `to_nfit_uuid()`.

## Risks
The code trusts firmware-provided NFIT lengths after per-structure validation, so malformed firmware can block initialization or suppress topology. `_FIT` updates support additions and unchanged entries but explicitly reject deletions. Static `mappings[ND_MAX_MAPPINGS]` requires hard failure when firmware exceeds mapping capacity. DSM command masks and deny masks are safety boundaries; mistakes can expose destructive security or firmware activation commands through ioctl. ARS work races with userspace ARS start requests and shutdown are managed with locks and cancel bits but remain concurrency-sensitive. Label fallback between Intel DSMs and `_LS*` methods is policy-heavy and can affect namespace visibility on locked or read-only-label DIMMs.

## Test Signals
Useful tests include nfit unit tests with synthetic NFIT tables, `_FIT` hot-add/update paths, malformed subtable length cases, DSM command-mask probing for Intel/HPE/MSFT/Hyper-V families, label access via DSM and `_LSI/_LSR/_LSW`, ARS busy/interrupted/overflow status handling, MCE-triggered rescan integration, sysfs `nfit/*` attributes, DIMM notification `flags` updates, firmware activation state visibility, teardown races, and namespace cookie compatibility across interleave sort orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.c

## Purpose
`intel.c` implements Intel-specific NFIT DSM support for NVDIMM security and firmware activation. It translates Intel vendor DSM payloads into libnvdimm `nvdimm_security_ops`, per-DIMM firmware activation ops, and bus-level firmware activation ops.

## Important APIs, Types, And Functions
- `dev_attr_firmware_activate_noidle` exposes a bus sysfs toggle that controls whether bus activation asks firmware to force idle devices or assume OS-idled devices.
- `intel_fwa_supported()` verifies that the Intel bus family and both bus firmware activation DSMs are present.
- Security helpers include `intel_security_flags()`, `intel_security_freeze()`, `intel_security_change_key()`, `intel_security_unlock()`, `intel_security_disable()`, `intel_security_erase()`, `intel_security_overwrite()`, and `intel_security_query_overwrite()`.
- Exported ops pointers are `intel_security_ops`, `intel_fw_ops`, and `intel_bus_fw_ops`.
- Bus firmware activation helpers include `intel_bus_fwa_businfo()`, `intel_bus_fwa_state()`, `intel_bus_fwa_capability()`, and `intel_bus_fwa_activate()`.
- DIMM firmware activation helpers include `intel_fwa_dimminfo()`, `intel_fwa_state()`, `intel_fwa_result()`, and `intel_fwa_arm()`.

## Control Flow
Security calls construct an `ND_CMD_CALL` package with `NVDIMM_FAMILY_INTEL`, copy passphrases where needed, call `nvdimm_ctl()`, and translate Intel status codes to Linux errors. `get_flags` short-circuits user security state while overwrite is in progress because firmware reports indeterminate state during overwrite.

Firmware activation is split into bus and DIMM flows. Bus state refresh calls `NVDIMM_BUS_INTEL_FW_ACTIVATE_BUSINFO`, maps firmware state and capability into libnvdimm enums, and caches capability/state in `acpi_nfit_desc`. Activation validates that the bus is armed, issues `NVDIMM_BUS_INTEL_FW_ACTIVATE`, invalidates cached bus state, and increments `fwa_count` so DIMM result caches are refreshed. DIMM state/result reads use `NVDIMM_INTEL_FW_ACTIVATE_DIMMINFO`; arm/disarm uses `NVDIMM_INTEL_FW_ACTIVATE_ARM` after validating current state.

## State And Persistence
State is cached in `struct acpi_nfit_desc` for bus firmware activation state, capability, activation count, and no-idle policy. Per-DIMM state/result/count live in `struct nfit_mem`. Passphrase material is copied into stack-based DSM packages and not persisted by this file.

## Dependencies And Integration Points
The file depends on libnvdimm command routing, `nfit.h` provider data, Intel payload definitions in `intel.h`, ACPI NFIT command masks established by `core.c`, and `memregion.h`/SMP-related infrastructure for activation contexts. `core.c` attaches these ops only for Intel-family DIMMs or buses with complete required DSM masks.

## Risks
Security status translation must remain exact because wrong errno choices can cause user tooling to retry, fail, or misreport destructive operations. Passphrase payload layout depends on packed structs and `TRAILING_OVERLAP`. Firmware activation state caching is invalidated by activation count rather than taking NFIT init locks in suspended contexts; stale counts or missed invalidations would hide results. The `firmware_activate_noidle` knob changes platform quiesce policy and can affect device safety during activation.

## Test Signals
Test with mocked Intel DSM command masks and payload statuses: unsupported commands, invalid passphrase, invalid state, overwrite busy, master/user passphrase paths, security freeze, DIMM arm/disarm idempotence, bus activation with armed/idle/busy states, activation count invalidation, and sysfs toggling of `firmware_activate_noidle`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.h

## Purpose
`intel.h` defines Intel NFIT DSM constants, status values, security payload layouts, SMART fields, and firmware activation payloads used by `intel.c` and `core.c`.

## Important APIs, Types, And Functions
- SMART definitions: `ND_INTEL_SMART`, `struct nd_intel_smart`, and shutdown-count/shutdown-valid flags consumed by `nfit_intel_shutdown_status()`.
- Security constants cover status sizes, passphrase sizes, firmware statuses, security state bits, and extended master-passphrase state bits.
- Packed payloads include get security state, set/unlock/disable passphrase, freeze lock, secure erase, overwrite, query overwrite, master passphrase, and master secure erase.
- Firmware activation constants define DIMM and bus states/results/capabilities and packed payloads for DIMM info, DIMM arm, bus info, and bus activation.
- Extern declarations publish `intel_security_ops`, `intel_fw_ops`, and `intel_bus_fw_ops`.

## Control Flow
The header has no runtime control flow, but its packed structs define the binary ABI passed inside `ND_CMD_CALL` packages to ACPI `_DSM` firmware. Status constants are later translated by Intel operation code into libnvdimm states and Linux errors.

## State And Persistence
No state is stored here. The file specifies field layouts for transient DSM buffers and bit definitions that drive cached state elsewhere.

## Dependencies And Integration Points
It is included by `core.c` for Intel SMART/shutdown and command masks, and by `intel.c` for all Intel-specific DSM wrappers. It depends on libnvdimm declarations for ops pointer types.

## Risks
The packed layouts and constants are ABI-sensitive. Any field order, size, or status collision mistake can corrupt firmware commands. `ND_INTEL_STATUS_OVERWRITE_UNSUPPORTED` and `ND_INTEL_STATUS_OQUERY_INPROGRESS` intentionally share a numeric value but apply to different commands, so command context is required when translating.

## Test Signals
Build-time structure layout checks are implicit through command behavior rather than explicit in this file. Unit tests should validate sizeof expected payloads, status-code translation by command context, and compatibility with Intel DSM documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/mce.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/nfit/mce.c

## Purpose
`mce.c` connects x86 machine-check notifications to NFIT persistent-memory error handling. It detects uncorrectable memory errors inside NFIT persistent memory ranges, records bad ranges in libnvdimm, notifies affected regions, and optionally schedules ARS.

## Important APIs, Types, And Functions
- `nfit_handle_mce()` is the notifier callback.
- `nfit_mce_register()` and `nfit_mce_unregister()` register/unregister the notifier with the x86 MCE decode chain.
- The notifier block uses `MCE_PRIO_NFIT`.

## Control Flow
The callback ignores non-memory, correctable, or unusable-address MCEs. It locks `acpi_desc_lock`, iterates active `acpi_descs`, takes each descriptor `init_mutex`, and searches pmem SPAs covering `mce->addr`. On a match it aligns the failing address by `MCI_MISC_ADDR_LSB`, adds a badrange to the nvdimm bus, notifies the matched region with `NVDIMM_REVALIDATE_POISON`, optionally schedules ARS when hardware-error scrubbing is enabled, marks the MCE with `MCE_HANDLED_NFIT`, and stops scanning.

## State And Persistence
It does not own persistent state. It reads the global NFIT descriptor list and writes badrange state into libnvdimm. `mce->kflags` is updated to indicate NFIT handled the event.

## Dependencies And Integration Points
The file is compiled only when `CONFIG_X86_MCE` enables the declarations in `nfit.h`. It depends on x86 MCE helpers, global `acpi_descs`, `nfit_spa_type()`, `nvdimm_bus_add_badrange()`, `nvdimm_region_notify()`, and `acpi_nfit_ars_rescan()`.

## Risks
The callback assumes NFIT topology remains valid under `acpi_desc_lock` and `init_mutex`; teardown must remove descriptors under the same lock. A subtle risk is using the last `nfit_spa` after unlocking `init_mutex`, though descriptor lifetime is protected by the outer list lock. Alignment depends on MCE misc bits. ARS scheduling failure is mostly ignored because recovery choices are limited in MCE context.

## Test Signals
Inject synthetic MCEs for addresses inside and outside pmem SPAs, correctable vs uncorrectable events, invalid-address MCEs, scrub-mode on/off, multiple NFIT descriptors, and teardown/register/unregister ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/mce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/nfit.h -->
# sources/distributed-fs/ceph-client/drivers/acpi/nfit/nfit.h

## Purpose
`nfit.h` is the internal contract for the ACPI NFIT driver. It defines UUIDs, command masks, NFIT object wrappers, per-DIMM and per-bus state structures, ARS state enums, block-window helpers, and cross-file function declarations.

## Important APIs, Types, And Functions
- UUID string macros map ACPI, Intel, HPE, Microsoft, and Hyper-V NFIT command families and SPA range types.
- Command masks define standard, Intel security, Intel firmware activation, bus firmware activation, full Intel command exposure, and denied ioctl command groups.
- `enum nfit_uuids`, `enum nvdimm_family_cmds`, and `enum nvdimm_bus_family_cmds` map family/function IDs.
- Wrapper structs `nfit_spa`, `nfit_dcr`, `nfit_bdw`, `nfit_idt`, `nfit_flush`, and `nfit_memdev` embed list nodes plus flexible ACPI table payloads.
- `struct nfit_mem` assembles all known table, ACPI, libnvdimm, flush, DSM, shutdown, security, and firmware state for one DIMM.
- `struct acpi_nfit_desc` owns bus-level lists, locks, work, ARS status, DSM masks, platform capabilities, and firmware activation cache.
- Inline helpers include `__to_nfit_memdev()` and `to_acpi_desc()`.
- Externs publish NFIT initialization, shutdown, notification, command, ARS, MCE, and Intel helper entry points.

## Control Flow
No executable control flow is implemented beyond simple inline selectors. The header defines the data relationships that `core.c`, `intel.c`, and `mce.c` rely on: descriptor to bus, descriptor to lists, DIMM to ACPI/libnvdimm objects, and optional compile-time MCE functions.

## State And Persistence
Most NFIT runtime state layout is defined here. Important persistent-in-memory fields include ARS state bits per SPA, bus scrub counters and flags, bus and DIMM DSM masks, dirty shutdown indicators, flush write-pending queue resources, and firmware activation state/count caches.

## Dependencies And Integration Points
The header depends on workqueues, libnvdimm, ndctl, ACPI, and ACPI UUID definitions. It is the shared boundary among NFIT core, Intel-specific operations, MCE handling, and external test/support code.

## Risks
Because this header defines cross-file state, field changes can silently alter lifetime, locking, or ABI assumptions in several files. Command mask macros use bit shifts and assume command IDs remain within `NVDIMM_CMD_MAX`/word width. Flexible-array wrappers require allocation sizes to match validated ACPI table lengths.

## Test Signals
Build all NFIT configurations with and without `CONFIG_X86_MCE`; exercise command masks, per-DIMM provider data, ARS state transitions, flush hint allocation, and Intel firmware/security op attachment. Static analysis should check bit shifts and container relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nfit/nfit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nhlt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/nhlt.c

## Purpose
`nhlt.c` provides exported helpers for ACPI NHLT audio topology tables. It stores the first NHLT table globally, offers endpoint and format lookup routines, and derives microphone counts for PDM microphone endpoints.

## Important APIs, Types, And Functions
- `acpi_nhlt_get_gbl_table()` obtains ACPI table index 0 for `ACPI_SIG_NHLT`, falling back to an empty table if none exists.
- `acpi_nhlt_put_gbl_table()` releases the global table pointer.
- `acpi_nhlt_endpoint_match()` matches endpoint link type, device type, stream direction, and bus ID, with negative arguments as wildcards.
- `acpi_nhlt_tb_find_endpoint()` and `acpi_nhlt_find_endpoint()` search a specific table or the global table.
- `acpi_nhlt_endpoint_find_fmtcfg()`, `acpi_nhlt_tb_find_fmtcfg()`, and `acpi_nhlt_find_fmtcfg()` search format configurations by channels, rate, valid bits, and bits per sample.
- `acpi_nhlt_endpoint_mic_count()` infers PDM microphone count from format channels and mic-array config.

## Control Flow
Callers first initialize the global table. Search helpers iterate NHLT endpoints and endpoint format configs through ACPI NHLT iterator macros. Mic-count logic validates PDM endpoints, computes maximum channel count from formats, reads endpoint capabilities, detects standard mic-array config, maps known array types to fixed counts, and handles vendor arrays by validating the variable-length payload.

## State And Persistence
The only module state is `acpi_gbl_nhlt`, which points to the ACPI table or a static `empty_nhlt`. There is no locking in this file, so lifecycle is expected to be controlled by ACPI core/audio users.

## Dependencies And Integration Points
It depends on `<acpi/nhlt.h>` structures and iterator macros and exports all public helpers to GPL modules. Consumers are typically Intel/SoC audio drivers that need endpoint, format, or microphone topology information from firmware.

## Risks
The helpers assume NHLT iterator macros correctly enforce bounds. `acpi_nhlt_put_gbl_table()` calls `acpi_put_table()` even when `acpi_gbl_nhlt` may be the static empty fallback, so correctness depends on ACPICA tolerating that pointer path or callers only putting after successful get semantics. Current global lookup is limited to table index 0. Vendor mic config validation must be exact to avoid reading beyond capabilities.

## Test Signals
Use synthetic NHLT tables with no table, multiple endpoints, wildcard searches, missing formats, standard two/four-mic arrays, vendor arrays with matching and mismatched `mics_count`, non-PDM endpoint rejection, and lifecycle get/put calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nhlt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/acpi/numa/Kconfig

## Purpose
This Kconfig file defines ACPI NUMA and HMAT build options for the ACPI NUMA directory.

## Important APIs, Types, And Functions
- `config ACPI_NUMA` defaults on when `NUMA && !X86`, enabling generic ACPI SRAT NUMA support on non-x86 architectures where selected.
- `config ACPI_HMAT` is a user-visible boolean for ACPI Heterogeneous Memory Attribute Table support.
- `ACPI_HMAT` depends on `ACPI_NUMA` and selects `HMEM_REPORTING` and `MEMREGION`.

## Control Flow
There is no runtime control flow. The configuration controls whether `srat.o` and `hmat.o` are built via the local Makefile and whether HMAT reporting infrastructure dependencies are enabled.

## State And Persistence
No runtime state is stored here. Build-time state determines compiled feature availability.

## Dependencies And Integration Points
The options integrate ACPI NUMA parsing with the wider kernel NUMA, hmem reporting, and memregion subsystems. The x86 exclusion in `ACPI_NUMA` reflects architecture-specific handling elsewhere.

## Risks
Incorrect dependency changes could build HMAT without SRAT/PXM mapping support or omit required memory reporting infrastructure. Since `ACPI_HMAT` selects dependencies, downstream code may assume those APIs exist.

## Test Signals
Compile matrix with NUMA on/off, x86/non-x86, ACPI_HMAT enabled/disabled, and verify the Makefile emits only expected objects and no unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/acpi/numa/Makefile

## Purpose
The Makefile maps ACPI NUMA Kconfig options to object files.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_ACPI_NUMA) += srat.o`
- `obj-$(CONFIG_ACPI_HMAT) += hmat.o`

## Control Flow
There is no runtime control flow. Kbuild includes SRAT and HMAT implementations based on configuration symbols.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
This file is the build integration point for `srat.c` and `hmat.c`. It relies on `Kconfig` to ensure dependencies are satisfied.

## Risks
The main risk is build skew: changing Kconfig without this Makefile, or vice versa, can compile code under unsupported dependency combinations.

## Test Signals
Check object inclusion in representative configs and run `make drivers/acpi/numa/` or full kernel builds for `CONFIG_ACPI_NUMA` and `CONFIG_ACPI_HMAT` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/hmat.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/numa/hmat.c

## Purpose
`hmat.c` parses ACPI HMAT and related SRAT entries to report heterogeneous memory performance, cache attributes, generic port coordinates, hmem devices, and memory-tier distance information.

## Important APIs, Types, And Functions
- `disable_hmat()` disables HMAT parsing during init.
- Global lists track `memory_target`, `memory_initiator`, and `memory_locality` objects; `target_lock` protects runtime target registration/coordinate lookup.
- Exported CXL namespace APIs: `hmat_get_extended_linear_cache_size()` and `acpi_get_genport_coordinates()`.
- Parsing functions include `srat_parse_mem_affinity()`, `srat_parse_genport_affinity()`, `hmat_parse_proximity_domain()`, `hmat_parse_locality()`, `hmat_parse_cache()`, and `hmat_parse_subtable()`.
- Attribute calculation and registration functions include `hmat_update_target_attrs()`, `hmat_register_target_initiators()`, `hmat_register_target_cache()`, `hmat_register_target_perf()`, `hmat_register_target_devices()`, `hmat_hotplug_target()`, and `hmat_register_targets()`.
- Memory-tier integration uses `hmat_set_default_dram_perf()` and `hmat_calculate_adistance()`.

## Control Flow
`hmat_init()` runs as a `subsys_initcall`. It exits if SRAT is disabled or HMAT is disabled, parses SRAT memory affinities to create memory targets and generic port affinities to create generic-port targets, then parses HMAT revision 1 or 2 proximity, locality, and cache structures. After parsing it registers hmem devices, node initiator links, cache attributes, performance coordinates, a node-hotplug notifier, and an abstract-distance algorithm if default DRAM performance setup succeeds.

Locality parsing normalizes firmware entries based on HMAT revision and data type, allocates initiator records, updates local target access when initiator and target match, and stores locality matrices for best-initiator selection. Target registration computes best initiator sets by prioritizing latency and bandwidth data, then publishes node relationships and performance attributes. Hotplug callbacks register delayed memory-only nodes when first memory is added.

## State And Persistence
Runtime state lives in global lists of targets, initiators, localities, per-target resource trees, cache lists, generic port handles, and access-coordinate arrays. State is intentionally retained after successful init for hotplug and exported CXL lookups. On parse failure, `hmat_free_structures()` releases allocated lists and resource children.

## Dependencies And Integration Points
The file integrates ACPI SRAT/HMAT table parsing, node/PXM mappings from `srat.c`, Linux node sysfs/cache/perf attribute APIs, `memregion` and `hmem_register_resource()`, CXL generic port consumers, node hotplug notifications, DAX hmem support, and memory-tier abstract distance calculations.

## Risks
Firmware table validation is length-based but still relies on variable-sized matrix arithmetic; overflow or malformed counts are important hazards. Best-initiator selection uses PXM bitmaps sized by `MAX_NUMNODES`; PXM values must be valid node-domain IDs. Generic port handling only supports ACPI device handles and skips PCI handles. Successful init keeps ACPI table memory and structures for future notifier use, so lifecycle mistakes can leak or dangle. Revision-specific normalization can misreport performance if firmware uses unexpected units.

## Test Signals
Test SRAT-only, absent HMAT, disabled HMAT, invalid revisions, malformed locality/cache lengths, memory-only nodes, hotplug first-memory registration, generic port ACPI handle coordinates, extended-linear cache lookup, DAX hmem resource creation, default DRAM performance selection, and abstract distance conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/hmat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/srat.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/numa/srat.c

## Purpose
`srat.c` implements generic ACPI SRAT/SLIT NUMA parsing. It maps ACPI proximity domains to Linux node IDs, records memory affinity ranges, delegates CPU affinity handling to architecture hooks, handles generic initiators, integrates CXL fixed memory windows, and exports ACPI node lookup helpers.

## Important APIs, Types, And Functions
- Global maps: `pxm_to_node_map`, `node_to_pxm_map`, `nodes_found_map`, `acpi_srat_revision`, `acpi_numa`, and `last_real_pxm`.
- Public helpers: `disable_srat()`, `pxm_to_node()`, `node_to_pxm()`, `acpi_map_pxm_to_node()`, `srat_disabled()`, `bad_srat()`, `acpi_numa_init()`, `acpi_node_backed_by_real_pxm()`, and `acpi_get_node()`.
- Optional `fix_pxm_node_maps()` supports NUMA emulation.
- Parsers cover SLIT, SRAT memory affinity, x2APIC, legacy processor affinity, GICC, generic initiator, RINTC, and CEDT CFMWS entries.
- Weak hooks allow architecture-specific CPU and memory block behavior, such as `numa_fill_memblks()` and affinity init functions.

## Control Flow
`acpi_numa_init()` parses SRAT header to capture revision, then parses processor/generic initiator subtables before memory affinity subtables. Memory affinities validate enabled entries, map PXM to nodes, add NUMA memory blocks, mark hotplug ranges, update `max_possible_pfn`, and count parsed ranges. SLIT parsing validates locality distances and publishes node distances. After SRAT, CXL CFMWS ranges are parsed to extend existing memblocks or allocate fake PXMs for CXL-only windows. The function returns success only when memory blocks were parsed, otherwise `-ENOENT`.

`acpi_get_node()` walks an ACPI handle and parents looking for `_PXM`, then translates the proximity domain with `pxm_to_node()`.

## State And Persistence
The core persistent state is the bidirectional PXM/node maps and parsed node masks. `last_real_pxm` separates firmware SRAT PXMs from fake PXMs created for CFMWS. Memory affinity parsing updates global NUMA memblock state and hotplug annotations.

## Dependencies And Integration Points
This file integrates ACPICA table parsing, Linux NUMA memblock setup, architecture-specific CPU affinity callbacks, memory hotplug, CXL CEDT parsing, SLIT node-distance APIs, ACPI `_PXM` evaluation, and exported node/PXM helpers consumed by NFIT, HMAT, PCI, and other ACPI-aware subsystems.

## Risks
SRAT errors call `bad_srat()` and disable SRAT globally while continuing parse callbacks, so one malformed memory entry can discard firmware NUMA data. `fix_pxm_node_maps()` copies only bounded arrays and must preserve reverse mappings under NUMA emulation. CFMWS fake PXMs must not collide with real PXMs. SLIT validation rejects suspicious equal remote/local distances, which may disable firmware distance data on buggy BIOSes. PXM values outside limits map to `NUMA_NO_NODE`.

## Test Signals
Test valid and invalid SRAT revisions, enabled/disabled memory affinities, hotplug and non-volatile memory flags, too many PXMs, malformed lengths, SLIT invalid distances, CPU affinity arch hooks, generic initiators on x86/arm64, CFMWS windows overlapping and not overlapping SRAT memblocks, `_PXM` parent fallback, and NUMA emulation remapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/numa/srat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nvs.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/nvs.c

## Purpose
`nvs.c` records ACPI NVS regions and, when sleep support is enabled, saves/restores their contents across suspend and resume.

## Important APIs, Types, And Functions
- `struct nvs_region` and `nvs_region_list` record all ACPI NVS physical ranges for general iteration.
- `acpi_nvs_register()` adds an NVS range and registers it for suspend save/restore.
- `acpi_nvs_for_each_region()` iterates registered ranges for APEI or other ACPI users.
- Under `CONFIG_ACPI_SLEEP`, `struct nvs_page` tracks page-sized save units, mapped kernel address, saved data page, and unmap mode.
- Suspend lifecycle functions are `suspend_nvs_alloc()`, `suspend_nvs_save()`, `suspend_nvs_restore()`, and `suspend_nvs_free()`.

## Control Flow
Registration appends the raw region and splits it into page-bounded `nvs_page` entries for suspend. Before suspend, `suspend_nvs_alloc()` allocates one page of backup storage per entry. `suspend_nvs_save()` maps each physical range using an existing ACPI permanent mapping if possible or `acpi_os_ioremap()` otherwise, then copies contents to backup pages. Resume copies backup data back into the mapped NVS addresses, and cleanup frees backup pages and unmaps addresses after resume.

## State And Persistence
Registered region metadata persists for the boot lifetime. Suspend backup data persists only across a suspend/resume cycle. Mapped addresses may remain until `suspend_nvs_free()` because restore runs with interrupts disabled and cannot unmap.

## Dependencies And Integration Points
It depends on ACPI memory mapping helpers from `osl.c`, kernel list/slab/page allocation APIs, and ACPI sleep infrastructure. `acpi_nvs_for_each_region()` provides an integration point for APEI.

## Risks
Registration allocations are not rolled back from `nvs_region_list` if suspend registration later fails. Save failure frees all NVS backup state, so resume restore will have nothing to copy. Non-page-aligned regions are split correctly, but many small regions can allocate many tracking objects and pages. Restore assumes mappings remain valid from save time.

## Test Signals
Test aligned and unaligned NVS ranges, allocation failure rollback in suspend paths, existing ACPI mapping vs fallback ioremap, save/restore byte accuracy, free after failed save, no-sleep configuration stubs, and iteration callback early termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/nvs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/osi.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/osi.c

## Purpose
`osi.c` implements Linux policy for ACPI `_OSI` interface strings. It handles command-line overrides, DMI quirks, Apple Darwin behavior, late ACPICA interface installation/removal, and logging of firmware `_OSI(Linux)`/`_OSI(Darwin)` queries.

## Important APIs, Types, And Functions
- `struct acpi_osi_entry` stores string/enable pairs; `struct acpi_osi_config` tracks default disabling and whether Linux/Darwin policy came from DMI or command line.
- `acpi_osi_setup()` parses one raw `acpi_osi=` string into setup entries or global disabling.
- `osi_setup()` is the `__setup("acpi_osi=", ...)` handler.
- `acpi_osi_setup_late()` applies queued interface changes with `acpi_update_interfaces()`, `acpi_install_interface()`, and `acpi_remove_interface()`.
- `acpi_osi_handler()` logs notable firmware queries.
- `early_acpi_osi_init()` applies DMI blacklist/Apple setup; `acpi_osi_init()` installs the interface handler and late setup.
- `acpi_osi_is_win8()` exposes ACPICA OSI data state to other code.

## Control Flow
Early boot DMI checks disable or enable selected OSI strings for known systems, and Apple hardware enables Darwin unless overridden. Command-line parsing can disable `_OSI` entirely, disable all vendor strings, disable all strings, re-enable defaults, add strings, or remove strings. During ACPI OS initialization, the handler is installed and queued string policy is applied to ACPICA. Runtime AML `_OSI` calls flow through the installed handler for logging while ACPICA supplies the actual supported result.

## State And Persistence
Policy state is in static `osi_config` and the initdata `osi_setup_entries` array. Once late setup runs, ACPICA owns the active interface list. Command-line and DMI flags are retained for one-time query messages.

## Dependencies And Integration Points
The file depends on ACPICA global OSI controls, DMI matching, x86 Apple platform detection, kernel setup parameter parsing, and ACPI initialization in `osl.c`.

## Risks
There are only 16 setup entries and 64 bytes per string; excess or long command-line entries are silently limited. OSI quirks are firmware-compatibility policy, so changes can regress specific machines. The file contains a duplicate `static struct acpi_osi_config osi_config;` declaration in the viewed source, which would be a compile issue unless hidden by source version specifics; this should be checked against the actual build baseline. `acpi_osi=` semantics are subtle, especially `!`, `!*`, and `!!`.

## Test Signals
Boot-parameter tests for empty string, `!`, `!*`, `!!`, add/remove named strings, Linux/Darwin command-line override of DMI, DMI quirk matches, Apple Darwin enable, `acpi_osi_is_win8()`, and firmware query logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/osi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/osl.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/osl.c

## Purpose
`osl.c` is the Linux ACPI OS services layer for ACPICA. It supplies printing, root table discovery, memory mappings, interrupt handling, timers, I/O and memory accessors, PCI config access, workqueue execution, debugger hooks, semaphores, hotplug scheduling, resource-conflict checks, cache wrappers, sleep callbacks, and ACPI OS initialization/termination.

## Important APIs, Types, And Functions
- Initialization/termination: `acpi_os_initialize()`, `acpi_os_initialize1()`, and `acpi_os_terminate()`.
- Root/table support: `acpi_os_get_root_pointer()`, `acpi_reserve_resources()`, and `acpi_request_region()`.
- Mapping support: `struct acpi_ioremap`, `acpi_os_map_iomem()`, `acpi_os_unmap_iomem()`, `acpi_os_get_iomem()`, `acpi_os_map_generic_address()`, and `acpi_os_unmap_generic_address()`.
- ACPICA predefined overrides: `acpi_os_predefined_override()`, `acpi_rev_override_setup()`, and `acpi_os_name_setup()`.
- Interrupt support: `acpi_os_install_interrupt_handler()`, `acpi_os_remove_interrupt_handler()`, and internal `acpi_irq()`.
- Delay/timer and accessors: `acpi_os_sleep()`, `acpi_os_stall()`, `acpi_os_get_timer()`, port/memory read/write helpers, and PCI config read/write helpers.
- Execution/hotplug: `acpi_os_execute()`, `acpi_os_wait_events_complete()`, `acpi_hotplug_schedule()`, and `acpi_queue_hotplug_work()`.
- Synchronization/debugger/cache: semaphore operations, debugger registration/read/write/wait helpers, spinlock wrappers, and ACPICA cache wrappers.
- Resource policy: `acpi_check_resource_conflict()`, `acpi_check_region()`, and `acpi_resources_are_enforced()`.
- Sleep hooks: `acpi_os_prepare_sleep()`, `acpi_os_prepare_extended_sleep()`, setter functions, and `acpi_os_enter_sleep()`.

## Control Flow
Early init reserves FADT I/O/memory regions. `acpi_os_get_root_pointer()` uses a lockdown-checked `acpi_rsdp=` override, architecture root pointer, EFI tables, or legacy scan. `acpi_os_initialize()` pre-maps FADT event/GPE/reset GAS addresses and marks OSL initialized; `acpi_os_initialize1()` creates the ACPICA workqueues and initializes OSI. Termination removes SCI handling, unmaps FADT mappings, and destroys workqueues.

Memory mapping uses permanent mapping mode after init. It reuses existing mappings under `acpi_ioremap_lock`, refcounts them, stores them in an RCU-protected list, and defers unmap/free through `queue_rcu_work()` after the last reference. Direct ACPI memory reads/writes first try an existing mapping under RCU and otherwise temporarily ioremap.

ACPICA deferred execution allocates one `acpi_os_dpc`, then queues it to notification or GPE workqueues; GPE work is forced to CPU 0 for known SMI safety. Hotplug work uses a separate ordered workqueue to avoid deadlocks against ACPI event queue flushing. The SCI handler validates the FADT GSI, registers a threaded shared IRQ, and increments handled/not-handled stats based on ACPICA's handler return.

## State And Persistence
Persistent static state includes SCI handler/context/IRQ, three workqueues, permanent mapping list/refcounts, OS initialization flag, FADT mapped logical addresses, resource-enforcement mode, optional OS name/revision override, debugger ops owner, sleep hook function pointers, and `poweroff_on_fatal`.

## Dependencies And Integration Points
The file is ACPICA's Linux binding and integrates with EFI, security lockdown, architecture ACPI table discovery, resource management, IRQ subsystem, PCI raw config access, workqueues, kernel debugger support, ACPI hotplug, NMI watchdog, ACPI address-range tracking, and PM sleep transitions.

## Risks
Mapping code is concurrency-sensitive: incorrect refcounts, RCU grace periods, or virtual-range lookup can leak mappings or unmap while in use. `acpi_os_vprintf()` uses a static 512-byte buffer and `vsprintf()`, so message length assumptions matter. SCI registration only supports the FADT SCI GSI. `acpi_os_delete_semaphore()` BUGs if waiters remain. Fatal ACPI signals can power off the machine by default. Resource enforcement policy directly affects native driver binding. Hotplug and workqueue flushing order is designed to avoid deadlock and should be preserved.

## Test Signals
Exercise RSDP override with lockdown, EFI and legacy root lookup, permanent mapping reuse/refcount/unmap, memory/port access widths, no-I/O-port builds, SCI install/remove, ACPICA deferred execution queues, hotplug scheduling under flush, debugger ops module ownership, semaphore timeout and invalid units, resource conflict strict/lax/no modes, FADT GAS mapping/unmapping, sleep hook return translations, and fatal signal policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/osl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_irq.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_irq.c

## Purpose
`pci_irq.c` implements ACPI `_PRT`-based PCI INTx routing. It finds routing entries for PCI devices and bridges, applies DMI quirks, allocates ACPI PCI link IRQs or static GSIs, registers/unregisters GSIs, and updates `pci_dev` IRQ state.

## Important APIs, Types, And Functions
- `struct acpi_prt_entry` stores PCI segment/bus/device, pin, optional link handle, and source index/GSI.
- DMI quirk tables and `do_prt_fixups()` rewrite known-bad firmware link sources.
- `acpi_pci_irq_check_entry()` validates one `_PRT` entry and converts it to `acpi_prt_entry`.
- `acpi_pci_irq_find_prt_entry()` obtains and scans a bridge/root `_PRT`.
- `acpi_pci_irq_lookup()` searches direct routing, then walks parent bridges with PCI INTx swizzling and CardBus handling.
- x86 IO-APIC support includes `acpi_reroute_boot_interrupt()` for boot interrupt variants.
- Public APIs are `acpi_pci_irq_enable()` and `acpi_pci_irq_disable()`.

## Control Flow
Enable starts from a device pin. It skips devices without pins or already managed IRQs, looks up `_PRT` routing, tolerates legacy IDE without ACPI routing, allocates a link IRQ if the entry references a link device, or uses a static GSI otherwise. It registers the GSI with trigger/polarity defaults, stores the Linux IRQ in `dev->irq`, marks `irq_managed`, and logs routing. If ACPI routing fails, it validates legacy `dev->irq` and may register an ISA fallback GSI.

Disable returns early for unpinned, unmanaged, non-positive IRQs, suspend-prepared devices, and runtime-suspending devices. It re-resolves the routing entry, frees link IRQs where applicable, unregisters the GSI, and clears `irq_managed`.

## State And Persistence
This file allocates temporary `acpi_prt_entry` objects per lookup and does not own long-lived routing state. Persistent effects are in ACPI PCI link state, GSI registration state, and `pci_dev` fields `irq` and `irq_managed`.

## Dependencies And Integration Points
It integrates ACPI `_PRT` evaluation, PCI core device/bus structures, ACPI PCI link devices, GSI registration, ISA/EISA fallback helpers, DMI firmware quirks, x86 IO-APIC boot interrupt rerouting, runtime PM, and interrupt polarity/trigger models for GIC/LPIC/x86.

## Risks
Firmware `_PRT` entries are often wrong, requiring DMI quirks and bridge-derived routing. Parent bridge swizzling must match PCI topology, especially for CardBus. Fallback to legacy IRQs can mask missing ACPI routing but may leave devices uninterruptible. Disable redoes lookup and can fail if firmware state changed. Suspend/runtime-suspend early returns intentionally preserve pin programming; altering them risks resume failures.

## Test Signals
Test static GSI and link-device `_PRT` entries, DMI fixups, ARI-enabled buses, bridge-derived swizzling, CardBus bridge pin inheritance, legacy IDE no-route tolerance, ISA fallback, x86 IO-APIC reroute variants, GIC/LPIC polarity defaults, enable idempotence for managed IRQs, and disable behavior during suspend/runtime suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_irq.c -->
