# subset-b-005011

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/irqdomain.c -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/irqdomain.c

## Purpose
Provides the irqdomain-backed PCI MSI/MSI-X integration layer. It decides whether a device should allocate interrupts through a hierarchical MSI irqdomain or the legacy architecture hooks, defines per-device MSI and MSI-X domain templates, and maps PCI requester IDs through OF/IORT firmware data for MSI routing.

## APIs, Types, And Functions
The externally used entry points are `pci_msi_setup_msi_irqs()`, `pci_msi_teardown_msi_irqs()`, `pci_setup_msi_device_domain()`, `pci_setup_msix_device_domain()`, `pci_msi_domain_supports()`, `pci_msi_domain_get_msi_rid()`, `pci_msi_map_rid_ctlr_node()`, `pci_msi_get_device_domain()`, and exported `pci_msix_prepare_desc()`. The file defines MSI and MSI-X `msi_domain_template` instances whose irq chip callbacks mask, unmask, startup, shutdown, and write MSI messages.

## Control Flow
Setup first checks `dev_get_msi_domain()` and uses `msi_domain_alloc_irqs_all_locked()` for hierarchical domains, otherwise falling back to `pci_msi_legacy_setup_msi_irqs()`. Device-domain setup refuses cross-mode creation when MSI-X/MSI is already enabled, reuses a matching per-device domain, removes the opposite-mode domain, and creates a new domain from the relevant template. Runtime IRQ operations mask/unmask the PCI MSI/MSI-X descriptor and conditionally call parent irqchip startup/shutdown or mask/unmask based on parent feature flags. RID mapping walks DMA aliases, chooses a usable alias RID, then applies OF `msi-map` or ACPI IORT translation.

## State And Persistence
State is in kernel memory only: device MSI domains attached to `struct device`, `msi_desc` fields, `msi_domain_info` flags, and firmware-derived fwnodes. Per-device MSI/MSI-X domains persist until device removal or until switching between MSI and MSI-X domain modes.

## Dependencies And Integration
Depends on generic MSI core helpers, irqdomain hierarchy support, `msi.h`, OF IRQ/MSI mapping, and ACPI IORT. It integrates directly with `msi.c` descriptor preparation/message programming and with architecture/irqchip parent domains that advertise `supported_flags` or global `msi_domain_info` flags.

## Risks And Test Signals
Risks include incorrect legacy fallback selection, stale per-device domain replacement when switching MSI modes, parent chip startup/shutdown mismatches, multi-MSI vector bit calculations, and DMA alias/RID translation errors on bridges or IOMMU-backed systems. Test signals include MSI and MSI-X enable/disable on hierarchical and legacy platforms, dynamic MSI-X allocation, OF `msi-map` and ACPI IORT routing, DMA alias devices, suspend/resume restore, and IRQ mask/unmask behavior under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/irqdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/legacy.c -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/legacy.c

## Purpose
Implements the legacy architecture-specific MSI setup and teardown path used when hierarchical MSI irqdomains are unavailable or disabled. It preserves weak arch hooks while adding generic descriptor/sysfs handling around them.

## APIs, Types, And Functions
Weak hooks are `arch_setup_msi_irq()`, `arch_teardown_msi_irq()`, `arch_setup_msi_irqs()`, and `arch_teardown_msi_irqs()`. PCI-facing helpers are `pci_msi_legacy_setup_msi_irqs()` and `pci_msi_legacy_teardown_msi_irqs()`. `pci_msi_setup_check_result()` converts partial MSI-X allocation failures into a positive available-vector count.

## Control Flow
The default `arch_setup_msi_irqs()` refuses multi-MSI for architectures that do not override it, then iterates unassociated descriptors and calls single-vector setup. Teardown iterates associated descriptors and tears down every used vector. The PCI wrapper normalizes partial MSI-X results and populates MSI sysfs entries after successful setup; teardown destroys those sysfs entries before invoking architecture teardown.

## State And Persistence
No persistent storage exists. State is held by MSI descriptors associated with the PCI device and by sysfs entries created by the generic MSI layer. Weak hooks are compile/link-time extension points.

## Dependencies And Integration
Depends on `msi.h`, generic descriptor iteration macros, and architecture-provided MSI setup implementations. `irqdomain.c` calls these helpers when no hierarchical domain is available; `msi.c` depends on them to allocate descriptor IRQ numbers in fallback mode.

## Risks And Test Signals
Risks are mostly compatibility-related: architectures returning positive retry counts, partial MSI-X allocation reporting, descriptor association state, and sysfs cleanup ordering. Test signals include booting on `CONFIG_PCI_MSI_ARCH_FALLBACKS` platforms, single MSI enablement, multi-MSI refusal without arch support, MSI-X partial allocation retry, and module/device removal leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/msi.c

