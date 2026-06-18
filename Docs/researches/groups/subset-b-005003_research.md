# subset-b-005003 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-tegra.c

## Purpose
`pci-tegra.c` is the NVIDIA Tegra PCIe host controller driver for Tegra20, Tegra30, Tegra124, Tegra210, and Tegra186 style root complexes. It owns controller bring-up, AFI/PADS register programming, per-root-port enablement, dynamic configuration-space windowing, MSI interrupt delivery, runtime/system PM, link training, and debugfs visibility for root-port link state.

## Important APIs, Types, And Functions
The main state is split between `struct tegra_pcie`, `struct tegra_pcie_port`, `struct tegra_msi`, and SoC descriptor tables `struct tegra_pcie_soc` / `struct tegra_pcie_port_soc`. `tegra_pcie_ops` provides `map_bus`, `read`, and `write` PCI config operations. `tegra_pcie_probe()` allocates a `pci_host_bridge`, parses DT child ports, requests clocks/resets/PHYs/regulators/MMIO/IRQs, sets up MSI, enables runtime PM, and calls `pci_host_probe()`. `tegra_pcie_pm_resume()` is the main hardware programming path: power on, default pinctrl, AFI setup, translation windows, MSI restore, PEX clock/reset, PHY power, pad settings, and port/link enablement. MSI uses `msi_create_parent_irq_domain()`, `tegra_msi_domain_alloc()`, `tegra_compose_msi_msg()`, and chained `tegra_pcie_msi_irq()`.

## Control Flow, State, And Persistence
Device-tree children describe each root port by `reg`, `nvidia,num-lanes`, optional reset GPIO, and availability. Parsed ports are stored in `pcie->ports`; failed links are disabled and removed from the list during `tegra_pcie_enable_ports()`. Config-space access is non-ECAM: bus 0 maps to each root port's config block, while downstream buses reprogram AFI BAR0 to move a 4 KiB config window. Hardware register state is not persistent; it is reconstructed on resume from in-memory driver state and static SoC descriptors. MSI allocation state persists only in the `msi->used` bitmap and is restored to `AFI_MSI_EN_VEC()` during resume.

## Dependencies And Integration Points
The driver integrates with OF PCI parsing, `pci_host_bridge`, IRQ domains, generic MSI library, debugfs, runtime PM, Tegra PMC powergating, Tegra cpuidle notifications, regulators, clocks, resets, pinctrl, GPIO, and generic PHY. It registers PCI fixups for Tegra root-port class and relaxed ordering. SoC compatibility data determines lane crossbar encodings, power supplies, Gen2 support, PADS PLL offsets, CML clock use, PME bits, ECTL programming, and hardware errata workarounds.

## Risks And Test Signals
Risk centers on hardware sequencing and DT correctness: invalid lane layouts fail probe, missing/legacy regulators change power behavior, config-window reprogramming must be serialized by PCI core assumptions, and link training can add boot latency when slots are empty. MSI paths depend on a 32-bit coherent DMA doorbell page and correct masking under `mask_lock`. Suspend/resume should be tested with active MSI devices, empty ports, Gen1-to-Gen2 retraining, PME turnoff, and legacy plus per-lane PHY bindings. Good signals are successful `pci_host_probe()`, stable enumeration after resume, no AFI error interrupts except expected master aborts during probing, populated `/sys/kernel/debug/pcie/ports`, and working INTx/MSI interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-ecam.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-ecam.c

## Purpose
`pci-thunder-ecam.c` provides Cavium Thunder ECAM host support and quirks for Thunder on-chip PCI devices whose config space is ECAM-like but contains incomplete or incorrect capability/BAR information. It wraps generic ECAM access with synthesized Enhanced Allocation capability data, BAR read suppression, BAR write filtering, and pass-2 high-address correction.

