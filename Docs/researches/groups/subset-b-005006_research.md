# Research Report: subset-b-005006

This grouped report covers PLDA-based PCIe host controllers, Intel VMD, PCI managed-resource helpers, DOE mailboxes, ECAM mapping, and PCI endpoint function configuration under the Ceph client Linux source tree. Each source file has a source-tree-aligned section delimited for deterministic splitting into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-microchip-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-microchip-host.c

## Purpose
Implements the Microchip PolarFire SoC AXI PCIe host controller using PLDA XpressRich-style register blocks. It provides Microchip-specific register mapping, interrupt/event decoding, ECC/error masking, MSI setup fixups, clock enablement, inbound/outbound address translation, and ECAM host probing.

## Important APIs, Types, And Functions
Key state is `struct mc_pcie`, which embeds `struct plda_pcie_rp` and stores bridge/control register bases. Event tables map PCIe, SEC, DED, and PLDA local interrupt bits into Linux hwirqs. Important functions include `mc_host_probe()`, `mc_platform_init()`, `mc_disable_interrupts()`, `mc_get_events()`, `mc_ack_event_irq()`, `mc_mask_event_irq()`, `mc_unmask_event_irq()`, `mc_pcie_setup_inbound_ranges()`, and `mc_pcie_enable_msi()`.

## Control Flow
Platform probe allocates the global `port`, maps either split `bridge`/`ctrl` resources or the legacy `apb` resource, disables and clears interrupts, reads MSI vector count/address from hardware, enables optional Fabric Interface clocks, and delegates to `pci_host_common_probe()`. ECAM setup calls `mc_platform_init()`, which programs config-space ATR window 0, fixes MSI capability fields in root-port config space, configures outbound memory windows, sets inbound ranges from `dma-ranges` or noncoherent MPFS defaults, installs Microchip event ops/chip, and initializes PLDA interrupts.

## State And Persistence
Persistent state is mostly hardware register state: ATR tables, MSI capability fields, interrupt masks/status, ECC bypass bits, and inbound windows. Driver state is devm-managed except the file-scope `port`, which reflects only one active controller context.

## Dependencies And Integration Points
Integrates with `pci-host-common`, `pci-ecam`, PLDA common code in `pcie-plda-host.c`, device tree resources and `dma-ranges`, optional clocks `fic0` through `fic3`, Linux irq domains, and PCI host enumeration.

## Risks
The file-scope `port` is fragile if multiple controllers are ever supported. Interrupt mask polarity differs among event classes and depends on `event_descs` correctness. Inbound ATR setup has hardware-specific noncoherent assumptions. MSI capability rewriting must match the bitstream-provided vector count and MSI address.

## Test Signals
Probe should log ECAM setup and enumerate downstream devices on `microchip,pcie-host-1.0`. Useful signals include MSI delivery, INTx delivery, SEC/DED/AER error interrupts, DMA coherent and noncoherent DMA traffic, fallback legacy `apb` resource binding, and boot with varied `dma-ranges`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-microchip-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda-host.c

## Purpose
Provides the shared PLDA PCIe root-port host implementation used by platform-specific PLDA controllers. It handles ECAM mapping, MSI and INTx irq domains, local event irq domains, ATR window programming, host bridge allocation/probing, and common teardown.

## Important APIs, Types, And Functions
Exports `plda_pcie_map_bus()`, `plda_init_interrupts()`, `plda_pcie_setup_window()`, `plda_pcie_setup_inbound_address_translation()`, `plda_pcie_setup_iomems()`, `plda_pcie_host_init()`, and `plda_pcie_host_deinit()`. Internal irq handlers include `plda_handle_msi()`, `plda_handle_intx()`, and `plda_handle_event()`. `plda_allocate_msi_domains()` creates the parent MSI domain.

