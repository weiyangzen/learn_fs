# subset-b-005007 Research

Grouped source-tree-aligned research for the PCI endpoint and hotplug files in subset B. Each section preserves the source path for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-test.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-test.c

## Purpose
Implements the `pci_epf_test` endpoint-function driver used to validate PCI endpoint controller behavior from a root-complex test client. It exposes a BAR-hosted command/status register block and exercises BAR access, outbound memory mapping, DMA transfers, INTx/MSI/MSI-X delivery, platform-MSI doorbells, and dynamic BAR subrange mapping.

## Important APIs, Types, and Functions
`struct pci_epf_test` stores per-function state: BAR virtual addresses, the selected test-register BAR, EPC feature pointer, delayed command work, DMA channels, transfer completion state, configured BAR sizes, and temporary doorbell BAR metadata. `struct pci_epf_test_reg` is the little-endian ABI shared with the host and carries commands, status bits, source/destination PCI addresses, size, checksum, interrupt selection, flags, capabilities, and doorbell metadata.

Core handlers are `pci_epf_test_cmd_handler()`, `pci_epf_test_read()`, `pci_epf_test_write()`, `pci_epf_test_copy()`, `pci_epf_test_raise_irq()`, `pci_epf_test_enable_doorbell()`, `pci_epf_test_disable_doorbell()`, `pci_epf_test_bar_subrange_setup()`, and `pci_epf_test_bar_subrange_clear()`. Lifecycle hooks are wired through `pci_epf_test_event_ops` and `ops`: `.bind`, `.unbind`, `.epc_init`, `.epc_deinit`, `.link_up`, `.link_down`, and `.add_cfs`.

## Control Flow
Probe allocates driver state, assigns `test_header`, initializes default BAR sizes, and installs event ops. Bind gets EPC features, chooses the first free BAR for the control register block, allocates BAR spaces, and records the EPC feature contract. `epc_init` initializes DMA if possible, writes the PCI config header for physical functions or VF1, publishes capabilities in the test register, sets BARs, configures MSI/MSI-X if supported, and starts command polling immediately unless the controller supplies a link-up notifier. Link-up starts the delayed command worker; link-down, deinit, and unbind cancel it and clear hardware mappings.

The command worker polls every 1 ms. It atomically reads and clears `reg->command`, clears status, rejects DMA commands when DMA channels are unavailable, dispatches exactly one command value, updates status, raises the selected interrupt, and requeues itself. Data operations repeatedly call `pci_epc_mem_map()` because controller alignment may map less than the requested host PCI range; each loop unmaps before advancing the PCI address.

## State and Persistence
All state is kernel-resident and tied to the EPF device lifetime. Configfs BAR size attributes persist only while the EPF instance exists and are rejected after the EPF has been bound to an EPC. The host-visible ABI is the BAR register block; status bits are written back there and the host observes command completion by interrupt and memory reads. Doorbell enable temporarily remaps a BAR to an MSI message address and disable restores the BAR mapping to normal EPF memory.

## Dependencies and Integration Points
This file depends on the PCI endpoint core (`pci_epf_*`, `pci_epc_*`), EPC memory mapping (`pci_epc_mem_map()` and `pci_epc_mem_unmap()`), the endpoint MSI-doorbell helper (`pci_epf_alloc_doorbell()`), DMAengine, CRC32, configfs, delayed workqueues, and PCI register definitions. It integrates with userspace through configfs function creation and BAR-size attributes, with the host-side PCI endpoint test driver through the BAR ABI, and with EPC controller drivers through feature flags and operation callbacks.

## Risks and Edge Cases
The command register is polled rather than interrupt-driven, so host writes can be delayed by the workqueue interval and concurrent command writes are not queued. DMA is optional and may silently fall back to CPU copy if channel allocation fails at init; command handling rejects DMA later when unsupported. The copy path must handle partial mappings correctly; a missed unmap would leak outbound windows. Doorbell setup overrides BAR inbound translation and relies on restore in disable/unbind paths. Subrange mapping mutates `bar->submap` and must restore the old mapping on `pci_epc_set_bar()` failure; `-ENOSPC` is surfaced as `STATUS_NO_RESOURCE`. Module exit destroys the workqueue before unregistering the EPF driver, so active instances must have canceled work during unbind/deinit.

## Test Signals
Useful test signals are host-side command completion bits, CRC match/mismatch for read/write, copy data verification by the root complex, successful MSI/MSI-X/INTx delivery, doorbell IRQ handling via `STATUS_DOORBELL_SUCCESS`, subrange signature validation, dmesg throughput logs from `pci_epf_test_print_rate()`, and failure injection on invalid PCI addresses, unsupported DMA, exhausted BAR resources, and controllers with reserved/fixed BARs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-vntb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-vntb.c

## Purpose
Implements `pci_epf_vntb`, an endpoint-function driver that exposes a virtual Non-Transparent Bridge between a PCI root complex and the local endpoint side. It maps NTB concepts onto endpoint BARs: a control/scratchpad BAR, a doorbell BAR, and memory-window BARs. It also creates a synthetic local PCI bus and registers a virtual PCI NTB device so in-kernel NTB clients can use the standard NTB API.

## Important APIs, Types, and Functions
`struct epf_ntb_ctrl` is the shared control region used by the remote host and local virtual NTB driver; it holds command, status, link state, memory-window address/size, scratchpad layout, doorbell data, and offsets. `struct epf_ntb` combines `struct ntb_dev`, the EPF pointer, configfs group, BAR assignments, memory-window sizes and backing addresses, doorbell mode, scratchpad count, atomic doorbell bits, and delayed command work.

Endpoint setup is handled by `epf_ntb_bind()`, `epf_ntb_init_epc_bar()`, `epf_ntb_config_spad_bar_alloc()`, `epf_ntb_epc_init()`, `epf_ntb_db_bar_init()`, `epf_ntb_mw_bar_init()`, and cleanup counterparts. Command processing lives in `epf_ntb_cmd_handler()`. NTB operations are implemented in `vntb_epf_ops`, including memory-window translation, scratchpad reads/writes, peer doorbell, doorbell read/clear, link state, and DMA device lookup.