## Important APIs, Types, And Functions
The exported integration object is `pci_thunder_ecam_ops`, a `struct pci_ecam_ops` with `pci_ecam_map_bus`, `thunder_ecam_config_read()`, and `thunder_ecam_config_write()`. Helper `set_val()` extracts byte/word/dword values from synthesized dwords. `handle_ea_bar()` constructs EA entry fragments from real BAR sizing behavior. `thunder_ecam_p2_config_read()` fixes pass-2 EA high-base bits using the config window start address. The platform driver binds `"cavium,pci-host-thunder-ecam"` to `pci_host_common_probe()`.

## Control Flow, State, And Persistence
Reads first inspect header type and class revision. Pass-2 endpoints with type-0 headers delegate selected EA high-dword reads to `thunder_ecam_p2_config_read()`. Older devices hide fixed BARs by returning zero for normal and SR-IOV BAR reads, then synthesize capability-chain links and EA entries for NIC, TNS, MSI-X, and several bridge devfns. Writes to fixed BAR regions are ignored so generic PCI sizing and assignment cannot corrupt firmware/hardware fixed mappings. The driver stores no mutable per-controller state beyond the common `pci_config_window`; all behavior is derived from config reads and the ECAM resource.

## Dependencies And Integration Points
This file depends on `linux/pci-ecam.h`, generic PCI config helpers, OF matching, and `pci-host-common`. It is also compiled for ACPI quirk paths when ACPI and PCI quirks are enabled, because Thunder ECAM operations are reused outside the OF platform driver.

## Risks And Test Signals
The synthesized capability chain is device-specific and can break enumeration if device IDs, revisions, header types, or capability offsets differ from the assumed Thunder parts. BAR sizing emulation intentionally writes all ones to real BARs and restores the original value, so it must only touch safe fixed BAR registers. Test with NIC/TNS/bridge devices should show stable EA capabilities, zeroed fixed BARs, no corrupted BAR assignments after enumeration, correct node bit in pass-2 high base reads, and no `Bad MSI-X cap header` or `Bad PCIe cap header` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-ecam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-pem.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-pem.c

## Purpose
`pci-thunder-pem.c` supports Cavium Thunder PEM PCIe root bridges, where the root bridge itself uses a PEM-specific indirect config access mechanism while devices behind it use ECAM. It also synthesizes fixed MSI-X/EA capability information and supports both OF and ACPI firmware descriptions, including legacy ACPI resource reconstruction.

## Important APIs, Types, And Functions
`struct thunder_pem_pci` stores synthesized EA entry dwords and the PEM register base. `thunder_pem_bridge_read()` and `thunder_pem_bridge_write()` implement indirect 32-bit config cycles via `PEM_CFG_RD` and `PEM_CFG_WR`. `thunder_pem_config_read()` / `thunder_pem_config_write()` route bus-start/devfn0 accesses to the bridge helpers and all other accesses to generic ECAM. `thunder_pem_init()` maps the PEM register space and constructs EA data for the fixed MSI-X BAR. `thunder_pem_ecam_ops` is the ACPI-facing ops object; `pci_thunder_pem_ops` is used by the OF platform driver.

## Control Flow, State, And Persistence
Initialization maps the PEM register block and stores `struct thunder_pem_pci` in `cfg->priv`. Reads of bridge config space trigger an indirect read, then patch capability pointers, PME vector, MSI-X table/PBA offsets, EA header, and EA entry dwords. Writes smaller than dword are expanded by read-modify-write; W1C bits are masked to avoid accidental clearing, and selected fields are forced to one to emulate read-only behavior. No persistent disk state exists; runtime state is the mapped PEM base plus EA values derived from the PEM resource start/end.

## Dependencies And Integration Points
The driver integrates with `pci-host-common`, generic ECAM, ACPI PCI root helpers, OF resources, `request_mem_region()` for legacy reservation, and Cavium-specific ACPI resource lookup via `"CAVA02B"`. It uses a non-standard `THUNDER_PCIE_ECAM_BUS_SHIFT` value of 24.