## Control Flow
Platform drivers populate `struct plda_pcie_rp`, then call `plda_pcie_host_init()`. The common path maps `apb` and `cfg` resources, allocates a host bridge, runs optional platform `host_init`, programs config and MEM ATR windows, sets default MSI metadata, initializes interrupts, assigns PCI ops/sysdata, and calls `pci_host_probe()`. Interrupt flow begins at the platform IRQ, chains into event demux, then dispatches INTx or MSI chained handlers as needed.

## State And Persistence
`struct plda_pcie_rp` stores bridge/config bases, irq domains, chained IRQ numbers, MSI bitmap/vector address/count, event bitmap, ops, and raw spinlock. MSI allocation state persists in `plda_msi.used`; ATR and interrupt masks persist in controller registers until deinit or reset.

## Dependencies And Integration Points
Depends on Linux PCI host bridge APIs, irq domains, generic MSI parent-domain helpers, device-tree child interrupt-controller nodes, platform resources named `apb` and `cfg`, and constants from `pcie-plda.h`.

## Risks
IRQ-domain cleanup must only run after all domains/handlers are initialized. `plda_irq_msi_domain_alloc()` allocates one vector regardless of `nr_irqs`, so callers expecting multi-vector atomic allocation need scrutiny. `plda_pcie_setup_iomems()` does not bound ATR index count. Locking around IMASK updates is central to race-free mask/unmask behavior.

## Test Signals
Build users include Microchip and StarFive PLDA controllers. Runtime signals are working ECAM config access, downstream enumeration, MSI allocation/free reuse, INTx interrupt handling, event interrupt masking/acking, host probe failure rollback, and clean root-bus removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda.h

## Purpose
Defines the common PLDA PCIe host-controller register interface, interrupt event model, state structures, platform hook contracts, exported helper prototypes, and small inline configuration helpers used by PLDA-based host drivers.

## Important APIs, Types, And Functions
Important constants cover bridge configuration registers, local interrupt masks/status, MSI address/status, ATR source/translation fields, and event IDs. Core types are `enum plda_int_event`, `struct plda_event_ops`, `struct plda_pcie_host_ops`, `struct plda_msi`, `struct plda_pcie_rp`, and `struct plda_event`. Inline helpers set default MSI values, enable root-port mode, set PCI class code, enable 64-bit prefetchable windows, disable LTR forwarding, disable functions, and write root-complex BARs.

## Control Flow
No standalone execution occurs here. The header defines the contract by which platform drivers customize common PLDA host flow: set fields in `plda_pcie_rp`, optionally supply `event_ops`, `event_irq_chip`, and `host_ops`, then call common host initialization and teardown.

## State And Persistence
The header describes persistent driver state stored per controller: device pointer, host bridge, irq domains, lock, MSI bitmap, register bases, event bitmap, and IRQ numbers. Inline helpers mutate persistent hardware configuration registers such as `GEN_SETTINGS`, `PCIE_PCI_IDS_DW1`, `PCIE_WINROM`, `PMSG_SUPPORT_RX`, `PCI_MISC`, and root BAR registers.

## Dependencies And Integration Points
It is included by `pcie-plda-host.c`, Microchip, and StarFive controller drivers. It relies on Linux PCI constants, irq domains, bit operations, and MMIO accessors available through including C files.

## Risks
Register bit definitions are shared ABI for multiple SoCs; a mistaken shift or mask affects all platform users. Event numbering bridges hardware bits and Linux irq domains, so changes require updating platform event mapping. Inline helpers assume the caller selected the correct function/register bank.

## Test Signals
Compile coverage across both PLDA platform drivers catches many declaration mismatches. Runtime validation comes from correct root-port class code, disabled unused functions, working MSI/INTx/event delivery, 64-bit prefetchable window behavior, and link enumeration on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-starfive.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-starfive.c

## Purpose
Implements the StarFive JH7110 PCIe host controller by adapting the shared PLDA host layer to JH7110 clocks, resets, PHY, syscon registers, PERST GPIO, optional regulator, root-port quirks, link polling, and suspend/resume.