## Control Flow
Probe initializes defaults, marks all NTB BAR roles as `NO_BAR`, and installs the EPF header. Bind requires a primary EPC, auto-assigns mandatory BARs for config, doorbell, and at least MW1, allocates the config/scratchpad BAR, initializes endpoint BARs/interrupts/memory windows, writes the endpoint header, and starts command polling. It then updates the synthetic PCI config space and PCI ID table, registers a global `pci-vntb` driver, scans a virtual PCI bus, and lets `pci_vntb_probe()` register the `ntb_dev`.

The command worker polls the remote control block, handles polling-mode doorbells by checking the doorbell BAR, executes host commands such as configure/teardown memory window and link up/down, writes command status, and requeues at 5 ms in polling mode or 500 ms when MSI doorbells are active. Memory-window configuration maps local outbound memory (`vpci_mw_phy[mw]`) to host-provided PCI addresses through `pci_epc_map_addr()`.

## State and Persistence
Runtime state is per EPF but some virtual PCI state is global: `pci_space`, `pci_vntb_table`, and `vntb_pci_driver`. Configfs attributes for `spad_count`, `db_count`, `num_mws`, memory-window sizes, virtual bus number, virtual vendor/device IDs, and explicit BAR selection are volatile EPF settings and should be finalized before bind. Link state and commands are shared through the config/scratchpad BAR. Doorbells are either platform-MSI backed or a memory BAR polled by the worker.

## Dependencies and Integration Points
Depends on PCI endpoint core, endpoint MSI-doorbell helpers, NTB core (`ntb_register_device()` and `ntb_dev_ops`), PCI bus scanning (`pci_scan_bus()`), workqueues, atomic bit operations, configfs, and EPC memory allocators. It integrates upward with NTB clients, sideways with the synthetic PCI driver, and downward with EPC set/clear BAR, map/unmap, MSI, and header operations.

## Risks and Edge Cases
The synthetic PCI driver and `pci_space` are global, making concurrent multiple vNTB EPF instances risky. Several configfs writers do not block changes after bind, so userspace can mutate values that were already consumed during BAR allocation. Doorbell MSI setup assumes immutable platform MSI support and falls back to polling; polling mode increases latency and CPU activity. `vntb_epf_peer_db_set()` derives an interrupt number from `ffs(db_bits)` and should be tested for zero or multi-bit inputs. Cleanup must cancel delayed work before freeing BAR memory and IRQs. BAR selection must avoid duplicate explicit assignments and controller-reserved BARs.

## Test Signals
Exercise NTB link up/down events, scratchpad read/write symmetry, memory-window translation, peer memory address reporting, doorbell delivery in both MSI and polling modes, virtual PCI bus enumeration, and `ntb_transport` or NTB netdev clients. Negative tests should include insufficient BARs, oversized `num_mws`, no MSI domain, multiple instances, missing EPC memory windows, and unbind while command polling is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-vntb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-cfs.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-cfs.c

## Purpose
Provides the configfs control plane for PCI endpoint configuration. It creates `/config/pci_ep/functions` and `/config/pci_ep/controllers`, lets userspace instantiate endpoint functions, configure PCI header and interrupt fields, expose function-driver-specific attributes, link EPFs to primary or secondary EPC interfaces, associate virtual EPFs with physical EPFs, and start or stop endpoint controllers.

## Important APIs, Types, and Functions
`struct pci_epf_group` wraps a configfs group, primary/secondary EPC subgroups, the EPF pointer, and an IDR index. `struct pci_epc_group` wraps a controller configfs group, EPC pointer, and `start` state. Exported entry points are `pci_ep_cfs_add_epc_group()`, `pci_ep_cfs_remove_epc_group()`, `pci_ep_cfs_add_epf_group()`, and `pci_ep_cfs_remove_epf_group()`.

Key callbacks include primary/secondary link and unlink handlers, `pci_epc_start_store()`, `pci_epf_make()`, `pci_epf_release()`, `pci_epf_type_add_cfs()`, and virtual EPF link/unlink callbacks. Attribute macros generate configfs accessors for PCI header fields and MSI/MSI-X interrupt counts.

## Control Flow
Module init registers the `pci_ep` subsystem and default `functions` and `controllers` groups. EPC creation in controller drivers calls `pci_ep_cfs_add_epc_group()`, which registers a controller group and obtains an EPC reference by name. EPF driver registration creates a function-type group under `functions`; userspace creating an item under that group calls `pci_epf_make()`, allocates an ID, creates an EPF device, initializes primary and secondary subgroups, and asks the function driver for optional type-specific configfs groups.

Linking a function to a controller calls `pci_epc_add_epf()`, `pci_epf_bind()`, and `pci_epc_notify_pending_init()`. Unlink warns if the EPC is still started, calls `pci_epf_unbind()`, and removes the EPF from the EPC. Writing `start=1` calls `pci_epc_start()`; writing `start=0` calls `pci_epc_stop()`.

## State and Persistence
Configfs items are the persistent user-visible state while mounted, but all objects are in-kernel and disappear on item deletion/module unload. `functions_idr` gives stable instance suffixes for active EPFs only. Header fields and MSI/MSI-X counts are stored directly in the `struct pci_epf` and consumed by function drivers when binding and initializing the EPC. `epc_group->start` mirrors whether the configfs control plane started the controller.

## Dependencies and Integration Points
Depends on configfs, IDR, PCI EPF/EPC libraries, and optional function-driver `add_cfs()` callbacks. It is the integration point between userspace endpoint setup scripts, EPF function drivers, and EPC controller drivers. It relies on the EPF bus to bind `pci_epf_create()` devices to registered EPF drivers.

## Risks and Edge Cases
Several attributes can be written regardless of bind/start state; function drivers must decide which settings are safe after bind. Unlink only warns if a controller is started, so userspace sequencing matters. Type-specific configfs group creation requires the EPF to be driver-bound; errors are logged but the EPF instance may still exist with fewer controls. `pci_ep_cfs_remove_epf_group()` manipulates configfs group entries and must match groups created by EPF driver registration. Virtual EPF association requires both PF and VF to be unbound.

## Test Signals
Create/delete EPF instances for each function type, set header/MSI attributes, link primary and secondary EPCs, verify `pci_epf_bind()` failures roll back EPC association, start/stop controllers through configfs, associate/disassociate virtual EPFs, and unload EPF/EPC modules while configfs objects exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-cfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-msi.c

