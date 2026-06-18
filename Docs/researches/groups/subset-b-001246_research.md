# subset-b-001246 research

This grouped report covers CXL core port, region, RAS, register, suspend, and trace infrastructure. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/port.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/port.c

Purpose: implements the central CXL core bus and device hierarchy for ports, root ports, downstream ports, endpoint ports, and decoders. It provides the sysfs-visible object model used by the rest of the CXL stack, connects physical upstream/downstream devices into the logical CXL decode topology, registers the `cxl` bus type, starts the memory-device, region, mailbox, RAS, and debugfs subsystems, and supplies exported helpers for CXL-aware PCI, ACPI, memdev, HDM, region, and PMU drivers.

Important APIs and types: the file defines `struct cxl_port` device lifetime, decoder device types, the global `cxl_bus_type`, the ordered `cxl_bus_wq`, debugfs root creation, `cxl_port_ida`, and an xarray mapping platform root uports to PCI buses. Exported entry points include `devm_cxl_add_port()`, `devm_cxl_add_root()`, `devm_cxl_add_dport()`, `devm_cxl_add_rch_dport()`, `devm_cxl_enumerate_ports()`, `cxl_pci_find_port()`, `cxl_mem_find_port()`, `cxl_root_decoder_alloc()`, `cxl_switch_decoder_alloc()`, `cxl_endpoint_decoder_alloc()`, `cxl_decoder_add()`, `cxl_decoder_add_locked()`, `cxl_decoder_autoremove()`, `cxl_bus_rescan()`, `cxl_bus_drain()`, `schedule_cxl_memdev_detach()`, `cxl_endpoint_get_perf_coordinates()`, and `cxl_port_setup_regs()`. It also exports type-check/conversion helpers like `is_cxl_port()`, `to_cxl_port()`, `is_root_decoder()`, `is_switch_decoder()`, and `to_cxl_endpoint_decoder()`.

Control flow: initialization creates `/sys/bus/cxl`, a `cxl` debugfs root, optional EINJ debugfs files, initializes mailbox and memdev support, allocates an ordered workqueue, registers the bus, then registers region and RAS drivers. Port creation starts in `cxl_port_alloc()`, assigns an ID, initializes xarrays for dports/endpoints/regions, sets the CXL bus/type, computes parent and host-bridge metadata, and initializes register maps. `cxl_port_add()` names root, switch, or endpoint ports and registers the device; `devm_cxl_add_port()` wires devres cleanup and sysfs links to `uport` and `parent_dport`. Dport creation validates IDs, creates `dportN` sysfs links, probes component registers or RCH RCRB-derived component registers, adds devres removal actions, records link latency, and initializes RAS/debugfs injection. Endpoint enumeration walks PCI-like ancestors from a memdev, finds or creates intermediate ports, probes dports, attaches endpoint references to each port, and restarts when a newly created port exposes more descendants. Decoder allocation initializes common defaults, assigns per-port decoder IDs, and device registration populates targets for switch/root decoders from existing dports.

State and persistence behavior: persistent kernel state is device-model backed. Ports own `dports`, `endpoints`, and `regions` xarrays, `decoder_ida`, depth, parent dport, host bridge, component register map, `commit_end`, and `dead` flags. Dports persist physical/register metadata, `rch` state, RCRB information, RAS mappings, target port IDs, latency, and CDAT coordinates. Endpoint references persist until memdev detach; bottom-up cleanup removes endpoint references and may garbage-collect dynamic switch ports when the last endpoint leaves. Decoders persist HPA range, interleave geometry, flags, target maps, region binding, commit/reset callbacks, and sysfs attributes. Root decoders additionally manage `memregion` IDs and `range_lock`.

Dependencies and integration points: depends on Linux driver core, sysfs, debugfs, devres, workqueues, PCI, xarray, IDA, memregion, platform devices, EINJ, CXL mailbox/memdev/region/RAS modules, component register probing from `regs.c`, RAS setup from `ras.c`, DPA management from `hdm.c`, and CDAT/performance helpers. It is the integration point for ACPI root creation, PCI endpoint discovery, CXL memdev detach, HDM decoder registration, region creation sysfs attributes, error injection files, and module autoload via CXL modalias values.