## Important APIs, Types, And Functions
Main state is `struct starfive_jh7110_pcie`, embedding `struct plda_pcie_rp`. Key functions are `starfive_pcie_probe()`, `starfive_pcie_parse_dt()`, `starfive_pcie_host_init()`, `starfive_pcie_host_deinit()`, `starfive_pcie_enable_phy()`, `starfive_pcie_clk_rst_init()`, `starfive_pcie_host_wait_for_link()`, and config-space wrappers that hide root-complex BAR0/BAR1.

## Control Flow
Probe allocates state, parses DT resources and domain number, enables runtime PM, installs StarFive host ops, configures an event bitmap that masks doorbell events, and calls `plda_pcie_host_init()`. The platform host init powers the PHY, programs syscon root-port/non-endpoint and clock-request fields, enables clocks/resets/regulator, asserts and deasserts PERST with PCIe timing waits, disables physical functions 1-3, enables root-port mode, clears RC BAR, sets class code, disables LTR forwarding, enables 64-bit prefetchable windows, and polls link.

## State And Persistence
Driver state holds syscon base selection from static PCI domain, reset and clock handles, PHY, regulator, PERST GPIO, and PLDA state. Hardware state persists in syscon AR/AW/RP/LNKSTA fields, PLDA bridge registers, ATR windows, interrupt masks, and downstream reset state.

## Dependencies And Integration Points
Depends on device tree, `starfive,stg-syscon`, Linux PHY, reset, clock, regulator, GPIO, runtime PM, PLDA common host helpers, and PCI generic config access. It registers as `starfive,jh7110-pcie`.

## Risks
Domain number is used to choose syscon offsets and must match DTS. `starfive_pcie_host_deinit()` calls PHY disable unconditionally, so optional PHY lifetime assumptions matter. Regulator enable failure is logged but not returned. Suspend/resume only handles PHY and clocks, relying on preserved PLDA/root-port state.

## Test Signals
Useful tests include JH7110 boot on both PCIe domains, endpoint enumeration after PERST timing, hidden RC BAR reads returning zero, MSI/INTx delivery through PLDA, link-down boot, suspend/resume with devices present, and remove path resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-starfive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/vmd.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/vmd.c

## Purpose
Implements Intel Volume Management Device support. VMD exposes a PCI device that contains an emulated PCI domain and root bus for hidden downstream root ports, with special config access, resource windows, MSI/MSI-X remapping or bypass, ACPI companion lookup, power-management quirks, and teardown.

## Important APIs, Types, And Functions
Core state types are `struct vmd_dev`, `struct vmd_irq_list`, and `struct vmd_irq`. Important functions include `vmd_probe()`, `vmd_enable_domain()`, `vmd_create_irq_domain()`, `vmd_msi_alloc()`, `vmd_irq()`, `vmd_pci_read()`, `vmd_pci_write()`, `vmd_domain_reset()`, `vmd_get_phys_offsets()`, `vmd_get_bus_number_start()`, `vmd_pm_enable_quirk()`, `vmd_remove()`, `vmd_suspend()`, and `vmd_resume()`.

## Control Flow
PCI probe checks Xen constraints, enables the VMD device with `pcim_enable_device()`, maps CFGBAR, sets DMA mask/mastering, chooses first vector offset, and calls `vmd_enable_domain()`. Domain setup derives bus/resource windows, optionally reads physical membar shadow offsets, decides whether MSI remapping is required, allocates VMD vectors and an MSI parent domain, creates an emulated root bus, scans children, resets downstream bridge windows, assigns resources, applies LTR/ASPM quirks, configures real root-port settings, and adds devices.

## State And Persistence
Persistent state includes emulated domain number, bus start, resources, CFGBAR mapping, child bus, IRQ lists, SRCU guards, MSI domain, VMD instance id/name, and config-space spinlock. Hardware state includes VMCONFIG MSI remap bits, MSI-X vectors, bridge windows, and child device power/link state.