## Purpose
Implements the endpoint-function MSI doorbell helper. It allocates platform MSI vectors for an EPC parent device and records the MSI message address/data in the first EPF so endpoint functions can expose those messages to a host as doorbell targets.

## Important APIs, Types, and Functions
`pci_epf_alloc_doorbell()` allocates `struct pci_epf_doorbell_msg` entries, initializes platform MSI interrupts, and records Linux virtual IRQs. `pci_epf_free_doorbell()` releases all platform MSI interrupts and clears EPF doorbell state. `pci_epf_write_msi_msg()` is the MSI message writer callback that copies generated `struct msi_msg` values into the EPF doorbell array.

## Control Flow
Allocation verifies that the requesting EPF is the first EPF on the EPC list, rejects duplicate allocation, locates an immutable platform MSI parent domain for `epc->dev.parent`, sets that domain on the parent device, allocates the message array, calls `platform_device_msi_init_and_alloc_irqs()`, and stores `msi_get_virq()` results per doorbell. The write callback looks up the EPC by device name and updates the matching doorbell message slot when the platform MSI layer creates or rewrites messages.

## State and Persistence
Doorbell state lives in `epf->db_msg` and `epf->num_db` until freed. The MSI domain is attached to the EPC parent device. The helper does not persist data outside the live kernel objects, and it intentionally supports only one EPF per EPC for doorbell allocation.

## Dependencies and Integration Points
Depends on irqdomain/MSI APIs, OF MSI mapping, platform-device MSI allocation, the EPC class lookup helper, and EPF state. It is consumed by `pci-epf-test.c` and `pci-epf-vntb.c` to implement host-visible doorbells.

## Risks and Edge Cases
The explicit TODO means multi-EPF doorbells are unsupported; using this helper when multiple EPFs share an EPC returns `-EINVAL`. Mutable MSI controllers and missing MSI domains are rejected. The write callback looks up the EPC by `dev_name(msi_desc_to_dev(desc))`, so naming consistency is important. Freeing releases all platform MSI IRQs for the EPC parent, which assumes this helper owns them.

## Test Signals
Test allocation/free cycles, duplicate allocation returning `-EBUSY`, missing or mutable MSI domain failure, IRQ request/use by caller drivers, correct MSI message address/data propagation, and rejection when the requester is not the first EPF on the EPC list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-ep-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-core.c

## Purpose
Provides the core library and class for PCI endpoint controllers. It registers EPC devices, exposes controller operations to endpoint functions, validates function/VF numbers, serializes controller callbacks, manages EPF attachment, delivers link/init/bus-master notifications, and adds EPCs to endpoint configfs.

## Important APIs, Types, and Functions
Key exported APIs include `pci_epc_get()/put()`, `pci_epc_get_features()`, `pci_epc_start()/stop()`, `pci_epc_raise_irq()`, `pci_epc_set_msi()/get_msi()`, `pci_epc_set_msix()/get_msix()`, `pci_epc_map_addr()/unmap_addr()`, `pci_epc_mem_map()/mem_unmap()`, `pci_epc_set_bar()/clear_bar()`, `pci_epc_write_header()`, `pci_epc_add_epf()/remove_epf()`, notification helpers, `__pci_epc_create()`, and `__devm_pci_epc_create()`.

## Control Flow
Module init registers the `pci_epc` class. Controller drivers create EPC objects with operation tables; creation initializes locks, the EPF list, class device, domain number, and configfs group. EPF configfs linking calls `pci_epc_add_epf()`, which allocates a function number and links the EPF into the controller list. EPF drivers then call exported wrappers; each wrapper validates function numbers and operation presence before locking `epc->lock` and invoking controller-specific callbacks.

Notifications walk the attached EPF list under `list_lock`, take each EPF lock, and call optional event ops for link up/down, EPC init/deinit, or bus master enable. `pci_epc_mem_map()` combines endpoint memory allocation, optional controller address alignment, and outbound mapping into one temporary host-PCI mapping used by test/data drivers.

## State and Persistence
EPC state includes class device lifetime, operation table, parent device, domain number, max functions/VFs, attached EPF list, function-number bitmap, configfs group, memory windows, and `init_complete`. The library persists only in-kernel state. References are managed through class device lookup and module owner counts.

## Dependencies and Integration Points
Depends on the Linux driver core, PCI endpoint function headers, endpoint configfs, domain-number helpers, and EPC controller operation implementations. It is the central integration point between hardware-specific EPC drivers, EPF function drivers, and configfs.

## Risks and Edge Cases
All wrappers return success when an optional operation is missing in several cases, so callers must know whether a no-op is acceptable. Function number allocation is limited by `BITS_PER_LONG` and `epc->max_functions`. `pci_epc_set_bar()` enforces power-of-two size, fixed/resizable BAR constraints, 64-bit BAR legality, and submap feature support; callers that mutate `struct pci_epf_bar` must keep it internally consistent. Notification callbacks run under EPC list locking and EPF locking, so callback reentrancy into configfs/link paths must be considered. `pci_epc_get()` calls `put_device(dev)` even on the error path where `dev` may be NULL; this relies on `put_device(NULL)` safety.

## Test Signals
Create/destroy EPC devices, link multiple EPFs until function limits, exercise all wrappers with missing and present ops, validate BAR error paths, test init notification before and after EPF bind, test VF validation, run endpoint-test transfers using `pci_epc_mem_map()`, and unload controller modules while references/configfs groups exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-mem.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-mem.c

## Purpose
Implements address-space allocation for endpoint controller memory windows. EPF and EPC core code use it to reserve local physical ranges that can be mapped to host PCI addresses for outbound transfers or memory windows.

## Important APIs, Types, and Functions
`pci_epc_multi_mem_init()` initializes one or more `struct pci_epc_mem` windows with bitmaps and per-window locks. `pci_epc_mem_init()` is the single-window wrapper. `pci_epc_mem_exit()` frees all window metadata. `pci_epc_mem_alloc_addr()` finds a free aligned region, ioremaps it, and returns virtual and physical addresses. `pci_epc_mem_free_addr()` unmaps and releases the bitmap region. `pci_epc_mem_get_order()` computes bitmap allocation order using the controller window page size rather than `PAGE_SIZE`.

