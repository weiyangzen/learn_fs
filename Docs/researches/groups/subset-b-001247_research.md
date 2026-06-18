# subset-b-001247 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/cxl.h -->
# sources/distributed-fs/ceph-client/drivers/cxl/cxl.h

Purpose: central private CXL core header for the port, decoder, region, PMEM, DAX-region, and driver-model objects shared by CXL ACPI/PCI/core services. It defines register offsets and bit fields for component, RAS, device-status, event, and mailbox blocks, plus helpers for HDM decoder count and interleave encoding/decoding.

Important APIs/types/functions: `struct cxl_decoder`, endpoint/switch/root decoder variants, `struct cxl_region` and `struct cxl_region_params`, `struct cxl_port`, `struct cxl_dport`, `struct cxl_ep`, `struct cxl_region_ref`, CXL bus driver registration helpers, and constructors such as `devm_cxl_add_port()`, `devm_cxl_add_endpoint()`, `devm_cxl_add_dport()`, `cxl_*_decoder_alloc()`, `devm_cxl_add_nvdimm_bridge()`, and region/DAX/PMEM conversion helpers.

Control flow and state: the header encodes the topology state machine: roots own ports, ports own dports/endpoints/regions via xarrays, decoders transition through manual/auto/auto-staged and region config states, and region flags track auto assembly, reset-required, lock, and normalized-addressing behavior. Persistence-related state is represented by `cxl_nvdimm`, `cxl_pmem_region`, PMEM mappings, and CXL region UUID/HPA/mode metadata.

Dependencies and integration: depends on Linux driver core, PCI, resource/range handling, libnvdimm, access-coordinate performance data, and CXL UAPI headers. It is the contract used by CXL PCI, port, PMEM, region, DAX, RAS, ACPI, and unit-test code.