## Dependencies And Integration Points
Integrates with PCI core bus/resource scanning, x86 MSI address format, generic MSI domains, ACPI companion lookup hooks, SRCU/RCU irq demux, Xen detection, PCI PM/ASPM/LTR helpers, and Intel PCI IDs.

## Risks
MSI remap versus bypass decisions affect interrupt correctness, especially under virtualization. Shared-vector lists require correct SRCU synchronization during free and demux. Config access is serialized to avoid hardware deadlock. Resource offset/shadow logic is critical for guest passthrough. ACPI hook installation is global and must be bracketed around scan.

## Test Signals
Validate NVMe devices behind VMD, interrupt delivery in remap and bypass modes, suspend/resume vector restoration, remove/shutdown cleanup, Xen guests, ACPI companion binding, VMD client IDs using BIOS PM quirks, and resource assignment with membar shadow offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/vmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/devres.c -->
# sources/distributed-fs/ceph-client/drivers/pci/devres.c

## Purpose
Provides device-managed PCI resource helpers for config-space remapping, IO-space remapping, device enable/disable, INTx state restore, memory-write-invalidate, BAR region requests, BAR mappings, ranged mappings, and legacy `pcim_iomap_table()` compatibility.

## Important APIs, Types, And Functions
Exports include `devm_pci_remap_iospace()`, `devm_pci_remap_cfgspace()`, `devm_pci_remap_cfg_resource()`, `pcim_set_mwi()`, `pcim_intx()`, `pcim_enable_device()`, `pcim_pin_device()`, `pcim_iomap_table()`, `pcim_iomap()`, `pcim_iounmap()`, `pcim_iomap_region()`, `pcim_iounmap_region()`, `pcim_iomap_regions()`, `pcim_request_region()`, `pcim_request_all_regions()`, and `pcim_iomap_range()`. Key internal records are `pcim_iomap_devres`, `pcim_intx_devres`, and `pcim_addr_devres`.

## Control Flow
Managed helpers allocate devres records before requesting resources or creating mappings. Release callbacks later unmap IO, release BAR regions, restore INTx, clear MWI, or disable devices. Modern APIs track each request/mapping in `pcim_addr_devres`; deprecated whole-BAR APIs also update the legacy iomap table so old callers can retrieve BAR mappings.

## State And Persistence
State is attached to `struct device` devres stacks. `pcim_enable_device()` sets `pdev->is_managed` and restore action, while `pcim_pin_device()` prevents automatic disable. Region/mapping records persist until detach or explicit release. The legacy iomap table persists as a devres object for compatibility.

## Dependencies And Integration Points
Depends on PCI core resource APIs, generic devres, ioremap helpers, `pci_iomap*`, `pci_request_region*`, `pci_enable_device()`, and PCI command-register INTx behavior. Used broadly by PCI drivers for failure-safe probe cleanup.

## Risks
Mixing deprecated whole-BAR table APIs with ranged mappings can confuse callers if they expect all mappings in the table. `pcim_iomap()` returns NULL while newer helpers return `IOMEM_ERR_PTR`, so callers must match conventions. Manual release must use the matching pcim helper or devres records remain inconsistent.

## Test Signals
Probe-error injection should release requested BARs and mappings. Driver detach should restore INTx, clear MWI, and disable unpinned devices. Validate `pcim_iomap_table()` compatibility, invalid BAR rejection, ranged mapping release, and repeated request/unmap cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/doe.c -->
# sources/distributed-fs/ceph-client/drivers/pci/doe.c

## Purpose
Implements PCIe Data Object Exchange mailbox support. It discovers DOE extended capabilities, creates ordered mailbox workers, caches supported protocols, exposes supported features via sysfs, and provides synchronous request/response exchange through `pci_doe()`.

