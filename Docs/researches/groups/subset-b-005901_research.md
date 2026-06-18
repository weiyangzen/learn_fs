<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci.h -->
# sources/distributed-fs/ceph-client/include/linux/pci.h

## Purpose
`include/linux/pci.h` is the main in-kernel PCI/PCIe public contract. It defines the object model for PCI devices, buses, host bridges, physical slots, drivers, config-space access, resource windows, IRQ allocation, reset, power management, hotplug rescan/remove locking, VPD parsing, SR-IOV, ACS/ATS/PASID/PRI, ASPM/PTM, fixups, DMA aliases, and common driver convenience helpers. It sits above UAPI register definitions from `uapi/linux/pci.h` and shared ID constants from `include/linux/pci_ids.h`, exposing the structures and prototypes used by PCI core code, controller drivers, PCI endpoint drivers, architecture glue, ACPI/OF integration, and PCIe service drivers.

## Important APIs, Types, and Functions
Core identity and resource macros include `PCI_DEVID()`, `PCI_BUS_NUM()`, `PCI_SLOT_ALL_DEVICES`, `PCI_STATUS_ERROR_BITS`, the `PCI_*_RESOURCE` layout, bridge-window aliases, `pci_resource_*()` accessors, and `pci_dev_for_each_resource()` / `pci_bus_for_each_resource()`. Error-response helpers (`PCI_ERROR_RESPONSE`, `PCI_SET_ERROR_RESPONSE()`, `PCI_POSSIBLE_ERROR()`) codify config-read failure handling.

Important types include `struct pci_dev`, `struct pci_bus`, `struct pci_host_bridge`, `struct pci_slot`, `struct pci_driver`, `struct pci_ops`, `struct pci_error_handlers`, `struct pci_dynids`, `struct msix_entry`, `struct pcie_ptm_ops`, `struct pci_ptm_debugfs`, `struct pci_fixup`, and `struct pci_bus_region`. Enums and bitwise typedefs define power states (`pci_power_t`, `PCI_D0` through `PCI_D3cold`), error channel states, PCIe reset states, device and bus flags, link widths, bus/link speeds, ERS recovery results, PCI probe flags, bus MPS policy, IRQ allocation flags, ASPM link-state bits, and fixup passes.

The exported API surface is broad: bus discovery (`pci_scan_root_bus()`, `pci_host_probe()`, `pci_scan_child_bus()`, `pci_bus_add_devices()`), device lookup/refcounting (`pci_get_device()`, `pci_get_slot()`, `pci_dev_get()`), capability search (`pci_find_capability()`, `pci_find_ext_capability()`, VSEC/DVSEC helpers), config access (`pci_read_config_*()`, `pci_write_config_*()`, `pci_bus_read_config_*()`, `pcie_capability_*()`), enablement and command bits (`pci_enable_device()`, `pci_set_master()`, `pci_intx()`), reset (`pci_reset_function()`, `pcie_flr()`, `pci_reset_bus()`), resources (`pci_assign_resource()`, `pci_request_region[s]()`, `pci_ioremap_bar()`, `pcim_iomap*()`), interrupts (`pci_alloc_irq_vectors*()`, `pci_request_irq()`, `pci_irq_vector()`), power management (`pci_save_state()`, `pci_set_power_state()`, PME wake helpers), hotplug (`pci_rescan_bus()`, rescan/remove locks), VPD (`pci_read_vpd()`, `pci_vpd_alloc()`, keyword/checksum helpers), SR-IOV (`pci_enable_sriov()`, VF lookup/count/autoprobe helpers), ACS/atomic operations, DMA aliases, and logging wrappers (`pci_err()`, `pci_WARN_ONCE()`, etc.).

## Control Flow
Typical driver flow is: a driver declares `struct pci_driver` and ID table, registers with `pci_register_driver()` or `module_pci_driver()`, receives a `probe()` callback with a matched `struct pci_dev`, enables the device, requests or maps BAR resources, allocates IRQ vectors, stores private data with `pci_set_drvdata()`, and later unwinds through `remove()`, `shutdown()`, suspend/resume callbacks, or ERS callbacks. The header does not implement those flows, but it fixes the callback signatures and lifecycle contracts that the PCI core drives.