Risks and test signals: bugs here affect ABI-like internal contracts across many drivers. Watch interleave conversions, resource lifetime, xarray keying by device pointers, region locking, reset flags, and CONFIG-gated inline fallbacks. Test signals include CXL topology enumeration, decoder sysfs programming, PMEM/DAX region creation, RAS setup, suspend/reset paths, and CXL unit tests that override `__mock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/cxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/cxlmem.h -->
# sources/distributed-fs/ceph-client/drivers/cxl/cxlmem.h

Purpose: private CXL memory-device header that defines Type-3 memdev objects, mailbox opcodes/payloads, event/poison/security/firmware state, and interfaces used by PCI, mem, PMEM, poison, security, EDAC, firmware-update, and debug paths.

Important APIs/types/functions: `struct cxl_memdev`, `struct cxl_memdev_state`, `struct cxl_dpa_info`, `struct cxl_event_state`, `struct cxl_poison_state`, `struct cxl_security_state`, `struct cxl_fw_state`, `enum cxl_opcode`, mailbox payload structs for identify, partition, LSA, health, poison, security, and firmware, plus exported helpers such as `cxl_internal_send_cmd()`, `cxl_dev_state_identify()`, `cxl_enumerate_cmds()`, `cxl_mem_dpa_fetch()`, `cxl_poison_state_init()`, `cxl_mem_sanitize()`, and `devm_cxl_add_memdev()`.

Control flow and state: CXL PCI builds `cxl_memdev_state`, enumerates mailbox commands, identifies capacity/partitions, and registers a `cxl_memdev`; CXL bus drivers later attach that memdev into port topology. State includes partition resources, media-ready status, firmware slot transfer state, delayed sanitize polling, event buffer and mutex, poison command bitmap and list cache, security command bitmap/state, and dirty shutdown support.

Dependencies and integration: includes UAPI CXL memory ioctl definitions, PCI, cdev, UUID, node, CXL event/mailbox headers, libnvdimm security constants, and `cxl.h`. It bridges CXL hardware mailbox protocol to user-visible CXL char devices, libnvdimm labels/security, EDAC, debugfs, and firmware upload.

Risks and test signals: payload layout must remain packed/spec-correct, command return-code translation drives error propagation, and concurrency depends on mailbox/event/poison/security locks. Test command enumeration, unsupported-command masking, poison list/inject/clear, sanitize poll completion, LSA read/write, firmware transfer alignment, partition capacity setup, and CONFIG_CXL_* fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/cxlmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/cxlpci.h -->
# sources/distributed-fs/ceph-client/drivers/cxl/cxlpci.h

Purpose: private CXL PCI header for register-location discovery, CDAT-over-DOE table layout, restricted CXL-device detection, flit-mode probing, and PCI/RAS integration hooks.

Important APIs/types/functions: `enum cxl_regloc_type`, `struct cdat_header`, `struct cdat_entry_header`, `union cdat_data`, `struct cdat_doe_rsp`, `cxl_pci_flit_256()`, `is_cxl_restricted()`, `read_cdat_data()`, `cxl_pci_setup_regs()`, and CONFIG_CXL_RAS-gated error/RAS setup declarations.

Control flow and state: the header gives CXL PCI code the register-block identifiers used to find component, virtual, memdev, and PMU register blocks. CDAT structures define parsing boundaries for topology/performance data cached in `struct cxl_port`. RCD detection switches path handling to root-complex register block behavior rather than normal upstream-port registers.

Dependencies and integration: depends on PCI core and `cxl.h`; consumed by `pci.c`, `mem.c`, `port.c`, RAS code, CDAT readers, and PMU setup. It connects PCIe capability state and DOE table access to the CXL bus model.

Risks and test signals: CDAT length/checksum/entry handling and RCD path logic are easy to regress because hardware topology differs between VH and RCH modes. Test with normal endpoints, RCiEP/RCD devices, missing register blocks, CONFIG_CXL_RAS off, DOE/CDAT absence, and PCIe flit-mode capability variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/cxlpci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/mem.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/mem.c

Purpose: CXL bus driver for memory expander devices. It takes a registered `cxl_memdev`, enumerates/attaches it into the CXL port topology, exposes debugfs/sysfs poison controls, optionally creates a CXL NVDIMM, and blocks unsafe suspend while active.

Important APIs/types/functions: `cxl_mem_probe()`, `devm_cxl_add_memdev()`, `trigger_poison_list_store()`, `cxl_mem_visible()`, debugfs handlers for DPA display, poison inject, and poison clear, and `cxl_mem_driver` with `CXL_DEVICE_MEMORY_EXPANDER`.

Control flow and state: probe requires media ready and no pending detach work, creates debugfs entries, calls `devm_cxl_enumerate_ports()`, finds the parent CXL port/dport, adds libnvdimm representation if PMEM capacity exists, adds an endpoint port under either RCH parent or normal port parent, calls optional attach callback, registers EDAC, increments active memdev suspend blocker, and registers devm cleanup. Poison sysfs visibility is controlled by enumerated poison command bits.

Dependencies and integration: depends on CXL core, port enumeration, CXL PCI helpers, CXL poison helpers, libnvdimm PMEM support, EDAC hooks, debugfs, and driver core device locking.

Risks and test signals: failure paths must unwind debugfs and active-suspend refs. Topology races are handled by single-threaded detach/rescan work but remain sensitive to pending detach checks and parent driver presence. Test media-not-ready, missing topology, RCH vs VH endpoint creation, PMEM disabled by platform, poison command visibility, EDAC failure tolerance, detach/rebind, and suspend blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/pci.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/pci.c

Purpose: PCI-facing CXL memory-device driver. It binds Type-3 CXL.mem PCI class devices, maps register blocks, initializes the mailbox, discovers capacity/commands/features/PMUs/events, creates the CXL memdev, and handles PCI error/reset and CPER event forwarding.

Important APIs/types/functions: `cxl_pci_probe()`, `__cxl_pci_mbox_send_cmd()`, `cxl_pci_setup_mailbox()`, event IRQ setup helpers, `cxl_event_thread()`, `cxl_pci_mbox_irq()`, `cxl_mbox_sanitize_work()`, RCD link sysfs attributes, PCI error handlers, and `cxl_handle_cper_event()`.

Control flow and state: probe enables PCI, creates `cxl_memdev_state`, maps memdev and component registers, initializes and sizes the mailbox, waits for media/mailbox readiness, enumerates commands, sets timestamp, initializes poison and DPA partitions, sets up features/firmware/sanitize notifiers/FWCTL, adds PMU instances, configures event interrupts if native OS control exists, and saves PCI state. Mailbox access is serialized by `mbox_mutex`, polls the doorbell, supports background commands, treats sanitize as asynchronous delayed-work polling, and uses irq wakeups where available.

Dependencies and integration: integrates PCI, CXL register mapping, CXL mailbox/core, feature/fwctl/fw-upload, CXL PMU, poison/event/EDAC consumers, AER/PCI error handlers, CPER kfifo work, host-bridge `_OSC` native CXL error control, and RCD sysfs.

Risks and test signals: mailbox timeouts, oversized payloads, return-code translation, background command synchronization, sanitize monopolization, event ownership with firmware, reset behavior after SBR, missing component registers, and PMU loop error handling are primary risks. Test kexec stale doorbell, tiny mailbox, no IRQ vectors, firmware-owned event logs, CPER delivery, AER slot reset, RCD attributes, and devices lacking DVSEC/component/PMU blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/pmem.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/pmem.c

Purpose: CXL persistent-memory bridge to libnvdimm. It registers CXL NVDIMM bridge, NVDIMM, and PMEM-region CXL bus drivers, implements LSA label commands through the CXL mailbox, exposes DIMM metadata, and creates libnvdimm PMEM regions from CXL PMEM regions.

Important APIs/types/functions: `devm_cxl_add_nvdimm_bridge()`, `cxl_nvdimm_probe()`, `cxl_pmem_get_config_size()`, `cxl_pmem_get_config_data()`, `cxl_pmem_set_config_data()`, `cxl_pmem_ctl()`, `cxl_nvdimm_bridge_probe()`, `cxl_pmem_region_probe()`, `detach_nvdimm()`, and the three CXL drivers registered in `cxl_pmem_init()`.

Control flow and state: NVDIMM probe reserves exclusive CXL commands, arms dirty-shutdown tracking, builds nvdimm command masks, and creates a libnvdimm DIMM with CXL attributes/security ops. Bridge probe registers a libnvdimm bus with `ndctl` callback. PMEM region probe inserts a persistent-memory iomem resource, derives NUMA/target node, builds mappings from CXL memdevs/nvdimms, validates serial numbers, computes an interleave-set cookie, and creates an `nd_region`.

Dependencies and integration: depends on libnvdimm, ndctl payloads, CXL mailbox LSA/security/dirty-shutdown helpers, iomem resources, NUMA node helpers, async driver core, and CXL region objects.

Risks and test signals: label-size bounds, flex allocation, mailbox failures, missing nvdimm driver data, invalid serial numbers, dirty-shutdown visibility, and bridge teardown invalidation are key risks. Test GET/SET LSA, exclusive command blocking, dirty shutdown paths with/without GPF DVSEC, PMEM region creation for multi-way mappings, nvdimm-bus unregister, platform PMEM disable, and security op interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/pmu.h -->
# sources/distributed-fs/ceph-client/drivers/cxl/pmu.h

Purpose: small private header defining the CXL Performance Monitoring Unit device object and constructor used when CXL PCI discovers PMU register blocks.

Important APIs/types/functions: `enum cxl_pmu_type`, `CXL_PMU_REGMAP_SIZE`, `struct cxl_pmu`, `to_cxl_pmu()`, and `devm_cxl_pmu_add()`.

Control flow and state: a PMU object records the parent-associated ID, per-device PMU index, type (`CXL_PMU_MEMDEV` here), mapped register base, and embedded device. `pci.c` counts PMU register blocks, maps each block, and calls `devm_cxl_pmu_add()` with the memdev ID and PMU index.

Dependencies and integration: depends on Linux device core and the CXL register-map type; integrates with CXL PCI enumeration and the separate CXL PMU implementation/perf path.

Risks and test signals: the file is simple, but register-map size/type/index associations must match CXL spec expectations and PMU consumers. Test devices with zero, one, and multiple PMU regblocks; failed map/add paths; and module namespace/export behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/port.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/port.c

Purpose: CXL bus driver for CXL ports. It enumerates switch/endpoint port services, reads CDAT, sets up HDM decoders and RAS, creates endpoint ports for memdevs, and opportunistically assembles committed regions.

Important APIs/types/functions: `cxl_port_probe()`, `cxl_switch_port_probe()`, `cxl_endpoint_port_probe()`, `cxl_ras_unmask()`, `discover_region()`, `cxl_port_add_dport()`, `devm_cxl_add_endpoint()`, CDAT binary sysfs read/visibility, and `cxl_port_driver`.

Control flow and state: switch probe resets dport count and caches CDAT. Endpoint probe reads/parses CDAT, registers a detach action for the memdev, sets up endpoint decoders, handles RCH RAS mapping, unmasks RAS errors when OS controls AER, and scans decoder children for auto-enabled regions. `cxl_port_add_dport()` lazily sets up switch registers/decoders/RAS on the first dport, adds the dport, parses downstream CDAT, and updates decoder targets. `devm_cxl_add_endpoint()` backfills `cxl_ep->next` links up the parent chain and creates the endpoint port.

Dependencies and integration: depends on CXL memdevs, decoder setup, CDAT parsing, PCI/AER, RAS helpers, devres groups, device locks, and the CXL bus.

Risks and test signals: first-dport devres grouping, RCH vs VH setup ordering, parent driver checks, region autodiscovery failures, and RAS unmask privilege are sensitive. Test switch rebind, endpoint detach/rebind, missing CDAT/RAS/registers, first and later dports, auto-region assembly from committed decoders, CDAT sysfs visibility, and OS-vs-BIOS AER ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/security.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/security.c

Purpose: implements libnvdimm security operations for CXL PMEM devices using CXL mailbox security commands.

Important APIs/types/functions: `cxl_pmem_get_security_flags()`, `cxl_pmem_security_change_key()`, `__cxl_pmem_security_disable()`, user/master disable wrappers, `cxl_pmem_security_freeze()`, `cxl_pmem_security_unlock()`, `cxl_pmem_security_passphrase_erase()`, and exported `cxl_security_ops`.

Control flow and state: operations translate libnvdimm passphrase types into CXL user/master passphrase payloads, copy fixed-length passphrase data into packed CXL command structures, send mailbox commands via `cxl_internal_send_cmd()`, and map CXL security-state bits into nvdimm security flags. `get_flags()` caches the last CXL security state in `mds->security.state`.

Dependencies and integration: depends on libnvdimm security APIs, CXL mailbox definitions, CXL PMEM NVDIMM provider data, and fixed NVDIMM passphrase length constants. It is consumed by `pmem.c` when creating CXL-backed nvdimms.

Risks and test signals: passphrase type translation, state-flag mapping, failed mailbox command behavior returning no flags, and sensitive stack buffers are key. Test user and master passphrase flows, frozen/locked/disabled state mapping, wrong passphrase errors, unlock/erase semantics, unavailable security commands, and mailbox return-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dax/Kconfig

Purpose: Kconfig menu for the DAX subsystem and its device, PMEM, HMEM, CXL, FS-DAX-compatible, and KMEM drivers.

Important APIs/types/functions: config symbols `DAX`, `DEV_DAX`, `DEV_DAX_PMEM`, `DEV_DAX_HMEM`, `DEV_DAX_CXL`, `DEV_DAX_HMEM_DEVICES`, `DEV_DAX_FSDEV`, and `DEV_DAX_KMEM`.

Control flow and state: the menu gates which DAX providers and consumers are compiled. `DEV_DAX` requires THP support for deterministic mmap mappings; PMEM depends on libnvdimm/NVDIMM_DAX; HMEM depends on EFI soft reserve and intentionally has CXL dependency tautologies to allow build ordering; CXL DAX depends on CXL bus/region and DAX; FSDEV is selected with FS_DAX; KMEM depends on memory hotplug.

Dependencies and integration: integrates kernel configuration with libnvdimm, CXL, EFI soft-reserve, NUMA memory info, FS_DAX, and memory hotplug.

Risks and test signals: incorrect dependencies can produce link failures or missing runtime drivers. Test allmodconfig/allyesconfig/minimal configs, DAX without KMEM, CXL DAX with/without HMEM, FS_DAX enabled, and NVDIMM_DAX-driven defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dax/Makefile

Purpose: build recipe for DAX core and DAX consumer/provider modules.

Important APIs/types/functions: builds `dax.o` from `super.o` and `bus.o`, `device_dax.o` from `device.o`, `dax_pmem.o`, `dax_cxl.o`, `fsdev_dax.o`, and always descends into `hmem/`.

Control flow and state: object inclusion follows Kconfig symbols. DAX core is built when `CONFIG_DAX` is enabled; specific consumers are separate modules/objects keyed by `CONFIG_DEV_DAX*`.

Dependencies and integration: integrates with kernel kbuild and DAX Kconfig, ensuring core bus/super objects are available before device drivers that register on that bus.

Risks and test signals: missing object linkage causes unresolved symbols such as DAX bus registration or exported constructors. Test module builds for each Kconfig combination, especially FSDEV and CXL/PMEM split modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/bus.c -->
# sources/distributed-fs/ceph-client/drivers/dax/bus.c

Purpose: DAX bus and device-region management core. It registers the `dax` bus, allocates DAX regions and dev_dax instances, exposes sysfs controls for dynamic partitioning, and dispatches dev_dax devices to device, kmem, or fsdev drivers.

Important APIs/types/functions: `alloc_dax_region()`, `devm_create_dev_dax()`, `kill_dev_dax()`, `static_dev_dax()`, `dax_pgoff_to_phys()`, `__dax_driver_register()`, `dax_driver_unregister()`, `dax_bus_init()/exit()`, sysfs handlers for `create`, `delete`, `size`, `mapping`, `align`, `memmap_on_memory`, and mapping child devices.

Control flow and state: `dax_region_rwsem` protects region resource partitioning; `dax_dev_rwsem` protects dev_dax size/id/memmap state; `dax_bus_lock` protects dynamic driver ID lists. Dynamic regions can create seed devices, resize unbound devices, allocate multiple mapping ranges, and expose child `mappingN` devices. Static regions are mostly read-only and carry prebuilt pgmaps. Binding checks refuse zero-size or invalid-ID devices.

Dependencies and integration: depends on driver core, resource trees, memremap alignment, DAX pseudo-device core, sysfs, xarray-like IDA allocation, and HMEM/PMEM/CXL producers. It exports the main DAX construction and bus-registration APIs.

Risks and test signals: locking order, resize while bound, stale pgmap after unbind, range/resource leaks, dynamic ID lifetime, static-vs-dynamic mismatch, and sysfs parsing are high-risk. Test create/delete/resize/mapping/align/memmap sysfs, multi-range devices, driver rebinding, static PMEM devices, kmem type matching, no KMEM config fallback, and resource conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/bus.h -->
# sources/distributed-fs/ceph-client/drivers/dax/bus.h

Purpose: public internal DAX bus header used by DAX region producers and DAX device drivers.

Important APIs/types/functions: DAX resource flags `IORESOURCE_DAX_STATIC` and `IORESOURCE_DAX_KMEM`, `alloc_dax_region()`, `struct dev_dax_data`, `devm_create_dev_dax()`, `enum dax_driver_type`, `struct dax_device_driver`, registration helpers, `kill_dev_dax()`, `static_dev_dax()`, HMEM platform wrapper, `dax_hmem_flush_work()`, and module alias macros.

Control flow and state: region producers allocate a `dax_region`, then create a `dev_dax` with optional pgmap/size/id/memmap-on-memory state. Drivers register with a type so the bus can match generic device-DAX, KMEM conversion, or FS-DAX-compatible drivers.

Dependencies and integration: depends on device, platform-device, range, and workqueue APIs. Included by DAX bus/core, PMEM, HMEM, CXL, device, fsdev, and kmem drivers.

Risks and test signals: type matching and resource flags control which driver binds by default; mistakes can turn reserved memory into System RAM unexpectedly or prevent device access. Test module alias matching, new_id/remove_id overrides, CXL/HMEM flush ordering, and static/dynamic device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/cxl.c -->
# sources/distributed-fs/ceph-client/drivers/dax/cxl.c

Purpose: CXL DAX-region consumer that turns CXL RAM regions into dev_dax devices, usually eligible for later conversion to System RAM by dax_kmem.

Important APIs/types/functions: `cxl_dax_region_probe()`, `cxl_dax_region_driver_register()`, `cxl_dax_region_init()/exit()`, and `cxl_dax_region_driver`.

Control flow and state: probe converts a `cxl_dax_region` HPA range into a DAX region using CXL region ID, derives target NUMA node from physical address, uses PMD alignment, marks the region `IORESOURCE_DAX_KMEM`, creates a dynamic dev_dax covering the whole range, and defaults `memmap_on_memory` to true. Init queues delayed registration on `system_long_wq` after flushing HMEM work to avoid racing soft-reserve fallback ownership.

Dependencies and integration: depends on CXL region objects, DAX bus APIs, NUMA helpers, and HMEM coordination.

Risks and test signals: race handling with HMEM fallback, NUMA fallback behavior, resource ownership, and default KMEM eligibility are key. Test CXL dynamic regions, CXL ranges also seen as soft-reserved, module load/unload with pending work, and dax_kmem binding after CXL DAX creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/cxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/dax-private.h -->
# sources/distributed-fs/ceph-client/drivers/dax/dax-private.h

Purpose: private DAX core header defining in-memory region, mapping, and device objects shared by bus, super, and DAX drivers.

Important APIs/types/functions: `struct dax_region`, `struct dax_mapping`, `struct dev_dax_range`, `struct dev_dax`, `run_dax()`, `to_dev_dax()`, `to_dax_mapping()`, `dax_pgoff_to_phys()`, `inode_dax()`, `dax_inode()`, `dax_bus_init()/exit()`, and `dax_align_valid()`.

Control flow and state: `dax_region` tracks parent range, target node, alignment, IDs, resource tree, seed, and youngest device. `dev_dax` tracks a DAX core object, optional kernel mapping for fsdev, cached size, alignment, target node, pgmap, memmap-on-memory preference, and one or more physical ranges with mapping children. `dax_align_valid()` gates allowed page/PMD/PUD mapping sizes by THP architecture config.

Dependencies and integration: depends on device, cdev, IDR/IDA, THP config, and DAX pseudo-filesystem functions implemented in `super.c`.

Risks and test signals: this is a shared private ABI; field semantics affect sysfs, mmap faults, fs-dax, kmem, and producers. Test alignment validation across PAGE/PMD/PUD configs, dynamic multi-range devices, pgmap lifetime, and conversions between inode/device/dax types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/dax-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/device.c -->
# sources/distributed-fs/ceph-client/drivers/dax/device.c

Purpose: generic device-DAX character driver providing direct `mmap()` access to dev_dax memory.

Important APIs/types/functions: VMA checks, PTE/PMD/PUD fault handlers, `dev_dax_huge_fault()`, `dax_mmap_prepare()`, `dax_get_unmapped_area()`, file operations, `dev_dax_probe()`, and `device_dax_driver`.

Control flow and state: open binds file mappings to the DAX inode and stores `dev_dax`. `mmap_prepare()` verifies alive state, shared mapping, alignment, and DAX-capable file, then installs DAX vm ops. Fault handlers translate pgoff to physical address, enforce alignment/fault-size compatibility, set folio mappings, and insert pages/folios. Probe builds or validates pgmap, reserves each range, sets `MEMORY_DEVICE_GENERIC`, sets `vmemmap_shift` for huge alignments, memremaps pages, adds cdev, marks DAX alive, and registers kill cleanup.

Dependencies and integration: depends on mm fault APIs, memremap_pages, DAX core, cdev, VFS, THP, and DAX bus.

Risks and test signals: private mappings, misalignment, multi-range translation, folio mapping state, huge fault fallback, stale pgmaps, and range reservation are high-risk. Test mmap with PAGE/PMD/PUD alignments, MAP_PRIVATE rejection, unaligned VMA rejection, SIGBUS out-of-range faults, dynamic multi-range devices, unbind/remap, and THP config variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/fsdev.c -->
# sources/distributed-fs/ceph-client/drivers/dax/fsdev.c

Purpose: FS-DAX-compatible dev_dax driver. It exposes dev_dax memory through DAX operations for filesystems rather than device-DAX mmap, using `MEMORY_DEVICE_FS_DAX` and order-0 folios.

Important APIs/types/functions: `fsdev_dax_direct_access()`, `fsdev_dax_zero_page_range()`, `fsdev_dax_recovery_write()`, `fsdev_pagemap_memory_failure()`, `fsdev_clear_folio_state()`, `fsdev_dax_probe()`, and `fsdev_dax_driver`.

Control flow and state: probe builds/validates pgmap, reserves ranges, caches total size, sets FS-DAX pgmap type/ops/owner, maps pages, clears stale compound folio state from previous drivers, computes data offset between pgmap and dev_dax range, adds a minimal cdev, installs DAX operations with `dax_set_ops()`, marks the device alive, and clears ops/folio state on cleanup. Direct-access translates pgoff to phys/kaddr/pfn and returns contiguous page availability clipped by cached size.

Dependencies and integration: depends on DAX core ops/holder failure notification, memremap_pages, fs-dax/iomap users, cdev, page/folio helpers, and DAX bus.

Risks and test signals: stale compound folio state, cached size correctness, range offset calculation, holder failure notification, and no-mmap semantics matter. Test binding after `device_dax`, filesystem `fs_dax_get()`, direct_access bounds, zero-page and recovery-write paths, memory failure notification, dynamic resize rejection while bound, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/fsdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/hmem/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dax/hmem/Makefile

Purpose: kbuild recipe for HMEM DAX resource discovery and device creation.

Important APIs/types/functions: builds `device_hmem.o` from `device.o` for resource collection and `dax_hmem.o` from `hmem.o` for platform-device conversion, with a comment that `device_hmem.o` deliberately precedes `dax_hmem.o`.

Control flow and state: object order supports initcall ordering: soft-reserve resources are collected before the HMEM platform driver consumes them.

Dependencies and integration: tied to `CONFIG_DEV_DAX_HMEM_DEVICES` and `CONFIG_DEV_DAX_HMEM` from DAX Kconfig.

Risks and test signals: object ordering affects discovery races with ACPI HMAT and CXL fallback. Test boot/module initialization ordering and HMEM device creation with and without CXL DAX enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/hmem/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/hmem/device.c -->
# sources/distributed-fs/ceph-client/drivers/dax/hmem/device.c

Purpose: discovers soft-reserved heterogeneous-memory resources and records them under a global HMEM resource tree, registering the `hmem_platform` device when needed.

Important APIs/types/functions: module parameter `disable`, `walk_hmem_resources()`, `hmem_register_resource()`, `hmem_register_one()`, `hmem_init()`, global `hmem_active`, and `hmem_platform`.

Control flow and state: boot-time `hmem_init()` walks soft-reserve resources and calls `hmem_register_resource()`. Registration is serialized by `hmem_resource_lock`, stores ranges in `hmem_active` with target NUMA node in `res->desc`, and registers one `hmem_platform` device once. `walk_hmem_resources()` lets the HMEM platform driver later consume the recorded child resources.

Dependencies and integration: depends on memregion soft-reserve walking, platform devices, DAX HMEM bus header, NUMA target-node helpers, and module parameter handling.

Risks and test signals: duplicate resource registration, disabled module parameter, target-node propagation via `desc`, and platform device one-shot registration are risks. Test soft-reserve discovery, duplicate overlaps, `hmem.disable=1`, missing platform registration, and handoff to `hmem.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/hmem/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/hmem/hmem.c -->
# sources/distributed-fs/ceph-client/drivers/dax/hmem/hmem.c