## Important APIs, Types, And Functions
Main types are opaque `struct pci_doe_mb`, `struct pci_doe_feature`, and internal stack-allocated `struct pci_doe_task`. Public functions are `pci_doe()`, `pci_find_doe_mailbox()`, `pci_doe_init()`, `pci_doe_destroy()`, `pci_doe_disconnected()`, plus sysfs init/teardown helpers. Important internals include `pci_doe_abort()`, `pci_doe_send_req()`, `pci_doe_recv_resp()`, `doe_statemachine_work()`, and `pci_doe_cache_features()`.

## Control Flow
`pci_doe_init()` scans PCI extended capabilities and creates a mailbox for each DOE capability. Creation allocates an ordered workqueue, aborts to reset the mailbox, and runs DOE discovery to populate an xarray of supported features. `pci_doe()` builds a stack task, queues it, waits for completion, and returns response length or errno. The worker sends headers/payload, starts GO, polls for ready/error/timeout, reads the response while acknowledging dwords, and aborts on failures.

## State And Persistence
Per-device mailboxes live in `pdev->doe_mbs`. Each mailbox persists its capability offset, feature xarray, waitqueue, ordered workqueue, cancel/dead flags, and optional sysfs attributes. Task state is per call and destroyed after completion.

## Dependencies And Integration Points
Depends on PCI config-space accessors, PCI DOE register definitions, xarray, workqueues, waitqueues, sysfs, and consumers such as CXL/SPDM protocols that locate mailboxes with `pci_find_doe_mailbox()`.

## Risks
The mailbox has no hardware interrupt path and relies on polling. Firmware/OS contention is only detected indirectly through busy/error status. Partial payload dword handling requires caller endian discipline. Abort failure marks a mailbox dead. Destroy/disconnect must cancel queued work before device removal.

## Test Signals
Exercise DOE discovery sysfs entries, `pci_find_doe_mailbox()` for discovery and vendor protocols, successful and short responses, oversized payload rejection, busy/error/timeout abort paths, hot-remove cancellation, and concurrent callers serialized by the ordered workqueue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/doe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/ecam.c -->
# sources/distributed-fs/ceph-client/drivers/pci/ecam.c

## Purpose
Provides generic PCI ECAM config-window allocation, mapping, freeing, bus add/remove hooks, and `map_bus` implementation for host controllers and ACPI/DT PCI roots using enhanced configuration access mechanism.

## Important APIs, Types, And Functions
Exports `pci_ecam_create()`, `pci_ecam_free()`, `pci_ecam_map_bus()`, and `pci_generic_ecam_ops`. With ACPI quirks enabled it also defines `pci_32b_ops` and `pci_32b_read_ops`. Internal helpers are `pci_ecam_add_bus()` and `pci_ecam_remove_bus()` for 32-bit per-bus mapping.

## Control Flow
`pci_ecam_create()` validates the bus range, allocates `struct pci_config_window`, clamps the desired bus range to available ECAM resource size, claims the physical ECAM region, maps the full window on 64-bit systems or allocates per-bus mapping storage on 32-bit systems, runs optional platform `ops->init()`, and returns the config window. PCI config accesses call `pci_ecam_map_bus()` through `pci_ops` to compute a bus/device/function/register address.

## State And Persistence
`pci_config_window` stores parent device, config resource, bus resource, bus shift, ops, and either one `win` mapping or an array of per-bus `winp` mappings. The ECAM iomem resource remains reserved and mappings remain active until `pci_ecam_free()`.

## Dependencies And Integration Points
Depends on PCI core config-read/write helpers, `pci_remap_cfgspace()`, iomem resource reservation, `struct pci_ecam_ops`, and host-controller drivers such as Microchip PLDA through `pci_host_common_probe()`.