## Control Flow
Initialization normalizes each requested window page size to at least `PAGE_SIZE`, calculates page count and bitmap size, allocates metadata, and sets `epc->windows`, `epc->mem`, and `epc->num_windows`. Allocation scans all windows that can fit the requested size, aligns size to the window page size, locks the window bitmap, reserves a free region, calculates physical address, ioremaps the region, and returns it. Free finds the window containing the physical address, iounmaps, recalculates the bitmap order, and releases the region.

## State and Persistence
State is stored in `epc->windows[]`, each window's bitmap, page count, page size, physical base, and mutex. Allocated regions are not persisted; they must be explicitly freed by callers. `epc->num_windows` acts as the initialization flag.

## Dependencies and Integration Points
Depends on ioremap/iounmap, bitmap region helpers, mutexes, and `struct pci_epc`. It is used by EPC core `pci_epc_mem_map()` and endpoint function drivers such as vNTB to allocate local outbound-memory backing.

## Risks and Edge Cases
Window size smaller than page size produces zero pages and should be avoided by controller drivers. Allocation may fail in one window after reserving a bitmap region if `ioremap()` fails; the code releases that region and continues. Freeing an address outside all windows only logs an error and leaks nothing else, but it indicates caller state corruption. The allocator is first-fit by window and bitmap region, with no persistence or compaction beyond freeing regions.

## Test Signals
Initialize single and multiple windows, allocate/free varying sizes and page sizes, exhaust windows, force ioremap failure if possible, verify no bitmap leak after failed mapping, and exercise allocation through `pci_epc_mem_map()` loops in endpoint-test read/write/copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epc-mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epf-core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epf-core.c

## Purpose
Provides the PCI endpoint function bus and helper library. It creates EPF devices, registers EPF drivers, binds/unbinds functions to EPCs, associates virtual functions with physical functions, allocates/assigns/free BAR backing memory, and exposes EPF driver configfs groups.

## Important APIs, Types, and Functions
Key exported APIs are `pci_epf_bind()`, `pci_epf_unbind()`, `pci_epf_add_vepf()`, `pci_epf_remove_vepf()`, `pci_epf_alloc_space()`, `pci_epf_assign_bar_space()`, `pci_epf_free_space()`, `pci_epf_register_driver()` via `__pci_epf_register_driver()`, `pci_epf_unregister_driver()`, `pci_epf_create()`, `pci_epf_destroy()`, and `pci_epf_align_inbound_addr()`. Bus callbacks match EPF devices by `pci_epf_device_id` or driver name and invoke driver probe/remove.

## Control Flow
Module init registers the `pci-epf` bus. Configfs creates EPF devices with names like `pci_epf_test.0`; `pci_epf_create()` stores the function type before the dot, initializes locks and VF tracking, and adds the device to the EPF bus. Driver registration validates bind/unbind ops, registers the driver, and creates configfs groups for each ID table entry. Binding first validates all associated VFs against EPC limits, binds VFs, then binds the PF and marks instances bound. Unbind calls VF unbinds then PF unbind and releases the driver module reference.

BAR allocation computes required BAR size based on EPC feature constraints, allocates coherent DMA memory from the EPC parent, and fills `struct pci_epf_bar`. Assignment is used for pre-existing physical ranges such as MSI doorbell message pages. Free releases coherent memory and clears BAR metadata.

## State and Persistence
State lives in `struct pci_epf`: name, device, driver, header, BAR arrays, EPC pointers, function/VF numbers, VF list, bound flags, configfs group, and event ops set by function drivers. Configfs groups for function types are tracked in each EPF driver and removed at unregister.

## Dependencies and Integration Points
Depends on the driver core, DMA coherent allocation, endpoint configfs, and EPC feature descriptions. It connects configfs-created EPF devices to function drivers such as `pci_epf_test` and `pci_epf_vntb`.

## Risks and Edge Cases
`pci_epf_bind()` calls `pci_epf_unbind()` on error, so partial VF/PF binds must tolerate cleanup. VF numbering reserves bit 0 because VFs start at 1. `pci_epf_add_vepf()` rejects association after either side is EPC-bound. BAR allocation assumes valid EPC pointers for the selected interface. `pci_epf_align_inbound_addr()` aligns to current BAR size and assumes power-of-two BAR sizes.

## Test Signals
Create EPFs before/after driver registration, bind/unbind PFs and VFs, test VF limits from EPC features, allocate fixed/resizable/64-bit BARs, assign BARs to unaligned physical addresses, unload EPF drivers with live configfs groups, and verify driver probe/remove matching by ID table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/pci-epf-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/host-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/pci/host-bridge.c

## Purpose
Provides small host-bridge helper routines for locating the root host bridge, managing host-bridge device references, installing release callbacks, and translating resources between CPU physical addresses and PCI bus address regions.

## Important APIs, Types, and Functions
Exports `pci_find_host_bridge()`, `pci_get_host_bridge_device()`, `pci_set_host_bridge_release()`, `pcibios_resource_to_bus()`, and `pcibios_bus_to_resource()`. Internal helpers are `find_pci_root_bus()` and `region_contains()`.

## Control Flow
Root-bus lookup walks `bus->parent` to the top and converts `root_bus->bridge` into `struct pci_host_bridge`. Resource-to-bus translation finds the host bridge window containing the resource and subtracts the window offset. Bus-to-resource translation searches windows of the same resource type, constructs the bus-visible region for each, chooses the one containing the requested bus region, and adds the offset to produce CPU resource coordinates.

## State and Persistence
This file owns no persistent state. It reads the host bridge `windows` list and manipulates references to existing bridge devices. Release callback data is stored in `struct pci_host_bridge`.

## Dependencies and Integration Points
Depends on core PCI bus/host bridge structures and resource window lists. It is used by ACPI hotplug helpers and other PCI code needing host-bridge lookup or address translation.

## Risks and Edge Cases
If no matching window is found, translations use offset zero; callers must ensure windows are populated for non-identity mappings. `pci_get_host_bridge_device()` manually increments the kobject reference and must be balanced by `pci_put_host_bridge_device()`. Resource type matching matters for bus-to-resource translation.

## Test Signals
Validate translations on systems with identity and non-identity host bridge windows, IO versus memory windows, nested PCI buses, host bridge reference get/put balancing, and callers using `pci_find_host_bridge()` on child buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/host-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/Kconfig