Risks and invariants: port and dport teardown depends on devres action ordering; bottom-up switch-port deletion assumes dports have already been destroyed. The port lock hierarchy uses depth-based lockdep classes and separate root-port locking because root dports are often added by platform drivers rather than the common port driver. Endpoint enumeration can return `-EAGAIN` to restart after topology changes, so regressions here risk missed ports or duplicate dports. Decoder target population must tolerate hot-added dports but must not silently accept enabled decoders with unresolved targets. `commit_end` ordering enforces decoder commit order, and region code relies on it. RCH paths rely on RCRB decoding and delayed host association. Debugfs EINJ injection must be gated to valid RCH/root-port contexts.

Test signals: CXL unit or QEMU/cxl_test coverage should exercise root, switch, endpoint, RCH, and platform-root port creation; sysfs links `uport`, `parent_dport`, and `dportN`; `modalias`, `devtype`, decoder attributes, target lists, region creation attributes, and bus `flush`; duplicate dport ID rejection; endpoint hot-remove garbage collection; `devm_cxl_enumerate_ports()` restart behavior; RCH dport register/RAS setup; CXL bus rescan/drain; debugfs EINJ file creation when EINJ is initialized; and performance coordinate aggregation across multi-switch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/ras.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/ras.c

Purpose: handles CXL RAS register setup and error reporting for CXL ports and memory devices, including CPER protocol error work items, component RAS register mapping, PCI error callbacks, and tracepoint emission for correctable and uncorrectable CXL RAS events.

Important APIs and control flow: CPER protocol errors enter `cxl_cper_handle_prot_err()`, which looks up the PCI device identified by the CPER agent address. Root/downstream/upstream ports are traced as port protocol errors; endpoint devices are matched to a `cxl_memdev` by parent device and traced as memdev errors. `cxl_ras_init()` registers a work item with CPER support; the work function drains `cxl_cper_prot_err_kfifo_get()` and calls the handler. `devm_cxl_dport_ras_setup()` and `devm_cxl_port_ras_setup()` map RAS component capability registers from a prepared `cxl_register_map`. `devm_cxl_dport_rch_ras_setup()` additionally maps RCH AER and disables RCH root interrupts when the host bridge owns native AER. Runtime error handling uses `cxl_handle_cor_ras()` for correctable status and `cxl_handle_ras()` for uncorrectable status/header-log capture. PCI error hooks are `cxl_cor_error_detected()` and `cxl_error_detected()`.

State and persistence behavior: no large persistent private state is owned here. Persistent effects are mapped `regs.ras` pointers in ports/dports/endpoints and a registered CPER work item. Error status is transient: status registers are read, masked, traced, and then cleared by writing status bits back. Uncorrectable handling copies the CXL 512-byte header log before clearing status. For PCI fatal/frozen conditions, the memdev driver is released to deactivate CXL.mem.

Dependencies and integration points: depends on PCI AER, CXL CPER event helpers, `cxl_register_map` from `regs.c`, trace events from `trace.h`, RCH AER helpers from `ras_rch.c`, memdev lookup on `cxl_bus_type`, and PCI error-recovery callbacks wired by CXL PCI code. It integrates with port/dport setup in `port.c` and with endpoint error handling in the memdev/PCI path.

Risks and invariants: all error paths guard the memdev device before using driver data, but CPER matching relies on parent-device identity to find the memdev. Header logs must be copied before clearing status. Multi-bit uncorrectable status uses the first-error field from capability control; wrong masking would misidentify the primary error. The RCH path must be invoked before endpoint RAS handling for RCD devices so root-complex downstream-port errors are not lost. Releasing the memdev driver in error recovery is intentionally disruptive and must not happen for merely correctable errors.

Test signals: CPER queue injection should produce `cxl_port_aer_*` or `cxl_aer_*` trace events according to PCIe port type. Component RAS absence should only log debug messages. Correctable status should clear and trace without requesting reset. Uncorrectable normal-channel errors should return `PCI_ERS_RESULT_NEED_RESET` after releasing the driver; frozen channels should warn and request reset; permanent failures should disconnect. RCH devices should exercise `cxl_handle_rdport_errors()` before endpoint RAS handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/ras_rch.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/ras_rch.c