## Purpose
Owns the core PCI MSI/MSI-X lifecycle: support checks, descriptor construction, message programming, masking, enable/disable, restore, shutdown, IRQ vector freeing, TPH tag updates, and global MSI disable. It is the main implementation behind public PCI IRQ vector APIs.

## APIs, Types, And Functions
Exports `pci_msi_mask_irq()`, `pci_msi_unmask_irq()`, `pci_write_msi_msg()`, `pci_msi_vec_count()`, `msi_desc_to_pci_dev()`, and many GPL/common internal entry points declared in `msi.h`: `__pci_enable_msi_range()`, `__pci_enable_msix_range()`, `pci_msi_shutdown()`, `pci_msix_shutdown()`, `pci_free_msi_irqs()`, restore helpers, and `msix_prepare_msi_desc()`. Important helpers include `pci_msi_supported()`, `pci_setup_msi_context()`, `msi_setup_msi_desc()`, `__msi_capability_init()`, `msix_map_region()`, `msix_setup_msi_descs()`, and `msi_verify_entries()`.

## Control Flow
MSI enablement validates global/device/bus support, D0 power state, existing MSI-X state, vector ranges, irqdomain feature support, and available vector count. It installs MSI device data/devres cleanup, creates the device MSI domain, then loops reducing requested vectors when setup reports a smaller supported count. MSI setup builds one descriptor, masks all MSI bits, allocates IRQs, verifies assigned message addresses against the device address mask, disables INTx, enables MSI, frees the legacy INTx IRQ, and replaces `dev->irq`. MSI-X setup enables and masks MSI-X globally, maps the table, creates one descriptor per requested entry, allocates IRQs, updates user entries, masks stale table entries, clears global mask-all, and disables INTx. Restore paths rewrite saved messages and masks after resume; shutdown paths disable MSI/MSI-X, restore INTx, and reallocate legacy IRQs.

## State And Persistence
State lives in `pci_dev` flags (`msi_enabled`, `msix_enabled`, `msix_base`, `msi_cap`, `msix_cap`, `msi_addr_mask`, `is_msi_managed`), `msi_desc` PCI attributes, cached MSI masks/MSI-X vector control, saved `msi_msg`, and global `pci_msi_enable`. There is no disk persistence. Devres cleanup automatically frees vectors for managed PCI devices.

## Dependencies And Integration
Depends on config-space accessors, `irqdomain`, generic MSI core, PCI core IRQ allocation, `ioremap` for MSI-X tables, irq affinity helpers, and arch hooks such as `arch_restore_msi_irqs()`. It integrates with `irqdomain.c` for allocation/teardown and with `pcidev_msi.c` capability discovery performed during enumeration.

## Risks And Test Signals
High-risk areas are ordering of hardware enable bits versus descriptor allocation, masking/unmasking while editing MSI-X table entries, multi-MSI count encoding, partial allocation retry semantics, D0/disconnected-device checks, resource cleanup after failed MSI-X setup, and restore after suspend/kexec. Test signals include MSI/MSI-X vector allocation with affinity, multi-MSI, invalid duplicate MSI-X entries, virtual MSI-X entries, devices with 32-bit MSI address masks, hot unplug, runtime/system suspend-resume, `pci_no_msi`, and fault injection around `ioremap`, descriptor insertion, and IRQ allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/msi.h -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/msi.h

## Purpose
Provides the private PCI MSI/MSI-X declarations and inline helpers shared by MSI implementation files. It centralizes mask/unmask behavior, MSI-X table address computation, vector-control writes, feature probing declarations, and legacy fallback prototypes.

## APIs, Types, And Functions
Defines `msix_table_size()`, `pci_msi_mask()`, `pci_msi_unmask()`, `pci_msix_desc_addr()`, `pci_msix_write_vector_ctrl()`, `pci_msix_mask()`, `pci_msix_unmask()`, `__pci_msi_mask_desc()`, `__pci_msi_unmask_desc()`, and `msi_multi_mask()`. It declares core lifecycle functions such as `__pci_enable_msi_range()`, `__pci_enable_msix_range()`, shutdown/restore/free helpers, `pci_msi_domain_supports()`, and per-device domain setup.

## Control Flow
Inline helpers dispatch on descriptor type: MSI-X uses table vector-control writes and optional read flushes, while MSI uses config-space mask registers through `pci_msi_update_mask()`. `msi_multi_mask()` computes a full mask for all vectors in a multi-MSI descriptor while guarding against oversized shifts.

