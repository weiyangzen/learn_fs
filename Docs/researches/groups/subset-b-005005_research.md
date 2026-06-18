# Research Report: subset-b-005005

This grouped report covers Renesas R-Car/RZ, Rockchip, Xilinx, and PLDA PCIe controller source files under `sources/distributed-fs/ceph-client/drivers/pci/controller`. Each section is delimited for reconciliation into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-host.c

Purpose: Implements the Renesas R-Car PCIe root-complex platform driver. It allocates a `pci_host_bridge`, initializes regulators, runtime PM, clocks, PHY, register windows, link training, INTx forwarding, MSI support, config-space access, and suspend/resume handling for older R-Car SoCs.

Important APIs/types/functions: `struct rcar_pcie_host` embeds shared `struct rcar_pcie` and host resources. `struct rcar_msi` tracks the 32-vector MSI bitmap, parent IRQ domain, and mask lock. PCI config access is exposed through `rcar_pcie_ops`, with `rcar_pcie_read_conf()` and `rcar_pcie_write_conf()` routing into `rcar_pcie_config_access()`. Other key paths include `rcar_pcie_hw_init()`, `rcar_pcie_enable()`, `rcar_pcie_enable_msi()`, `rcar_pcie_parse_map_dma_ranges()`, `rcar_pcie_probe()`, `rcar_pcie_resume()`, and the ARM-only abort workaround.

Control flow: Probe enables optional supplies and runtime PM, maps MMIO, obtains MSI IRQs and the `pcie_bus` clock, maps DMA inbound ranges, runs the SoC-specific PHY init callback from the OF match table, initializes the controller as a root port, waits for data-link active, enables MSI if configured, then calls `pci_host_probe()`. Config cycles special-case root bus devfn 0 as internal config space and use Type 0/Type 1 PIO for child buses. MSI interrupts read `PCIEMSIFR`, dispatch through the MSI domain, and clear unexpected vectors.

State and persistence: Runtime state is mainly MMIO register programming, runtime PM state, clock/PHY power, IRQ-domain allocations, and the MSI allocation bitmap. Inbound/outbound windows and MSI target registers persist in hardware until reset, suspend, or teardown. Resume rebuilds DMA windows, PHY/link state, MSI address and masks, and resource windows.

Dependencies/integration: Depends on Linux PCI host bridge APIs, generic MSI parent domains, irqdomain, runtime PM, regulators, clocks, PHY, OF resources, and common R-Car helpers from `pcie-rcar.c`/`pcie-rcar.h`.

Risks: Config reads can produce hardware aborts on ARM, hence the inline exception-table workaround. Sub-32-bit config writes perform read-modify-write and can be unsafe around RW1C fields. Window splitting is limited by `MAX_NR_INBOUND_MAPS`; bad DT ranges can fail mapping. Link-down is treated as no device. MSI IRQs are shared with non-MSI sources, so handler filtering must remain correct.

Test signals: Build on ARM and arm64 R-Car configs, DT probe for all compatible strings, link-up/link-down boot logs, config-space enumeration, MSI allocation/free, INTx behavior, DMA to inbound windows, suspend/resume with allocated MSIs, and ARM abort handler coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.c

Purpose: Provides shared low-level R-Car PCIe helper functions used by host and endpoint code. It wraps MMIO reads/writes, byte-lane read/modify/write, PHY/data-link polling, and inbound/outbound address translation programming.

Important APIs/types/functions: Exports `rcar_pci_write_reg()`, `rcar_pci_read_reg()`, `rcar_rmw32()`, `rcar_pcie_wait_for_phyrdy()`, `rcar_pcie_wait_for_dl()`, `rcar_pcie_set_outbound()`, and `rcar_pcie_set_inbound()`. All operate on `struct rcar_pcie` from `pcie-rcar.h`.

Control flow: Callers map the controller and then use these helpers during probe, resume, resource-window setup, and config-space operations. `rcar_pcie_wait_for_phyrdy()` polls `PCIEPHYSR.PHYRDY` with millisecond sleeps. `rcar_pcie_wait_for_dl()` polls `PCIETSTR.DATA_LINK_ACTIVE` with short delays. Outbound setup disables the translation window, computes a 128-byte unit mask, writes lower/upper PCIe address registers, and enables memory or I/O space. Inbound setup writes local CPU and optional PCIe root-port addresses as a paired lower/upper 64-bit window.