## Risks
Bus-range clamping can silently reduce discoverable buses after a warning. Nonstandard `bus_shift` affects address calculations and must match hardware. On 32-bit, config access before `.add_bus` maps the bus would fail. `ops->init()` errors must unwind mappings and resource reservations correctly.

## Test Signals
Validate ECAM resource conflict handling, full-window mapping on 64-bit, per-bus map/unmap on 32-bit, standard and nonstandard bus shifts, generic read/write config access, 32-bit-only quirk ops, and cleanup after host probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/ecam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/Kconfig

## Purpose
Defines the top-level PCI endpoint configuration menu and core endpoint feature switches. It controls whether endpoint controller/function libraries, configfs management, MSI doorbell support, and endpoint function drivers are exposed to the kernel build.

## Important APIs, Types, And Functions
Kconfig symbols are `PCI_ENDPOINT`, `PCI_ENDPOINT_CONFIGFS`, and `PCI_ENDPOINT_MSI_DOORBELL`. The file also sources `drivers/pci/endpoint/functions/Kconfig` to make endpoint function drivers visible inside the same menu.

## Control Flow
There is no runtime execution. Build-time flow starts with `menu "PCI Endpoint"`, allows enabling endpoint core when `HAVE_PCI` is present, optionally selects `CONFIGFS_FS` for configfs endpoint binding, optionally enables MSI doorbell support when `GENERIC_MSI_IRQ` exists, then enters the endpoint functions submenu.

## State And Persistence
State is kernel configuration. Enabling `PCI_ENDPOINT` changes which object files are built by the endpoint Makefile and whether endpoint controller/function frameworks are available to platform drivers.

## Dependencies And Integration Points
Integrates with the top-level PCI Kconfig, endpoint Makefile, configfs, generic MSI infrastructure, and endpoint function drivers such as test, NTB, VNTB, and MHI.

## Risks
Missing dependencies can expose build options that do not link on a platform. Because `PCI_ENDPOINT_CONFIGFS` selects configfs, enabling it changes userspace ABI availability. Endpoint function Kconfig inclusion under this menu means function symbols depend on the top-level endpoint core being sensible.

## Test Signals
Run Kconfig builds with endpoint disabled, endpoint core only, configfs enabled, MSI doorbell enabled, and individual endpoint functions. Confirm expected object inclusion and absence of unresolved configfs/MSI references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/Makefile

## Purpose
Builds the PCI endpoint core, optional configfs support, optional MSI doorbell support, and endpoint function subdirectory according to Kconfig selections.

## Important APIs, Types, And Functions
Object rules include `pci-ep-cfs.o` for `CONFIG_PCI_ENDPOINT_CONFIGFS`, `pci-epc-core.o`, `pci-epf-core.o`, `pci-epc-mem.o`, and `functions/` for `CONFIG_PCI_ENDPOINT`, plus `pci-ep-msi.o` for `CONFIG_PCI_ENDPOINT_MSI_DOORBELL`.

## Control Flow
No runtime flow exists. Kbuild evaluates `obj-$(CONFIG_...)` assignments and descends into `functions/` only when endpoint core is enabled.

## State And Persistence
The file persists build graph state only. Its ordering ensures endpoint core and memory helpers are built with endpoint function support.

## Dependencies And Integration Points
Consumes symbols from endpoint Kconfig and links core endpoint infrastructure used by endpoint controller drivers and endpoint function modules.

## Risks
If the `functions/` directory is not tied to `CONFIG_PCI_ENDPOINT`, function objects could build without core APIs. Adding new endpoint core objects requires updating this Makefile and the matching Kconfig dependency.

## Test Signals
Check `make drivers/pci/endpoint/` with endpoint options toggled, verify function subdir inclusion only when expected, and confirm module/object names align with Kconfig symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Kconfig

## Purpose
Defines selectable PCI endpoint function drivers: test, NTB, virtual NTB, and MHI endpoint. It exposes function-level dependencies and help text under the PCI Endpoint menu.