## State And Persistence
The header manipulates cached descriptor fields: `pci.mask_base`, `pci.msix_ctrl`, `pci.msi_mask`, `pci.msi_attrib`, and `msi_index`. No persistent state is introduced.

## Dependencies And Integration
Included by `msi.c`, `irqdomain.c`, and `legacy.c`. It depends on `linux/pci.h`, `linux/msi.h`, PCI MSI/MSI-X register constants, and `CONFIG_PCI_MSI_ARCH_FALLBACKS` for fallback declarations or warning stubs.

## Risks And Test Signals
Risks include missing write flushes, stale `msix_ctrl` cache, incorrect mask semantics for devices without per-vector masking, and shift overflow in multi-MSI masks. Test signals are MSI/MSI-X mask/unmask stress, vector-control cache validation, devices without mask support, and builds with and without arch fallback support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/pcidev_msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/pcidev_msi.c

## Purpose
Performs unconditional MSI and MSI-X capability discovery during PCI device initialization and disables any firmware-left-enabled MSI/MSI-X state to prevent interrupt storms before drivers take ownership.

## APIs, Types, And Functions
Provides `pci_msi_init()` and `pci_msix_init()`. These set `dev->msi_cap` and `dev->msix_cap` from PCI capability lookup, read capability control registers, clear enable bits if needed, and set a 32-bit MSI address mask for non-64-bit MSI devices.

## Control Flow
Each initializer searches for its capability. If absent, it returns. If present and already enabled, it writes the control register with the enable bit cleared. MSI additionally inspects the 64-bit flag and constrains `dev->msi_addr_mask` for 32-bit-only devices.

## State And Persistence
State is limited to `struct pci_dev` capability offsets and `msi_addr_mask`; hardware control bits are reset in PCI config space. There is no filesystem persistence.

## Dependencies And Integration
Depends on PCI config-space helpers and register constants from `../pci.h`. Enumeration code calls these before drivers request IRQ vectors, and `msi.c` later relies on initialized `msi_cap`, `msix_cap`, and address-mask fields.

## Risks And Test Signals
Risks include firmware leaving MSI/MSI-X enabled, broken devices requiring careful config writes, and wrong address mask setup for 32-bit MSI devices. Test signals include enumeration of devices with MSI already enabled, MSI-X already enabled, no capability, and 32-bit MSI-only capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/pcidev_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/npem.c -->
# sources/distributed-fs/ceph-client/drivers/pci/npem.c

## Purpose
Implements PCIe enclosure/status LED exposure for Native PCIe Enclosure Management and the ACPI `_DSM` PCIe SSD Status LED interface. It maps supported indication bits to Linux LED class devices so users can inspect and toggle enclosure indications.

## APIs, Types, And Functions
Main externally called functions are `pci_npem_create()` and `pci_npem_remove()`. Key types are `struct indication`, `struct npem_led`, `struct npem_ops`, `struct npem`, and `struct dsm_output`. Backend functions include direct NPEM config-space access (`npem_get_active_indications()`, `npem_set_active_indications()`) and ACPI DSM access (`dsm_evaluate()`, `dsm_get_active_indications()`, `dsm_set_active_indications()`).

## Control Flow
Creation prefers ACPI `_DSM` when all required LED functions exist, otherwise it probes the PCI NPEM extended capability and checks capability bits. Initialization filters supported indications, allocates one `npem_led` per supported bit, composes LED names, and registers LED class devices. LED `brightness_get` and `brightness_set` lazily initialize the active indication cache, serialize through a mutex, and either update NPEM control/status registers with command-completion polling or evaluate the `_DSM` set-state function.

## State And Persistence
`dev->npem` owns an allocated `struct npem` with backend ops, cached supported and active indication bitmasks, lazy initialization flag, mutex, capability offset, and flexible LED array. State is runtime-only but mirrors platform LED hardware/firmware state.

## Dependencies And Integration
Depends on PCI config-space access, ACPI DSM evaluation, LED class registration, mutexes, bit operations, and NPEM PCI register definitions. It integrates with PCI device create/remove paths that call `pci_npem_create()` and `pci_npem_remove()`.

## Risks And Test Signals
Risks include backend selection differences, lazy `_DSM` initialization failures before IPMI OpRegions are ready, stale active-indication cache, command-completion timeout, unsupported/reserved bit handling, LED unregister cleanup, and ACPI buffer validation. Test signals include platforms with native NPEM only, DSM-only platforms, partial DSM status code 4 handling, concurrent LED toggles, remove while LEDs are registered, and command timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/npem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/of.c -->
# sources/distributed-fs/ceph-client/drivers/pci/of.c