Purpose: implements RAS/AER support specific to CXL devices attached to a Root Complex Host (RCH). These devices expose downstream-port AER and component registers through an RCRB rather than a normal PCIe downstream-port function, so the file maps RCRB AER, disables root command interrupts, snapshots AER state, and bridges RCH downstream-port errors into the common CXL RAS handlers.

Important APIs and control flow: `cxl_dport_map_rch_aer()` uses `cxl_rcrb_to_aer()` to find the AER extended capability offset inside the dport RCRB and maps it with `devm_cxl_iomap_block()`. `cxl_disable_rch_root_ints()` clears correctable, nonfatal, and fatal interrupt enables in `PCI_ERR_ROOT_COMMAND`. `cxl_handle_rdport_errors()` looks up the dport for a PCI endpoint with `cxl_pci_find_port()`, copies the AER capability through `cxl_rch_get_aer_info()`, derives severity via `cxl_rch_get_aer_severity()`, prints the AER record with `pci_print_aer()`, and then calls correctable or uncorrectable CXL RAS handling using the dport's RAS register mapping.

State and persistence behavior: persistent state is the mapped `dport->regs.dport_aer` pointer and `dport->rcrb.base` captured by port setup. Error state is transient: all AER capability registers are copied with 32-bit reads because the capability is MMIO-mapped, then uncorrectable and correctable status are cleared in the RCRB. No private allocation is retained by this file beyond devm mappings.

Dependencies and integration points: depends on RCRB helpers from `regs.c`, common CXL RAS functions from `ras.c`, PCI AER structures and constants, `cxl_pci_find_port()` from `port.c`, and `struct cxl_dev_state`/`cxl_memdev` from `cxlmem.h`. It is invoked from `devm_cxl_dport_rch_ras_setup()` and from CXL PCI error handlers for RCD devices.

Risks and invariants: RCRB AER access must use MMIO reads, not PCI config-space helpers. The severity check currently tests uncorrectable status first, then correctable status, and ignores masked bits; mask handling must match PCI AER semantics. Interrupt disabling is conservative because reset defaults may already disable these bits. Missing `dport_aer` mapping should be a no-op, not fatal, because some platforms may not expose a usable RCRB AER block.

Test signals: RCD/RCH test platforms should show AER mapping from the RCRB, root command bits cleared, copied/cleared AER status, correct `pci_print_aer()` severity, and propagation into `trace_cxl_aer_correctable_error()` or `trace_cxl_aer_uncorrectable_error()` through the common RAS handlers. Fault injection should include no-AER and masked-status cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/ras_rch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/region.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/region.c

Purpose: implements CXL region creation, configuration, autodiscovery, commit/reset, endpoint target attachment, DPA/HPA translation, poison debugfs, performance attributes, and child PMEM/DAX region activation. Regions are active host physical address ranges backed by root, switch, and endpoint HDM decoders across a CXL memory topology.

Important APIs and types: the main type is `struct cxl_region` with `struct cxl_region_params`, root decoder pointer, HPA range, flags, access coordinates, notifier blocks, and optional child PMEM/DAX/NVDIMM bridge state. Key exported APIs include `is_cxl_region()`, `cxl_get_poison_by_endpoint()`, `cxl_dpa_to_region()`, `cxl_validate_translation_params()`, `cxl_calculate_dpa_offset()`, `cxl_calculate_position()`, `cxl_calculate_hpa_offset()`, `cxl_add_to_region()`, `cxl_port_get_spa_cache_alias()`, `cxl_region_contains_resource()`, `cxl_region_init()`, and `cxl_region_exit()`. Sysfs attributes include `uuid`, `commit`, `interleave_ways`, `interleave_granularity`, `resource`, `size`, `mode`, `extended_linear_cache_size`, `locked`, and `target0` through `target15`.

