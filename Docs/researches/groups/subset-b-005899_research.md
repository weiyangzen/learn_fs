# Research: subset-b-005899

Grouped research for Linux Open Firmware/Devicetree, OMAP legacy platform, overflow/packing, padata, and page metadata headers under `sources/distributed-fs/ceph-client/include/linux`. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of.h -->
# sources/distributed-fs/ceph-client/include/linux/of.h

## Purpose
This is the central Open Firmware / Devicetree API header. It defines the in-memory device-tree object model (`struct device_node`, `struct property`, phandles, iterators, reconfiguration records), root/chosen/alias globals, node/property lookup helpers, property decoding helpers, phandle parsing, dynamic changesets, machine matching, overlays, and config-disabled stubs.

## Important APIs, types, and functions
Key types are `phandle`, `ihandle`, `struct property`, `struct device_node`, `struct of_phandle_args`, `struct of_phandle_iterator`, `struct of_reconfig_data`, `struct of_changeset_entry`, `struct of_changeset`, and overlay notification types. Node APIs include `of_node_init()`, `of_node_get()/of_node_put()`, `of_find_node_by_*()`, `of_get_parent()`, child iterators, CPU node helpers, alias helpers, `of_match_node()`, `of_device_get_match_data()`, and `of_machine_*()` helpers. Property APIs include `of_find_property()`, `of_get_property()`, typed scalar/array readers, string readers, count helpers, `of_property_present()`, and property iterators. Phandle APIs include `__of_parse_phandle_with_args()`, `of_parse_phandle_with_args()`, fixed/optional variants, mapped arguments, count helpers, `of_for_each_phandle()`, and `of_phandle_args_equal()`. Dynamic APIs expose reconfig notifiers, node attach/detach, property add/remove/update, changeset apply/revert/destroy, and helper constructors. Overlay APIs expose FDT apply/remove and overlay notifiers.

## Control flow
With `CONFIG_OF`, callers search or iterate the live tree with reference-returning APIs, decode big-endian property cells, parse phandle lists into node plus argument arrays, and use `_OF_DECLARE()` section entries for early OF init tables. Dynamic updates are collected in an `of_changeset`, applied atomically enough to roll back partial failures, and optionally reverted later. Overlay apply parses an overlay FDT into changesets and notifies subscribers before and after apply/remove. With `CONFIG_OF` or dynamic overlay support disabled, inline stubs return neutral values such as `NULL`, `false`, `-ENOSYS`, `-EINVAL`, or `-ENOTSUPP`.

## State and persistence
The header exposes global tree state (`of_root`, `of_chosen`, `of_aliases`, `of_stdout`) and per-node/per-property runtime state: child/sibling links, dead property lists, flags, kobjects, fwnodes, data pointers, and reference counts. Dynamic nodes/properties are marked with `OF_DYNAMIC`; detached, populated, overlay, and overlay-free states are flag bits. Changesets persist a reversible log of node/property mutations until destroyed. The tree is memory-resident kernel state derived from firmware DTB/PROM and can be changed by overlays or dynamic code.

## Dependencies and integration points
It depends on Linux types, bitops, cleanup/free annotations, kobjects, mod_devicetable, property/fwnode APIs, lists, byteorder, optional SPARC PROM interfaces, NUMA, module autoloading, kexec FDT setup, and notifiers. It is foundational for OF address, IRQ, platform, DMA, IOMMU, clock, graph, reserved-memory, network, PCI, and driver matching layers.

## Risks and test signals
Risks include leaked node references when iterator loops exit early, property length/endian mistakes, phandle argument count mismatches, stale pointers after detach/overlay removal, duplicate aliases, incorrect disabled-config assumptions, and notifier rollback bugs. Test signals include DT-enabled and `!CONFIG_OF` builds, dtc/schema boot tests, phandle parsing with fixed/optional/mapped args, overlay apply/remove/revert, dynamic property update notifiers, CPU/NUMA node lookup, module modalias generation, and reference-leak detection around scoped and non-scoped iterators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_address.h -->
# sources/distributed-fs/ceph-client/include/linux/of_address.h

## Purpose
This header declares Devicetree address translation and resource extraction helpers for `reg`, `ranges`, `dma-ranges`, MMIO mapping, and PCI-style address windows.

## Important APIs, types, and functions
`struct of_pci_range_parser`/`of_range_parser` tracks parser state for range entries. `struct of_pci_range`/`of_range` holds bus, CPU, parent bus, size, and flags. `of_range_count()` reports remaining entries in an initialized parser. Translation APIs include `of_translate_address()`, `of_translate_dma_address()`, and `of_translate_dma_region()`. Resource and mapping helpers include `of_address_to_resource()`, `of_iomap()`, `of_io_request_and_map()`, `__of_get_address()`, `of_get_address()`, `of_get_pci_address()`, `of_property_read_reg()`, `of_pci_address_to_resource()`, `of_pci_range_to_resource()`, `of_range_to_resource()`, `of_address_count()`, and `of_dma_is_coherent()`.

## Control flow
Callers decode a node's address cells through `__of_get_address()` or `of_property_read_reg()`, translate them through parent `ranges` or `dma-ranges`, then convert the result into a Linux `struct resource` or ioremapped pointer. Range users initialize a parser and iterate with `for_each_of_pci_range()` until `of_pci_range_parser_one()` returns `NULL`. Disabled address support leaves translation unavailable, returning `OF_BAD_ADDR`, `NULL`, `IOMEM_ERR_PTR(-EINVAL)`, or negative errno.

## State and persistence
The parser stores iteration cursor state only. No persistent storage is owned here; persistent state is firmware-provided address cells and kernel resource mappings created by downstream callers.

## Dependencies and integration points
It integrates OF node/property decoding with the resource tree, I/O mapping, PCI host bridge windows, DMA configuration, and platform-device population. It depends on `linux/of.h`, `ioport.h`, `io.h`, and `CONFIG_OF_ADDRESS`/`CONFIG_OF`.

## Risks and test signals
Risks include wrong `#address-cells`/`#size-cells`, range parser cursor reuse causing wrong counts, malformed `reg` length, DMA-vs-CPU address confusion, resource flag loss, and leaked requested mappings. Test with nested buses, empty and multiple `ranges`, PCI BAR conversion, `dma-ranges`, non-coherent DMA nodes, `!CONFIG_OF_ADDRESS` builds, and `of_address_count()` on sparse `reg` lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_address.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_clk.h -->
# sources/distributed-fs/ceph-client/include/linux/of_clk.h

## Purpose
This header declares OF helpers for common clock framework initialization and clock parent name/count lookup from Devicetree clock bindings.

## Important APIs, types, and functions
When `CONFIG_COMMON_CLK && CONFIG_OF`, it exports `of_clk_get_parent_count()`, `of_clk_get_parent_name()`, and `of_clk_init()`. Disabled builds provide stubs returning zero, `NULL`, or no-op.

## Control flow
Clock provider initialization passes an OF match table to `of_clk_init()`, which scans DT clock provider nodes and invokes matching init callbacks. Clock consumers or providers inspect `clocks`/`clock-names` style parent relationships through count/name helpers.

## State and persistence
No state is stored in the header. Clock provider registrations and clock tree state live in common clock framework code and persist for device lifetime.

## Dependencies and integration points
It depends on `struct device_node`, `struct of_device_id`, `CONFIG_COMMON_CLK`, and `CONFIG_OF`. It integrates early OF-declared clock providers with CCF and DT clock bindings.

## Risks and test signals
Risks include parent index mismatches, missing clock provider init order, assuming names exist when only phandles exist, and silent no-op behavior without CCF/OF. Test early clock init, provider match order, parent count/name parsing, deferred probe of clock consumers, and disabled-config compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_device.h -->
# sources/distributed-fs/ceph-client/include/linux/of_device.h

## Purpose
This header connects OF node matching with the generic device/driver model, including driver match tables, modalias/uevent generation, DMA configuration, and bus-id creation.

## Important APIs, types, and functions
`of_match_device()` finds a matching `struct of_device_id` for a `struct device`. `of_driver_match_device()` checks a driver's `of_match_table`. `of_device_modalias()`, `of_device_uevent()`, and `of_device_uevent_modalias()` expose OF compatibility data to userspace/module loading. `of_dma_configure_id()` and `of_dma_configure()` configure DMA parameters from an OF node and optional requester ID. `of_device_make_bus_id()` constructs a stable device name.

## Control flow
The driver core invokes match and uevent helpers during binding and hotplug. Device creation or probe configures DMA using the node, `dma-ranges`, coherency, and optional ID before the driver performs DMA. Without `CONFIG_OF`, match/modalias fail or no-op and DMA configuration returns success without applying OF data.

## State and persistence
The header stores no state. It affects device state by selecting a driver match, setting DMA masks/ops/coherency in implementation code, and populating uevent environment variables.

## Dependencies and integration points
It depends on `linux/device/driver.h`, OF match tables, the device model, module autoloading, uevents, and DMA/IOMMU setup paths.

## Risks and test signals
Risks include mismatched compatible tables, modalias truncation, drivers binding without DMA being configured, optional requester ID mistakes with IOMMUs, and relying on OF match in non-OF builds. Test OF driver binding, module autoload modaliases, uevent contents, DMA-coherent and non-coherent devices, IOMMU IDs, and `!CONFIG_OF` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/of_dma.h

## Purpose
This header declares OF integration for the DMAEngine API, allowing DMA controllers and routers to be registered by DT node and allowing clients to request channels by phandle/name.