Purpose: converts recorded HMEM soft-reserve resources into per-range `hmem` platform devices and dev_dax instances, while deferring CXL-described ranges to CXL when appropriate.

Important APIs/types/functions: module parameter `region_idle`, `dax_hmem_probe()`, `dax_hmem_flush_work()`, `__hmem_register_device()`, `hmem_register_cxl_device()`, `process_defer_work()`, `hmem_register_device()`, `dax_hmem_platform_probe()`, and module init/exit.

Control flow and state: init requests CXL modules when CXL DAX is enabled, creates an ordered workqueue, and registers platform drivers. The platform probe walks collected HMEM resources. For CXL-described resources, it waits for CXL discovery once and drops resources claimed by CXL regions; otherwise it allocates a memregion ID, creates an `hmem` platform device with `memregion_info`, and `dax_hmem_probe()` allocates a DAX region and dev_dax. `region_idle` creates zero-size seed devices instead of default full-size KMEM-eligible devices.

Dependencies and integration: depends on DAX bus, memregion allocator, platform devices, CXL region ownership checks, soft-reserve resource intersection helpers, workqueues, and module autoload.

Risks and test signals: CXL-vs-HMEM ownership race, deferred work lifetime, memregion ID cleanup, region_idle behavior, and IORESOURCE_DAX_KMEM flag selection are key. Test CXL soft-reserve ranges before/after CXL probe, non-CXL soft reserve, module unload with workqueue, region_idle seeds, and dev_dax creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/hmem/hmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/kmem.c -->
# sources/distributed-fs/ceph-client/drivers/dax/kmem.c