## Risks And Test Signals
Main risks are incorrect root segment/node/index reconstruction for legacy ACPI firmware, accidental W1C status clearing during sub-dword writes, and capability synthesis mismatches between T88 and other variants. Test signals include correct root bridge enumeration at bus start, preserved status bits after byte/word config writes, valid MSI-X and EA capability layout, ACPI systems reserving PEM/config resources without conflicts, and downstream devices using normal ECAM after the bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-thunder-pem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-v3-semi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-v3-semi.c

## Purpose
`pci-v3-semi.c` drives the V3 Semiconductor V360EPC PCI local-bus-to-PCI bridge, notably on ARM Integrator/AP systems. It programs local-bus windows for PCI memory, I/O, config cycles, inbound DMA ranges, error interrupts, FIFO policy, and reset sequencing for a legacy non-ECAM host bridge.

## Important APIs, Types, And Functions
`struct v3_pci` stores device/MMIO state, config window base, non-prefetchable and prefetchable local memory windows, bus addresses, and optional Integrator syscon regmap. `v3_pci_ops` provides `v3_map_bus()`, `v3_pci_read_config()`, and `v3_pci_write_config()`. `v3_pci_probe()` allocates the host bridge, enables the clock, maps controller/config resources, installs the error IRQ, programs bridge windows, parses `dma-ranges`, handles Integrator-specific reset/syscon setup, and calls `pci_host_probe()`.

## Control Flow, State, And Persistence
Config access temporarily repurposes local-bus window 1 for PCI config cycles. `v3_map_bus()` expands non-prefetchable memory window 0 to 512 MiB, maps window 1 to config space, returns the config address, and then read/write wrappers call `v3_unmap_bus()` to restore window 1 as prefetchable memory and shrink window 0 back to 256 MiB. Probe disables PCI slave access, asserts reset, enables retry, configures endianness/byte-enable mode, programs outbound windows from host bridge resources, programs up to two inbound DMA windows, enables interrupts, deasserts reset, and locks the system register. Hardware state is volatile and reprogrammed only on probe; the driver has no PM hooks.

## Dependencies And Integration Points
The driver depends on OF PCI host bridge resources, `dma-ranges`, `devm_pci_alloc_host_bridge()`, clocks, platform IRQs, syscon/regmap for `"arm,integrator-ap-syscon"`, and generic PCI config helpers. It expects exact 256 MiB prefetchable and non-prefetchable windows, a 16 MiB config resource, and at most two inbound DMA mappings.

## Risks And Test Signals
The largest risk is temporary window remapping during config access; broken serialization or unexpected overlapping-window behavior would corrupt memory or config transactions. Resource geometry is strict, so malformed DT windows fail probe. DMA range sizes must match hardware encodings. Test by enumerating devices behind both bus 0 and subordinate buses, validating memory/I/O windows, forcing config reads after normal memory traffic, checking parity/master/target abort interrupt logs, and verifying Integrator reset/mailbox initialization on compatible boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-v3-semi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-versatile.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-versatile.c

## Purpose
`pci-versatile.c` is the ARM Versatile PCI host bridge driver. It maps Versatile PCI controller registers and config windows, finds the FPGA PCI core's own slot, hides that slot from normal enumeration, sets inbound SDRAM mappings, and registers a basic PCI host bridge.

## Important APIs, Types, And Functions
Global MMIO pointers `versatile_pci_base` and `versatile_cfg_base[]` back the controller and type/config spaces. `versatile_map_bus()` returns config-space addresses unless the target slot is in `pci_slot_ignore`. `pci_versatile_ops` uses `pci_generic_config_read32` and `pci_generic_config_write`. `versatile_pci_probe()` maps resources, programs outbound memory maps from host bridge windows, discovers the local PCI core, enables memory/master/invalidate on it, writes BAR0-2 to SDRAM, sets a QEMU compatibility signal, and calls `pci_host_probe()`.