Enumeration flow starts from host bridge allocation (`pci_alloc_host_bridge()` / `devm_pci_alloc_host_bridge()`), arch/platform `struct pci_ops` config access, root bus scan, bridge scans, resource window sizing/assignment, IRQ mapping/swizzling, fixup passes, and device registration on `pci_bus_type`. Hotplug and rescan code reuse the same bus/device add/remove APIs behind `pci_lock_rescan_remove()`.

Power/error control flow uses saved config state, `current_state`, PME capability bits, D3cold policy bits, and `pci_channel_state_t`. Driver error recovery callbacks progress from `error_detected()` to optional `mmio_enabled()`, `slot_reset()`, and `resume()`, with reset-prep/done hooks available for function reset paths. PCIe capability RMW helpers choose locked access for shared registers such as `PCI_EXP_LNKCTL`, `PCI_EXP_LNKCTL2`, and `PCI_EXP_RTCTL`.

## State and Persistence Behavior
`struct pci_dev` is the persistent kernel representation of a PCI function. It caches identifiers, class/revision/header type, capability offsets, PCIe flags, DMA/MSI limits, current power state, PME and wake policy, BAR and bridge resources, IRQ, driver binding, device-managed state, error state, config-save buffer, sysfs resource attributes, VPD metadata, ACS and supported speed data, reset method order, and many feature-specific members behind Kconfig gates. Some fields are user-visible indirectly through sysfs, procfs, debugfs, or driver attributes.

`struct pci_bus` persists parent/child topology, device and slot lists, bridge resources, bus-number resources, config ops, domain number, current/max bus speed, firmware/legacy sysfs resources, and bus flags. `struct pci_host_bridge` persists root-bus policy: native service ownership, firmware resource preservation, MSI-domain selection, DMA ranges, resource windows, private host-controller data, and arch callbacks.

State is both runtime and suspend/resume relevant. `pci_save_state()` / `pci_restore_state()` preserve config space; `struct pci_saved_state` is opaque to callers; `struct pci_vpd` serializes VPD access with a mutex; MSI state has raw spinlock protection; `pci_cfg_access_lock()` and `pci_dev_lock()` serialize config/device operations; `pci_dev_is_disconnected()` uses `READ_ONCE()` on the error state because recovery can change it without a common reader lock.

## Dependencies and Integration Points
The header depends on core kernel types (`device`, `resource`, `kobject`, `list_head`, `atomic_t`, locks), MSI APIs, DMA mapping, `asm/pci.h`, UAPI PCI register definitions, PCI ID definitions, ACPI/OF conditionals, and many Kconfig symbols. It integrates with `drivers/pci/*`, PCIe port services (AER, DPC, PME, PTM, ASPM, bandwidth control), arch-specific PCI setup, controller drivers supplying `struct pci_ops`, endpoint drivers using `struct pci_driver`, VFIO through driver override and driver-managed DMA, IOMMU/DMA alias code, sysfs/procfs resource exposure, and hotplug implementations.

The `CONFIG_PCI` and feature-specific `#ifdef` sections are a major part of the contract. When PCI or a feature is disabled, this header provides inline stubs that return neutral values or errors such as `-EIO`, `-ENOSPC`, `-EINVAL`, `-ENOSYS`, or `false`, allowing drivers and generic code to compile across configurations.

## Risks
The largest risk is contract drift: `struct pci_dev` and `struct pci_bus` are central shared state, so field semantic changes can break drivers, sysfs behavior, power management, hotplug, or virtualization. Callers must not assume all feature fields exist without the matching Kconfig option. Config-space helpers can return all-ones data on real hardware failure, so code must distinguish possible error responses from valid values. Resource and reset APIs can affect other functions behind a bridge; bus reset and secondary bus reset use require care around hotplug and multifunction devices. Power-state transitions, D3cold policy, MSI masking quirks, ACS/ATS/PASID/PRI enablement, and DMA alias handling have security and data-corruption consequences when misused.