## Purpose
Provides PCI/Open Firmware integration: mapping PCI devices and buses to device tree nodes, parsing host bridge resources and interrupts, creating dynamic OF nodes for PCI devices/host bridges, and reading PCI-related DT properties.

## APIs, Types, And Functions
Exports `of_pci_find_child_device()`, `of_pci_get_devfn()`, `of_get_pci_domain_nr()`, `of_pci_check_probe_only()`, `of_irq_parse_and_map_pci()`, `of_pci_supply_present()`, `of_pci_get_max_link_speed()`, `of_pci_get_slot_power_limit()`, and `of_pci_get_equalization_presets()`. Other integration functions include `pci_set_of_node()`, `pci_set_bus_of_node()`, `pci_host_bridge_of_msi_domain()`, `devm_of_pci_bridge_init()`, and dynamic node make/remove helpers under `CONFIG_PCI_DYNAMIC_OF_NODES`.

## Control Flow
Device enumeration finds child OF nodes by PCI devfn, including `multifunc-device` containers, and attaches fwnodes to PCI devices/buses. Host bridge init parses `bus-range`, `ranges`, and `dma-ranges`, requests bus resources, remaps I/O windows, and configures IRQ swizzling/mapping. IRQ parsing uses a device node when available, otherwise builds a PCI interrupt spec, swizzles up the bridge chain until an OF node is found, and calls `of_irq_parse_raw()`. Dynamic node creation builds an OF changeset, adds PCI properties through `of_property.c`, applies it, stores the changeset in `np->data`, and attaches the node to the device or bridge.

## State And Persistence
State is in device/bus `of_node` pointers, `of_node_reused`, dynamic OF node flags, applied `of_changeset` objects, parsed resource lists, and host bridge windows. Dynamic nodes persist only in the live kernel device tree and are reverted on remove.

## Dependencies And Integration
Depends on OF core, OF IRQ/address helpers, PCI resource management, platform bus lookup, irqdomain MSI helpers, and `of_property.c` property synthesis. It integrates with host bridge probing, PCI enumeration, IRQ assignment, dynamic OF overlays, and PCI link/slot tuning code.

## Risks And Test Signals
Risks include refcount leaks on OF nodes, mismatched firmware versus Linux bus numbering in interrupt maps, invalid `linux,pci-probe-only` handling, malformed ranges/dma-ranges, dynamic changeset cleanup ordering, and slot power limit rounding. Test signals include DT host bridge enumeration, missing child nodes, interrupt-map swizzling across bridges, dynamic node add/remove, malformed ranges, power-supply property detection, max-link-speed parsing, slot-power-limit boundary values, and equalization preset array errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/of_property.c -->
# sources/distributed-fs/ceph-client/drivers/pci/of_property.c

## Purpose
Synthesizes standard Open Firmware properties for dynamically created PCI device and host bridge nodes. It encodes PCI address cells, ranges, interrupts, compatible strings, and host bridge windows into an `of_changeset`.

## APIs, Types, And Functions
Exports `of_pci_add_properties()` and `of_pci_add_host_bridge_properties()`. Internal types include `struct of_pci_addr_pair` and `struct of_pci_range_entry`. Helpers generate `bus-range`, `ranges`, `reg`, `interrupts`, `interrupt-controller`, `interrupt-map`, `compatible`, and host bridge `ranges` properties.

## Control Flow
For bridges, property generation adds `device_type = "pci"`, bus range, and interrupt-map information for child devices. For endpoints, it adds interrupt-controller metadata when an interrupt pin exists. Common flow then adds ranges, address/size cell counts, config-space `reg`, compatible strings based on vendor/device and class, and interrupt pin data. Host bridge generation emits device type, address/size cells, and translated memory ranges using bridge windows and parent address-cell width.

## State And Persistence
No independent state is stored. The function allocates temporary range arrays and string arrays, adds properties to a caller-owned `of_changeset`, and frees temporary memory. Applied changeset lifetime is managed by the caller in `of.c`.

## Dependencies And Integration
Depends on OF changeset APIs, PCI resource helpers, OF IRQ parsing, PCI swizzling, and resource-window lists. It is used by dynamic OF node creation for PCI devices and host bridges.

## Risks And Test Signals
Risks include incorrect cell counts, endian/width encoding mistakes, bad interrupt-map sizing, failure to free temporary allocations on error, compatible string allocation failures, and host bridge parent address-cell assumptions. Test signals include dynamic bridge and endpoint node creation, bridges with multiple children and INTx pins, empty or I/O-only ranges, 64-bit memory resources, invalid parent `#address-cells`, and changeset rollback after mid-property failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/of_property.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/p2pdma.c -->
# sources/distributed-fs/ceph-client/drivers/pci/p2pdma.c