State and persistence: The file stores no state. It mutates hardware registers through the mapped controller base. Address windows persist in controller registers until explicitly reprogrammed or reset.

Dependencies/integration: Depends on Linux PCI resource helpers such as `resource_entry`, `pci_pio_to_address()`, `roundup_pow_of_two()`, and `upper_32_bits()/lower_32_bits()`. The helper API is the narrow shared contract consumed by `pcie-rcar-host.c` and R-Car endpoint code.

Risks: `rcar_rmw32()` shifts masks by byte offset and assumes the caller passes register-relative masks correctly. Window masks round sizes up, so caller-side range splitting must prevent unwanted overmapping. `rcar_pcie_set_inbound()` uses adjacent entries for 64-bit windows, so index management is critical.

Test signals: Compile/link coverage for both R-Car host and endpoint users, successful PHY/data-link polling on hardware, config/resource enumeration through programmed outbound windows, DMA through inbound mappings, and suspend/resume reprogramming of windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.h

Purpose: Defines the shared R-Car PCIe register map, bit fields, constants, core data structure, access direction enum, and helper prototypes for R-Car PCIe controller code.

Important APIs/types/functions: The header defines `struct rcar_pcie { struct device *dev; void __iomem *base; }`, access constants `RCAR_PCI_ACCESS_READ` and `RCAR_PCI_ACCESS_WRITE`, MSI capacity `INT_PCI_MSI_NR`, resource/window limits, register address macros such as `PCIECAR`, `PCIECCTLR`, `PCIETCTLR`, `PCIETSTR`, `PCIEMSIFR`, `PCIELAR()`, `PCIEPALR()`, `PCICONF()`, and capability offset helpers `RCONF()`, `REXPCAP()`, and `RVCCAP()`.

Control flow: There is no executable flow. The macro definitions drive all register-level control in `pcie-rcar-host.c`, `pcie-rcar.c`, and endpoint support. Config access macros encode bus/device/function fields for controller PIO config cycles.

State and persistence: No state is allocated here. Constants describe persistent hardware register locations and bit meanings used by runtime code to initialize link state, MSI routing, config space, and memory windows.

Dependencies/integration: Depends on kernel bit macros and PCI structures included by users. It is tightly coupled with R-Car hardware manuals and the shared helper implementation in `pcie-rcar.c`.

Risks: Any incorrect offset or bit field corrupts controller programming across host and endpoint drivers. Window count constants (`MAX_NR_INBOUND_MAPS`, `RCAR_PCI_MAX_RESOURCES`) constrain resource parsing. Some macros encode legacy Gen1/Gen2/Gen3 behavior; new SoCs should not reuse them without register compatibility review.

Test signals: Build all R-Car PCIe variants, compare register definitions against vendor manuals, validate link training, MSI, config reads/writes, and resource windows on each compatible SoC generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-ep.c

Purpose: Implements the Rockchip AXI PCIe endpoint-controller driver for RK3399 endpoint mode. It exposes a `pci_epc` to endpoint-function drivers, manages BAR programming, outbound address translation, MSI/INTx generation, PERST# handling, and link training notification.

Important APIs/types/functions: `struct rockchip_pcie_ep` wraps shared `struct rockchip_pcie`, EPC object, outbound region state, IRQ trigger window, PERST state, and delayed link-training work. It implements `pci_epc_ops`: `write_header`, `set_bar`, `clear_bar`, `align_addr`, `map_addr`, `unmap_addr`, `set_msi`, `get_msi`, `raise_irq`, `start`, `stop`, and `get_features`. Key local helpers include `rockchip_pcie_prog_ep_ob_atu()`, `rockchip_pcie_ep_send_msi_irq()`, `rockchip_pcie_ep_link_training()`, and `rockchip_pcie_ep_hide_broken_msix_cap()`.

Control flow: Probe creates the EPC, parses shared Rockchip DT resources, initializes outbound memory windows, enables clocks, initializes the controller in endpoint mode through common helpers, hides the unsupported MSI-X capability, enables function 0, notifies endpoint core initialization, and optionally requests a PERST# GPIO IRQ. `start()` enables selected functions and begins link training. Link training polls Gen1/link-up state, optionally retrains to Gen2, then calls `pci_epc_linkup()`. PERST assertion cancels training and reports linkdown; deassertion retrains.