## Test Signals
Useful signals include allmodconfig and feature-matrix builds with PCI, MSI, SR-IOV, AER, DPC, ASPM, PTM, OF, ACPI, and PCI domains toggled; PCI device probe/remove smoke tests; hotplug add/remove/rescan tests; suspend/resume with config restore and PME wake; MSI/MSI-X allocation fallback to INTx; malformed capability-list traversal; SR-IOV VF creation/removal and sysfs controls; BAR request/iomap/release tests; PCIe FLR and bus reset tests; AER/ERS injection where available; and static checks for direct field access, missing refcount puts, and feature-stub return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_hotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/pci_hotplug.h

## Purpose
`include/linux/pci_hotplug.h` defines the public interface between PCI hotplug controller drivers and the PCI hotplug core. It describes the callback table a hotplug controller provides for slot operations, the `struct hotplug_slot` object registered with the core, registration/initialization/add/delete/destroy/deregister helpers, and ACPI/native-ownership helpers used by PCIe hotplug and SHPC paths.

## Important APIs, Types, and Functions
`struct hotplug_slot_ops` is the central contract. Its callbacks cover user or core requests to enable or disable a slot, set the attention LED, run hardware tests, query power/attention/latch/adapter status, and optionally reset a slot. The `reset_slot()` callback receives a `bool probe` argument so code can ask whether reset is supported before doing it.

`struct hotplug_slot` carries the callback table plus core-owned linkage to `struct pci_slot`, module owner, and module name. `hotplug_slot_name()` resolves the underlying `pci_slot` kobject name through `pci_slot_name()`.

Registration APIs are `__pci_hp_register()`, `__pci_hp_initialize()`, `pci_hp_add()`, `pci_hp_del()`, `pci_hp_destroy()`, and `pci_hp_deregister()`. Public macros `pci_hp_register()` and `pci_hp_initialize()` inject `THIS_MODULE` and `KBUILD_MODNAME`, avoiding extra include chaining for callers.

ACPI/native helpers include `pciehp_is_native()`, `acpi_get_hp_hw_control_from_firmware()`, `shpchp_is_native()`, `acpi_pci_check_ejectable()`, `acpi_pci_detect_ejectable()`, and `hotplug_is_native()`. Without ACPI, inline stubs treat PCIe hotplug and SHPC as native and firmware-control requests as successful.

## Control Flow
A hotplug controller allocates/fills `struct hotplug_slot`, supplies `hotplug_slot_ops`, then initializes/registers it against a parent PCI bus and slot number. The PCI hotplug core calls the ops in response to sysfs requests, controller events, or slot-management flows. Removal paths delete and destroy the slot object, then deregister the hotplug slot so the core stops exposing and invoking it.

`hotplug_is_native()` combines cached bridge state (`bridge->is_pciehp`) with ACPI ownership queries. It returns true when a PCIe hotplug bridge is OS-native or when SHPC ownership is native.

## State and Persistence Behavior
The header stores no state itself, but it defines ownership boundaries. The hotplug driver owns the callback implementation and lifetime of the `hotplug_slot` object until registration hands core-owned fields to the hotplug core. The core owns `pci_slot`, module metadata, and user-visible slot name. Persistent user-visible behavior is surfaced through slot sysfs attributes backed by these callbacks.

## Dependencies and Integration Points
This header depends on `struct pci_bus`, `struct pci_slot`, `struct pci_dev`, `struct module`, and `u8`/`u32` kernel types provided through surrounding PCI includes. With `CONFIG_ACPI`, it includes `linux/acpi.h` and integrates with ACPI slot ejectability and firmware ownership negotiation. Runtime users include PCIe hotplug (`pciehp`), SHPC hotplug, ACPI hotplug glue, and generic PCI slot reset code.

## Risks
Callback return semantics and slot lifetime are the main risks. A driver must not free a hotplug slot while sysfs or the hotplug core can still call its ops. `reset_slot()` must distinguish probe mode from actual reset to avoid disruptive bus resets during capability checks. Native ownership must be respected; controlling firmware-owned hotplug hardware can race platform firmware and produce duplicate or missing hotplug events. Status callbacks must tolerate hardware removal and transient presence/latch states.