## Purpose
Defines build-time configuration for PCI hotplug support and its platform-specific controller drivers. It gates generic PCI hotplug, ACPI hotplug, CompactPCI, SHPC, native PCIe, PowerNV, RPA, S390, OCTEON, and legacy Compaq/IBM drivers.

## Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. Important symbols include `HOTPLUG_PCI`, `HOTPLUG_PCI_ACPI`, `HOTPLUG_PCI_ACPI_AMPERE_ALTRA`, `HOTPLUG_PCI_ACPI_IBM`, `HOTPLUG_PCI_CPCI`, `HOTPLUG_PCI_CPCI_GENERIC`, `HOTPLUG_PCI_SHPC`, `HOTPLUG_PCI_POWERNV`, `HOTPLUG_PCI_RPA`, `HOTPLUG_PCI_RPA_DLPAR`, and `HOTPLUG_PCI_S390`.

## Control Flow
The top-level `HOTPLUG_PCI` menu depends on PCI and sysfs and defaults to enabled for USB4. Nested symbols become visible only when hotplug is enabled. Dependencies constrain drivers to supported architectures and firmware interfaces, such as ACPI, x86 PCI BIOS, ARM SMCCC discovery, PowerPC EEH, or S390 64-bit.

## State and Persistence
State is the kernel configuration selected at build time. It persists in `.config` and determines which objects are built into the kernel or as modules.

## Dependencies and Integration Points
Integrates with `drivers/pci/hotplug/Makefile` to select object files. The comments and dependencies encode intended ownership boundaries: ACPI hotplug as a fallback, native PCIe/SHPC where available, and platform extensions layered on ACPI hotplug.

## Risks and Edge Cases
Incorrect dependencies can expose unusable drivers on unsupported platforms or hide required hotplug support. `HOTPLUG_PCI_ACPI` is a bool and depends on `HOTPLUG_PCI=y`, so modular combinations are constrained. Platform extensions depend on core ACPI hotplug and must not be enabled without it.

## Test Signals
Run Kconfig dependency checks for representative x86, ARM64, PowerPC, and S390 configs; verify selected symbols build the expected modules; and validate that USB4 configs enable hotplug support by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/Makefile

## Purpose
Maps hotplug Kconfig symbols to object files and composite modules for the PCI hotplug subsystem.

## Important APIs, Types, and Functions
This is build metadata. It defines objects for `pci_hotplug`, `acpiphp`, `cpqphp`, `ibmphp`, `pciehp`, `shpchp`, `rpaphp`, `rpadlpar_io`, `pnv-php`, and platform-specific single-object drivers. It conditionally includes `cpci_hotplug_core.o`, `cpci_hotplug_pci.o`, and `acpi_pcihp.o` in the core `pci_hotplug` object depending on config symbols.

## Control Flow
Object order is meaningful: native hotplug drivers are linked before `acpiphp` so they can bind before ACPI fallback. `acpiphp_ibm` is linked after `acpiphp` because it registers attention callbacks against the ACPI hotplug core.

## State and Persistence
The file persists build composition only. Runtime state is in the compiled modules and drivers selected by this metadata.

## Dependencies and Integration Points
Integrates Kconfig with kbuild. It aligns ACPI helper inclusion with `CONFIG_ACPI` and CompactPCI core inclusion with `CONFIG_HOTPLUG_PCI_CPCI`.

## Risks and Edge Cases
Changing object order can alter driver binding precedence. Missing conditional object inclusion can produce unresolved symbols or remove helper exports. Composite object lists must match source files and symbol dependencies.

## Test Signals
Build hotplug configurations for ACPI-only, CPCI, native PCIe, IBM/Compaq legacy, and allmodconfig; inspect module contents and link order for expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpi_pcihp.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpi_pcihp.c

## Purpose
Provides common ACPI helper functions for PCI hotplug drivers. It arbitrates OS control of SHPC hotplug through ACPI `_OSC`/`OSHP`, and detects whether ACPI namespace objects represent ejectable PCI slots.

## Important APIs, Types, and Functions
Exports `acpi_get_hp_hw_control_from_firmware()`, `acpi_pci_check_ejectable()`, and `acpi_pci_detect_ejectable()`. Internal helpers are `acpi_run_oshp()`, `pcihp_is_ejectable()`, and the namespace walk callback `check_hotplug()`.

## Control Flow
For firmware control, the helper locates the ACPI PCI root for the host bridge. If `_OSC` was used, it trusts `native_shpc_hotplug`; otherwise it searches from the hotplug controller or parent bridge handles upward and evaluates `OSHP` until success or the root bridge is reached. For ejectability, it checks for `_ADR` plus `_EJ0` or a true `_RMV`, and ensures the object's parent matches the PCI bus bridge handle.

## State and Persistence
Only module parameter `debug_acpi` persists while loaded. All other behavior is query-based against firmware state.

## Dependencies and Integration Points
Depends on ACPI core, PCI ACPI root lookup, host bridge lookup, PCI hotplug, and namespace walking. It is compiled into `pci_hotplug` when ACPI is enabled and is used by ACPI hotplug and SHPC/native arbitration paths.

## Risks and Edge Cases
The OSHP search up the ACPI hierarchy is explicitly called suspect relative to the PCI Firmware Specification. Firmware may omit `_OSC`, `OSHP`, `_EJ0`, or `_RMV`, making detection heuristic. `acpi_get_name()` allocated buffers must be freed on all paths, which this file does.

## Test Signals
Test systems with `_OSC` granting and denying SHPC control, systems requiring `OSHP`, ejectable slots with `_EJ0`, removable slots with `_RMV`, non-ejectable PCI devices, and ACPI-disabled platforms where root lookup returns no ACPI root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpi_pcihp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp.h

## Purpose
Defines the internal data model and APIs for the ACPI PCI hotplug driver. It connects generic hotplug slots, ACPI namespace functions, PCI bridge/bus state, and optional platform attention-LED providers.

## Important APIs, Types, and Functions
Important structs are `slot`, `acpiphp_bridge`, `acpiphp_slot`, `acpiphp_func`, `acpiphp_context`, `acpiphp_root_context`, and `acpiphp_attention_info`. It defines flags `SLOT_ENABLED`, `SLOT_IS_GOING_AWAY`, `FUNC_HAS_STA`, and `FUNC_HAS_EJ0`, plus `ACPI_STA_ALL`. Inline helpers convert hotplug slots and ACPI hotplug contexts back to driver objects.