State and persistence: Driver state includes the outbound-region bitmap and addresses, reserved IRQ outbound window, current MSI PCI address/function, pending INTx state, PERST/link booleans, and hardware BAR/ATU/config registers. EPC memory windows are allocated through `pci_epc_multi_mem_init()` and persist until endpoint memory exit.

Dependencies/integration: Depends on Linux PCI endpoint core, endpoint-function framework, GPIO IRQs, delayed work, and shared Rockchip helpers/register macros from `pcie-rockchip.c`/`.h`.

Risks: Outbound regions are derived from 1 MiB windows and `rockchip_ob_region(addr)`; misaligned or duplicate mappings return busy or target the wrong region. MSI generation dynamically reprograms a dedicated outbound window and must track function/address changes. Unsupported MSI-X is hidden by editing the capability list; errors can expose unusable MSI-X to the host. PERST and polling paths must avoid reporting linkup after reset.

Test signals: EPC configfs operation, endpoint-function bind/unbind, BAR sizing and host enumeration, MSI and INTx delivery, PERST assert/deassert, Gen1/Gen2 training logs, outbound DMA mapping/unmapping, and RK3399 endpoint DT compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-host.c

Purpose: Implements the Rockchip AXI PCIe root-complex driver. It parses host resources, powers regulators and PHY lanes, trains the link, programs AXI wrapper address translation, handles controller/client/legacy interrupts, supports suspend/resume, and registers a PCI host bridge.

Important APIs/types/functions: The driver uses shared `struct rockchip_pcie` and host `pci_ops` through `rockchip_pcie_ops`. Important functions include config access helpers (`rockchip_pcie_rd_own_conf()`, `rockchip_pcie_rd_other_conf()`, `rockchip_pcie_wr_conf()`), `rockchip_pcie_host_init_port()`, `rockchip_pcie_setup_irq()`, `rockchip_pcie_cfg_atu()`, `rockchip_pcie_prog_ob_atu()`, `rockchip_pcie_prog_ib_atu()`, `rockchip_pcie_suspend_noirq()`, `rockchip_pcie_resume_noirq()`, and `rockchip_pcie_probe()`.

Control flow: Probe allocates a host bridge, parses common DT plus host regulators, enables clocks and supplies, initializes resets/PHYs/link training, creates an INTx domain, programs outbound memory/I/O/message regions and inbound memory, maps the message region, requests system/client IRQs and chains legacy INTx, enables interrupts, then invokes `pci_host_probe()`. Config reads use local RC config space for the root bus and ECAM-like address offsets for downstream devices after switching the wrapper to Type 0 or Type 1 config access. Suspend sends PME_TURN_OFF, waits for L2, powers down PHY/clocks/0.9V; resume reverses setup.

State and persistence: State lives in regulator enable state, clocks, PHY lane power, `lanes_map`, IRQ domain, message region mapping, and wrapper ATU registers. The driver powers off unused lanes after link training.

Dependencies/integration: Depends on OF PCI parsing, regulator framework, GPIO PERST, PHY, reset/clock helpers from `pcie-rockchip.c`, irqdomain, chained IRQs, and Linux PCI host bridge APIs.

Risks: Sub-32-bit writes to own config space use read-modify-write and can corrupt adjacent RW1C bits. The controller supports only one device directly below the root port. ATU programming assumes memory and I/O windows exist and splits them into 1 MiB regions. Suspend depends on endpoint PME/L2 behavior and may fail if the link does not enter L2.

Test signals: RK3399 host boot enumeration, regulator and clock sequencing, Gen1/Gen2 training, lane-map debug logs, INTx delivery, controller error logs, memory/I/O BAR access, suspend/resume with endpoint traffic, and DT variants with optional 12V/3.3V supplies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.c

Purpose: Provides common Rockchip AXI PCIe resource, reset, PHY, clock, and configuration-access helpers shared by host and endpoint drivers.

Important APIs/types/functions: Exports `rockchip_pcie_parse_dt()`, `rockchip_pcie_init_port()`, `rockchip_pcie_get_phys()`, `rockchip_pcie_deinit_phys()`, `rockchip_pcie_enable_clocks()`, `rockchip_pcie_disable_clocks()`, and `rockchip_pcie_cfg_configuration_accesses()`. These operate on the shared `struct rockchip_pcie` declared in `pcie-rockchip.h`.