## Important APIs, types, and functions
`struct of_dma` records a controller/router list entry, OF node, translation callback, optional route allocation callback, router pointer, and controller data. `struct of_dma_filter_info` carries capability masks and filter callbacks. APIs include `of_dma_controller_register()`, `devm_of_dma_controller_register()`, `of_dma_controller_free()`, `of_dma_router_register()`, `of_dma_router_free`, `of_dma_request_slave_channel()`, `of_dma_simple_xlate()`, and `of_dma_xlate_by_chan_id()`.

## Control flow
DMA controller drivers register a node plus translation callback. DMA clients parse their `dmas` property and name, then `of_dma_request_slave_channel()` locates the provider and calls its xlate/router callbacks to return a `struct dma_chan`. The devm wrapper registers the controller and installs cleanup with `devm_add_action_or_reset()`. Disabled `CONFIG_DMA_OF` returns `-ENODEV`, `ERR_PTR(-ENODEV)`, `NULL`, or no translation.

## State and persistence
Persistent runtime state is the registered OF DMA controller/router list and provider-private `of_dma_data`. The header's devm cleanup ties registration lifetime to the device.

## Dependencies and integration points
It depends on `linux/of.h`, DMAEngine, DMA router support, device-managed cleanup, and phandle argument parsing from `of.h`.

## Risks and test signals
Risks include leaking controller registrations, wrong `#dma-cells` interpretation, route allocation lifetime bugs, returning NULL vs ERR_PTR inconsistently, and using the simple xlate for nontrivial hardware. Test controller registration/free, devm cleanup on probe failure, named DMA channel lookup, router allocation/release, invalid phandles, and disabled `CONFIG_DMA_OF` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_fdt.h -->
# sources/distributed-fs/ceph-client/include/linux/of_fdt.h

## Purpose
This header declares flattened Devicetree (FDT) boot-time and unflattening interfaces used before the live `device_node` tree exists.

## Important APIs, types, and functions
It defines `OF_DT_HEADER`, global early DT cell counts (`dt_root_addr_cells`, `dt_root_size_cells`), boot parameter pointers (`initial_boot_params`, physical address, `__dtb_start`, `__dtb_end`), and unflattening via `of_fdt_unflatten_tree()`. Early scan APIs include `of_scan_flat_dt()`, subnode scans, property lookup, address/size helpers, compatibility checks, phandle lookup, chosen/memory/stdout scans, reserved-memory reservation, root scan, verification, node scan, machine-name/match helpers, `unflatten_device_tree()`, `unflatten_and_copy_device_tree()`, `early_init_devtree()`, and `early_get_first_memblock_info()`.

## Control flow
Boot code verifies an FDT blob, scans flat nodes for root/chosen/memory/reserved-memory data, adds memory to architecture/memblock state, picks machine compatibility, and later unflattens the blob into `struct device_node` objects. Arbitrary FDT scans use callback iteration over node offsets. Disabled early-flat-tree support provides small no-op or `-ENODEV` stubs.

## State and persistence
Early global DT pointers and root cell widths persist through boot. Reserved-memory and memblock changes become system memory-management state. After unflattening, state moves into the live OF tree.

## Dependencies and integration points
It depends on init annotations, errno/types, FDT layout, architecture memory setup, memblock/reserved-memory code, and OF live-tree creation.

## Risks and test signals
Risks include invalid FDT headers, wrong physical/virtual pointer handling, cell-width misdecoding, memory range truncation, reserved memory being missed, and boot-order bugs before allocators are ready. Test early boot on DT platforms, malformed FDT rejection, `/chosen` cmdline/stdout parsing, memory node parsing, reserved-memory reservation, built-in DTB ranges, and `!CONFIG_OF_EARLY_FLATTREE` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_fdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_graph.h -->
# sources/distributed-fs/ceph-client/include/linux/of_graph.h

## Purpose
This header declares helpers for parsing OF graph bindings, where devices expose ports and endpoints connected by remote-endpoint phandles.

## Important APIs, types, and functions
`struct of_endpoint` stores parsed port id, endpoint id, and local endpoint node. Iterators include `for_each_endpoint_of_node()`, `for_each_of_graph_port()`, and `for_each_of_graph_port_endpoint()`. APIs include `of_graph_is_present()`, `of_graph_parse_endpoint()`, endpoint/port count helpers, `of_graph_get_port_by_id()`, next endpoint/port helpers, endpoint lookup by regs, remote endpoint/port/parent lookup, and `of_graph_get_remote_node()`.

## Control flow
Drivers inspect whether a graph is present, iterate ports/endpoints, parse each endpoint's `reg` values, and follow `remote-endpoint` links to the peer endpoint, port, or device node. Scoped iterators use cleanup-based `of_node_put()`; non-scoped endpoint iteration requires manual put when leaving early.

## State and persistence
No state is stored here. Returned nodes are references into the live OF tree whose lifetime is controlled by node reference counts.

## Dependencies and integration points
It depends on OF nodes, cleanup annotations, errno, and graph binding conventions. It integrates display, media, audio, and interconnect-style drivers that need DT-described topology.

## Risks and test signals
Risks include leaked node refs on early loop exit, malformed bidirectional graph links, missing `reg` properties, port-vs-ports container ambiguity, and assuming unique endpoint ids. Test graph parsing with single and multi-port devices, broken remote links, scoped iterator cleanup, disabled `CONFIG_OF`, and media/display pipeline probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_graph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/of_iommu.h

## Purpose
This header declares OF helpers for configuring IOMMU mappings and reserved regions for devices described by Devicetree.

## Important APIs, types, and functions
With `CONFIG_OF_IOMMU`, it exports `of_iommu_configure()` and `of_iommu_get_resv_regions()`. Disabled builds return `-ENODEV` or no-op. Forward declarations cover `struct device`, `struct device_node`, and `struct iommu_ops`.

## Control flow
Device setup calls `of_iommu_configure()` with the master node and optional requester ID, allowing OF IOMMU specifiers to attach the device to an IOMMU domain. Later, reserved regions are appended to a list with `of_iommu_get_resv_regions()`.

## State and persistence
The header holds no state. IOMMU domain attachment, device links, and reserved-region lists are maintained by IOMMU core/provider code.

## Dependencies and integration points
It integrates OF phandle specifiers with the IOMMU core, DMA configuration, bus setup, and reserved-memory/identity-mapping policy.

## Risks and test signals
Risks include interpreting requester IDs incorrectly, missing reserved regions, failing open in disabled builds, and probe deferral loops when IOMMU providers are unavailable. Test devices with `iommus` properties, multi-ID masters, reserved region enumeration, DMA configuration interaction, provider deferral, and `!CONFIG_OF_IOMMU` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_irq.h -->
# sources/distributed-fs/ceph-client/include/linux/of_irq.h

## Purpose
This header declares OF interrupt parsing, interrupt-map iteration, irqdomain mapping, MSI domain lookup, and platform IRQ initialization interfaces.

## Important APIs, types, and functions
`of_irq_init_cb_t` names early IRQ controller init callbacks. `struct of_imap_parser` and `struct of_imap_item` support parsing `interrupt-map`. Workaround flags support old 32-bit PowerMac mappings. Core APIs include `of_irq_parse_raw()`, `irq_create_of_mapping()`, `of_irq_to_resource()`, `of_irq_init()`, `of_irq_parse_one()`, `of_irq_count()`, `of_irq_get()`, `of_irq_get_byname()`, `of_irq_get_affinity()`, `of_irq_to_resource_table()`, `of_irq_find_parent()`, interrupt-map parser helpers, OF MSI domain lookup/configuration/xlate, and `irq_of_parse_and_map()`.

## Control flow
Drivers parse an indexed or named interrupt specifier from a device node, find the interrupt parent, translate raw cells through interrupt maps/irqdomains, and create Linux IRQ mappings. Early boot calls `of_irq_init()` over OF-declared interrupt controllers. MSI paths locate a matching MSI irqdomain and configure device MSI state. Disabled `CONFIG_OF_IRQ` stubs return zero, `NULL`, or errno, while SPARC keeps `irq_of_parse_and_map()` declared separately.

## State and persistence
Parser structs hold transient cursor and parent-args state; callers must release `item.parent_args.np` on premature iterator exit. Persistent state is irqdomain mappings, irq resources, MSI configuration, and legacy workaround globals on PowerMac.

## Dependencies and integration points
It depends on OF, `linux/irq.h`, irqdomains, resources, cpumasks, device model, MSI domains, and architecture-specific SPARC/PPC behavior.

## Risks and test signals
Risks include leaked parent node references, incorrect interrupt-cell counts, oldworld PowerMac workaround regressions, MSI token mismatch, missing affinity data, and disabled-stub return values hiding absent IRQs. Test interrupt-map parsing, named/indexed IRQ lookup, IRQ resource tables, MSI domains, SPARC/PPC builds, irqdomain mapping failures, and `!CONFIG_OF_IRQ` compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_mdio.h -->
# sources/distributed-fs/ceph-client/include/linux/of_mdio.h

## Purpose
This header declares OF helpers for registering MDIO buses, discovering PHY/MDIO devices, fixed-link handling, and connecting network devices to PHYs.