## Important APIs, Types, And Functions
Kconfig symbols are `PCI_EPF_TEST`, `PCI_EPF_NTB`, `PCI_EPF_VNTB`, and `PCI_EPF_MHI`. `PCI_EPF_TEST`, `PCI_EPF_NTB`, and `PCI_EPF_VNTB` select `CONFIGFS_FS`; `PCI_EPF_TEST` selects `CRC32`; `PCI_EPF_VNTB` depends on `NTB`; `PCI_EPF_MHI` depends on `MHI_BUS_EP`.

## Control Flow
No runtime code executes. The configuration controls which function driver object files are built by the endpoint functions Makefile and which userspace configfs endpoint functions can be instantiated.

## State And Persistence
State is compile-time kernel configuration. Module selection determines whether named endpoint function drivers register on the `pci_epf` bus at runtime.

## Dependencies And Integration Points
Integrates with endpoint core (`PCI_ENDPOINT`), configfs endpoint composition, NTB subsystem, MHI endpoint core, CRC helper library, and `drivers/pci/endpoint/functions/Makefile`.

## Risks
Function drivers rely on endpoint controller capabilities such as BARs, MSI/MSI-X, and secondary EPC support, but Kconfig cannot express most hardware feature requirements. Selecting configfs from multiple function drivers broadens userspace ABI even if no endpoint controller is present.

## Test Signals
Build each function as built-in and module, verify dependency rejection when `PCI_ENDPOINT`, `NTB`, or `MHI_BUS_EP` is unavailable, and instantiate configfs functions for selected drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Makefile

## Purpose
Maps PCI endpoint function Kconfig symbols to their endpoint function driver objects.

## Important APIs, Types, And Functions
Build rules are `pci-epf-test.o` for `CONFIG_PCI_EPF_TEST`, `pci-epf-ntb.o` for `CONFIG_PCI_EPF_NTB`, `pci-epf-vntb.o` for `CONFIG_PCI_EPF_VNTB`, and `pci-epf-mhi.o` for `CONFIG_PCI_EPF_MHI`.

## Control Flow
No runtime flow exists. Kbuild includes only object files whose Kconfig symbol is enabled.

## State And Persistence
The Makefile stores build-time mapping state. Runtime registration is handled by each endpoint function driver module or built-in init function.

## Dependencies And Integration Points
Consumes symbols from `functions/Kconfig` and is reached from the parent endpoint Makefile when `CONFIG_PCI_ENDPOINT` is enabled.

## Risks
Whitespace or object-name drift can break module builds. New endpoint function drivers require matching additions here and in Kconfig. A rule without a matching dependency could build a function driver without required subsystem APIs.

## Test Signals
Enable each endpoint function symbol independently and verify only the expected object builds and links. Module autoload names should match the registered `pci_epf_driver` names in the corresponding C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-mhi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-mhi.c

## Purpose
Implements a PCI endpoint function for MHI endpoint devices, primarily Qualcomm platforms. It presents PCI IDs and BAR/MSI resources to the host, wires endpoint controller address mapping and interrupt callbacks into the MHI EP core, and optionally uses DMAengine for larger transfers.

## Important APIs, Types, And Functions
Key types are `struct pci_epf_mhi`, `struct pci_epf_mhi_ep_info`, and `struct pci_epf_mhi_dma_transfer`. Platform descriptors cover SDX55, SM8450, and SA8775P. Important functions include `pci_epf_mhi_bind()`, `pci_epf_mhi_epc_init()`, `pci_epf_mhi_link_up()`, `pci_epf_mhi_bus_master_enable()`, `pci_epf_mhi_alloc_map()`, `pci_epf_mhi_iatu_read/write()`, DMA sync/async helpers, and `pci_epf_mhi_unbind()`.