## Control Flow, State, And Persistence
Boot parameter `pci_slot_ignore=` updates the global ignore bitmap before probing. Probe scans 32 slots through config base 0 for fixed device/class IDs, then adds the discovered local slot to the ignore bitmap and writes `PCI_SELFID`. All config accesses use config base 1 with bus/devfn/offset addressing. Runtime state is global and process-lifetime only; hardware mappings are programmed once at probe and there are no suspend/resume paths.

## Dependencies And Integration Points
The driver integrates with OF platform matching `"arm,versatile-pci"`, generic PCI host bridge allocation, host bridge window parsing, ARM `PAGE_OFFSET` physical mapping, PCI reassignment flags, and QEMU's historic IRQ mapping compatibility behavior.

## Risks And Test Signals
The driver assumes a single controller and uses global state, so multiple instances are not safe. It depends on finding the local PCI core and on SDRAM identity-style inbound mapping. Test signals are detection of the PCI core slot, hidden self device during enumeration, working reassigned resources, correct IRQ behavior on modern QEMU and hardware, and functional config reads for non-ignored slots. Failure to find `VP_PCI_DEVICE_ID`/`VP_PCI_CLASS_ID` is a hard probe error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene-msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene-msi.c

## Purpose
`pci-xgene-msi.c` implements the APM X-Gene v1 PCIe MSI controller. It exposes a PCI MSI parent domain backed by 16 MSI termination frames, statically partitions frame targeting across CPUs, composes endpoint MSI messages, and chains per-frame GIC interrupts into Linux MSI IRQs.

## Important APIs, Types, And Functions
`struct xgene_msi` stores the MSI IRQ domain, physical MSI register base, mapped registers, allocation bitmap, bitmap mutex, and 16 GIC IRQs. `xgene_allocate_domains()` creates the MSI parent irq domain using `xgene_msi_domain_ops` and `xgene_msi_parent_ops`. `xgene_irq_domain_alloc()` allocates one vector from `NR_MSI_VEC`, installs `xgene_msi_bottom_irq_chip`, and enables resend behavior. `xgene_compose_msi_msg()` selects a target frame from effective CPU affinity. `xgene_msi_isr()` reads `MSIINTn`, then read-to-clear `MSInIRx`, computes hwirqs, and dispatches `generic_handle_domain_irq()`.

## Control Flow, State, And Persistence
Probe allocates a single global `xgene_msi_ctrl`, maps the MSI register region, records its physical start as the endpoint doorbell base, initializes the bitmap, creates the domain, clears stale read-to-clear state, obtains 16 platform IRQs, pins each GIC IRQ to a CPU modulo `num_possible_cpus()`, and installs chained handlers. Runtime state is the allocation bitmap and GIC IRQ table. There is no persistent state and no PM restoration path in this file.

## Dependencies And Integration Points
The MSI host matches `"apm,xgene1-msi"` and is checked by `pci-xgene.c` before root complex probing. It depends on IRQ domains, generic MSI library, chained IRQ helpers, CPU affinity APIs, OF PCI, and platform IRQ resources. The static global implies a single MSI controller instance.

## Risks And Test Signals
Capacity is reduced from raw hardware vectors to `NR_MSI_VEC` because vectors are reserved congruently across CPU frame groups. Affinity composition assumes CPU indices fit the frame convention; unusual CPU counts should be tested. Read-to-clear MSI registers make interrupt-loss bugs possible if handling order changes. Test signals are successful MSI domain discovery by the X-Gene PCIe driver, clean stale IRQ clearing at probe, endpoint MSI/MSI-X delivery on multiple CPUs, affinity changes causing regenerated MSI messages, and no `unexpected MSI`/WARN reports under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene.c

## Purpose
`pci-xgene.c` drives APM X-Gene PCIe root complexes for OF systems and supplies ACPI ECAM ops for X-Gene v1/v2 quirks. It programs controller CSR/CFG windows, outbound and inbound address translations, DMA ranges, root-port IDs, config access behavior, and link status reporting.