## Important APIs, types, and functions
When `CONFIG_OF_MDIO` is enabled, APIs include `of_mdiobus_child_is_phy()`, `__of_mdiobus_register()`, `of_mdiobus_register()`, `__devm_of_mdiobus_register()`, `devm_of_mdiobus_register()`, `of_mdio_find_device()`, `of_phy_find_device()`, `of_phy_connect()`, `of_phy_get_and_connect()`, `of_mdio_find_bus()`, fixed-link register/deregister/test helpers, `of_mdiobus_phy_device_register()`, and `of_mdio_parse_addr()`. The address parser reads `reg`, logs invalid addresses, and enforces `addr < PHY_MAX_ADDR`.

## Control flow
An MDIO controller registers its bus from a DT node, children are classified as PHY or MDIO devices, and network drivers locate/connect PHYs by node or fixed-link description. Devm registration binds bus cleanup to the parent device. Without OF MDIO, bus registration falls back to non-DT `mdiobus_register()`/`devm_mdiobus_register()`, while lookup/connect/fixed-link helpers return unavailable results.

## State and persistence
Bus/PHY/device registrations persist in MDIO and PHY core state. Fixed-link registrations create software PHY state tied to the node. This header itself stores no state.

## Dependencies and integration points
It depends on device, PHY/MDIO, module owner, OF property helpers, net_device, and devm APIs. It integrates Ethernet MAC drivers, MDIO controllers, PHYLIB, and fixed-link DT bindings.

## Risks and test signals
Risks include invalid `reg` addresses, child classification errors, fixed-link leaks, module owner mismatches in wrappers, fallback registration masking missing OF support, and PHY connection lifetime issues. Test MDIO bus registration with mixed child nodes, invalid addresses, fixed-link register/deregister, PHY connect/disconnect, devm cleanup, and `!CONFIG_OF_MDIO` fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_net.h -->
# sources/distributed-fs/ceph-client/include/linux/of_net.h

## Purpose
This header declares OF network-device helpers for PHY interface mode, MAC address discovery, NVMEM MAC fallback, and netdev lookup by node.

## Important APIs, types, and functions
With `CONFIG_OF && CONFIG_NET`, it exports `of_get_phy_mode()`, `of_get_mac_address()`, `of_get_mac_address_nvmem()`, `of_get_ethdev_address()`, and `of_find_net_device_by_node()`. Stubs return `-ENODEV` or `NULL`.

## Control flow
Network drivers read DT properties to choose `phy_interface_t`, obtain a MAC address from standard properties or NVMEM, copy it to a `net_device`, and optionally locate an existing netdev tied to a DT node.

## State and persistence
The header stores no state. MAC addresses copied into `net_device` persist as device configuration; NVMEM state is external.

## Dependencies and integration points
It depends on PHY interface definitions, OF, `struct net_device`, NVMEM-backed address lookup, and network device registration.

## Risks and test signals
Risks include invalid or all-zero MAC handling, PHY mode string mismatch, NVMEM lookup ordering, stale netdev-by-node references, and disabled NET/OF stubs. Test DT MAC property variants, NVMEM MAC cells, PHY mode parsing, netdev lookup ref/lifetime behavior, and non-OF network builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/of_pci.h

## Purpose
This header declares OF helpers for PCI device-node lookup, devfn decoding, OF probe-only policy, and PCI interrupt mapping.

## Important APIs, types, and functions
When OF and PCI are enabled, it exports `of_pci_find_child_device()`, `of_pci_get_devfn()`, and `of_pci_check_probe_only()`. When OF IRQ is enabled, it exports `of_irq_parse_and_map_pci()`. Disabled stubs return `NULL`, `-EINVAL`, no-op, or zero.

## Control flow
PCI host/driver code matches a child node to a PCI `devfn`, decodes DT `reg` into a devfn, honors firmware probe-only policy, and maps PCI slot/pin interrupt swizzles through OF IRQ parsing.

## State and persistence
No state is owned by the header. Probe-only policy and IRQ mappings affect PCI core runtime state.

## Dependencies and integration points
It depends on OF, PCI, OF IRQ, PCI device nodes, and architecture host-bridge code.

## Risks and test signals
Risks include devfn decoding errors, wrong child node association for multifunction devices, probe-only policy regressions, IRQ pin swizzle mistakes, and zero IRQ fallback masking failures. Test PCI DT child lookup, multifunction slots, `reg` parsing, probe-only firmware settings, PCI INTx mapping, and `!CONFIG_PCI`/`!CONFIG_OF_IRQ` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pdt.h -->
# sources/distributed-fs/ceph-client/include/linux/of_pdt.h

## Purpose
This header declares interfaces for building a Linux device tree by querying an Open Firmware PROM through platform-supplied callback operations.

## Important APIs, types, and functions
`struct of_pdt_ops` contains PROM access callbacks: `nextprop`, `getproplen`, `getproperty`, `getchild`, `getsibling`, and `pkg2path`. `prom_early_alloc()` provides early allocation, and `of_pdt_build_devicetree()` builds the in-memory tree from a root phandle plus operations table.

## Control flow
Architecture PROM code supplies callbacks. The builder walks children/siblings, enumerates properties, allocates device nodes/properties early, resolves paths, and constructs the Linux OF tree.

## State and persistence
State created by `of_pdt_build_devicetree()` persists as the live OF tree. The callbacks access firmware PROM state but the header itself stores no state.

## Dependencies and integration points
It depends on phandle definitions from OF headers, early allocation, and architecture PROM implementations, especially legacy Open Firmware systems.

## Risks and test signals
Risks include callback buffer length mistakes, property length mismatch, zero phandle termination errors, early allocation leaks, and incorrect full paths. Test PROM tree builds, empty property lists, long paths, missing children/siblings, and architecture boot on PDT-based OF systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_platform.h -->
# sources/distributed-fs/ceph-client/include/linux/of_platform.h

## Purpose
This header declares OF platform-device creation, population, depopulation, and auxiliary naming/platform-data overrides.

## Important APIs, types, and functions
`struct of_dev_auxdata` maps compatible plus physical address to an override device name and platform data, with `OF_DEV_AUXDATA()` initializer. Device APIs include `of_device_alloc()`, `of_device_add()`, `of_device_register()`, `of_device_unregister()`, and `of_find_device_by_node()`. Population APIs include `of_platform_bus_probe()`, `of_platform_device_create()`, `of_platform_device_destroy()`, `of_platform_populate()`, `of_platform_default_populate()`, `of_platform_depopulate()`, `devm_of_platform_populate()`, and `devm_of_platform_depopulate()`.

## Control flow
Platform or bus code walks DT children, matches bus nodes, creates platform devices, assigns resources and optional auxdata, and marks nodes populated. Depopulate tears child devices back down. Devm variants tie populate/depopulate to device lifetime. Address support disabled makes population/device creation unavailable with `-ENODEV` or `NULL`.

## State and persistence
Created platform devices persist in the device model. OF node flags such as populated/populated bus are managed by implementation code. Auxdata provides non-DT platform data for legacy consumers.

## Dependencies and integration points
It integrates OF nodes with the platform bus, resource/address parsing, driver core, and legacy board conversion paths. It depends on `CONFIG_OF` and `CONFIG_OF_ADDRESS`.

## Risks and test signals
Risks include duplicate device creation, stale populated flags, auxdata overuse or wrong physical address matching, partial populate rollback leaks, and devm depopulate order bugs. Test recursive DT population, default bus matches, auxdata overrides, probe failure cleanup, depopulation on driver remove, and disabled address builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_reserved_mem.h -->
# sources/distributed-fs/ceph-client/include/linux/of_reserved_mem.h

## Purpose
This header declares reserved-memory framework types and OF helpers that bind DT `reserved-memory` regions to devices and convert memory-region entries to resources.

## Important APIs, types, and functions
`struct reserved_mem` records name, ops, base, size, and private data. `struct reserved_mem_ops` supplies node validation/fixup/init and per-device init/release callbacks. `RESERVEDMEM_OF_DECLARE()` places reserved-memory handlers in OF init tables. APIs include `of_reserved_mem_device_init_by_idx()`, `of_reserved_mem_device_init_by_name()`, `of_reserved_mem_device_init()`, `of_reserved_mem_device_release()`, `of_reserved_mem_lookup()`, region-to-resource helpers by index/name, and region count.

## Control flow
Early reserved-memory scanning matches compatible regions to declared ops, validates/fixes/initializes them, and later device setup attaches a referenced memory region by index or name. Device release calls the region's release operation. Disabled `CONFIG_OF_RESERVED_MEM` returns `-ENOSYS`, `NULL`, or no-op while preserving declarations as stubs.

## State and persistence
Reserved regions persist as physical memory excluded from normal allocation or managed by special allocators such as CMA/shared-dma-pool. Device attachment state is maintained by reserved-memory implementation and device-specific ops.

## Dependencies and integration points
It depends on OF declaration macros, device model, resources, and reserved-memory boot scanning. It integrates with DMA mapping, CMA, carveouts, remoteproc, framebuffer, and other devices with `memory-region` bindings.

## Risks and test signals
Risks include wrong region index/name, invalid alignment/base/size fixups, device release omissions, overlapping reserved regions, and disabled-config failures hidden by stubs. Test reserved-memory compatible declarations, named and indexed memory-region references, resource conversion, DMA/CMA attachment, release paths, and malformed/overlapping reserved-memory DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_reserved_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oid_registry.h -->
# sources/distributed-fs/ceph-client/include/linux/oid_registry.h

## Purpose
This header defines the kernel's ASN.1 object identifier registry enum and lookup/parse/format declarations used by certificate, crypto, key, Kerberos, Authenticode, TPM, and security parsers.