## Purpose
Implements PCI peer-to-peer DMA memory providers and consumers. It lets drivers expose BAR memory as ZONE_DEVICE pages, allocate/free peer memory, publish providers, choose compatible providers by topology distance, and expose a sysfs mmap allocator.

## APIs, Types, And Functions
Key types are `struct pci_p2pdma`, `struct pci_p2pdma_pagemap`, `struct p2pdma_provider`, and `struct pci_p2pdma_map_state`. Exported APIs include `pcim_p2pdma_init()`, `pcim_p2pdma_provider()`, `pci_p2pdma_add_resource()`, `pci_p2pdma_distance_many()`, `pci_p2pmem_find_many()`, allocation/free and scatterlist helpers, `pci_p2pmem_publish()`, `pci_p2pdma_enable_store()`, and `pci_p2pdma_enable_show()`.

## Control Flow
Provider initialization allocates `struct pci_p2pdma`, initializes an xarray cache, records MMIO BAR bus offsets, and registers devres cleanup. Adding a resource validates BAR/offset/size, creates a gen_pool and sysfs group, maps BAR memory with `devm_memremap_pages()` as `MEMORY_DEVICE_PCI_P2PDMA`, and adds it to the pool with page-map ref ownership. Allocation uses RCU to read `pdev->p2pdma`, allocates from the owner pool, and takes the page-map percpu reference. Topology checks find parent PCI devices, walk upstream bridges to common ancestors, account for ACS redirects, consult CPU support and host bridge whitelist rules, cache map types in an xarray, and return distance or unsupported.

## State And Persistence
State is runtime-only: `pdev->p2pdma` is RCU-protected, `gen_pool` tracks allocations, `p2pmem_published` controls discoverability, `map_types` caches client map decisions, and dev_pagemap/percpu refs guard page lifetime. Sysfs exposes `p2pmem/size`, `available`, `published`, and `allocate`.

## Dependencies And Integration
Depends on DMA mapping internals, `genalloc`, `memremap_pages`, dev_pagemap, percpu refs, xarray, PCI topology/ACS helpers, sysfs binary attributes, and scatterlist APIs. Consumers integrate through PCI P2PDMA public helpers and configfs/sysfs attribute parsers.

## Risks And Test Signals
High-risk areas are RCU lifetime, page refcount initialization for mmap, gen_pool owner refs, sysfs unmap ordering, ACS redirect decisions, stale xarray cached map types, random provider choice ties, and host bridge whitelist correctness. Test signals include adding/removing resources, mmap allocation/unmap, concurrent allocation during provider removal, scatterlist allocation/free, published provider discovery, unsupported non-PCI clients, ACS redirection warnings, cross-host-bridge systems, and fault injection for `memremap_pages`, sysfs creation, and gen_pool failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/p2pdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-acpi.c

## Purpose
Implements PCI/ACPI integration: PCI Firmware Specification DSM support, host bridge resource handling, `_HPX/_HPP` configuration programming, wake and power management, ACPI companion lookup, ACPI-backed MSI domains, and generic ECAM root scanning on ARM64/RISC-V.

## APIs, Types, And Functions
Defines `pci_acpi_dsm_guid` and many PCI core hooks: `pci_acpi_preserve_config()`, `pci_acpi_program_hp_params()`, `pciehp_is_native()`, `shpchp_is_native()`, PM notifier helpers, `acpi_pci_choose_state()`, `pci_set_acpi_fwnode()`, `pci_dev_acpi_reset()`, ACPI power/wakeup helpers, bus add/remove hooks, companion lookup hook registration, `pci_host_bridge_acpi_msi_domain()`, and architecture ECAM functions such as `pci_acpi_scan_root()`. Internal `_HPX` support uses type 0, 1, 2, and 3 record structs.

## Control Flow
Boot initialization honors FADT `NO_MSI` and `NO_ASPM`, then initializes ACPI PCI slots and hotplug. Host bridge setup evaluates DSMs to preserve boot config and optimize reset delays. `_HPX/_HPP` programming walks bridge ACPI scopes, decodes package records, and applies allowed PCI/PCIe register changes. Power helpers translate ACPI sleep states to PCI D-states, coordinate `_REG` config-space availability around D3cold, propagate wake to bridges/root buses, and decide when resume is required. Companion lookup uses an optional registered hook under an rwsem, otherwise searches ACPI children by `_ADR`. ACPI MSI lookup uses a registered fwnode provider callback to find an IRQ domain.

## State And Persistence
State includes host bridge flags (`preserve_config`, `ignore_reset_delay`, native hotplug/AER ownership), PCI device delays and wake flags, ACPI companion pointers, notifier registrations, `pci_acpi_find_companion_hook`, and `pci_msi_get_fwnode_cb`. Firmware methods may change hardware config/power state, but no disk state is written.