Control flow: `rockchip_pcie_parse_dt()` maps either RC `axi-base` or EP `mem-base`, maps `apb-base`, obtains PHYs, reads `num-lanes` and max link speed, obtains PM/core reset controls, grabs PERST/reset GPIO depending on mode, and gets all clocks. `rockchip_pcie_init_port()` asserts resets, initializes all PHYs, deasserts PM resets, programs generation/lane/mode bits, powers PHYs, waits for PLL lock, and deasserts core resets. `rockchip_pcie_cfg_configuration_accesses()` programs outbound region 0 as Type 0 or Type 1 config access.

State and persistence: The helper fills shared driver state fields such as MMIO bases, resources, PHY pointers, reset arrays, clocks, lane count, link generation, GPIO, and mode flag. Hardware reset, client config, and region-0 translation registers persist after initialization until reprogrammed or reset.

Dependencies/integration: Uses platform resources by name, OF PCI max-link-speed, reset controls, PHY framework, clock bulk APIs, GPIO descriptors, and local Rockchip register definitions.

Risks: Resource names are ABI with DT. The common parser already obtains PHYs; endpoint code also calls `rockchip_pcie_get_phys()` after parsing, so changes around PHY acquisition must account for both users. Reset order is hardware-sensitive; the header explicitly warns not to reorder core reset deassert sequencing. All four PHY lanes are initialized even if fewer lanes are used.

Test signals: Host and endpoint builds, probe with legacy and per-lane PHY models, reset/clock error-path unwinding, PHY PLL lock timeout handling, Type 0/Type 1 config enumeration, and endpoint mode initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.h

Purpose: Defines Rockchip AXI PCIe register offsets, bit fields, address translation constants, reset names, shared controller state, MMIO accessors, and common helper prototypes for host and endpoint drivers.

Important APIs/types/functions: Central type is `struct rockchip_pcie`, holding `reg_base`, `apb_base`, PHYs, resets, clocks, regulators, PERST GPIO, lane/link fields, IRQ domain, message region, RC/EP mode flag, and endpoint memory resource. Static inline `rockchip_pcie_read()` and `rockchip_pcie_write()` wrap APB MMIO. Register macros cover client config/status, core management, RC config, AXI outbound/inbound windows, endpoint BAR configuration, MSI/MSI-X controls, and message generation.

Control flow: No executable flow beyond inline MMIO accessors. The constants determine setup paths in `pcie-rockchip.c`, RC paths in `pcie-rockchip-host.c`, and EPC paths in `pcie-rockchip-ep.c`.

State and persistence: The header declares the in-memory state shape shared by both modes. Register definitions describe persistent controller state for link training, BAR windows, ATU regions, interrupts, and MSI/INTx generation.

Dependencies/integration: Includes kernel clock, reset, PCI, and ECAM headers. It is a private local interface and is not intended as a cross-subsystem ABI.

Risks: Duplicate definitions of `ROCKCHIP_PCIE_AT_MIN_NUM_BITS`, `ROCKCHIP_PCIE_AT_MAX_NUM_BITS`, and `ROCKCHIP_PCIE_AT_SIZE_ALIGN` exist in the header and should remain consistent if edited. Bit-field write-mask helpers encode the upper-half write-mask convention of `PCIE_CLIENT_CONFIG`; replacing them with plain values would break atomic updates. Reset-name order matters.

Test signals: Full compile coverage for host and endpoint objects, host enumeration, endpoint BAR/MSI behavior, static inspection against hardware manuals, and runtime logs for link, lanes, interrupts, and ATU programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rzg3s-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rzg3s-host.c

Purpose: Implements the built-in Renesas RZ/G3S and RZ/G3E PCIe root-complex driver. It manages SYSC mode/reset signals, runtime PM clocks, reset controls, PHY programming, config-space access, inbound/outbound windows, INTx/MSI domains, link-speed selection, and noirq suspend/resume.

Important APIs/types/functions: Major types are `struct rzg3s_pcie_host`, `struct rzg3s_pcie_msi`, `struct rzg3s_pcie_soc_data`, `struct rzg3s_sysc`, and `struct rzg3s_pcie_port`. PCI access uses separate `rzg3s_pcie_root_ops` for root config mapping and `rzg3s_pcie_child_ops` for child bus PIO requests. Key functions include `rzg3s_pcie_host_setup()`, `rzg3s_pcie_probe()`, `rzg3s_pcie_host_init()`, `rzg3s_pcie_parse_map_dma_ranges()`, `rzg3s_pcie_parse_map_ranges()`, `rzg3s_pcie_init_irqdomain()`, `rzg3s_pcie_init_msi()`, and `rzg3s_pcie_set_max_link_speed()`.