## Important APIs, types, and functions
`enum OID` lists recognized OIDs, with comments containing dotted numeric forms consumed by `build_OID_registry.pl`; `OID__NR` is the unknown/sentinel value. APIs are `look_up_OID()`, `parse_OID()`, and `sprint_oid()`.

## Control flow
ASN.1 parsers pass DER OID bytes to `look_up_OID()` or `parse_OID()` to map known encodings to enum values, then switch on the enum to select algorithms or semantic fields. `sprint_oid()` formats an OID for diagnostics.

## State and persistence
The registry is compile-time generated/static data. There is no runtime mutable state. The enum ordering and specially formatted comments are part of the build contract.

## Dependencies and integration points
It depends only on basic Linux types but integrates with generated OID registry data, X.509/PKCS parsers, public-key crypto, keyrings, CIFS/SPNEGO/Kerberos, module signing, IMA, and TPM key parsing.

## Risks and test signals
Risks include editing enum/comment format so the generator fails, enum value drift across generated tables, missing newer algorithm OIDs, DER length validation mistakes in consumers, and unknown OIDs falling through incorrectly. Test the OID generator, certificate parsing for RSA/ECDSA/GOST/SM2/SHA3/ML-DSA, unknown OID handling, formatted OID output, and build-time generated table consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oid_registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/olpc-ec.h -->
# sources/distributed-fs/ceph-client/include/linux/olpc-ec.h

## Purpose
This header declares OLPC XO embedded-controller command constants, SCI source bits, driver callbacks, and EC command/wakeup helpers.

## Important APIs, types, and functions
It defines XO EC command IDs such as firmware revision, SCI mask/query, WLAN reset/wakeup, DCON power, ebook mode, and SCI inhibit commands. SCI source masks cover game keys, battery events, ebook/WLAN, AC power, critical battery, and GP wake. `struct olpc_ec_driver` supplies suspend/resume, `ec_cmd`, and wakeup availability. APIs under `CONFIG_OLPC_EC` include `olpc_ec_driver_register()`, `olpc_ec_cmd()`, wakeup set/clear, SCI mask/query, wakeup availability, and `xo1_do_sleep()`.

## Control flow
Platform EC driver registers callbacks and private data. Subsystems issue EC commands through `olpc_ec_cmd()`, manipulate wakeup masks, query SCI status, and participate in suspend/resume. Disabled EC support makes command return `-ENODEV` and wakeup helpers no-op/false.

## State and persistence
EC hardware stores firmware state, SCI masks, wakeup bits, and sleep behavior. Kernel runtime state is the registered driver and callback argument in implementation code.

## Dependencies and integration points
It depends on bit macros and platform devices. It integrates OLPC laptop platform drivers with power, battery, WLAN, display controller, input/SCI, and suspend paths.

## Risks and test signals
Risks include command buffer length mismatches, SCI mask bit confusion between XO-1 and XO-1.5, sleep-state ABI issues, wakeup mask races, and disabled-config callers not handling `-ENODEV`. Test EC command transactions, firmware revision read, SCI query/mask, WLAN reset/wakeup, suspend/resume, wake source availability, and `!CONFIG_OLPC_EC` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/olpc-ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-dma.h

## Purpose
This header exposes the legacy TI OMAP system DMA interface, register/bit definitions, channel parameter structures, platform data, and compatibility wrappers. It explicitly warns new code to use DMAEngine instead.

## Important APIs, types, and functions
It defines interrupt/status bits, channel control bits, data types, sync modes, port/addressing modes, FIFO/thread fields, sysconfig idle/reset bits, chain modes, priorities, errata bits, controller capability bits, register offsets/types, burst/endian/color/write/channel modes, `struct omap_dma_channel_params`, `struct omap_dma_lch`, `struct omap_dma_dev_attr`, `struct omap_dma_reg`, `SDMA_FILTER_PARAM()`, and `struct omap_system_dma_plat_info`. APIs include `omap_get_plat_info()`, `omap_set_dma_priority()`, `omap_request_dma()`, `omap_free_dma()`, USB-OMAP-gated channel setup/start/stop/position/status helpers, `omap_dma_running()`, and `omap_lcd_dma_running()`.

## Control flow
Legacy clients request a logical channel by device ID and callback, configure transfer/source/destination/sync/channel parameters, start DMA, receive callbacks for enabled IRQ/status bits, poll positions/status if needed, and free the channel. Platform code provides register maps, errata, capability display, clear/read/write callbacks, and DMAEngine slave maps.

## State and persistence
Runtime state is per-channel (`omap_dma_lch`) and controller platform data: channel ownership, callbacks, IRQ masks, saved CSR, chain state, register layout, errata, and hardware registers. Hardware DMA transfer state persists until stopped/reset.

## Dependencies and integration points
It depends on platform devices, OMAP architecture configs, DMAEngine slave maps, USB OMAP, framebuffer OMAP, and SoC-specific DMA controller implementations.

## Risks and test signals
Risks include legacy API use in new drivers, channel leaks, errata bit misconfiguration, register-width/stride mistakes, callback races during free, address mode/index errors, OMAP1 vs OMAP2 feature confusion, and IRQ mask mishandling. Test OMAP1/OMAP2+ compile paths, DMA request/free, transfer parameter programming, source/destination positions, IRQ callbacks, errata-specific behavior, USB/FB gated APIs, and concurrent channel use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-gpmc.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-gpmc.h

## Purpose
This header declares OMAP General Purpose Memory Controller helpers, NAND/OneNAND integration hooks, chip-select programming APIs, and timing calculation interfaces.

## Important APIs, types, and functions
It includes platform GPMC data, defines `GPMC_CONFIG_WP`, legacy IRQ-domain numbers, `struct gpmc_nand_ops`, `struct gpmc_onenand_info`, and forward declarations. APIs include `gpmc_omap_get_nand_ops()`, `gpmc_omap_onenand_set_timings()`, `gpmc_calc_timings()`, `gpmc_cs_write_reg()`, `gpmc_calc_divider()`, `gpmc_cs_set_timings()`, `gpmc_cs_program_settings()`, `gpmc_cs_request()`, `gpmc_cs_free()`, `gpmc_configure()`, and `gpmc_read_settings_dt()`.

## Control flow
Board/device code reads DT settings, calculates timings, requests a chip-select window, programs settings/timings, and uses NAND or OneNAND-specific hooks as needed. Disabled `CONFIG_OMAP_GPMC` stubs return `NULL` or `-EINVAL` for OMAP-specific NAND/OneNAND helpers, while common timing/programming declarations remain external.

## State and persistence
GPMC controller registers, chip-select allocation, timing registers, and NAND/OneNAND mode state persist in hardware/controller implementation. The header stores no state.

## Dependencies and integration points
It depends on OMAP GPMC platform data, DT settings, NAND/OneNAND platform data, device nodes, and memory-controller/register programming code.

## Risks and test signals
Risks include bad timing calculations, chip-select window conflicts, write-protect misconfiguration, legacy IRQ number assumptions, and disabled GPMC stubs in storage drivers. Test NAND/OneNAND probe, DT timing parsing, CS request/free collisions, sync read/write timing, IRQ-domain mapping, and OMAP GPMC disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-gpmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-iommu.h

## Purpose
This header declares OMAP IOMMU context save/restore and domain activation controls for the OMAP virtual address-space management driver.

## Important APIs, types, and functions
With `CONFIG_OMAP_IOMMU`, it exports `omap_iommu_save_ctx()`, `omap_iommu_restore_ctx()`, `omap_iommu_domain_deactivate()`, and `omap_iommu_domain_activate()`. Disabled stubs no-op or return `-ENODEV`.

## Control flow
Power-management paths save and restore IOMMU hardware context around suspend or clock gating. Domain users can deactivate and reactivate an OMAP IOMMU domain around runtime changes.

## State and persistence
Persistent state is IOMMU hardware registers and domain mappings maintained by the OMAP IOMMU implementation. Header stubs intentionally preserve builds when hardware support is absent.

## Dependencies and integration points
It depends on `struct device`, `struct iommu_domain`, OMAP IOMMU driver code, PM flows, and generic IOMMU domain management.

## Risks and test signals
Risks include lost context across suspend, activating domains with stale mappings, callers ignoring `-ENODEV`, and ordering bugs with clocks/resets. Test OMAP IOMMU suspend/resume, domain deactivate/activate cycles, remote processor/media users, and disabled config compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/omap-mailbox.h

## Purpose
This minimal header defines the OMAP mailbox message scalar type and a helper macro to cast arbitrary message data to a 32-bit mailbox word.

## Important APIs, types, and functions
`typedef uintptr_t mbox_msg_t` represents a mailbox message value. `omap_mbox_message(data)` casts through `mbox_msg_t` and truncates to `u32`.

## Control flow
Mailbox clients use the macro when writing a message word to OMAP mailbox hardware or APIs. There are no functions or runtime branches.

## State and persistence
No state is stored. Message persistence is hardware/mailbox-queue dependent outside this header.

## Dependencies and integration points
It integrates legacy OMAP mailbox users with interprocessor communication code. It assumes `uintptr_t`/`u32` are available via included dependencies from callers.

## Risks and test signals
Risks include pointer truncation on 64-bit builds, type visibility if included standalone, and endian/width assumptions for mailbox payloads. Test compile coverage on OMAP mailbox users and message value round trips through hardware/register APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omap-mailbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omapfb.h -->
# sources/distributed-fs/ceph-client/include/linux/omapfb.h

## Purpose
This header declares OMAP framebuffer platform data for LCD panel/controller selection and a board-init helper for setting LCD configuration.