## Dependencies And Integration
Depends on ACPI core, PCI hotplug/slot code, PCI ECAM, IOMMU reset coordination, runtime PM, irqdomain/MSI, and PCI resource assignment. It plugs into PCI enumeration, PM callbacks in `pci-driver.c`, MSI domain discovery, host bridge scanning, and platform-specific ARM64/RISC-V root creation.

## Risks And Test Signals
Risks include malformed ACPI packages, over-broad `_HPX` register writes, wake propagation mistakes, D3cold `_REG` ordering, companion lookup races, firmware quirks around bridge D3 and reset delays, MSI disabling via FADT, and ECAM resources not reserved in ACPI namespace. Test signals include ACPI root scan, `_HPX/_HPP` record decoding, DSM preserve-config and delay functions, bridge hotplug wake from D3, `_RST` reset success/failure with IOMMU coordination, companion hook set/clear concurrency, FADT MSI/ASPM disabling, and ARM64/RISC-V ECAM mapping failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.c

## Purpose
Implements an in-memory PCI-to-PCI bridge/root-port configuration-space emulator for host controller drivers whose hardware lacks a real bridge function. It provides default PCI/PCIe register behavior while allowing controller-specific read/write callbacks.

## APIs, Types, And Functions
Exports `pci_bridge_emul_init()`, `pci_bridge_emul_cleanup()`, `pci_bridge_emul_conf_read()`, and `pci_bridge_emul_conf_write()`. Central data is `struct pci_bridge_reg_behavior`, with static behavior tables for base bridge config space and PCIe capability space. `pci_bridge_emul_read_ssid()` implements the subsystem vendor/device capability.

## Control Flow
Initialization fills standard bridge class/header defaults, allocates behavior tables, places optional SSID and PCIe capabilities, links capability pointers, adjusts behavior for PCIe reserved bits, and applies flags disabling prefetch memory or I/O forwarding. Reads select base config, SSID capability, PCIe capability, or extended space, call driver callbacks if provided, fall back to in-memory config, mask reserved bits to zero, and shift/truncate to requested access size. Writes read the old 32-bit value, compute an access mask, apply RW and W1C behavior, update in-memory config, transform W1C bits for callback visibility, then invoke the relevant callback.

## State And Persistence
All emulated state lives in the caller-owned `struct pci_bridge_emul`: base config, PCIe config, capability offsets, subsystem IDs, behavior table copies, callback ops, and private data pointer. No persistent storage exists.

## Dependencies And Integration
Depends on PCI register constants and little-endian config layouts declared in `pci-bridge-emul.h`. Host controller drivers call the read/write functions from their PCI config-space accessors and may implement callbacks to reflect selected writes into hardware.

## Risks And Test Signals
Risks include incorrect RO/RW/W1C masks, capability overlap or bad next pointers, improper partial write shifting, returning nonzero reserved bits, callback mismatch for W1C semantics, and unsupported extended config behavior. Test signals include byte/word/dword config reads/writes, W1C status clearing, PCIe capability reads, SSID capability placement, no-prefmem/no-I/O flags, invalid access sizes, and controller callback observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.h -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.h

## Purpose
Declares the data model and API for the PCI bridge configuration-space emulator. It describes the emulated base bridge header, PCIe capability header, callback operations, feature flags, and read/write entry points.

## APIs, Types, And Functions
Defines `struct pci_bridge_emul_conf`, `struct pci_bridge_emul_pcie_conf`, `pci_bridge_emul_read_status_t`, `struct pci_bridge_emul_ops`, and `struct pci_bridge_emul`. Public functions are `pci_bridge_emul_init()`, `pci_bridge_emul_cleanup()`, `pci_bridge_emul_conf_read()`, and `pci_bridge_emul_conf_write()`. Flags include `PCI_BRIDGE_EMUL_NO_PREFMEM_FORWARD` and `PCI_BRIDGE_EMUL_NO_IO_FORWARD`.

## Control Flow
The header establishes the callback contract: read callbacks may handle a register or let common emulation read from memory; write callbacks receive old, new, and mask values after common behavior filtering. The implementation uses the declared structs as byte-accurate config-space backing storage.

## State And Persistence
`struct pci_bridge_emul` stores emulated config state, behavior-table pointers allocated at init, optional capability locations, subsystem IDs, callback ops, and driver private data. State is caller-owned and memory-only.

## Dependencies And Integration
Depends on kernel types and PCI register layout assumptions. It is consumed by host controller drivers and implemented by `pci-bridge-emul.c`.