Control flow: Probe allocates a host bridge, maps AXI/config registers, parses child port vendor/device IDs and reference clock, obtains the SYSC regmap, sets RC mode/reset signals, obtains/deasserts reset controls, enables runtime PM, sets up inbound/outbound windows and IRQ domains, initializes config/header/PHY/reset state, optionally raises link speed, then registers root and child PCI ops with `pci_host_probe()`. Child config cycles program request address, byte enables, Type 0/Type 1 read/write transaction type, issue the request, and poll completion. MSI setup allocates DMA pages, finds an enabled AXI window containing the DMA address, aligns an MSI window, programs receive registers, and creates a generic MSI parent domain.

State and persistence: Persistent hardware state includes SYSC function bits, reset deassertion state, CFGU permission windows, vendor/device/class/bus registers, AXI/P-window mappings, MSI receive window, INTx/MSI masks, PHY tables, and negotiated link speed. Driver state includes IRQ domains, MSI bitmap/DMA page, reset arrays, raw hardware lock, and parsed port IDs.

Dependencies/integration: Depends on Linux PCI host bridge APIs, generic config helpers, MSI library, irqdomain/chained IRQs, runtime PM, reset framework, regmap/syscon, OF PCI max-link-speed, clock framework, and Renesas DT bindings.

Risks: Child config writes smaller than 32 bits use read-modify-write and warn about RW1C corruption. MSI requires the allocated DMA address to fall within an already enabled AXI window. Window splitting must obey power-of-two and alignment constraints with only eight windows. Suspend failure recovery is complex because SYSC/reset/clock ordering is strict. `sysc_np` must exist in DT for `syscon_node_to_regmap()`.

Test signals: Probe on both `renesas,r9a08g045-pcie` and `renesas,r9a09g047-pcie`, config reads on root and child buses, MSI and INTx delivery, DMA through inbound windows, link speed capping from DT, noirq suspend/resume, reset error paths, and PHY-setting validation against hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rzg3s-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-common.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-common.h

Purpose: Provides shared Xilinx PCIe interrupt index constants used by multiple Xilinx host drivers, especially CPM and PL DMA variants.

Important APIs/types/functions: Defines symbolic interrupt numbers such as `XILINX_PCIE_INTR_LINK_DOWN`, `HOT_RESET`, `CFG_PCIE_TIMEOUT`, `CFG_TIMEOUT`, `CORRECTABLE`, `NONFATAL`, `FATAL`, `CFG_ERR_POISON`, `PME_TO_ACK_RCVD`, `INTX`, `PM_PME_RCVD`, `MSI`, `SLV_UNSUPP`, `SLV_UNEXP`, `SLV_COMPL`, `SLV_ERRP`, `SLV_CMPABT`, `SLV_ILLBUR`, `MST_DECERR`, `MST_SLVERR`, and `SLV_PCIE_TIMEOUT`.

Control flow: The header has no runtime logic. Drivers use these indices to build bit masks with `BIT(XILINX_PCIE_INTR_*)`, populate interrupt-cause tables, map event IRQs in irqdomains, and route INTx/MSI status.

State and persistence: No state. The constants encode hardware interrupt bit positions and therefore indirectly affect persistent interrupt mask/status programming.

Dependencies/integration: Includes PCI, ECAM, and platform-device headers for users. Included by `pcie-xilinx-cpm.c` and `pcie-xilinx-dma-pl.c`; older `pcie-xilinx.c` and `pcie-xilinx-nwl.c` carry their own local definitions.

Risks: `XILINX_PCIE_INTR_PM_PME_RCVD` and `XILINX_PCIE_INTR_MSI` both use bit 17 for different controller variants. Shared users must select the semantic appropriate to their hardware. Wrong indices lead to unmasked errors, missed INTx/MSI, or misleading logs.

Test signals: Compile both CPM and PL DMA drivers, verify event masks against hardware manuals, trigger AER/error interrupts, INTx, MSI, PME, and timeout events where supported, and confirm cause strings match the asserted bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-cpm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-cpm.c