Control flow: user-defined regions are created through root-decoder sysfs attributes implemented here and exposed in `port.c`. Creation allocates a `memregion` ID, registers a `cxl_region` child under the root decoder, and devres-registers `unregister_region()`. Users set interleave ways, granularity, size, UUID for PMEM, and endpoint targets. `alloc_hpa()` allocates an HPA resource from the root decoder window and advances state to interleave-active. Target writes call `attach_target()`, validate the endpoint decoder, root dport position, DPA allocation, mode/type, interleave support, and size relationship, then walk endpoint-to-root ports attaching `cxl_region_ref` objects and assigning free switch/root decoders. When all targets are present, `cxl_region_setup_targets()` programs or validates downstream target lists and the region becomes active. Writing `commit=1` invalidates CPU cache for the range and commits endpoint and upstream decoders bottom-up. Writing `commit=0` queues reset, releases the region driver, resets decoders, and returns to active-but-uncommitted.

Autodiscovery flow: firmware-enabled endpoint decoders call `cxl_add_to_region()`. The file finds the matching root decoder, optionally invokes root translation setup, serializes construction with `range_lock`, either finds an existing auto region by range or constructs a new one, stages endpoint decoders until the interleave set is complete, sorts targets by computed topology position, validates preprogrammed switch decoder geometry and target lists, marks the region committed, and attaches the region driver.

State and persistence behavior: region state is guarded by `cxl_rwsem.region`; endpoint DPA information is guarded by `cxl_rwsem.dpa`. `p->state` transitions through idle, interleave-active, active, commit, and reset-pending states. `p->res`, `hpa_range`, `targets[]`, `nr_targets`, interleave geometry, UUID, and optional cache size persist while the region device exists. Each involved port keeps a `cxl_region_ref` in `port->regions`; references track decoder assignment, endpoint refs, target counts, and target-list setup progress. Decoder `cxld->region` pins the region device. Locked/autodiscovered/normalized-addressing flags alter teardown, translation, and debugfs behavior. Resource insertion failures for autodiscovered ranges are tolerated because firmware/system RAM may already own subresources.

Dependencies and integration points: depends on root/switch/endpoint decoder helpers from `port.c`, DPA allocation and partition helpers from `hdm.c`, performance and bandwidth calculations from `cdat.c`, EDAC registration, PMEM bridge creation in `region_pmem.c`, DAX child creation in `region_dax.c`, memory-tier and node notifier APIs, CPU cache invalidation, memregion allocation, iomem resource management, debugfs, CXL poison mailbox helpers, and tracepoint translation support. It exposes root decoder sysfs region-control attributes to `port.c`.

Translation behavior: aligned interleaves use CXL encoded interleave ways/granularity to calculate position, DPA offsets, and HPA offsets. MOD3 host-bridge interleaves with unaligned root addresses use special reconstruction through `decode_pos()`, `restore_parent()`, and candidate testing. Optional root callbacks translate between SPA and CXL HPA. Normalized Addressing regions disable DPA-to-HPA poison translation. Extended Linear Cache support adjusts resource start and presents alias lookup via `cxl_port_get_spa_cache_alias()`.

Risks and invariants: the state machine is subtle and depends on lock ordering, target list setup/teardown symmetry, and decoder commit ordering. Cache invalidation is mandatory before commit and reset unless test config bypasses it. Out-of-order decoder shutdown blocks later free-decoder allocation. Auto-region staging intentionally exposes temporary target positions before sorting. MOD3 translation is complex and not algebraically invertible for HPA-to-DPA, so it enumerates candidates. Region size must equal endpoint DPA size times interleave ways plus cache size. RCH and VH endpoints cannot mix in one region. PMEM UUID uniqueness is checked across CXL regions before activation. Any transition away from committed state must release the region driver.

Test signals: region sysfs tests should cover configuration ordering, invalid granularity/ways, size alignment, UUID parsing/duplicates, target attach/detach, commit/reset, locked-region reset refusal, and root decoder capability visibility. Topology tests should include multi-host-bridge, switch, x1/x2/x4/x8/x16, x3/x6/x12, RCH-only, VH-only, and mismatched RCH/VH cases. Autodiscovery tests should validate position sorting and preprogrammed decoder checks. Translation tests should round-trip DPA/HPA for aligned and unaligned MOD3 regions, root SPA/HPA callbacks, cache alias ranges, and normalized-addressing rejection. Poison debugfs tests should validate inject/clear offset checks, cache-size exclusion, DPA resolution, and missing capability suppression. Probe tests should verify PMEM child creation, DAX child creation, EDAC registration failures being nonfatal, System RAM overlap suppression for DAX, and memory-tier attribute updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/region_dax.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/region_dax.c