## Control Flow
Probe stores platform info and event ops. Bind maps the endpoint controller `mmio` resource and doorbell IRQ. EPC init sets BAR0, MSI count, config header, EPC features, and optional DMA channels. On link up, the driver fills `mhi_ep_cntrl` callbacks and registers the MHI endpoint controller. Bus-master-enable powers up MHI when the host enables bus mastering. Link down, EPC deinit, and unbind power down/unregister MHI and clear resources.

## State And Persistence
State persists in `pci_epf_mhi`: MMIO mapping/physical address, BAR size, endpoint function pointer, MHI controller, DMA channels/workqueue/list, lock, and endpoint feature pointer. MHI runtime state is owned by the MHI EP core after registration.

## Dependencies And Integration Points
Depends on PCI endpoint core/EPC APIs, MHI EP core, platform resources named `mmio` and `doorbell`, DMAengine for DMA-capable variants, and Qualcomm PCI vendor/device identities.

## Risks
DMA init/deinit is called from several failure paths and must not double-release channels. Async DMA stores copied buffer metadata and assumes callback lifetime remains valid. iATU mapping uses alignment offsets from EPC features. MHI power-up depends on host bus mastering events.

## Test Signals
Test configfs creation for each EPF name, host enumeration with expected PCI IDs/MSI count, MHI channel bring-up, doorbell IRQ delivery, small iATU transfers, large DMA transfers and timeouts, async callback cleanup, link down/up cycles, and unbind/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-mhi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-ntb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-ntb.c

## Purpose
Implements a PCI endpoint function that builds a non-transparent bridge from two endpoint controller interfaces. It exposes config, scratchpad, doorbell, and memory-window BARs to two hosts so each host can signal and map memory through the endpoint SoC.

## Important APIs, Types, And Functions
Core types are `struct epf_ntb`, `struct epf_ntb_epc`, and packed shared `struct epf_ntb_ctrl`. Important functions include `epf_ntb_bind()`, `epf_ntb_epc_create()`, `epf_ntb_init_epc_bar()`, `epf_ntb_config_spad_bar_alloc()`, `epf_ntb_epc_init_interface()`, `epf_ntb_cmd_handler()`, `epf_ntb_configure_db()`, `epf_ntb_configure_mw()`, `epf_ntb_link_up()`, and cleanup/free helpers. Configfs attributes expose `spad_count`, `db_count`, `num_mws`, and `mw1`-`mw4`.

## Control Flow
Probe allocates `epf_ntb` and installs ops. Bind waits until both primary and secondary EPCs are attached, creates per-interface state, chooses free BARs, allocates config/self-scratchpad memory, programs config/peer-scratchpad/doorbell/memory BARs, configures MSI/MSI-X, writes endpoint headers, and starts delayed command polling. Hosts write commands into shared control regions; the work handler configures or tears down doorbells and memory windows, and raises link events once both sides request link up.

## State And Persistence
Persistent state includes user-configured counts/sizes, per-interface EPC features, BAR assignments, BAR memory, peer outbound allocations, MSI-X table offsets, shared control registers, linkup flags, and delayed work. Shared control memory is host-visible and is the protocol state between host NTB drivers and this EPF.

## Dependencies And Integration Points
Depends on PCI endpoint core with primary and secondary EPC support, EPC BAR/MSI/MSI-X/address mapping APIs, configfs, and host-side NTB drivers that understand the control protocol.

## Risks
The command handler polls every 5 ms and has little synchronization around host-written control fields. BAR selection and sizing must satisfy both EPC feature sets. Cleanup loops use BAR ranges that need careful bounds. Doorbell mapping differs between MSI and MSI-X. Shared packed structures are ABI with host drivers.

## Test Signals
Instantiate via configfs with two EPCs, vary doorbell/scratchpad/MW sizes, validate MSI and MSI-X doorbells, memory-window map/unmap, peer scratchpad visibility, link-up/down commands from both hosts, bind waiting for the second EPC, unbind cleanup, and stress command polling during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-ntb.c -->