Purpose: Implements Xilinx Versal CPM/CPM5 PCIe host bridge support. It uses generic ECAM config access, CPM SLCR interrupt plumbing, controller event domains, INTx domains, bridge enablement, and variant-specific register offsets.

Important APIs/types/functions: `struct xilinx_cpm_pcie` stores bridge registers, CPM SLCR base, INTx/event domains, config window, IRQ numbers, lock, and `struct xilinx_cpm_variant`. Key functions include `xilinx_cpm_pcie_init_irq_domain()`, `xilinx_cpm_setup_irq()`, `xilinx_cpm_pcie_event_flow()`, `xilinx_cpm_pcie_intx_flow()`, `xilinx_cpm_pcie_intr_handler()`, `xilinx_cpm_pcie_parse_dt()`, `xilinx_cpm_pcie_init_port()`, and `xilinx_cpm_pcie_probe()`.

Control flow: Probe selects variant data, creates IRQ domains except for CPM5NC host, finds the bus range, maps `cpm_slcr`, creates a PCI ECAM window from `cfg`, maps `cpm_csr` for CPM5 variants, initializes bridge interrupts and bridge-enable state, maps/request event IRQs, chains INTx and the main event IRQ, assigns generic ECAM ops, and calls `pci_host_probe()`. Event flow reads IDR masked by IMR, dispatches each bit through the CPM domain, acknowledges controller and SLCR miscellaneous status, and INTx flow dispatches `IDRN` bits to the wired domain.

State and persistence: Persistent state includes interrupt masks, SLCR local interrupt enable/status, bridge-enable bit, and ECAM mapping. Driver state includes the irqdomains, chained handler bindings, raw spinlock, and variant register offsets.

Dependencies/integration: Uses Linux PCI host bridge and ECAM helpers, irqdomain/chained IRQ APIs, OF platform resources, and shared Xilinx interrupt constants. Compatible strings distinguish CPM, CPM5 host0/host1, and CPM5NC host behavior.

Risks: CPM5NC intentionally skips interrupt setup and port init, so changes must preserve this special case. Event and INTx domains share the same child interrupt-controller node but different bus tokens. Register base selection differs between CPM and CPM5. Missing cleanup of chained handlers or ECAM windows on error can leave stale IRQ plumbing.

Test signals: Boot enumeration on each compatible variant, ECAM config access, link status logs, controller error interrupt logs, INTx delivery, SLCR local interrupt acknowledgement, CPM5 host1 register offsets, CPM5NC enumeration without IRQ setup, and error-path unbind/probe retry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-cpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-dma-pl.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-dma-pl.c

Purpose: Implements Xilinx PL XDMA/QDMA PCIe host bridge support. It provides config-space mapping, link validation, bridge enablement, MSI parent-domain support, separate low/high MSI status handlers, INTx and event irqdomains, and variant-specific register layout for QDMA.

Important APIs/types/functions: `struct pl_dma_pcie` holds register/config mappings, physical MSI base, IRQ domains, MSI state, locks, and variant data. `struct xilinx_msi` tracks MSI bitmap/domain and two MSI IRQ lines. Key paths include `xilinx_pl_dma_pcie_map_bus()`, `xilinx_pl_dma_pcie_init_port()`, `xilinx_pl_dma_pcie_init_irq_domain()`, `xilinx_pl_dma_pcie_init_msi_irq_domain()`, `xilinx_request_msi_irq()`, `xilinx_pl_dma_pcie_setup_irq()`, `xilinx_pl_dma_pcie_parse_dt()`, and `xilinx_pl_dma_pcie_probe()`.

Control flow: Probe allocates a host bridge, gets the bus range and variant, creates an ECAM window over the primary resource, optionally maps QDMA bridge registers from `breg`, requests `msi0` and `msi1`, initializes bridge status/masks/MSI decode mode, creates event/INTx/MSI domains, maps and requests event/error/INTx IRQs, then registers PCI host ops. Config mapping rejects downstream accesses when link is down and uses `cfg_base` for QDMA versus `reg_base` for XDMA. MSI handlers drain low/high status registers, clear bits, find mappings, and invoke generic IRQ handling.

State and persistence: State includes ECAM window mappings, MSI bitmap allocations, event/INTx irqdomains, interrupt masks, MSI base registers, MSI status masks, bridge-enable state, and physical register base used as MSI target.

Dependencies/integration: Depends on generic PCI/ECAM APIs, generic MSI parent domains, irqdomain, OF resources and named IRQs, and shared Xilinx interrupt constants.