## Risks And Test Signals
Risks include structure layout drift from PCI config offsets, wrong callback interpretation, uninitialized capability offsets, and forgetting cleanup for allocated behavior tables. Test signals include compile-time struct size checks, host driver config-space tests, capability layout validation, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-driver.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-driver.c

## Purpose
Implements the PCI bus type and driver binding core. It handles dynamic IDs, device/driver matching, probe/remove/shutdown, NUMA-aware probe execution, runtime/system PM dispatch, DMA/IOMMU setup, uevents, and registration of the PCI bus with the driver core.

## APIs, Types, And Functions
Exports `pci_add_dynid()`, `pci_match_id()`, `__pci_register_driver()`, `pci_unregister_driver()`, `pci_dev_driver()`, `pci_dev_get()`, `pci_dev_put()`, and `pci_bus_type`. Key internals include `struct pci_dynid`, `pci_match_device()`, sysfs `new_id`/`remove_id`, `pci_call_probe()`, `pci_device_probe()`, `pci_device_remove()`, `pci_device_shutdown()`, PCI PM callbacks, `pci_dma_configure()`, and `pci_driver_init()`.

## Control Flow
Driver matching honors binding disallow rules, `driver_override`, dynamic IDs, static ID tables, and `override_only` entries. Probe assigns IRQs, allocates platform IRQ state, takes a device reference, optionally runs probe work on a housekeeping CPU local to the device NUMA node, sets runtime PM state, and records `pci_dev->driver`. Remove runs driver remove with runtime PM barriers, frees IRQs, removes SR-IOV state, unwinds runtime PM, marks D0 state unknown, and drops the reference. PM callbacks route legacy and modern driver callbacks across suspend/resume/hibernate/runtime phases while saving/restoring config state, PTM, PME, bridge power-up actions, and fixups. Bus initialization allocates the probe workqueue and registers `pci_bus_type` and optionally the PCIe port bus.

## State And Persistence
State includes per-driver dynamic ID lists, `pci_dev->driver`, probe flags, runtime PM usage counts, saved PCI config state, current power state, bus type registration, and a global probe workqueue. Sysfs driver attributes mutate dynamic ID state but no disk persistence is used.

## Dependencies And Integration
Depends on the Linux driver core, PCI core helpers, PM core, CPU hotplug/housekeeping masks, IOMMU/DMA APIs, OF/ACPI DMA configuration, SR-IOV, AER/EEH recovery uevents, and PCIe port bus registration. It is the central integration point for all PCI drivers.

## Risks And Test Signals
High-risk areas are dynamic ID parsing and duplicate detection, driver_override matching, probe workqueue CPU selection under hotplug, runtime PM reference balancing, remove ordering versus `runtime_idle`, PM state-save warnings, D3cold bridge resume propagation, DMA default-domain cleanup, and bus registration failure unwind. Test signals include sysfs `new_id/remove_id`, driver override binding, SR-IOV VF autoprobe disabled/enabled, probe failure cleanup, hotplug remove, kexec shutdown bus-master clearing, suspend/resume/hibernate/runtime PM matrices, IOMMU default domain errors, and uevent modalias contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-label.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-label.c

## Purpose
Exposes firmware-provided PCI device labels and indexes through sysfs. ACPI `_DSM` device names are preferred; SMBIOS type 41 onboard-device names are used as a fallback when ACPI naming is unavailable.

## APIs, Types, And Functions
Defines attribute groups `pci_dev_smbios_attr_group` and `pci_dev_acpi_attr_group`. Helpers include `device_has_acpi_name()`, `find_smbios_instance_string()`, `dsm_get_label()`, `dsm_label_utf16s_to_utf8s()`, and sysfs show callbacks for `label`, `index`, and `acpi_index`.

## Control Flow
Visibility callbacks hide SMBIOS attributes when ACPI naming DSM exists and hide ACPI attributes when it does not. SMBIOS lookup scans DMI onboard device records and matches segment, bus, and devfn. ACPI lookup evaluates the PCI device-name DSM, validates a two-element package, emits the integer index, and emits either ASCII string data or UTF-16 buffer data converted to UTF-8.

## State And Persistence
No state is stored. Sysfs output is generated on demand from ACPI and DMI firmware tables.

## Dependencies And Integration
Depends on DMI, ACPI DSM APIs, NLS UTF-16 conversion, sysfs, `pci_acpi_dsm_guid`, and PCI device identity fields. The attribute groups are referenced by PCI device sysfs group definitions elsewhere in the PCI core.