Purpose: creates a lightweight `cxl_dax_region` child device for committed CXL RAM regions that should be handed to the DAX/hmem path instead of becoming directly managed System RAM.

Important APIs and control flow: `cxl_dax_region_alloc()` verifies under `cxl_rwsem.region` that the parent region is committed, allocates `struct cxl_dax_region`, snapshots the parent HPA range, initializes a CXL bus device with type `cxl_dax_region_type`, and parents it to the `cxl_region`. `devm_cxl_add_dax_region()` names the child `dax_region%d`, adds it to the device model, and registers `cxlr_dax_unregister()` as a devres action on the parent region. `to_cxl_dax_region()` is exported for consumers.

State and persistence behavior: the child persists only a pointer back to the parent region and a snapshot of the committed HPA range. It has no independent target list or decoder state. Release frees the small allocation; devres unregister ties its lifetime to the parent region driver binding.

Dependencies and integration points: depends on CXL core device typing and base attributes from `port.c`, region state from `region.c`, and downstream DAX/hmem consumers that match `CXL_DEVICE_DAX_REGION`. It is invoked from `cxl_region_probe()` for RAM regions when the range is not already online as System RAM.

Risks and invariants: allocation assumes committed region parameters are stable while the region driver is bound. If region state changes, the parent driver is expected to be released before reset, which unregisters the DAX child. Since the range is a snapshot, later mutation without driver release would create stale DAX metadata.

Test signals: committed RAM region probe should produce `dax_regionN` with correct HPA range and CXL modalias. Uncommitted regions should fail with `-ENXIO`. Parent region unbind/reset/delete should unregister the child. System RAM overlap tests should confirm `region.c` suppresses this path before calling into this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/region_dax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/region_pmem.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/region_pmem.c

Purpose: creates a `cxl_pmem_region` bridge device for committed persistent CXL regions and connects it to the CXL NVDIMM bridge so the nvdimm subsystem can consume the region's endpoint mappings.

Important APIs and control flow: `cxl_pmem_region_alloc()` verifies committed state, allocates a flexible `struct cxl_pmem_region` sized for all targets, snapshots the HPA range and each endpoint mapping, finds the common `cxl_nvdimm_bridge` from the first memdev endpoint, stores a bridge reference in the parent region, and initializes the child device. `devm_cxl_add_pmem_region()` names and registers `pmem_region%d`, then under the bridge device lock registers a devres action on the NVDIMM bridge to unregister the pmem region. It also registers a parent-region devres action that releases the NVDIMM bridge reference and coordinates unregister if the region goes away first. `is_cxl_pmem_region()` and `to_cxl_pmem_region()` are exported.

State and persistence behavior: the pmem region snapshots committed endpoint mappings: memdev references, DPA starts, DPA sizes, and interleave positions. It pins each memdev until release. The parent region stores `cxlr->cxl_nvb` and `cxlr->cxlr_pmem` while the bridge is active. Device removal is coordinated through both the NVDIMM bridge and CXL region devres domains to handle either side disappearing first.

Dependencies and integration points: depends on region state from `region.c`, memdev/endpoint decoder helpers, `cxl_find_nvdimm_bridge()`, the CXL bus modalias model, and nvdimm bridge driver behavior. It is called by `cxl_region_probe()` for PMEM regions after optional EDAC setup.

Risks and invariants: the code assumes all targets in a region share the same CXL NVDIMM bridge because regions do not span root devices. Bridge locking is required when unregistering from either region or bridge context. Snapshotting under `cxl_rwsem.region` is necessary so target mappings cannot change while the child is built. Error paths must drop the bridge reference and clear `cxlr->cxl_nvb` to avoid stale pointers.