## Important APIs, Types, And Functions
`struct xgene_pcie` stores OF/device pointers, clock, CSR/config bases, config physical address, link state, and IP version. PCI operations are `xgene_pcie_map_bus()`, `xgene_pcie_config_read32()`, and generic writes. `xgene_pcie_setup()` clears firmware mappings, writes vendor/device IDs, programs outbound ranges via `xgene_pcie_map_ranges()`, maps inbound DMA ranges via `xgene_pcie_parse_map_dma_ranges()`, and reports link status. ACPI paths export `xgene_v1_pcie_ecam_ops` and `xgene_v2_pcie_ecam_ops`.

## Control Flow, State, And Persistence
Config access rejects nonzero devfn on the root bus and hides root BAR0/BAR1 because they are used for PCI-to-native translation. It writes `RTDID` before each config access so hardware emits the right BDF. Root-bus reads clear the v1 RRS Software Visibility bit to avoid endless retries on nonexistent devices. Probe defers until the X-Gene MSI domain is ready when `CONFIG_PCI_XGENE_MSI` and the MSI node exist. Hardware translation state is built at probe and not persisted; the in-memory state records only mapping bases, clock, and link status.

## Dependencies And Integration Points
The driver uses OF/ACPI PCI helpers, generic ECAM for ACPI, clocks, memblock headers, host bridge resource windows, `dma-ranges`, X-Gene MSI readiness detection, and generic PCI host probing. It expects named OF resources `"csr"` and `"cfg"` for platform mode.

## Risks And Test Signals
Risks include invalid inbound DMA range sizing or exceeding three hardware inbound regions, hidden root BAR behavior confusing diagnostics, and config retries if the v1 RRS quirk regresses. Outbound memory windows below minimum sizes only warn while still programming masks, so resource tests matter. Signals include deferred probe until MSI is present, correct `RTDID`-based config access for subordinate buses, endpoints DMAing through programmed PIMs, root BARs not being assigned by PCI core, and accurate link-up lane/speed messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera-msi.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera-msi.c

## Purpose
`pcie-altera-msi.c` is the companion MSI controller for Altera PCIe. It maps the MSI CSR and vector slave regions, creates a PCI MSI parent domain, allocates up to the DT-provided vector count, composes per-vector MSI doorbell addresses, and dispatches chained controller interrupts.

## Important APIs, Types, And Functions
`struct altera_msi` stores the vector allocation bitmap, mutex, platform device, inner MSI domain, CSR/vector MMIO bases, vector physical base, vector count, and parent IRQ. `altera_msi_isr()` loops over `MSI_STATUS`, clears each pending vector by dummy-reading the vector slave address, and invokes `generic_handle_domain_irq()`. `altera_irq_domain_alloc()` allocates one vector, installs `altera_msi_bottom_irq_chip`, and sets `MSI_INTMASK`. `altera_compose_msi_msg()` points endpoints at `vector_phy + hwirq * 4`.

## Control Flow, State, And Persistence
Probe maps `"csr"` and `"vector_slave"`, reads `num-vectors`, creates the MSI parent domain, obtains the platform IRQ, and installs a chained handler. Allocation/free updates the `used` bitmap and the hardware interrupt mask. Removal masks all vectors, removes the chained handler, removes the IRQ domain, and clears drvdata. There is no persistent storage or suspend/resume restoration; state is volatile controller registers plus the in-memory bitmap.

## Dependencies And Integration Points
The driver binds `"altr,msi-1.0"` and registers at `subsys_initcall`, early enough for host bridge probing. It depends on IRQ domains, `irq-msi-lib`, generic MSI flags, OF resource mapping, and platform IRQs. The main Altera host controller relies on this separate MSI provider when endpoints request MSI/MSI-X.

## Risks And Test Signals
`num-vectors` must not exceed the fixed `MAX_MSI_VECTORS` bitmap capacity; the code trusts DT enough that oversized values are a review concern. Only single-vector allocations are expected (`WARN_ON(nr_irqs != 1)`). Test with MSI and MSI-X endpoints should show vector-specific doorbell writes, `MSI_INTMASK` changes on allocation/free, status clearing via vector reads, clean removal, and no `unexpected MSI` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera-msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera.c