## Test Signals
Test with `CONFIG_HOTPLUG_PCI`, `CONFIG_HOTPLUG_PCI_PCIE`, SHPC, and ACPI combinations. Exercise slot registration and deregistration, sysfs enable/disable/status paths, LED and latch status callbacks, reset probe versus reset execution, ACPI firmware-owned versus OS-native bridges, surprise removal, repeated add/remove cycles, and module unload while slots are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_hotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_ids.h -->
# sources/distributed-fs/ceph-client/include/linux/pci_ids.h

## Purpose
`include/linux/pci_ids.h` is a shared PCI class/vendor/device/subsystem ID registry for kernel code. It supplies symbolic constants for PCI class codes and selected vendor/device IDs that are used by multiple drivers or core code. The file explicitly instructs maintainers to keep IDs numerically sorted and to avoid adding entries unless definitions are shared between multiple drivers.

## Important APIs, Types, and Functions
This header contains no functions or types. Its API is macro constants. The first block defines PCI base classes, subclasses, and selected programming interfaces, including storage, network, display, multimedia, memory/CXL, bridge, communication, system, input, docking, processor, serial bus, wireless, intelligent, satellite, crypto, signal processing, accelerator, and catch-all classes.

The remainder defines `PCI_VENDOR_ID_*`, `PCI_DEVICE_ID_*`, `PCI_SUBVENDOR_ID_*`, `PCI_SUBDEVICE_ID_*`, and a small number of subsystem IDs. In this snapshot the registry contains roughly 121 class/base-class constants, 286 vendor IDs, 2367 device IDs, 11 subvendor IDs, and 96 subdevice IDs. It includes common vendors used elsewhere in this subset, such as `PCI_VENDOR_ID_ALIBABA`, `PCI_VENDOR_ID_AMPERE`, `PCI_VENDOR_ID_QCOM`, `PCI_VENDOR_ID_ROCKCHIP`, and `PCI_VENDOR_ID_SAMSUNG`, which are consumed by the DesignWare PCIe VSEC header.

## Control Flow
There is no runtime control flow. The constants are consumed at compile time in driver ID tables, PCI fixups, class checks, quirk matching, feature allowlists, and vendor-specific capability handling. Typical control flow happens in users such as `pci_match_id()`, driver `id_table` matching, or quirk dispatch that compares `struct pci_dev` fields against these constants.

## State and Persistence Behavior
The header holds no mutable state and creates no objects. Its persistence is source-level ABI within the kernel tree: renaming, removing, or changing a numeric value breaks code that uses the symbolic constant to match hardware. Sorting and sharing rules are the maintainability constraints that keep the registry stable.

## Dependencies and Integration Points
The file is standalone except for include guards and is included by `include/linux/pci.h` and many drivers. It integrates with `struct pci_device_id` tables, `MODULE_DEVICE_TABLE(pci, ...)`, quirk declarations, class checks such as `pci_is_vga()` and `pci_is_display()`, PCIe vendor-specific logic, and subsystem-specific drivers that need shared symbolic IDs rather than local definitions.

## Risks
Incorrect numeric IDs cause drivers or quirks to bind to the wrong hardware or fail to bind to intended hardware. Adding single-use IDs here increases global churn and creates a false impression of shared semantics. Duplicate vendor aliases, legacy IDs, mixed case names, and comments recording vendor quirks require careful preservation because external hardware documentation is inconsistent. Sorting violations make future maintenance and review harder.

## Test Signals
Build coverage is the primary signal because all users compile these constants into match tables. Additional signals include `modinfo` alias checks for affected drivers, PCI device match tests on known hardware or emulated devices, quirk activation logs, `lspci -n` comparisons against expected vendor/device pairs, and simple scripts that verify numeric sort order and duplicate definitions when editing the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pci_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcie-dwc.h -->
# sources/distributed-fs/ceph-client/include/linux/pcie-dwc.h