Test signals: committed PMEM region probe should create `pmem_regionN` with correct HPA range, mapping count, DPA starts/sizes, and positions. Missing bridge should return `-ENODEV`. Parent region deletion and NVDIMM bridge removal should both unregister the child without double-unregister. Memdev reference counts should balance across errors and normal release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/region_pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/regs.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/regs.c

Purpose: provides common CXL register discovery and mapping infrastructure for component registers, device registers, PMU registers, PCI DVSEC register locator blocks, and RCRB-derived resources used by RCH/RCD devices.

Important APIs and control flow: `cxl_probe_component_regs()` scans the CXL.cache/CXL.mem component capability array for HDM decoder and RAS capabilities, recording offsets and sizes in `struct cxl_component_reg_map`. `cxl_probe_device_regs()` scans the CXL device capability array for status, primary mailbox, and memdev registers. `devm_cxl_iomap_block()` requests and devm maps a physical MMIO range. `cxl_map_component_regs()`, `cxl_map_device_regs()`, and `cxl_map_pmu_regs()` persistently map selected capabilities. `cxl_find_regblock_instance()`, `cxl_find_regblock()`, and `cxl_count_regblock()` parse the PCI CXL register locator DVSEC and decode BAR/offset pairs. `cxl_setup_regs()` temporarily maps a register block, probes its contained capabilities, and unmaps it. RCRB helpers include `cxl_rcrb_to_aer()`, `cxl_dport_map_rcd_linkcap()`, `__rcrb_to_component()`, and `cxl_rcd_component_reg_phys()`.

State and persistence behavior: probe functions fill caller-owned map structures and do not retain state. Persistent mappings are devm-owned by the supplied host device. `cxl_setup_regs()` uses a temporary `ioremap()` in `map->base` only for probing and clears it before returning. RCRB helpers request/map 4 KiB windows temporarily except when returning a devm mapping for RCD link capabilities.

Dependencies and integration points: depends on Linux PCI config-space helpers, MMIO accessors, resource reservation, CXL register layout constants, PMU register definitions, and CXL core `struct cxl_register_map`. Port setup uses it to discover component/RAS/HDM registers; memdev setup uses it for mailbox/status/memdev registers; RCH/RCD code uses the RCRB helpers for AER, link capabilities, and component register physical addresses.

Risks and invariants: DVSEC decoding must reject offsets beyond the BAR length, otherwise later mapping would access invalid MMIO. Capability array probing assumes backward-compatible headers and length formulas; unknown/vendor capabilities are skipped. `devm_cxl_iomap_block()` returns NULL on resource conflicts, so callers must treat mapping failure distinctly from absent capabilities. RCRB access manually requests and maps a 4 KiB window and must release it on all exits. `__rcrb_to_component()` relies on PCI BAR semantics in an MMIO RCRB image, including 64-bit BAR handling and component block alignment.

Test signals: tests should cover component maps containing HDM and RAS, missing component headers, device maps missing required status/mailbox/memdev registers, multiple register locator instances, BAR-too-small warnings, count-only DVSEC scans, PMU mapping, RCRB AER offset discovery, RCRB PCIe capability mapping, invalid RCRB IDs, zero/unaligned component BARs, and devm cleanup of all persistent mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/suspend.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/suspend.c

Purpose: provides a tiny shared active-CXL-memory counter used by CXL memory drivers and suspend/PM policy code to know whether CXL memory is currently active.

Important APIs and control flow: `cxl_mem_active()` returns whether the atomic counter is nonzero. `cxl_mem_active_inc()` increments the counter and is exported in the CXL namespace. `cxl_mem_active_dec()` decrements the counter and is also exported. There is no init/exit flow beyond static zero initialization of `mem_active`.

State and persistence behavior: all state is a single static `atomic_t mem_active`. It persists for module lifetime and is not tied to an individual device. The file does not guard against underflow; callers must balance increments and decrements.

Dependencies and integration points: depends on Linux atomics and CXL mem headers. It integrates with CXL memory activation paths elsewhere in the driver tree and any suspend logic that checks `cxl_mem_active()`.