Risks: Link-up checks reduce but cannot eliminate races before PIO config access; comments note link-down PIO can require controller reset. Probe assigns `err = xilinx_pl_dma_pcie_setup_irq(port);` but does not branch on that error before `pci_host_probe()`, so IRQ setup failures may be masked by later probe behavior. MSI bitmap memory is allocated with `kzalloc()` and domain cleanup does not visibly free it. QDMA uses an offset register accessor, so variant mistakes corrupt accesses.

Test signals: XDMA and QDMA DT probe, config-space enumeration, link-down config rejection, MSI low/high vector delivery including multi-MSI allocations, INTx delivery, event/error IRQ logs, QDMA `breg` mapping, bridge-enable register state, and IRQ setup failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-dma-pl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-nwl.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-nwl.c

Purpose: Implements the Xilinx NWL PCIe bridge host controller. It manages bridge/config/ECAM mappings, PHY and clock enablement, bridge translation setup, link waiting, misc/INTx/MSI interrupt handling, and PCI host registration.

Important APIs/types/functions: `struct nwl_pcie` stores bridge, PCIe, and ECAM bases/physical addresses, PHY array, IRQs, MSI state, INTx domain, clock, and legacy mask lock. `struct nwl_msi` tracks 64 MSI vectors and two MSI IRQ lines. Key functions include `nwl_pcie_bridge_init()`, `nwl_pcie_parse_dt()`, `nwl_pcie_phy_enable()`, `nwl_pcie_init_irq_domain()`, `nwl_pcie_enable_msi()`, `nwl_pcie_map_bus()`, `nwl_pcie_misc_handler()`, `nwl_pcie_leg_handler()`, and MSI high/low handlers.

Control flow: Probe maps `breg`, `pcireg`, and `cfg`, chains INTx, obtains PHYs and clock, enables PHYs, initializes bridge windows and message filtering, waits for PHY link, enables ECAM, requests misc IRQ, clears/enables misc and legacy masks, creates INTx/MSI domains, configures MSI if enabled, then calls `pci_host_probe()`. Config mapping returns ECAM addresses only for root devfn 0 or downstream buses with link up.

State and persistence: Persistent hardware state includes egress bridge and ECAM base registers, ingress subtractive decode, message filters, MSI base/masks, misc/legacy masks, and bridge config interrupt enable. Driver state includes PHY/clock power, chained IRQ handlers, MSI bitmap, and irqdomains.

Dependencies/integration: Uses Linux PCI host bridge and ECAM helpers, PHY and clock frameworks, OF resources/IRQs, generic MSI parent domains, and chained irqdomain handling.

Risks: `nwl_pcie_phy_enable()` loops over the whole four-element PHY array and can call PHY helpers on NULL after DT ends early unless platform data guarantees all entries are valid or helper behavior tolerates it. Error paths after IRQ-domain/MSI setup do not remove domains before PHY cleanup. MSI setup uses chained handlers for named IRQs and assumes MSII capability is present. ECAM size is forced to max.

Test signals: Probe on `xlnx,nwl-pcie-2.11`, clock/PHY enable and disable, link wait timeout, ECAM enumeration, misc error interrupts, INTx delivery, MSI low/high vectors, DMA-coherent path setting, remove/unbind, and link-down config access handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-nwl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx.c

Purpose: Implements the older Xilinx AXI PCIe host controller driver. It maps controller/ECAM registers, validates config-space access by link state and root-port device number, handles legacy INTx and MSI through irqdomains, logs controller errors, initializes interrupts, enables the bridge, and registers a PCI host bridge.

Important APIs/types/functions: `struct xilinx_pcie` stores device, register base, MSI bitmap, map lock, MSI domain, legacy domain, and resources. Key functions include `xilinx_pcie_map_bus()`, `xilinx_allocate_msi_domains()`, `xilinx_pcie_init_irq_domain()`, `xilinx_pcie_intr_handler()`, `xilinx_pcie_init_port()`, `xilinx_pcie_parse_dt()`, and `xilinx_pcie_probe()`.

Control flow: Probe allocates the host bridge, initializes the MSI bitmap lock, maps the first `reg` resource with config semantics, requests the shared controller IRQ, initializes hardware interrupt masks and bridge-enable bit, creates legacy and optional MSI domains, assigns `xilinx_pcie_ops`, and calls `pci_host_probe()`. The single interrupt handler reads IDR and IMR, logs link/error causes, decodes INTx/MSI from root-port interrupt FIFO registers, dispatches to the appropriate domain, and clears IDR status.