## Purpose
`pcie-altera.c` is the Altera/Intel FPGA PCIe root-port host driver for multiple IP generations. It implements custom config transactions using TLP FIFOs for v1, modified packet/direct-root access for Stratix 10 v2, and direct Agilex-style root/endpoint config mechanisms for v3. It also handles INTx/AER interrupt domains and link retraining.

## Important APIs, Types, And Functions
`struct altera_pcie` stores platform data, CRA/HIP bases, IRQ, root bus number, INTx domain, bus range, and version data. Version dispatch is through `struct altera_pcie_ops` and `struct altera_pcie_data`. Config operations enter `altera_pcie_cfg_read()` / `altera_pcie_cfg_write()`, validate link/device visibility, hide root BAR0, then call `_altera_pcie_cfg_read()` / `_altera_pcie_cfg_write()`. Key helpers include `tlp_read_packet()`, `s10_tlp_read_packet()`, `get_tlp_header()`, `aglx_ep_read_cfg()`, `altera_pcie_retrain()`, and version-specific ISRs.

## Control Flow, State, And Persistence
Probe selects OF match data, maps `"Cra"` and for v2/v3 `"Hip"`, installs a chained interrupt handler, creates a four-line INTx domain, clears/enables interrupts for v1/v2 or enables CFG/AER for v3, retrains links where useful, sets host bridge sysdata/ops, and calls `pci_host_probe()`. Config reads/writes either directly access root-port config, target Agilex endpoint windows after writing `AGLX_BDF_REG`, or build config TLP headers and wait for completions. The driver updates `root_bus_nr` when software writes `PCI_PRIMARY_BUS`, so bus-number state follows PCI core changes.

## Dependencies And Integration Points
The driver integrates with OF match strings for root-port 1.0, 2.0, and 3.0 F/P/R tile variants; generic PCI host bridge; irq domains; chained IRQs; and the separate Altera MSI provider. `bridge->child_ops` is not used here; config routing is internal to the `pci_ops`.