## Purpose
`include/linux/pcie-dwc.h` provides small shared definitions for Synopsys DesignWare PCIe controller support. In this snapshot it describes vendor-specific extended capability identifiers used to recognize RAS DES VSEC blocks on DesignWare-based controllers from several vendors.

## Important APIs, Types, and Functions
`struct dwc_pcie_vsec_id` contains a PCI vendor ID, vendor-specific extended capability ID, and VSEC revision. `dwc_pcie_rasdes_vsec_ids[]` is a sentinel-terminated static const table with entries for Alibaba, Ampere, Qualcomm, Rockchip, and Samsung, all using VSEC ID `0x02` and revision `0x4`.

The file has no functions. The empty `{}` terminator is part of the table contract for users that iterate until a zero entry.

## Control Flow
There is no executable flow in the header. Consumer code is expected to inspect a PCIe VSEC or DVSEC, compare the device vendor and VSEC metadata against `dwc_pcie_rasdes_vsec_ids[]`, and enable the appropriate DesignWare RAS DES handling only for matching vendor/revision combinations. The comment notes that VSEC IDs are vendor allocated, so matching only the VSEC ID is insufficient.

## State and Persistence Behavior
The table is compile-time constant data with internal linkage in each translation unit that includes the header. It persists only as static read-only data and has no runtime mutation or allocation.

## Dependencies and Integration Points
The header depends on `linux/pci_ids.h` for vendor constants. It integrates with DesignWare PCIe controller or service code that scans vendor-specific PCIe extended capabilities and needs a common allowlist for RAS DES-capable VSECs.

## Risks
Because VSEC IDs are vendor scoped, using `vsec_id` without also checking `vendor_id` and `vsec_rev` can misidentify unrelated vendor capabilities. Adding a vendor with the wrong revision could enable unsupported register decoding. Since the array is `static const` in a header, very broad inclusion would duplicate data, though the table is tiny.

## Test Signals
Build tests should cover all users of the table. Runtime signals include detecting the expected RAS DES capability on known Alibaba, Ampere, Qualcomm, Rockchip, or Samsung DesignWare PCIe hardware; rejecting the same VSEC ID for other vendors; and validating behavior when the VSEC revision differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcie-dwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-lynx.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs-lynx.h

## Purpose
`include/linux/pcs-lynx.h` declares factory and teardown helpers for NXP Lynx PCS integration with the kernel phylink subsystem. It lets Ethernet MAC/controller drivers create a `struct phylink_pcs` either from an MDIO bus/address pair or from firmware node data, then destroy it when no longer needed.

## Important APIs, Types, and Functions
`lynx_pcs_create_mdiodev(struct mii_bus *bus, int addr)` creates a Lynx PCS backed by an MDIO device at a specific address. `lynx_pcs_create_fwnode(struct fwnode_handle *node)` creates one from firmware node description. `lynx_pcs_destroy(struct phylink_pcs *pcs)` releases the object returned by the create helpers.

The header exposes `struct phylink_pcs` from phylink as the consumer-facing object and depends on `struct mii_bus` plus `struct fwnode_handle` through included headers.

## Control Flow
A MAC driver obtains MDIO or firmware information during probe, calls one of the create helpers, passes the returned PCS to phylink setup, and calls `lynx_pcs_destroy()` during remove or probe-error unwinding. The PCS implementation behind these prototypes handles link-mode configuration and PCS operations through phylink callbacks.

## State and Persistence Behavior
The header itself stores no state. The created PCS object persists across the network device lifetime or until explicit destroy. Lifetime is caller-managed; a driver must not destroy the PCS while phylink can still call its PCS operations.

## Dependencies and Integration Points
The header includes `linux/mdio.h` and `linux/phylink.h`. It integrates with NXP/Freescale Ethernet controllers and any driver that uses a Lynx PCS with phylink, MDIO, and firmware description.

## Risks
The main risks are lifetime mismatch, passing an invalid MDIO address or firmware node, failing to unwind after partial probe, and creating duplicate PCS objects for the same hardware block. Since only prototypes are visible here, users must follow the implementation's error-pointer or NULL return convention as documented by the implementation.