Purpose: DAX driver that converts dev_dax ranges into managed System RAM using memory hotplug.

Important APIs/types/functions: `dax_kmem_range()`, memory-tier helpers, `dev_dax_kmem_probe()`, CONFIG_MEMORY_HOTREMOVE-gated `dev_dax_kmem_remove()`, `device_dax_kmem_driver`, and module init/exit.

Control flow and state: probe validates target NUMA node, calculates abstract distance/memory type, aligns ranges to memory-block boundaries, warns about truncation, initializes node memory type, allocates driver data and static memory group, reserves each range as System RAM, and calls `add_memory_driver_managed()` with optional `MHP_MEMMAP_ON_MEMORY`. Remove attempts `remove_memory()` for each range; failures mark `any_hotremove_failed` and intentionally preserve resource/name state until reboot.

Dependencies and integration: depends on memory hotplug, memory tiers, memremap/pagemap, DAX bus, NUMA, resource reservation, and kmem DAX matching via `IORESOURCE_DAX_KMEM`.

Risks and test signals: irreversible hotremove failures, range truncation, invalid target node, memory type lifetime, request_mem_region conflicts, and memmap-on-memory support are high-risk. Test binding/unbinding with memory offline/online, mixed range alignment, target-node absence, memmap_on_memory true/false, resource conflicts, no CONFIG_MEMORY_HOTREMOVE behavior, and kexec resource naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/kmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/pmem.c -->
# sources/distributed-fs/ceph-client/drivers/dax/pmem.c