## Important APIs, types, and functions
`struct omap_lcd_config` holds panel name, controller name, reset GPIO, and data line count. `struct omapfb_platform_data` wraps the LCD config. `omapfb_set_lcd_config()` stores early board LCD configuration. It also includes the UAPI OMAP framebuffer header.

## Control flow
Architecture/board setup calls `omapfb_set_lcd_config()` during init, and the OMAP framebuffer driver consumes the platform data to select panel/controller wiring.

## State and persistence
LCD configuration persists as platform data for the framebuffer driver lifetime. The header itself stores no state.

## Dependencies and integration points
It depends on UAPI `linux/omapfb.h`, init annotations, and legacy OMAP framebuffer/platform setup.

## Risks and test signals
Risks include fixed 16-byte name truncation, invalid reset GPIO, incorrect data-line count, and legacy platform data conflicting with DT display descriptions. Test board init, panel/controller name matching, reset GPIO behavior, and OMAP framebuffer probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/omapfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once.h -->
# sources/distributed-fs/ceph-client/include/linux/once.h

## Purpose
This header provides static-key-backed helpers to run a function exactly once from fast paths, with hard-IRQ-safe and sleepable variants.

## Important APIs, types, and functions
Low-level helpers are `__do_once_start()`, `__do_once_done()`, `__do_once_sleepable_start()`, and `__do_once_sleepable_done()`. Public macros are `DO_ONCE()`, `DO_ONCE_SLEEPABLE()`, `get_random_once()`, and `get_random_sleepable_once()`.

## Control flow
Each macro instantiation creates a static done flag and a static true jump label. The first caller that wins `__do_once_*_start()` runs the supplied function, then `__do_once_*_done()` marks done and patches the static branch out of the fast path. Separate macro expansion sites are separate once instances; shared one-time behavior must be wrapped in a common helper.

## State and persistence
State is per-callsite static data in `.data..do_once`: a boolean done flag and static key. Once completed, state persists for module/kernel lifetime and the branch is optimized away.

## Dependencies and integration points
It depends on jump labels/static keys, module ownership, type-safe variadic macro calls, random byte helpers for wrappers, and concurrency primitives in implementation code.

## Risks and test signals
Risks include assuming two callsites share state, running sleepable work from the IRQ-safe variant, deadlocks because hard IRQs are blocked in the generic start path, module unload interactions, and argument side effects only on the winning call. Test concurrent callers, module unload after once completion, static-key patching, sleepable contexts, and random-once wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once_lite.h -->
# sources/distributed-fs/ceph-client/include/linux/once_lite.h

## Purpose
This header provides a lightweight call-once macro family that does not use jump-label patching.

## Important APIs, types, and functions
`DO_ONCE_LITE()` unconditionally performs once-guarded function execution. `DO_ONCE_LITE_IF()` runs the function once only when a condition is true. `__ONCE_LITE_IF()` implements the static boolean guard in `.data..once`.

## Control flow
The condition is evaluated into a local boolean. If true and the per-callsite static flag is not set, the flag is set and the function is invoked. The macro returns whether the input condition was true, not whether the function actually ran.

## State and persistence
State is a per-expansion static `bool __already_done` that persists for kernel/module lifetime. There is no static-key patching and no explicit locking.

## Dependencies and integration points
It depends on basic types and likely/unlikely/compiler section support inherited from broader kernel headers. It is useful in low-overhead paths where jump-label infrastructure is not desired.

## Risks and test signals
Risks include races because the guard is not atomic, misunderstanding the return value, separate state per macro expansion, and side-effect arguments only executing once. Test concurrent calls if used in shared paths, conditional false-then-true behavior, and build coverage for section placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once_lite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oom.h -->
# sources/distributed-fs/ceph-client/include/linux/oom.h

## Purpose
This header declares the out-of-memory killer interface, OOM context data, task OOM-origin helpers, OOM reaper safety checks, notifiers, and global enable/disable controls.

## Important APIs, types, and functions
`enum oom_constraint` identifies cpuset, memory-policy, memcg, or unconstrained OOM contexts. `struct oom_control` carries zonelist, nodemask, memcg, GFP mask, allocation order/sysrq marker, total pages, chosen victim, badness points, and constraint. It exports `oom_lock`, `oom_adj_mutex`, origin helpers, `tsk_is_oom_victim()`, `check_stable_address_space()`, `oom_badness()`, `out_of_memory()`, `exit_oom_victim()`, OOM notifier registration, `oom_killer_disable()/enable()`, and `find_lock_task_mm()`.

## Control flow
Allocation failure builds an `oom_control`, determines constraints, computes victim badness, selects/kills a task, and marks OOM-victim state. Page fault paths call `check_stable_address_space()` before installing mappings if the OOM reaper may have made the mm unstable. Notifiers and disable/enable gates coordinate global OOM behavior.

## State and persistence
Persistent runtime state includes global locks, task signal flags (`oom_flag_origin`, `oom_mm`), mm `MMF_UNSTABLE`, notifier chains, and chosen victim fields during OOM handling. State is in-memory scheduler/mm state, not durable.

## Dependencies and integration points
It depends on scheduler signal state, nodemasks, memcg, mm fault codes, page allocation GFP/order, task/mm locking, and uapi OOM score definitions.

## Risks and test signals
Risks include killing the wrong task due to constraint calculation, OOM reaper races causing data corruption, deadlocks under OOM locks, notifier side effects, and failing to clear victim/origin state. Test global and memcg OOM, cpuset/mempolicy constraints, sysrq-triggered OOM, OOM reaper with concurrent faults, oom_killer_disable timeout, notifier registration, and victim exit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/oom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/openvswitch.h -->
# sources/distributed-fs/ceph-client/include/linux/openvswitch.h

## Purpose
This header is the kernel-private Open vSwitch wrapper that includes the UAPI OVS definitions and adds an internal clone-action attribute constant.

## Important APIs, types, and functions
It includes `<uapi/linux/openvswitch.h>` and defines `OVS_CLONE_ATTR_EXEC` as clone action attribute index 0, representing a u32 flag controlling whether clone actions mutate flow keys.

## Control flow
OVS action parsing/execution code can inspect this attribute while handling clone actions. There are no functions or state transitions in the header.

## State and persistence
No state is stored. The attribute value affects per-packet action execution state in Open vSwitch datapath code.

## Dependencies and integration points
It integrates kernel datapath internals with the OVS netlink UAPI definitions.

## Risks and test signals
Risks include attribute numbering conflicts with UAPI action parsing, inconsistent clone flow-key mutation semantics, and userspace/kernel version assumptions. Test OVS clone actions with and without execute semantics, netlink policy parsing, and datapath compatibility with userspace ovs-vswitchd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/openvswitch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/osq_lock.h -->
# sources/distributed-fs/ceph-client/include/linux/osq_lock.h

## Purpose
This header declares the optimistic spin queue lock used by sleeping locks such as mutexes and rwsems to perform MCS-like optimistic spinning.

## Important APIs, types, and functions
`struct optimistic_spin_queue` contains an atomic encoded tail CPU value. `OSQ_UNLOCKED_VAL` and `OSQ_LOCK_UNLOCKED` initialize the lock. APIs are `osq_lock_init()`, `osq_lock()`, `osq_unlock()`, and `osq_is_locked()`.

## Control flow
Callers initialize the queue, attempt `osq_lock()` while optimistic spinning is allowed, and call `osq_unlock()` to hand off/clear the queue. `osq_is_locked()` reads whether the tail differs from unlocked.

## State and persistence
The only persistent state is `tail`, an atomic queue tail encoding. Per-CPU queue nodes and handoff details live in implementation code.

## Dependencies and integration points
It depends on atomic operations and integrates with mutex/rwsem optimistic spinning and scheduler owner-running heuristics.

## Risks and test signals
Risks include stale CPU encoding, unlock handoff races, spinning when owner cannot run, initialization omissions, and architecture atomic ordering bugs. Test mutex/rwsem contention, preemption/CPU hotplug stress, lockdep/debug builds, and fairness/latency under heavy contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/osq_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/overflow.h -->
# sources/distributed-fs/ceph-client/include/linux/overflow.h

## Purpose
This header centralizes integer overflow, bounds, and allocation-size helpers. It provides type min/max helpers, checked arithmetic, intentional wrapping arithmetic, range checks, safe structure/flexible-array size calculations, and stack flexible-array construction helpers.

## Important APIs, types, and functions
Core helpers include `type_min()`, `type_max()`, `check_add_overflow()`, `check_sub_overflow()`, `check_mul_overflow()`, `check_shl_overflow()`, `wrapping_add/sub/mul()`, `wrapping_assign_add/sub()`, `overflows_type()`, `range_overflows()`, `range_end_overflows()`, typed variants, `castable_to_type()`, `size_mul()`, `size_add()`, `size_sub()`, `array_size()`, `array3_size()`, `flex_array_size()`, `struct_size()`, `struct_size_t()`, `struct_offset()`, `DEFINE_RAW_FLEX()`, `DEFINE_FLEX()`, `STACK_FLEX_ARRAY_SIZE()`, `typeof_flex_counter()`, `overflows_flex_counter_type()`, and `__set_flex_counter()`.

## Control flow
Checked arithmetic delegates to compiler overflow builtins and forces `__must_check` via `__must_check_overflow()`. Wrapping helpers intentionally use overflow builtins to avoid wrap sanitizers. Constant expressions use `__builtin_choose_expr()` paths so compile-time calculations remain constant when possible; runtime paths use checked arithmetic. Size helpers saturate at `SIZE_MAX`, enabling allocator callers to detect impossible sizes. Flexible-array stack helpers build a union with byte storage sized from `struct_size_t()` and optionally initialize `__counted_by` counters.