## Test Signals
Probe/remove tests on Lynx PCS users, MDIO enumeration with valid and invalid addresses, firmware-node lookup, phylink mode changes, autonegotiation and fixed-link operation, suspend/resume if supported by users, and leak/error-path tests around create/destroy are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-lynx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-rzn1-miic.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs-rzn1-miic.h

## Purpose
`include/linux/pcs-rzn1-miic.h` declares helpers for the Renesas RZ/N1 MIIC PCS implementation. It exposes a small create/destroy interface that lets a MAC or platform driver instantiate a phylink PCS from a device and device-tree node.

## Important APIs, Types, and Functions
`miic_create(struct device *dev, struct device_node *np)` creates a `struct phylink_pcs` associated with the given device and device-tree node. `miic_destroy(struct phylink_pcs *pcs)` releases the created PCS object. The header forward-declares `struct phylink` and `struct device_node`; it uses `struct device` without an explicit local include, relying on includers or implementation context to provide it.

## Control Flow
During probe, a Renesas networking driver locates the MIIC node, calls `miic_create()`, wires the returned PCS into phylink, and destroys it on remove or probe failure. Runtime link configuration and state reporting are delegated through phylink PCS methods implemented outside this header.

## State and Persistence Behavior
No state is stored in the header. The PCS instance created by `miic_create()` persists until `miic_destroy()`. The caller owns lifetime sequencing relative to phylink registration and network device teardown.

## Dependencies and Integration Points
The interface integrates with the phylink subsystem, OF/device-tree descriptions, Renesas RZ/N1 MIIC hardware support, and MAC drivers that need a PCS object separate from the Ethernet MAC. It likely pairs with DT bindings under `include/dt-bindings/net/pcs-rzn1-miic.h` and the corresponding driver implementation.

## Risks
Risks include missing forward declaration or include coverage for `struct device` in unusual include orders, invalid device-tree nodes, mismatched create/destroy ownership, and phylink callbacks racing teardown. The interface is minimal, so consumers must rely on implementation behavior for error returns and supported link modes.

## Test Signals
Build tests for all MIIC users catch include-order issues. Runtime tests should cover probe from valid and invalid device-tree nodes, phylink attach/detach, interface mode transitions supported by MIIC, link up/down reporting, module or platform-driver remove, and probe-error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-rzn1-miic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-mtk-lynxi.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs/pcs-mtk-lynxi.h

## Purpose
`include/linux/pcs/pcs-mtk-lynxi.h` declares the MediaTek LynxI PCS factory interface for phylink users. It allows a MediaTek Ethernet driver to create a PCS object from device, firmware node, regmap, and an analog register offset/value selector, then destroy it during teardown.

## Important APIs, Types, and Functions
`mtk_pcs_lynxi_create(struct device *dev, struct fwnode_handle *fwnode, struct regmap *regmap, u32 ana_rgc3)` returns a `struct phylink_pcs *` for the MediaTek LynxI PCS. `mtk_pcs_lynxi_destroy(struct phylink_pcs *pcs)` releases it. The API exposes `regmap` because the PCS implementation shares register access with a parent system controller or Ethernet block, and `ana_rgc3` identifies the analog control register context needed by the implementation.

## Control Flow
A MediaTek MAC driver builds or obtains its `regmap`, locates firmware data, calls `mtk_pcs_lynxi_create()` during probe, attaches the returned PCS to phylink, and calls `mtk_pcs_lynxi_destroy()` after detaching phylink or on probe failure. Runtime link setup flows through the returned `phylink_pcs` operations.

## State and Persistence Behavior
The header stores no state. The created PCS object persists across the network device lifetime and likely retains references or pointers to device, firmware node/regmap context, and register offsets. Lifetime and ordering are caller-managed.

## Dependencies and Integration Points
The header includes `linux/phylink.h` and `linux/regmap.h`, integrating with phylink, firmware-node based hardware description, regmap-backed register access, and MediaTek Ethernet drivers.