Purpose: libnvdimm PMEM-DAX driver that creates a static dev_dax device from an NVDIMM DAX namespace.

Important APIs/types/functions: `__dax_pmem_probe()`, `dax_pmem_probe()`, `dax_pmem_driver`, and module init/exit.

Control flow and state: probe obtains a namespace, temporarily enables it to read the PFN info block, calls `nvdimm_setup_pfn()` to populate pgmap, disables the namespace, reserves metadata before `dataoff`, parses namespace ID into DAX region/device IDs, adjusts the DAX range to data start, allocates a static DAX region with namespace alignment, and creates a static dev_dax with the pgmap and full data size.

Dependencies and integration: depends on libnvdimm namespace/PFN helpers, nd device drivers, DAX bus, memory resources, and PMEM namespace metadata layout.

Risks and test signals: metadata reservation, namespace-name parsing, PFN superblock alignment/dataoff, static pgmap lifetime, and namespace enable/disable sequencing are key. Test valid and corrupt PFN info, metadata conflicts, namespace naming, different alignments, and static device-DAX binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/pmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/super.c -->
# sources/distributed-fs/ceph-client/drivers/dax/super.c

Purpose: DAX core pseudo-filesystem and exported service layer. It allocates `struct dax_device`, maintains liveness with SRCU, manages DAX holders/ops, exposes direct-access/copy/zero/recovery helpers, and registers the DAX char-device major and bus.