## Control Flow
The header declares the contract between `acpiphp_core.c` and `acpiphp_glue.c`: core registers/deregisters slots and attention providers, while glue enables/disables slots and computes status. Platform extensions register `acpiphp_attention_info` callbacks.

## State and Persistence
The structures declared here define runtime state. A bridge owns a list of slots, a kref, PCI bus/device references, and a going-away flag. A slot owns a PCI bus/device number and functions. Function contexts tie ACPI device hotplug callbacks to slot membership.

## Dependencies and Integration Points
Depends on ACPI, mutex declarations, and `pci_hotplug.h`. It is shared by the ACPI core, glue, Ampere extension, and IBM extension.

## Risks and Edge Cases
Header-level invariants matter: one physical slot may contain multiple ACPI function objects; bridge references protect notification handlers against removal; and attention callbacks are global to acpiphp. Mismanaging `SLOT_IS_GOING_AWAY` or context references can cause use-after-free during ACPI notifications.

## Test Signals
Compile-test all ACPI hotplug files, verify structure assumptions in slot enumeration, test attention provider registration/unregistration, and exercise dock/eject events where contexts and bridge refs are stressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ampere_altra.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ampere_altra.c

## Purpose
Provides an Ampere Altra ACPI hotplug extension that controls slot attention LEDs by making ARM SMCCC calls to system firmware.

## Important APIs, Types, and Functions
`set_attention_status()` maps hotplug LED state to firmware LED commands and sends `HANDLE_OPEN`, `REQUEST`, and `HANDLE_CLOSE` SMC calls. `get_attention_status()` is unsupported. `altra_led_probe()` reads a firmware UUID property and registers `ampere_altra_attn` with acpiphp. `altra_led_remove()` unregisters it. The ACPI platform ID is `AMPC0008`.

## Control Flow
When the platform device probes, it reads four `u32` UUID words from firmware node property `uuid`, then registers global acpiphp attention callbacks. Setting attention status finds the root port for the slot bus, disables local IRQs, opens a firmware service handle, sends a LED attention request keyed by root-port slot and PCI domain nibble, closes the handle, restores IRQs, and returns firmware errors as `-ENODEV`.

## State and Persistence
The only persistent runtime state is `led_service_id[4]` and registration of the global attention callback while the platform driver is bound.

## Dependencies and Integration Points
Depends on ACPI platform device matching, ARM SMCCC, PCI root-port lookup, hotplug slot structures, and acpiphp attention registration.

## Risks and Edge Cases
The provider cannot report attention status, so reads return `-EINVAL`. Firmware call failures map to `-ENODEV` without detailed status. The request encodes only low PCI domain bits. IRQs are disabled around all SMCCC calls, so firmware latency matters. Only one acpiphp attention provider can be registered globally.

## Test Signals
Probe with and without `uuid`, set LED off/on/blink from hotplug sysfs, verify SMCCC failure handling, unload the module and confirm callback removal, and test systems with no root port for a slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ampere_altra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_core.c

## Purpose
Implements the generic hotplug-slot interface for ACPI PCI hotplug. It registers slots with the PCI hotplug core, exposes enable/disable/status/attention operations, and provides a global registration point for platform-specific attention LED handlers.

## Important APIs, Types, and Functions
Exports `acpiphp_register_attention()`, `acpiphp_unregister_attention()`, `acpiphp_register_hotplug_slot()`, and `acpiphp_unregister_hotplug_slot()`. Static hotplug ops include `enable_slot()`, `disable_slot()`, `set_attention_status()`, `get_power_status()`, `get_attention_status()`, `get_latch_status()`, and `get_adapter_status()`. `acpiphp_init()` logs module status and honors `acpiphp_disabled`.

## Control Flow
Slot registration allocates `struct slot`, assigns `acpi_hotplug_slot_ops`, links it to the `acpiphp_slot`, names it by `_SUN`, and calls `pci_hp_register()`. Hotplug-core enable/disable callbacks delegate to glue functions `acpiphp_enable_slot()` and `acpiphp_disable_slot()`. Status callbacks translate ACPI glue state into generic hotplug values. Attention callbacks call the registered provider under a module reference.

## State and Persistence
Global state consists of `acpiphp_disabled` and one `attention_info` pointer. Per-slot state is allocated for each registered hotplug slot and freed on unregister. The generic hotplug core exposes these slots through sysfs.

## Dependencies and Integration Points
Depends on PCI hotplug core, ACPI PCI glue functions, module reference counting, and optional platform extensions such as Ampere/IBM attention providers.

## Risks and Edge Cases
Only one attention provider can be registered. If `try_module_get()` fails, the provider pointer is cleared. Slot registration may fail with `-EBUSY` when a native driver already registered the slot; glue can still track the slot internally without sysfs exposure. Power/latch/adapter status are derived from ACPI glue state and may be heuristic when firmware `_STA` is unreliable.