## State and persistence
No persistent state is stored. The macros affect compile-time diagnostics, generated code, sanitizer behavior, and stack object layout.

## Dependencies and integration points
It depends on compiler helpers, limits, constant-expression detection, array/build-bug helpers, and flexible-array annotations from compiler type support. It integrates broadly with memory allocation, bounds checking, hardened usercopy/FORTIFY patterns, and counted flexible arrays.

## Risks and test signals
Risks include ignoring `__must_check` overflow results, signed/unsigned type surprises, `check_shl_overflow()` with negative or too-large shifts, treating `SIZE_MAX` saturation as a valid allocation size, stack exhaustion from `DEFINE_FLEX()`, and using flexible counter helpers without prior overflow checks. Test compile-time constant folding, signed/unsigned boundary cases, 32-bit and 64-bit builds, UBSAN/integer-wrap sanitizer builds, allocator overflow KUnit tests, flexible-array counted-by cases, and warning enforcement for unchecked results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/overflow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/packing.h -->
# sources/distributed-fs/ceph-client/include/linux/packing.h

## Purpose
This header declares generic bitfield pack/unpack helpers for hardware protocols/register layouts whose bit numbering, byte order, or word ordering differs from native C layout. It also supplies compile-time validation for table-driven field mappings.

## Important APIs, types, and functions
`GEN_PACKED_FIELD_STRUCT()` defines `struct packed_field_u8` and `struct packed_field_u16`. `PACKED_FIELD()` maps a packed bit range to an unpacked structure field. Validation macros include `CHECK_PACKED_FIELD()`, overlap/order checks, size checks, generated `CHECK_PACKED_FIELDS_1..50`, and `CHECK_PACKED_FIELDS()`. Quirks are `QUIRK_MSB_ON_THE_RIGHT`, `QUIRK_LITTLE_ENDIAN`, and `QUIRK_LSW32_IS_FIRST`. APIs include `packing()`, `pack()`, `unpack()`, `pack_fields_u8/u16()`, `unpack_fields_u8/u16()`, and generic `pack_fields()`/`unpack_fields()`.

## Control flow
Single-field callers use `pack()`/`unpack()` or the lower-level `packing()` with an operation enum. Table-driven callers declare packed-field arrays, then `pack_fields()` or `unpack_fields()` first performs compile-time validation of field order, overlap, storage size, and packed-buffer bounds, then dispatches by `_Generic()` to the u8 or u16 implementation.

## State and persistence
The header stores no state. Field mapping arrays are static caller data, and packed buffers are caller-owned hardware/protocol byte arrays.

## Dependencies and integration points
It depends on array size, bitops, build-bug assertions, min/max, offsets, and integer types. It integrates with network switch/PHY/register drivers and any subsystem needing endian/bit-order-quirked serialization.

## Risks and test signals
Risks include incorrect bit numbering, field overlap, unsupported field storage sizes, field arrays larger than 50 without regenerating macros, pbuf length not compile-time constant for generic helpers, quirk misselection, and silent truncation if unpacked field sizes are wrong. Test pack/unpack round trips across all quirks, ascending and descending field tables, compile-time failures for overlap/out-of-range fields, u8/u16 table dispatch, and hardware register golden vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/packing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/padata.h -->
# sources/distributed-fs/ceph-client/include/linux/padata.h

## Purpose
This header declares the padata parallelization framework, which runs work in parallel on selected CPUs and optionally serializes completion in sequence order. It also declares a multithreaded job interface.

## Important APIs, types, and functions
Core structs are `padata_priv` for a job, `padata_list`, `padata_serial_queue`, `padata_cpumask`, `parallel_data`, `padata_shell`, `padata_mt_job`, and `padata_instance`. Flags and CPU-mask types include `PADATA_CPU_SERIAL`, `PADATA_CPU_PARALLEL`, `PADATA_INIT`, `PADATA_RESET`, and `PADATA_INVALID`. APIs under `CONFIG_PADATA` include `padata_init()`, `padata_alloc()/free()`, shell alloc/free, `padata_do_parallel()`, `padata_do_serial()`, `padata_do_multithreaded()`, and `padata_set_cpumask()`.

## Control flow
Clients allocate an instance and shell, initialize `padata_priv` with parallel and serial callbacks, and submit through `padata_do_parallel()`. The framework assigns sequence numbers and parallel CPUs, then serializes completion on callback CPUs through reorder and serial queues before `padata_do_serial()`. Cpumasks can be changed by replacing `parallel_data` under RCU. Multithreaded jobs split a range into chunks, optionally NUMA-aware. Without `CONFIG_PADATA`, only `padata_do_multithreaded()` remains as a direct single-threaded call over the entire range.

## State and persistence
Persistent runtime state includes workqueues, per-CPU reorder/serial queues, cpumasks, sequence counters, processed counters, shell RCU pointers, kobject state, hotplug node, mutex, flags, and refcounts.

## Dependencies and integration points
It depends on refcounting, compiler/RCU annotations, workqueues, spinlocks, lists, kobjects, cpumasks, CPU hotplug, and module init. It is used by parallel crypto/IPsec and other bulk processing paths.

## Risks and test signals
Risks include sequence reorder deadlocks, cpumask replacement races, refcount leaks, CPU hotplug interactions, callback CPU invalidation, workqueue teardown ordering, and disabled-config changing parallelism semantics. Test ordered completion under out-of-order parallel work, cpumask changes while jobs run, CPU hotplug, padata instance free with in-flight jobs, multithreaded chunk alignment/min sizes, and `!CONFIG_PADATA` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/padata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags-layout.h -->
# sources/distributed-fs/ceph-client/include/linux/page-flags-layout.h

## Purpose
This header computes how non-flag fields are packed into `page->flags`: zone, sparsemem section, NUMA node, KASAN tag, last CPU/PID, LRU generation, and LRU refs.

## Important APIs, types, and functions
It defines `ZONES_SHIFT`, `ZONES_WIDTH`, `SECTIONS_SHIFT`, `SECTIONS_WIDTH`, `NODES_WIDTH`, optional `NODE_NOT_IN_PAGE_FLAGS`, `KASAN_TAG_WIDTH`, `LAST__PID_SHIFT/MASK`, `LAST__CPU_SHIFT/MASK`, `LAST_CPUPID_SHIFT/WIDTH`, optional `LAST_CPUPID_NOT_IN_PAGE_FLAGS`, `LRU_REFS_WIDTH`, `NR_NON_PAGEFLAG_BITS`, and `NR_UNUSED_PAGEFLAG_BITS`.

## Control flow
All logic is compile-time preprocessor selection. It chooses bit widths based on configured zones, sparsemem mode, vmemmap mode, NUMA bits, KASAN tagging, NUMA balancing, LRU generation widths, and available bits after `NR_PAGEFLAGS`. It emits build errors when configured fields cannot fit.

## State and persistence
No runtime state is stored. The computed layout is persistent ABI between memory-management code, generated bounds, and architecture assumptions for the kernel build.

## Dependencies and integration points
It depends on NUMA settings, generated bounds, sparsemem architecture constants, KASAN configs, NUMA balancing, LRU generation constants, and `BITS_PER_LONG`. It integrates with `page-flags.h`, page allocator, memory hotplug, vmscan, and page/folio metadata accessors.

## Risks and test signals
Risks include insufficient flag bits on unusual 32-bit/NUMA/sparsemem configs, node or last-cpupid falling out of flags and requiring alternate lookup, KASAN tag width pressure, and VDSO/bounds generation constraints. Test allyesconfig-like MM configs, 32-bit sparsemem, NUMA balancing, KASAN SW/HW tags, LRU generation, generated bounds, and compile-time error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags-layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags.h -->
# sources/distributed-fs/ceph-client/include/linux/page-flags.h

## Purpose
This is the central page/folio flag API. It defines page flag bits, compound-page head/tail handling, folio conversion, flag policy macros, generated-style Page/Folio accessors, mapping flag encodings, page type encodings, and allocator sanity masks.

## Important APIs, types, and functions
`enum pageflags` defines core bits such as locked, writeback, referenced, uptodate, dirty, lru, head, waiters, active, workingset, owner/private bits, reserved, reclaim, swapbacked, unevictable, dropbehind, mlocked, hwpoison, young/idle, and arch bits, plus aliases for readahead, swapcache, checked, anon-exclusive, mappedtodisk, fscache/Xen/migration/reported/hotplug/compound-second-page uses. Core helpers include `_compound_head()`, `compound_head()`, `set_compound_head()`, `clear_compound_head()`, `page_folio()`, `folio_page()`, `PageTail()`, `PageCompound()`, `PagePoisoned()`, `const_folio_flags()`, `folio_flags()`, many `Page*`/`folio_*` accessors, `folio_test_uptodate()`/mark helpers with barriers, writeback start declarations, folio large/head helpers, page type ops (`PageBuddy`, `PageOffline`, `PageTable`, `PageGuard`, `PageSlab`, `PageZsmalloc`, `PageUnaccepted`, `PageLargeKmalloc`, `PageNetpp`), `PageHuge()`, hwpoison checks, movable-ops flags, anon-exclusive helpers, `folio_has_private()`, and check masks.