Important APIs/types/functions: `struct dax_device`, `dax_read_lock()/unlock()`, `dax_direct_access()`, copy/zero/recovery helpers, `dax_holder_notify_failure()`, cache/sync/nocache/nomc setters, `dax_set_ops()`, `kill_dax()`, `run_dax()`, `dax_dev_get()`, `alloc_dax()`, `put_dax()`, `inode_dax()`, `dax_inode()`, `dax_get_private()`, FS-DAX holder APIs, and `dax_core_init()/exit()`.

Control flow and state: DAX devices are private inodes on a pseudo filesystem, keyed by char devt and allocated from a slab cache. Alive state is guarded by `dax_srcu`; `kill_dax()` clears alive, notifies holders of pre-remove failure, waits for SRCU readers, and clears holder data. `alloc_dax()` allocates a minor, inode, private data, and ops; device drivers later add cdevs. FS-DAX can exclusively acquire a holder on block-backed or devdax-backed DAX devices.

Dependencies and integration: depends on VFS, pseudo_fs, cdev, SRCU, xarray host mapping for block DAX, DAX operations, cache flush APIs, FS_DAX, block layer, and DAX bus init.

Risks and test signals: liveness races, holder exclusivity, aliasing-cache rejection, ops replacement, char minor cleanup, and init error unwind are key. Test direct_access before/after kill, fs_dax_get exclusivity, block-device host lookup, dax_set_ops conflicts, cache-copy variants, memory failure notification, module init failures, and final inode destruction warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dax/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dca/Kconfig