## Risks And Test Signals
Risks include malformed DSM packages, UTF-16 conversion length handling, SMBIOS/ACPI precedence, matching wrong segment/bus/devfn, and visibility inconsistencies when firmware data is incomplete. Test signals include ACPI-label systems, SMBIOS-only systems, no-label systems, UTF-16 buffer labels, invalid DSM return objects, and sysfs attribute visibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-mid.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-mid.c

## Purpose
Provides Intel MID-specific PCI power-management routing. It detects supported Intel Atom MID CPU families and enables alternate PCI power state callbacks backed by Intel MID platform firmware helpers.

## APIs, Types, And Functions
Provides `pci_use_mid_pm()`, `mid_pci_set_power_state()`, and `mid_pci_get_power_state()`. Internal state is `pci_mid_pm_enabled`, initialized by `mid_pci_init()` from the `lpss_cpu_ids` x86 CPU table.

## Control Flow
At `arch_initcall`, the file matches the current CPU against Saltwell MID and Silvermont MID IDs. If matched, it sets the global flag. Later PCI PM code can query `pci_use_mid_pm()` and route set/get power state operations through `intel_mid_pci_set_power_state()` and `intel_mid_pci_get_power_state()`.

## State And Persistence
State is a single read-mostly boolean set at boot. There is no persistence beyond runtime memory.

## Dependencies And Integration
Depends on x86 CPU matching, Intel family IDs, Intel MID platform PM helpers, and PCI PM integration points declared in `pci.h`. It is architecture-specific and only meaningful on supported x86 MID platforms.

## Risks And Test Signals
Risks include CPU ID table drift versus the platform power implementation, enabling MID PM on unsupported systems, and regressions in get/set power-state translation. Test signals include boot on matching and non-matching CPUs, PCI D-state transitions on MID hardware, and build coverage for x86 platform configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-mid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-pf-stub.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-pf-stub.c

## Purpose
Implements a minimal whitelist PCI driver for SR-IOV physical functions that need SR-IOV support but no functional device driver. It claims selected PF devices and delegates SR-IOV configuration to the simple PCI core helper.

## APIs, Types, And Functions
Defines `pci_pf_stub_whitelist`, `pci_pf_stub_probe()`, and `pf_stub_driver`. The driver table currently includes Amazon vendor device `0x0053`, exports a PCI module device table, and uses `pci_sriov_configure_simple` as `.sriov_configure`.

## Control Flow
Module PCI driver registration binds only devices in the whitelist. Probe logs that the device is claimed and returns success. SR-IOV sysfs configuration is handled by the generic simple helper.

## State And Persistence
No private state is allocated. Binding state is maintained by the PCI driver core and SR-IOV state by generic PCI infrastructure.

## Dependencies And Integration
Depends on the PCI module-driver framework and SR-IOV core helper. It integrates with sysfs SR-IOV controls for whitelisted PFs.

## Risks And Test Signals
Risks are limited but include accidental binding to an ID that later needs a real driver, missing IDs, and SR-IOV helper behavior changes. Test signals include module autoload/match table behavior, PF binding, `sriov_numvfs` enable/disable, and unbind/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-pf-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-stub.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pci-stub.c

## Purpose
Implements a generic PCI stub driver used to reserve devices, commonly for VM assignment. It binds only dynamic IDs supplied through module parameters or the PCI driver's `new_id` sysfs interface.

## APIs, Types, And Functions
Defines module parameter `ids`, `pci_stub_probe()`, `stub_driver`, `pci_stub_init()`, and `pci_stub_exit()`. The driver has no static ID table and sets `driver_managed_dma = true`.

## Control Flow
Initialization registers the PCI driver, parses comma-separated `vendor:device[:subvendor[:subdevice[:class[:class_mask]]]]` strings from the `ids` module parameter, validates at least vendor/device fields, and calls `pci_add_dynid()` for each valid entry. Probe only logs a successful claim. Exit unregisters the driver, which frees dynamic IDs through PCI driver-core cleanup.

## State And Persistence
Runtime state is in the PCI driver's dynamic ID list and device binding relationships. The boot/module parameter is init data and is discarded after initialization. There is no persistent storage.

## Dependencies And Integration
Depends on PCI driver registration, dynamic ID support in `pci-driver.c`, module parameter parsing, and sysfs bind/unbind flows. It is often used with VFIO/KVM workflows that require a device to be detached from its normal driver.

## Risks And Test Signals
Risks include malformed ID parsing, dynamic ID addition failures after partial registration, binding devices that should remain managed by real drivers, and DMA/IOMMU expectations due to `driver_managed_dma`. Test signals include module parameter parsing with multiple IDs, sysfs `new_id`/bind/unbind flows, invalid ID warnings, driver unregister cleanup, and VM assignment smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pci-stub.c -->