## Test Signals
Register/unregister slots, enable/disable via sysfs, read power/latch/adapter status, test attention callback provider install/removal, verify `disable=1` prevents glue enumeration, and test slot-name collisions returning `-EBUSY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_glue.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_glue.c

## Purpose
Implements the ACPI-to-PCI glue for ACPI PCI hotplug. It discovers ACPI hotplug slots under PCI bridges, installs ACPI notification contexts, registers user-visible hotplug slots when appropriate, rescans/removes PCI devices on ACPI events, and manages bridge/slot lifetimes.

## Important APIs, Types, and Functions
Important exported or externally used functions are `acpiphp_enumerate_slots()`, `acpiphp_remove_slots()`, `acpiphp_check_host_bridge()`, `acpiphp_enable_slot()`, `acpiphp_disable_slot()`, and status helpers. Internal core functions include context reference helpers, `free_bridge()`, `acpiphp_add_context()`, `cleanup_bridge()`, `enable_slot()`, `disable_slot()`, `get_slot_status()`, `trim_stale_devices()`, `acpiphp_check_bridge()`, `hotplug_event()`, and `acpiphp_hotplug_notify()`.

## Control Flow
Enumeration starts from a PCI bus ACPI companion, allocates an `acpiphp_bridge`, pins the PCI bus/device, installs a root or bridge hotplug context, adds the bridge to `bridge_list`, and walks one ACPI level to add contexts for function objects with `_ADR`. Each function is grouped into a physical slot by device number; ejectable or dock slots not owned by native hotplug are registered with the hotplug core.

ACPI notifications grab context and bridge refs, take `pci_lock_rescan_remove()`, and handle bus check, device check, or eject request. Bridge checks iterate slots: if the slot is present, stale devices are trimmed and the slot is enabled; otherwise it is disabled. Enabling rescans the slot, scans bridges in two passes, assigns resources, sanitizes devices lacking resources, configures PCIe settings, connects ACPI config-space regions, and adds devices. Disabling removes all PCI functions for the slot and trims ACPI devices, then eject executes `_EJ0` when present.

## State and Persistence
State is kept in `bridge_list`, each bridge's kref/refcounted contexts, slots, function lists, slot flags, and ACPI device hotplug contexts. References pin PCI buses and bridge devices across notifications and module unload. No disk persistence exists.

## Dependencies and Integration Points
Depends on ACPI scan/hotplug context locks, PCI core scanning/removal/resource assignment, runtime PM for bridges, dock support, native hotplug detection, and `acpiphp_core.c` slot registration.

## Risks and Edge Cases
Lifetime is complex: ACPI notifications may race with bridge removal, so `is_going_away`, context locks, krefs, and PCI rescan locks are critical. Native hotplug bridges are mostly left to native drivers, but ACPI still scans non-hotplug bridges below them. Firmware `_STA` can be absent or misleading, so fallback vendor-ID reads are used. Resource assignment failures remove devices during sanitize. Eject is synchronized with `acpi_scan_lock` to avoid ACPI scan races.

## Test Signals
Boot enumeration on root and downstream bridges, ACPI bus/device/eject notifications, dock/undock, native-hotplug coexistence, stale device removal, resource exhaustion leading to sanitize removal, bridge removal during notification, and status reads after `_STA` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ibm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ibm.c

## Purpose
Provides IBM-specific ACPI PCI hotplug extensions. It registers an acpiphp attention LED provider, parses IBM `APCI` ACPI table data, evaluates `APLS` to set LEDs, synthesizes ACPI netlink events, and exposes the raw aPCI table through sysfs.

## Important APIs, Types, and Functions
`union apci_descriptor` models IBM table descriptors. `ibm_slot_from_id()` locates a slot descriptor by hotplug slot user number. `ibm_set_attention_status()` evaluates `APLS`. `ibm_get_attention_status()` derives LED state from table fields. `ibm_handle_events()` combines IBM notification subevents into netlink events. `ibm_get_table_from_acpi()` reads and concatenates `APCI` buffers. `ibm_read_apci_table()` serves `/sys/bus/pci/slots/apci_table`. Init/exit install/remove ACPI notify handler, sysfs file, and attention callbacks.

## Control Flow
Init walks the ACPI namespace looking for present devices with hardware ID `IBM37D0` or `IBM37D4`, fetches its ACPI device, registers attention callbacks with acpiphp, installs an ACPI device notify handler, sizes the APCI table, and creates the sysfs binary attribute. Setting LED state reads the current APCI table, maps Linux slot `_SUN` to IBM slot ID, and evaluates `APLS(slot_id, status)`. Reading the table re-evaluates `APCI`, validates it as a package of buffers, concatenates the buffers, and copies them to userspace only from offset zero.

## State and Persistence
Global state includes the IBM ACPI handle, a notification accumulator, the sysfs bin attribute size, and registered attention callbacks. APCI table contents are read fresh from firmware and not cached beyond temporary allocations.

## Dependencies and Integration Points
Depends on ACPI namespace walking/evaluation/notifications, acpiphp attention registration, PCI slots kset, sysfs binary attributes, and ACPI netlink event generation.

## Risks and Edge Cases
APCI parsing trusts descriptor lengths from firmware while walking a flat buffer; malformed tables can break lookup. The sysfs table read only supports whole-table reads from position zero. Notification synthesis uses a single global `ibm_note`, relying on ACPI serialization assumptions. Attention registration can fail if another provider is active. Init assumes `pci_slots_kset` is ready.

## Test Signals
Load on systems with and without IBM IDs, set/get attention LEDs, read `apci_table`, inject or observe ACPI notifications, test malformed/missing APCI/APLS firmware responses, and unload to confirm sysfs and notify handler cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ibm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug.h

## Purpose
Defines the internal interface and data structures for CompactPCI hotplug support, including PICMG 2.1 hot-swap CSR bits, slot state, controller callbacks, and core/PCI helper APIs.

## Important APIs, Types, and Functions
Defines HS CSR bit masks (`HS_CSR_INS`, `HS_CSR_EXT`, `HS_CSR_LOO`, and related bits), `struct slot`, `struct cpci_hp_controller_ops`, and `struct cpci_hp_controller`. Declares controller/bus lifecycle functions, internal PCI helper functions, and `cpci_hotplug_init()`.

## Control Flow
Board drivers provide a `cpci_hp_controller` with operations for querying or interrupting on ENUM, then register a bus range. The core uses the declared helpers to register hotplug slots, scan slots, manipulate LEDs, and configure/unconfigure PCI devices.

## State and Persistence
The header defines runtime state only. Slots track bus, devfn, cached `pci_dev`, latch/adapter state, extraction state, and hotplug core registration. Controllers track IRQ and operation callbacks.

## Dependencies and Integration Points
Depends on PCI and `pci_hotplug.h`. Shared by CompactPCI core, PCI helper implementation, generic port I/O driver, and other board-specific CompactPCI drivers.

## Risks and Edge Cases
The generic `struct slot` name is shared with ACPI hotplug but isolated by source inclusion. Controller ops are partially optional depending on interrupt versus polling mode; callers must validate required callbacks. Cached `pci_dev` references must be balanced.

## Test Signals
Compile all CPCI configurations, register/unregister controllers and buses, verify HS CSR bit handling, and run insertion/extraction scenarios through both interrupt and polling controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_core.c

## Purpose
Implements the CompactPCI hotplug core. It registers CompactPCI slots with the PCI hotplug core, owns a single platform controller, handles ENUM events via interrupt or polling thread, tracks insertion/extraction state, and delegates PCI configuration to CPCI PCI helper functions.

## Important APIs, Types, and Functions
Exports `cpci_hp_register_controller()`, `cpci_hp_unregister_controller()`, `cpci_hp_register_bus()`, `cpci_hp_unregister_bus()`, `cpci_hp_start()`, `cpci_hp_stop()`, and `cpci_hotplug_init()`. Important internal functions include hotplug slot ops, `init_slots()`, `check_slots()`, `event_thread()`, `poll_thread()`, `cpci_hp_intr()`, `cpci_start_thread()`, and `cleanup_slots()`.

## Control Flow
A board driver registers the controller, registers slots for a bus range, and starts the subsystem. Start initializes cold-inserted slots, starts either an IRQ-driven event thread or polling thread, and enables ENUM interrupts if present. The IRQ handler validates shared IRQ ownership, disables ENUM interrupt, and wakes the thread. The worker calls `check_slots()`, which clears INS bits, configures inserted slots, detects extraction requests, waits for userspace extraction handling, handles improper removals, and re-enables interrupts when stable.

## State and Persistence
Global state includes `slot_list`, `slots`, `extracting`, `controller`, `cpci_thread`, `thread_finished`, and `cpci_debug`. Slot state tracks latch/adapter status, extraction in progress, and a cached `pci_dev` reference. No persistent storage is used.

## Dependencies and Integration Points
Depends on PCI hotplug core, kthreads, IRQ APIs, semaphores, atomic counters, and CPCI PCI helper routines. Board drivers such as `cpcihp_generic` provide controller operations and bus ranges.

## Risks and Edge Cases
Only one controller is supported. IRQ callbacks are required only in interrupt mode; polling uses `query_enum()`. `thread_finished` is a plain int shared with worker lifecycle. Improper removal is detected by HS CSR reads returning `0xffff`. `enable_slot()` hotplug op is a no-op because insertion is handled by ENUM processing. Cleanup must stop the thread before freeing slots/controller IRQs.

## Test Signals
Run controller registration failures, slot registration ranges, cold insertion clearing, insertion and extraction flows, improper removal, shared IRQ filtering, polling mode, stop/unregister while extraction is pending, and sysfs hotplug disable operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_pci.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_pci.c

## Purpose
Provides the PCI configuration-space operations used by the CompactPCI hotplug core. It reads and writes the CompactPCI Hot Swap capability, controls attention LEDs, detects insertion/extraction bits, and configures or removes PCI devices for a CPCI slot.

## Important APIs, Types, and Functions
Exports `cpci_get_attention_status()`, `cpci_set_attention_status()`, `cpci_get_hs_csr()`, `cpci_check_and_clear_ins()`, `cpci_check_ext()`, `cpci_clear_ext()`, `cpci_led_on()`, `cpci_led_off()`, `cpci_configure_slot()`, and `cpci_unconfigure_slot()`.

## Control Flow
HS CSR helpers find `PCI_CAP_ID_CHSWP` on the slot devfn and read/write the capability status/control word. Insert and extract bits are write-one-to-clear where appropriate. Configure locks PCI rescan/removal, finds or scans the slot device, adds bridge children through `pci_hp_add_bridge()`, assigns unassigned bridge resources, and adds devices. Unconfigure locks rescan/removal, removes all functions in the slot, drops the cached slot device reference, and clears `slot->dev`.

## State and Persistence
Persistent runtime state is mostly in the caller's `struct slot`: cached `pci_dev`, adapter/latch status managed by the core, and bus/devfn. Hardware state is the HS CSR in PCI config space.

## Dependencies and Integration Points
Depends on PCI config-space access, PCI hotplug bridge helpers, resource assignment, and global PCI rescan/remove locking. It is called by `cpci_hotplug_core.c` on ENUM events and sysfs disable.

## Risks and Edge Cases
Most HS CSR helpers return success-like zero when the capability is missing or config reads fail, so callers can miss hardware failures. `cpci_configure_slot()` scans all functions only when the cached device is absent. Resource assignment operates at the parent bridge and may affect more than the slot. Cached `pci_dev` refs must be released exactly once on unconfigure/release.

## Test Signals
Test cards with and without Hot Swap capability, INS/EXT bit clear behavior, LED on/off, bridge insertion, resource assignment failures, multifunction slots, unconfigure after surprise removal, and repeated configure/unconfigure cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_generic.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_generic.c

## Purpose
Implements a generic polling CompactPCI hotplug controller driver for x86 systems where the chassis exposes the `#ENUM` signal as a bit in a port-I/O register.