## Control flow
Flag accessors route operations to the correct physical `struct page`: any page, head page, no-tail, no-compound, or first tail page for compound-only flags. Compound-head lookup reads `compound_info`, either as a direct head pointer with bit 0 as tail marker or as a mask when HugeTLB vmemmap optimization allows. Uptodate setting uses a write barrier before setting the bit; testing uses a read barrier after observing the bit. Page type helpers encode special non-mapcount page states in the high byte of `page_type`, with debug checks when setting/clearing.

## State and persistence
Persistent runtime state is in `struct page`: `flags`, `compound_info`, `mapping`, `page_type`, and related folio fields. Flags track page cache, writeback, LRU, reclaim, swap, memory failure, migration, allocator, compound, and owner-specific state across page lifetime. Allocator masks define what must be clear at free/prep while preserving exceptional hwpoison state.

## Dependencies and integration points
It depends on mm types, generated bounds, bitops/bug/mmdebug, memory barriers, page allocator, file cache, reclaim, swap, highmem, KSM, THP/HugeTLB, memory failure, migration, Xen, page idle, memory hotplug, slab, zsmalloc, page pool, and architecture-specific page bits.

## Risks and test signals
Risks include operating on tail pages with the wrong policy, missing memory barriers around uptodate data visibility, alias-bit confusion across subsystems, corrupting `page_type` mapcount/type encoding, stale compound head during split races, allocator free/prep flag leaks, and improper use of owner-private flags. Test page allocator debug checks, folio split/merge, THP/HugeTLB, writeback and page-cache uptodate ordering, KSM/anon mapping flags, swapcache, memory failure/hwpoison, migration movable-ops, highmem, page idle, and 32-bit/64-bit config variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-isolation.h -->
# sources/distributed-fs/ceph-client/include/linux/page-isolation.h

## Purpose
This header declares pageblock isolation helpers used by memory hotplug/offline, CMA, compaction, and other page-range isolation workflows.

## Important APIs, types, and functions
With `CONFIG_MEMORY_ISOLATION`, inline helpers test/set/clear the `PB_migrate_isolate` pageblock bit and compare migratetypes. Disabled stubs return false/no-op. `enum pb_isolate_mode` distinguishes memory offlining, CMA allocation, and other isolation. External APIs include `init_pageblock_migratetype()`, `pageblock_isolate_and_move_free_pages()`, `pageblock_unisolate_and_move_free_pages()`, `start_isolate_page_range()`, `undo_isolate_page_range()`, `test_pages_isolated()`, and `page_is_unmovable()`.

## Control flow
Callers mark pageblocks isolate, move free pages out of normal free lists, scan for unmovable pages according to isolation mode, and either complete isolation or undo it. Memory-offline mode treats poison/offline pages specially; CMA mode has different reporting expectations.

## State and persistence
State persists in pageblock migratetype and isolation bits. Isolated ranges remain unavailable to normal allocation until unisolated.

## Dependencies and integration points
It depends on pageblock flags, migratetypes, zones, PFN/page conversion, memory isolation config, memory hotplug, CMA, compaction, and page allocator free lists.

## Risks and test signals
Risks include leaving pageblocks isolated after failure, misclassifying unmovable pages, races with allocator/compaction, CMA starvation, and disabled isolation stubs hiding unsupported workflows. Test memory hotplug offline/online, CMA allocation isolation, compaction with isolate bits, poisoned/offline pages, rollback paths, and `!CONFIG_MEMORY_ISOLATION` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-isolation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_counter.h -->
# sources/distributed-fs/ceph-client/include/linux/page_counter.h

## Purpose
This header declares hierarchical page counters used by memory cgroups and device memory cgroups to track usage, limits, watermarks, and memory protection.

## Important APIs, types, and functions
`struct page_counter` contains hot `usage`, v1 `failcnt`, effective min/low and usage accounting fields, watermarks, protection support flags, limit fields (`min`, `low`, `high`, `max`), and parent pointer. Helpers include `page_counter_init()`, `page_counter_read()`, `page_counter_cancel()`, `page_counter_charge()`, `page_counter_try_charge()`, `page_counter_uncharge()`, min/low/high/max setters, `page_counter_memparse()`, `page_counter_reset_watermark()`, and `page_counter_calculate_protection()`.

## Control flow
Counters are initialized with parent linkage and max default. Charging walks/updates hierarchy and can fail with a pointer to the failing counter. Uncharge/cancel reverse charges. Limit setters update thresholds; protection calculation propagates effective min/low values from root to children. Watermark reset snapshots current usage.

## State and persistence
Persistent state includes atomic usage, fail counts, protection accounting, high/max/min/low limits, watermarks, and parent hierarchy. Cacheline padding isolates hot usage from colder fields.

## Dependencies and integration points
It depends on atomics, cacheline layout, page size, memcg/cgroup dmem configs, and memory control group reclaim/OOM logic.

## Risks and test signals
Risks include hierarchical charge leaks, limit races, watermark ordering, failcnt tracking differences between cgroup v1/v2, protection miscalculation, 32-bit maximum differences, and false sharing regressions. Test memcg charge/uncharge under hierarchy, max/high/min/low changes, watermark reset, recursive protection, memparse inputs, 32-bit builds, and concurrent charge stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ext.h -->
# sources/distributed-fs/ceph-client/include/linux/page_ext.h

## Purpose
This header declares optional per-page extension storage used by page owner, page idle, page table check, and other clients needing metadata outside `struct page`.

## Important APIs, types, and functions
With `CONFIG_PAGE_EXTENSION`, `struct page_ext_operations` describes each client's offset, size, need/init callbacks, and shared flag usage. `enum page_ext_flags` defines shared flags such as owner allocated and optional young/idle bits. `struct page_ext` contains shared flags. Globals and APIs include `early_page_ext`, `page_ext_size`, `pgdat_page_ext_init()`, `early_page_ext_enabled()`, init functions for sparse/flatmem, `page_ext_get()`, `page_ext_from_phys()`, `page_ext_put()`, `page_ext_lookup()`, `page_ext_data()`, `page_ext_next()`, iterator struct and helpers, and `for_each_page_ext()`. Disabled stubs return `NULL`/false or no-op.

## Control flow
Boot or memory hotplug allocates page_ext arrays when any client needs them. Clients locate a page's extension by page, PFN, or physical address, access their private area by registered offset, and put references if required. Iteration must run under RCU read lock and can fast-step within a memory section or relookup at section boundaries.

## State and persistence
Page extension arrays persist per page descriptor after allocation. Shared flags and client data persist for page lifetime or until memory hotplug teardown. `early_page_ext` indicates early allocation mode.

## Dependencies and integration points
It depends on mmzone, stacktrace, sparsemem section layout, RCU locking discipline, memory hotplug, page owner, page idle, page table check, and page allocator initialization.

## Risks and test signals
Risks include missing RCU read lock during iteration, stale extension pointers across memory sections/hotplug, offset/size overlap between clients, shared flag collisions, and assuming page_ext exists when disabled or not needed. Test page owner/page idle/page table check configs, sparsemem and flatmem, memory hotplug add/remove, physical lookup, RCU iterator range scans, and disabled `CONFIG_PAGE_EXTENSION` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_frag_cache.h -->
# sources/distributed-fs/ceph-client/include/linux/page_frag_cache.h

## Purpose
This header declares the page fragment cache API used to allocate small aligned fragments from cached pages, commonly for networking buffers.

## Important APIs, types, and functions
It defines `PAGE_FRAG_CACHE_ORDER_MASK` depending on maximum fragment cache size, `PAGE_FRAG_CACHE_PFMEMALLOC_BIT`, `encoded_page_decode_pfmemalloc()`, `page_frag_cache_init()`, `page_frag_cache_is_pfmemalloc()`, `page_frag_cache_drain()`, `__page_frag_cache_drain()`, `__page_frag_alloc_align()`, `page_frag_alloc_align()`, `page_frag_alloc()`, and `page_frag_free()`.

## Control flow
Callers initialize a cache, allocate fragments with size/GFP/alignment, and eventually drain/free. Alignment wrapper checks power-of-two alignment and passes an encoded mask. The encoded page value carries page order and pfmemalloc metadata.

## State and persistence
State persists in `struct page_frag_cache` (not defined here) through its `encoded_page` and offset/count fields in mm task types. Cached pages persist until drained or exhausted.

## Dependencies and integration points
It depends on bits/log2, mm task page-frag cache types, GFP allocation, page allocator, pfmemalloc semantics, and networking memory allocation paths.

## Risks and test signals
Risks include alignment mask misuse, pfmemalloc propagation errors, cache drain leaks, fragment size exceeding cache order, and high-order page assumptions when `PAGE_SIZE` differs from max cache size. Test network RX/TX allocations, pfmemalloc sockets, alignment-sensitive users, cache drain on teardown, high-order and base-page configs, and WARN on non-power-of-two alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_frag_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_idle.h -->
# sources/distributed-fs/ceph-client/include/linux/page_idle.h

## Purpose
This header provides folio young/idle flag operations for configurations where page idle bits do not fit in `page->flags` and are stored in page extensions.

## Important APIs, types, and functions
Under `CONFIG_PAGE_IDLE_FLAG && !CONFIG_64BIT`, it defines `folio_test_young()`, `folio_set_young()`, `folio_test_clear_young()`, `folio_test_idle()`, `folio_set_idle()`, and `folio_clear_idle()` using `PAGE_EXT_YOUNG` and `PAGE_EXT_IDLE`.