Risks and test signals: the primary risk is imbalance, especially on probe/remove or error paths, because a negative atomic value still makes `cxl_mem_active()` return true. Test signals include activation/deactivation balance under region probe failures, remove paths, suspend attempts with active memory, and lockdep/KUnit-style assertions in callers that pair inc/dec operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/trace.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/trace.c

Purpose: instantiates the CXL tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` in exactly one translation unit.

Important APIs and control flow: the file includes `<cxl.h>`, `core.h`, defines `CREATE_TRACE_POINTS`, and includes `trace.h`. It exports no callable functions; build/link side effects create the tracepoint definitions for all `TRACE_EVENT()` declarations in the header.

State and persistence behavior: tracepoint state is managed by the kernel tracing subsystem. This file owns no runtime data structures beyond the generated tracepoint objects.

Dependencies and integration points: depends on the trace event declarations in `trace.h` and on all types referenced by those declarations being visible from the included headers. RAS, event, poison, and mailbox paths call the generated `trace_cxl_*()` functions.

Risks and test signals: if another file defines `CREATE_TRACE_POINTS` for the same header, duplicate definitions result; if this file is omitted, users get unresolved trace symbols. Build tests with tracing enabled and disabled, plus runtime checks under `/sys/kernel/tracing/events/cxl/`, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/trace.h -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/trace.h

Purpose: declares all CXL trace events for RAS/AER errors, mailbox event-log overflow, generic event records, general media records, DRAM records, memory module events, memory sparing events, and poison list/inject/clear records. It translates CXL specification bitfields and event payloads into stable tracepoint fields and readable trace output.

Important APIs and control flow: the header sets `TRACE_SYSTEM cxl`, defines flag/stringification helpers for RAS uncorrectable/correctable statuses, common event header fields, DPA flags, PLDM component IDs, media descriptors, media transaction types, validity flags, health/media status, memory sparing flags, and poison metadata. Trace events include `cxl_port_aer_uncorrectable_error`, `cxl_aer_uncorrectable_error`, `cxl_port_aer_correctable_error`, `cxl_aer_correctable_error`, `cxl_overflow`, `cxl_generic_event`, `cxl_general_media`, `cxl_dram`, `cxl_memory_module`, `cxl_memory_sparing`, and `cxl_poison`. Common macros `CXL_EVT_TP_entry`, `CXL_EVT_TP_fast_assign()`, and `CXL_EVT_TP_printk()` ensure consistent header capture across event-log tracepoints.

State and persistence behavior: trace events copy relevant record data into trace buffers at emission time. Uncorrectable AER events embed the full 512-byte header log array but omit it from the formatted print string. Event-log tracepoints store decoded timestamps, UUIDs, flags, handles, component IDs, HPA/DPA translations, region names, and region UUIDs. `cxl_poison` performs DPA-to-HPA translation at trace time when a region is available and records `ULLONG_MAX` for unknown mappings.

Dependencies and integration points: depends on Linux tracepoint infrastructure, PCI, unaligned little-endian helpers, CXL public/internal headers, event payload structs, region translation (`cxl_dpa_to_hpa()`), and UUID helpers. It is included by `trace.c` for instantiation and by RAS/mailbox/poison/event code for trace emission.

Risks and invariants: field layouts become ABI-like for tracing consumers, so renaming/removing fields can break tools. Many helpers decode packed little-endian CXL payloads with `get_unaligned_*`; mistakes here misreport hardware events. `cxl_general_media` and `cxl_dram` include optional region data and must handle NULL regions. `cxl_poison` calls translation helpers and can return sentinel HPAs for normalized-addressing or unresolved regions. The header contains specification string tables; typos or stale spec values produce misleading trace output even if binary fields are correct.

Test signals: compile tests should instantiate all tracepoints through `trace.c`. Runtime tests should verify event directories under tracing, RAS status string decoding, overflow record timestamps/counts, generic event hex payload preservation, media/DRAM DPA flags and HPA/alias translation, memory module health decoding, memory sparing fields, and poison events for list/inject/clear with and without a region. User-space tools such as rasdaemon or trace-cmd are useful compatibility signals because they depend on stable names and fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/trace.h -->