## Risks
Passing the wrong `regmap` or `ana_rgc3` value can direct PCS operations at the wrong registers. Destroying the PCS before phylink is detached can leave callbacks with stale state. As with other PCS factory headers, error-return conventions must be followed from the implementation.

## Test Signals
Build coverage for MediaTek Ethernet users, probe/remove with valid firmware data, phylink link-mode changes, autonegotiation behavior, register access tracing for expected `regmap` offsets, suspend/resume where applicable, and leak/error-path tests around create/destroy are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-mtk-lynxi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-xpcs.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs/pcs-xpcs.h

## Purpose
`include/linux/pcs/pcs-xpcs.h` defines the public helper interface for Synopsys DesignWare XPCS, a phylink PCS used by several Ethernet MAC drivers. It declares supported autonegotiation mode constants, known PCS/PMA identity values, an identity structure, conversion and configuration helpers, MDIO/fwnode-based constructors, and destroy routines.

## Important APIs, Types, and Functions
Autonegotiation/interface mode constants include `DW_AN_C73`, `DW_AN_C37_SGMII`, `DW_2500BASEX`, `DW_AN_C37_1000BASEX`, and `DW_10GBASER`. `enum dw_xpcs_pcs_id` names native, NXP SJA1105/SJA1110, and generic DesignWare PCS IDs plus an ID mask. `enum dw_xpcs_pma_id` names native PMA, several DesignWare PMA generations and rates, Wangxun TXGBE 10G PMA, and Meta FBNIC 100G PMA. `struct dw_xpcs_info` pairs PCS and PMA IDs.

The opaque `struct dw_xpcs` is the implementation object. `xpcs_to_phylink_pcs()` exposes its phylink PCS facade. `xpcs_get_an_mode()` maps a `phy_interface_t` to an XPCS autonegotiation mode. `xpcs_config_eee_mult_fact()` configures EEE multiplier behavior. Constructors are `xpcs_create_mdiodev()` and `xpcs_create_fwnode()` for raw XPCS objects, plus `xpcs_create_pcs_mdiodev()` for callers that only need `struct phylink_pcs`. Destructors are `xpcs_destroy()` and `xpcs_destroy_pcs()`.

## Control Flow
A MAC driver discovers an XPCS instance through MDIO or firmware node, creates it, maps the requested PHY interface to an AN mode, optionally configures EEE behavior, passes the phylink PCS object to phylink, and destroys it on teardown. The implementation behind this header handles hardware ID probing, supported mode selection, link configuration, and phylink PCS callbacks.

## State and Persistence Behavior
The header defines no mutable state, but the opaque `dw_xpcs` instance created by the constructors persists across MAC/phylink lifetime. It likely holds MDIO/fwnode accessors, probed identity, supported mode tables, and PCS state. The caller must keep the underlying bus/fwnode resources alive for the lifetime of the XPCS object and avoid using the phylink PCS after destruction.

## Dependencies and Integration Points
The header includes clock, firmware node, MDIO, PHY, phylink, and type definitions. It integrates with DesignWare Ethernet controllers such as stmmac, switch drivers using NXP XPCS variants, Wangxun and Meta hardware IDs, MDIO bus infrastructure, phylink, PHY interface mode selection, and EEE configuration paths.

## Risks
Autonegotiation mode selection must match the requested `phy_interface_t`; a wrong mode can break link establishment or advertise invalid capabilities. Hardware ID matching must use masks and PMA/PCS pairing correctly because multiple vendors reuse or wrap XPCS blocks. Lifetime bugs can occur if MDIO devices, firmware nodes, or phylink callbacks outlive the XPCS object. EEE multiplier configuration is hardware-sensitive and can affect power/link stability.

## Test Signals
Build all XPCS consumers, probe known MDIO and firmware-node XPCS instances, verify `xpcs_get_an_mode()` across SGMII, 1000BASE-X, 2500BASE-X, 10GBASE-R, and Clause 73 modes, test link up/down and autonegotiation with phylink, validate identity matching on NXP/DesignWare/Wangxun/Meta devices, exercise EEE configuration, and run remove/error-path tests to catch lifetime leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-xpcs.h -->