Purpose: minimal Kconfig symbol for the Intel Direct Cache Access service module.

Important APIs/types/functions: `config DCA` as a tristate.

Control flow and state: this symbol controls whether the DCA core and sysfs service are built. It does not expose prompt text or dependencies in this snippet, so selection is expected from provider drivers or architecture/platform config.

Dependencies and integration: integrates with kbuild through `drivers/dca/Makefile` and with clients/providers through `<linux/dca.h>` exported symbols.

Risks and test signals: because it is dependency-light, invalid selections can surface at provider build/runtime rather than config time. Test provider configs that select DCA, modular vs built-in builds, and absence of DCA when clients use stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dca/Makefile

Purpose: kbuild recipe for the DCA service module.

Important APIs/types/functions: `obj-$(CONFIG_DCA) += dca.o` and `dca-objs := dca-core.o dca-sysfs.o`.

Control flow and state: when DCA is enabled, core provider/requester logic and sysfs class support are linked into one module/object.

Dependencies and integration: ties the Kconfig symbol to the two implementation files.

Risks and test signals: missing either object breaks exported APIs or sysfs provider/requester representation. Test built-in and module builds and exported symbol resolution for DCA providers/clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/dca-core.c -->
# sources/distributed-fs/ceph-client/drivers/dca/dca-core.c