## Important APIs, Types, and Functions
Module parameters are `debug`, `bridge`, `first_slot`, `last_slot`, `port`, and `enum_bit`. `validate_parameters()` parses and validates them. `query_enum()` reads the port and tests the configured bit. `cpcihp_generic_init()` requests the I/O port, finds the bridge and subordinate bus, registers a CPCI controller and bus range, and starts the CPCI core. `cpcihp_generic_exit()` stops and unregisters everything.

## Control Flow
Init validates configuration, reserves one I/O port, resolves the bridge specified as hexadecimal `<bus>:<slot>` in domain 0, uses its subordinate bus as the hotplug bus, provides only `query_enum()` controller ops so the core uses polling mode, registers slots, and starts the CPCI worker. Exit stops polling, unregisters slots and controller, and releases the I/O region.

## State and Persistence
State is global module parameter/configuration state plus the selected subordinate `pci_bus`, generic controller ops, and controller struct. It persists while the module is loaded.

## Dependencies and Integration Points
Depends on x86 port I/O, PCI device lookup, CompactPCI core APIs, module parameters, and the selected bridge's subordinate bus.

## Risks and Edge Cases
No IRQ mode is supported, so detection latency is tied to the CPCI polling interval. Error paths after `request_region()` and bridge lookup can return without releasing the I/O region in some early failures. The driver assumes PCI domain 0 and a valid bridge with a subordinate bus. Parameters are required and parse with legacy `simple_strtoul()`.

## Test Signals
Load with missing/invalid parameters, invalid bridge, busy I/O port, valid bridge and slot range, simulated ENUM bit transitions, module unload after partial init failure, and insertion/extraction behavior through the CPCI polling thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_generic.c -->