## Control flow
Each helper obtains the folio's `page_ext`, tests/sets/clears the relevant bit, and puts the extension. Missing page_ext returns false or no-op. On 64-bit or disabled page-idle configs, these helpers are supplied by `page-flags.h` or become false/no-op there.

## State and persistence
Young/idle state persists in page_ext flags for affected 32-bit configurations. No separate header state exists.

## Dependencies and integration points
It depends on bitops, page flags, page_ext, page idle tracking, memory reclaim/idle page tracking, and architectures with limited page flag bits.

## Risks and test signals
Risks include page_ext absence causing lost idle/young state, missing puts, races with reclaim/page-idle scanners, and config-specific API differences. Test 32-bit `CONFIG_PAGE_IDLE_FLAG`, idle page tracking sysfs/proc interfaces, reclaim young clearing, page_ext allocation, and 64-bit compile paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_owner.h -->
# sources/distributed-fs/ceph-client/include/linux/page_owner.h

## Purpose
This header declares page-owner tracking hooks that record allocation stack/metadata for debugging page leaks and fragmentation.

## Important APIs, types, and functions
With `CONFIG_PAGE_OWNER`, it exports `page_owner_inited`, `page_owner_ops`, and implementation hooks for reset, set, split, folio owner copy, migration reason, dump, and pagetype mixed-count printing. Inline wrappers `reset_page_owner()`, `set_page_owner()`, `split_page_owner()`, `folio_copy_owner()`, `folio_set_owner_migrate_reason()`, and `dump_page_owner()` call implementations only when the static key is enabled. Disabled builds provide no-ops.

## Control flow
Page allocation calls set-owner when page owner is initialized. Free/reset clears owner data. Folio split/copy/migration updates metadata. Dump paths print owner info for diagnostics. Static key gating keeps disabled overhead low.

## State and persistence
Page-owner data persists in page_ext client storage while pages are allocated or tracked. Static key state records whether page-owner tracking is initialized.

## Dependencies and integration points
It depends on jump labels/static keys, page_ext operations, allocation/free paths, folio split/migration, seq_file pagetype reporting, and debugfs/page_owner users.

## Risks and test signals
Risks include missing hooks causing stale owner data, static key not enabled when expected, page_ext offset bugs, split/copy owner inconsistencies, and high overhead when enabled. Test `CONFIG_PAGE_OWNER`, debugfs page_owner output, allocation/free/split/migration paths, mixed pagetype reporting, and disabled no-op compile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_owner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ref.h -->
# sources/distributed-fs/ceph-client/include/linux/page_ref.h

## Purpose
This header provides atomic page/folio reference-count operations with optional debug tracepoint instrumentation and freeze/unfreeze support for migration/splitting.

## Important APIs, types, and functions
It declares page-ref tracepoints and, under `CONFIG_DEBUG_PAGE_REF`, instrumentation hooks. Public helpers include `page_ref_count()`, `folio_ref_count()`, `page_count()`, `set_page_count()`, `folio_set_count()`, `init_page_count()`, add/sub/inc/dec variants, return/test variants, `page_ref_add_unless_zero()`, folio equivalents, `folio_try_get()`, `folio_ref_try_add()`, `page_ref_freeze()`, `folio_ref_freeze()`, `page_ref_unfreeze()`, and `folio_ref_unfreeze()`.

## Control flow
All ref changes update `page->_refcount` atomically and optionally emit debug tracepoint callbacks when enabled. Try-get adds only when refcount is not zero. Freeze atomically changes an expected count to zero, blocking new speculative gets; unfreeze asserts count is zero, validates a nonzero target count, and publishes it with release ordering.

## State and persistence
Persistent state is the atomic `_refcount` in `struct page`/folio. Debug tracepoint enablement and trace records are external instrumentation state.

## Dependencies and integration points
It depends on atomics, mm types, page flags, tracepoint definitions, VM debug assertions, folio/page lifecycle, page cache, GUP, migration, split, allocator, and memory-management tracing.

## Risks and test signals
Risks include refcount underflow/overflow, freezing with wrong expected count, unfreezing to zero, missing trace events in debug mode, speculative get races after free, and incorrect folio-vs-page usage. Test page allocation/free refcounts, GUP/pagecache pins, migration/split freeze paths, debug tracepoints, VM_BUG_ON assertions, concurrent put/get stress, and `CONFIG_DEBUG_PAGE_REF` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_reporting.h -->
# sources/distributed-fs/ceph-client/include/linux/page_reporting.h

## Purpose
This header declares the free-page reporting device interface, used to report unused guest/system pages to a backing device or hypervisor.

## Important APIs, types, and functions
It defines `PAGE_REPORTING_CAPACITY`, `PAGE_REPORTING_ORDER_UNSPECIFIED`, and `struct page_reporting_dev_info`, which contains a `report()` callback, delayed work item, atomic state, and minimum reporting order. APIs are `page_reporting_register()` and `page_reporting_unregister()`.

## Control flow
A reporting device registers callbacks. Background delayed work gathers free pages into scatterlists and calls `report()`. Unregister tears down reporting work and device state.

## State and persistence
Persistent runtime state is the registered device info, delayed work, atomic reporting state, and selected reporting order. Reported page state is tracked by allocator/page flags outside this header.

## Dependencies and integration points
It depends on mmzone, scatterlists, delayed work, page allocator free lists, virtio-balloon or similar reporting devices, and `PG_reported` page flags.

## Risks and test signals
Risks include unregister races with delayed work, reporting pages that are reallocated, wrong order/capacity assumptions, scatterlist callback failures, and state-machine stalls. Test register/unregister under load, free page reporting cycles, callback error handling, page allocation races, order selection, and virt/hypervisor integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_reporting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_table_check.h -->
# sources/distributed-fs/ceph-client/include/linux/page_table_check.h

## Purpose
This header declares page table check instrumentation that validates page-table mappings and page allocation/free transitions to catch illegal aliasing or mapping state.

## Important APIs, types, and functions
With `CONFIG_PAGE_TABLE_CHECK`, it exports `page_table_check_disabled`, `page_table_check_ops`, implementation hooks for zeroing page metadata, clearing PTE/PMD/PUD mappings, setting batches of PTEs/PMDs/PUDs, and clearing PTE ranges. Inline wrappers are `page_table_check_alloc()`, `page_table_check_free()`, `page_table_check_pte_clear()`, `page_table_check_pmd_clear()`, `page_table_check_pud_clear()`, `page_table_check_ptes_set()`, `page_table_check_pmds_set()`, `page_table_check_puds_set()`, and `page_table_check_pte_clear_range()`. Convenience macros handle single PMD/PUD set.

## Control flow
Allocation/free and page-table manipulation paths call wrappers. If the static key says checks are disabled, wrappers return immediately; otherwise they call the validating implementation. Disabled `CONFIG_PAGE_TABLE_CHECK` compiles every wrapper to no-op.

## State and persistence
Check metadata persists in page_ext client storage. Static key state controls runtime enable/disable. No state is stored in the header itself.

## Dependencies and integration points
It depends on page_ext, jump labels, mm/page table types (`pte_t`, `pmd_t`, `pud_t`), allocation/free paths, and architecture page table update hooks.

## Risks and test signals
Risks include missing architecture hook coverage, false positives from legitimate aliasing, static key polarity misunderstandings, stale page_ext metadata after free, and batching count mistakes. Test `CONFIG_PAGE_TABLE_CHECK`, mapping/unmapping PTE/PMD/PUD ranges, huge mappings, fork/munmap/mremap, allocation/free zeroing, disabled runtime path, and architecture-specific page table helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_table_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pageblock-flags.h -->
# sources/distributed-fs/ceph-client/include/linux/pageblock-flags.h

## Purpose
This header defines pageblock-level flags and helpers used by the buddy allocator, compaction, migratetype selection, hugepage grouping, and memory isolation.

## Important APIs, types, and functions
`enum pageblock_bits` defines migratetype bits, compact-skip, and optional isolate bit. It defines `NR_PAGEBLOCK_BITS`, `MIGRATETYPE_MASK`, `MIGRATETYPE_AND_ISO_MASK`, `pageblock_order`, `pageblock_nr_pages`, alignment helpers, and external helpers `get_pfnblock_migratetype()`, `get_pfnblock_bit()`, `set_pfnblock_bit()`, and `clear_pfnblock_bit()`. Under `CONFIG_COMPACTION`, `get_pageblock_skip()`, `set_pageblock_skip()`, and `clear_pageblock_skip()` manipulate `PB_compact_skip`; otherwise they are no-op/false.

## Control flow
Allocator and compaction code classify PFN blocks by migratetype bits, align PFN ranges to pageblock boundaries, mark blocks skipped by compaction, and optionally isolate blocks for memory isolation. `pageblock_order` is chosen from hugetlb variable/fixed size, THP PMD order, or maximum allocation order.

## State and persistence
Pageblock flags persist in the memory-section/pageblock metadata managed by mm/page_alloc. Migratetype and skip/isolate state affect allocation and compaction decisions until changed.

## Dependencies and integration points
It depends on page types, hugepage/THP configs, memory isolation, compaction, page allocator migratetypes, PFN/page conversion, and alignment macros.

## Risks and test signals
Risks include wrong pageblock size for hugepage/THP configurations, migratetype bit overlap, isolate bit not preserved with migratetype, compaction skip staleness, and alignment mistakes during memory hotplug/CMA. Test migratetype set/get, compaction skip behavior, hugepage/THP pageblock sizing, CMA/memory isolation, memory hotplug ranges, and `!CONFIG_COMPACTION` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pageblock-flags.h -->