## Risks And Test Signals
Custom TLP completion polling can time out or mis-handle malformed packets. Byte-enable and alignment logic is critical for sub-dword config writes. V1/V2 root bus tracking must remain synchronized with PCI core bus renumbering. Agilex interrupt handling maps CFG/AER to a single domain hwirq. Test signals include successful root and subordinate config cycles, hidden RC BAR0, link retrain only when link is up and capable, INTx delivery for all four pins, AER/CFG interrupt handling on v3, and clean removal via `pci_stop_root_bus()`/`pci_remove_root_bus()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-apple.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-apple.c

## Purpose
`pcie-apple.c` drives Apple SoC PCIe host bridges. The controller is ECAM-compliant after initialization, so the driver mainly handles core/port bring-up, per-port interrupts, MSI routing, REFCLK/PERST sequencing, and RID-to-SID mappings needed for IOMMU/DART integration.

## Important APIs, Types, And Functions
`struct apple_pcie` holds controller state, global MSI bitmap, port list, event completion, parent IRQ fwspec, vector count, and hardware descriptor. `struct apple_pcie_port` tracks per-port MMIO, PHY, IRQ domain, RID/SID bitmap, and port index. `apple_pcie_probe()` allocates the host bridge, maps core base, initializes MSI, and calls `pci_host_common_init()` with `apple_pcie_cfg_ecam_ops`. `apple_pcie_init()` sets up each DT child port. `apple_pcie_enable_device()` and `apple_pcie_disable_device()` allocate/free RID-to-SID hardware entries for devices behind root ports.

## Control Flow, State, And Persistence
MSI setup parses `msi-ranges`, finds the wired parent IRQ domain, allocates a bitmap, and creates a PCI MSI parent domain. Each port setup asserts PERST, enables app/ref clocks, waits for PHY refclk acks, deasserts PERST, waits for port ready, creates a 32-hwirq port IRQ domain, programs MSI doorbell/mapping registers, discovers RID/SID table size by write/read probing, registers link up/down IRQ handlers, starts LTSSM, and waits briefly for link-up completion. State is in bitmaps and port lists; hardware register state is set during probe and not persisted to storage.

## Dependencies And Integration Points
The driver binds `"apple,pcie"` and `"apple,t6020-pcie"` with `hw_info` offsets. It integrates with generic ECAM/common host code, OF IRQ parsing, GPIO PERST, IRQ domains, generic MSI library, DART/IOMMU mapping via `iommu-map`, and PCI host bridge `enable_device`/`disable_device` hooks. The configured MSI doorbell address must be excluded from IOVA handling by platform integration.

## Risks And Test Signals
Risk areas include fixed 32-bit MSI doorbell assumptions, correct `msi-ranges` parsing, RID/SID table exhaustion, REFCLK handshake timeouts, and per-generation register offset differences. Test signals include ports reaching ready, link-up/down IRQs, working INTx and MSI/MSI-X, correct RID-to-SID mappings for devices behind each root port, clean SID release on device removal, and no `MSI_BAD_DATA`, RID2SID map errors, completion aborts, or link timeout warnings beyond intentionally empty slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-aspeed.c

## Purpose
`pcie-aspeed.c` is the ASPEED AST2600/AST2700 PCIe root complex driver. It programs H2X/SCU/AHBC setup, per-port clock/PHY/PERST sequencing, custom root and child config transactions, address remapping, INTx handling, and an integrated 64-vector MSI parent domain.

## Important APIs, Types, And Functions
`struct aspeed_pcie` stores host bridge, device, H2X register base, syscon regmaps, platform descriptor, port list, TX tag, root bus number, H2X reset, INTx/MSI domains, MSI bitmap, and AST2700 MSI-clear workaround state. `struct aspeed_pcie_rc_platform` selects setup, mapping, interrupt register offsets, and MSI doorbell address. Config paths are split into AST2600 (`aspeed_ast2600_conf()`) and AST2700 (`aspeed_ast2700_config()`, `aspeed_ast2700_child_config()`) operations. IRQ logic uses `aspeed_pcie_intr_handler()`, `aspeed_pcie_intx_map()`, `aspeed_irq_msi_domain_alloc()`, and `aspeed_irq_compose_msi_msg()`.

## Control Flow, State, And Persistence
Probe allocates the host bridge, records root bus number, maps H2X registers, gets H2X reset, initializes the mutex, runs platform setup, maps the first MEM range, parses DT child PCI ports, creates INTx/MSI domains, requests the shared IRQ, and calls `pci_host_probe()`. AST2600 setup unlocks AHBC, enables RC memory, resets H2X, enables RX/MSI paths, sets TX tags, and assigns root/child PCI ops. AST2700 setup programs SCU decode/path registers, disables endpoint function, resets H2X, enables direct bridge mode, prepares 64-bit prefetch remap, assigns ops, and enables double MSI status clearing. Runtime state includes TX tag and MSI allocation bitmap; hardware state is volatile and rebuilt at probe.

## Dependencies And Integration Points
The driver integrates with OF child port nodes (`device_type = "pci"` and devfn), clocks, generic PHY in RC mode, reset controls, syscon regmaps (`aspeed,ahbc` or `aspeed,pciecfg`), IRQ domains, MSI library, host bridge `ops`/`child_ops`, and shared platform IRQs. It uses `PROBE_PREFER_ASYNCHRONOUS`.

## Risks And Test Signals
Config transaction timeout windows are short, so slow or absent devices must return clean PCI errors. AST2600 root port is expected at slot 8, while AST2700 root bus accepts only devfn 0. MSI status handling differs by generation and AST2700 requires a double clear. Test signals include root and child config reads/writes, TX tag wraparound, MEM remap correctness, per-port PHY/clock/reset sequencing, INTx level handling, MSI/MSI-X vector allocation across both status registers, and no CR tx/rx timeout logs for present devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-aspeed.c -->