Purpose: Intel DCA broker that connects requester devices with DCA providers, grouped by PCI root complex, and exports provider/requester/tag APIs.

Important APIs/types/functions: `dca_add_requester()`, `dca_remove_requester()`, `dca3_get_tag()`, legacy `dca_get_tag()`, `alloc_dca_provider()`, `free_dca_provider()`, `register_dca_provider()`, `unregister_dca_provider()`, notifier registration, domain helpers, and `dca_init()/exit()`.

Control flow and state: global `dca_domains` holds provider lists per PCI root complex under `dca_lock`; provider add/remove events use a blocking notifier chain. Requesters are added by finding a provider that manages the device, calling provider ops to allocate a slot, and creating sysfs requester devices. Providers create sysfs provider devices before joining a domain; IOAT v3 blocking logic prevents unsupported multi-root/provider configurations and can unregister existing providers.

Dependencies and integration: depends on PCI root-complex discovery, provider ops from `<linux/dca.h>`, sysfs helper functions in `dca-sysfs.c`, raw spinlocks, blocking notifiers, and exported symbols for other drivers.

Risks and test signals: lock dropping during provider registration, provider/domain teardown, sysfs rollback, legacy `dca_get_tag(NULL)` behavior, IOAT provider blocking, and notifier order are key. Test multiple providers, multiple PCI roots, requester add/remove rollback, get_tag before/after removal, notifier clients, module unload, and sysfs device cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/dca-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/dca-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/dca/dca-sysfs.c

Purpose: sysfs/class support for DCA providers and requesters.

Important APIs/types/functions: `dca_sysfs_add_req()`, `dca_sysfs_remove_req()`, `dca_sysfs_add_provider()`, `dca_sysfs_remove_provider()`, `dca_sysfs_init()`, `dca_sysfs_exit()`, global `dca_class`, `dca_idr`, and `dca_idr_lock`.

Control flow and state: provider registration allocates an ID from `idr`, creates `/sys/class/dca/dcaN` under the provider device, and stores the class device in `dca->cd`. Requester registration creates `requesterN` child class devices using slot-derived minor numbers. Removal unregisters/destroys class devices and releases IDR entries. Init registers the class after initializing IDR/spinlock.

Dependencies and integration: depends on device class APIs, IDR, spinlocks, DCA core structs, and sysfs helper calls from `dca-core.c`.

Risks and test signals: requester minor collisions, static `req_count` naming, provider ID rollback on device_create failure, and synchronization with DCA core locks are risks. Test provider add/remove loops, requester add/remove slots, class registration failure, ID reuse, and cleanup after core unregisters all providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dca/dca-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/devfreq/Kconfig

Purpose: Kconfig menu for the Linux devfreq framework, governors, and several platform devfreq drivers.

Important APIs/types/functions: `PM_DEVFREQ`, governor symbols for simple-ondemand, performance, powersave, userspace, passive, and platform driver symbols such as Exynos bus, HiSilicon uncore, i.MX bus/DDRC, Tegra, MediaTek CCI, Rockchip DMC, Sunxi MBUS, plus inclusion of `drivers/devfreq/event/Kconfig`.

Control flow and state: enabling `PM_DEVFREQ` selects OPP and opens governor/driver menus. Governors are separate tristates; platform drivers select required governors and event frameworks. Help text documents the devfreq model: one representative device frequency, optional OPP notifier use, and driver-supplied target callbacks.

Dependencies and integration: integrates with OPP, PM_DEVFREQ_EVENT, architecture/platform symbols, ACPI/PPTT/PCC, common clock, SMCCC, and devfreq event devices.

Risks and test signals: dependency mistakes can overbuild platform drivers or miss governor/event requirements. Test Kconfig combinations for each platform, governor module builds, event Kconfig inclusion, COMPILE_TEST paths, and OPP/devfreq core availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/devfreq/Makefile

Purpose: kbuild recipe for devfreq core, event framework, governors, and platform drivers.

Important APIs/types/functions: builds `devfreq.o`, `devfreq-event.o`, governor objects, platform driver objects (`exynos-bus.o`, `hisi_uncore_freq.o`, `imx-bus.o`, `imx8m-ddrc.o`, `mtk-cci-devfreq.o`, `rk3399_dmc.o`, `sun8i-a33-mbus.o`, `tegra30-devfreq.o`), and descends into `event/`.

Control flow and state: object inclusion follows Kconfig symbols and keeps core/event/governor/platform implementation separated.

Dependencies and integration: ties `drivers/devfreq/Kconfig` symbols to compiled objects and the devfreq event subdirectory.

Risks and test signals: missing object mapping causes enabled drivers/governors to be absent or unresolved. Test all relevant modular/built-in combinations, event framework builds, and platform driver symbol names after refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/Makefile -->