State and persistence: Runtime state includes MSI bitmap allocations and irqdomains. Hardware state includes interrupt masks/status, MSI base registers programmed from the driver object page, and bridge-enable bit.

Dependencies/integration: Uses Linux PCI host bridge and generic config helpers, OF address/IRQ parsing, irqdomain, generic MSI library, and `pci_irqd_intx_xlate` for INTx.

Risks: MSI target address is `ALIGN_DOWN(virt_to_phys(pcie), SZ_4K)`, tying interrupt writes to the physical page containing driver data rather than a separately allocated DMA object. The top-level MSI ack is effectively a no-op because the shared interrupt handler already clears status. Downstream config access is inherently racy with link state. The driver supports only one device directly under the root port.

Test signals: Probe on `xlnx,axi-pcie-host-1.00.a`, bridge enable, root and downstream config reads, link-up/down logs, INTx/MSI delivery, MSI allocation/free for up to 128 vectors, controller error interrupts, and shared IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Kconfig

Purpose: Defines Kconfig options for PLDA-based PCIe host controller support, including the shared PLDA host core and Microchip/StarFive host drivers.

Important APIs/types/functions: The menu is `PLDA-based PCIe controllers` and depends on `PCI`. `PCIE_PLDA_HOST` is a hidden bool selecting `IRQ_MSI_LIB`. `PCIE_MICROCHIP_HOST` is a tristate depending on `PCI_MSI && OF`, selects `PCI_HOST_COMMON` and `PCIE_PLDA_HOST`, and describes Microchip AXI PCIe host bridge support. `PCIE_STARFIVE_HOST` is a tristate depending on `PCI_MSI && OF` and `ARCH_STARFIVE || COMPILE_TEST`, selects `PCIE_PLDA_HOST`, and builds module `pcie-starfive.ko` when modular.

Control flow: No runtime control flow. During kernel configuration, enabling a concrete PLDA host driver selects the shared helper object and MSI library support needed by the source files in this directory.

State and persistence: Kconfig choices persist in the generated kernel `.config` and determine which objects are compiled built-in or as modules.

Dependencies/integration: Integrates with the PCI controller Kconfig hierarchy and the sibling `Makefile`. It controls compilation of `pcie-plda-host.o`, `pcie-microchip-host.o`, and `pcie-starfive.o`.

Risks: The concrete drivers require `PCI_MSI`; systems without MSI cannot build these host drivers. `PCIE_PLDA_HOST` is hidden and selected, so dependency mistakes in concrete drivers can produce missing helper symbols. `COMPILE_TEST` broadens StarFive coverage beyond native architecture and must not imply runtime support.

Test signals: `olddefconfig` and menuconfig visibility, builds for Microchip and StarFive as built-in and modules, dependency checks with `PCI_MSI=n`, and link coverage that shared PLDA symbols are present when either concrete driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Makefile

Purpose: Maps PLDA PCIe Kconfig symbols to build objects.

Important APIs/types/functions: `obj-$(CONFIG_PCIE_PLDA_HOST) += pcie-plda-host.o` builds the shared PLDA host helper. `obj-$(CONFIG_PCIE_MICROCHIP_HOST) += pcie-microchip-host.o` builds the Microchip host driver. `obj-$(CONFIG_PCIE_STARFIVE_HOST) += pcie-starfive.o` builds the StarFive host driver.

Control flow: No runtime flow. Kbuild expands these assignments based on `.config`, compiling objects built-in or into modules according to the tristate values inherited from Kconfig.

State and persistence: Build output state is controlled by generated configuration. The file itself is declarative and has no runtime state.

Dependencies/integration: Must remain consistent with `plda/Kconfig` symbols and with actual source filenames in the same directory. It participates in the parent PCI controller Makefile traversal.

Risks: A symbol/name mismatch silently drops a driver from the build or causes a missing object error. Because `PCIE_PLDA_HOST` is selected by concrete drivers, disabling or renaming the shared object breaks both Microchip and StarFive builds.

Test signals: `make drivers/pci/controller/plda/` with each relevant config, module builds for Microchip/StarFive, and allmodconfig/allyesconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Makefile -->
