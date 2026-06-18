# Research: subset-b-004998

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-j721e.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-j721e.c

Purpose: TI J721E-family Cadence PCIe wrapper driver. It binds Cadence core RC/EP support to TI user, interrupt, syscon, reset GPIO, runtime PM, PHY, lane-count, and link-down interrupt wiring for J721E, J7200, AM64, J784S4, and J722S compatible strings.

Important APIs/types/functions: `struct j721e_pcie`, `struct j721e_pcie_data`, `j721e_pcie_probe()`, `j721e_pcie_remove()`, `j721e_pcie_ctrl_init()`, `j721e_pcie_set_mode()`, `j721e_pcie_set_link_speed()`, `j721e_pcie_set_lane_count()`, `j721e_pcie_start_link()`, `j721e_pcie_stop_link()`, `j721e_pcie_link_up()`, `j721e_pcie_link_irq_handler()`, and PM callbacks. It plugs `j721e_pcie_ops` into `struct cdns_pcie_ops` and optionally uses `cdns_ti_pcie_host_ops` for 32-bit root-bus config access.

Control flow: probe selects RC or EP from match data, allocates a host bridge or endpoint structure, maps `intd_cfg` and `user_cfg`, validates `num-lanes`, enables runtime PM, programs syscon straps while power-cycling the controller, requests link-state IRQ, enables link-down reporting, initializes PHY, then calls `cdns_pcie_host_setup()` or `cdns_pcie_ep_setup()`. RC probe also handles optional reset GPIO, optional `pcie_refclk`, and PERST delay. Resume replays control setup, IRQ enable, PHY enable, RC link setup, BAR availability reset, and host address translation init.

State/persistence: runtime state is in `struct j721e_pcie`, Cadence RC/EP state, syscon strap bits, user link-training register, interrupt-distribution registers, PHY state, reset GPIO, and runtime PM usage. Configuration is reconstructed on resume; hardware strap values are latched through the deliberate PM power-cycle in `j721e_pcie_ctrl_init()`.

Dependencies/integration: Linux platform, GPIO, clock, runtime PM, regmap/syscon, IRQ, PCI host bridge, PCI endpoint, and Cadence common host/EP libraries. DT properties include `ti,syscon-pcie-ctrl`, optional `ti,syscon-acspcie-proxy-ctrl`, `num-lanes`, `max-link-speed`, resources, IRQs, PHYs, reset GPIO, and SoC compatible data.

Risks: strap programming depends on power-cycle ordering; failures before the second `pm_runtime_get_sync()` can leave the controller off. Lane masks differ for one-, two-, and four-lane devices. Link setup logs timeout but Cadence host setup currently treats some link failures as non-fatal. RC root config byte access differs by SoC, so the wrong `byte_access_allowed` setting can break config cycles. Link-down IRQ only logs and clears status; it does not recover the link.

Test signals: boot and enumerate on each compatible in RC mode, endpoint function binding in EP mode, link-down IRQ clear behavior, PERST timing, suspend/resume with link restoration, max-link-speed programming, x1/x2/x4 lane programming, 32-bit-only root config access on J721E/J784S4, and no leaked runtime PM reference on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-j721e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-sky1.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-sky1.c

Purpose: CIX Sky1 PCIe host glue for the Cadence HPA controller. It supplies Sky1 register-bank offsets, ECAM config-space setup, link-training control through strap registers, link-up detection through the HPA debug-status register, and host setup quirks.

Important APIs/types/functions: `struct sky1_pcie`, `sky1_pcie_resource_get()`, `sky1_pcie_start_link()`, `sky1_pcie_stop_link()`, `sky1_pcie_link_up()`, `sky1_pcie_probe()`, and `sky1_pcie_remove()`. `sky1_pcie_ops` implements Cadence link operations. Probe fills `struct cdns_plat_pcie_of_data` offsets and calls `cdns_pcie_hpa_host_setup()`.

Control flow: probe allocates `struct sky1_pcie` and a PCI host bridge, maps `reg`, `cfg`, `rcsu_strap`, `rcsu_status`, and `msg`, creates a generic ECAM window from the bridge bus range, installs ECAM pci_ops, sets HPA ECAM mode and root-port IDs, marks inbound mapping disabled, records register-bank offsets, and starts HPA host setup. Link start/stop toggles `LINK_TRAINING_ENABLE` in `STRAP_REG(1)`; link-up checks bit 0 in `IP_REG_I_DBG_STS_0`.

State/persistence: the driver stores ECAM resources and Cadence RC state in `struct sky1_pcie` and `struct cdns_pcie_rc`. Persistent hardware effects are HPA outbound windows, optional message region, strap link-training bit, root-port vendor/device IDs, and ECAM mapping. Remove only frees the ECAM window, relying on devm for mappings.

Dependencies/integration: platform resources, `pci_ecam_create()`, generic ECAM ops, Cadence HPA host/common code, and DT compatible `cix,sky1-pcie-host`. It uses the HPA register-bank abstraction from `pcie-cadence.h`.

Risks: `sky1_pcie_remove()` does not call `cdns_pcie_host_disable()`, so teardown coverage depends on platform lifetime expectations. The `struct cdns_plat_pcie_of_data` is allocated and filled manually despite only offsets being used. `rcsu_status` is mapped but not read. Inbound map is disabled, so DMA translation assumptions must be validated by platform/IOMMU design. Wrong bank offsets would misprogram HPA translation registers.

Test signals: ECAM root and child config access, link train/stop register toggles, HPA link-up polling, message region setup, enumeration under generic ECAM ops, removal/unbind behavior, and DMA/IOMMU behavior with `no_inbound_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-sky1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-ep.c

Purpose: Cadence PCIe endpoint controller implementation for the Linux PCI EPC framework. It programs endpoint configuration headers, BAR apertures, inbound BAR translations, outbound mappings, MSI/MSI-X/INTx delivery, SR-IOV VF addressing, function enablement, and endpoint startup.

Important APIs/types/functions: EPC callbacks in `cdns_pcie_epc_ops`: `cdns_pcie_ep_write_header()`, `cdns_pcie_ep_set_bar()`, `cdns_pcie_ep_clear_bar()`, `cdns_pcie_ep_map_addr()`, `cdns_pcie_ep_unmap_addr()`, MSI/MSI-X setters/getters, `cdns_pcie_ep_raise_irq()`, `cdns_pcie_ep_map_msi_irq()`, and `cdns_pcie_ep_start()`. Public setup/teardown are `cdns_pcie_ep_setup()` and `cdns_pcie_ep_disable()`.

Control flow: setup maps `reg` and `mem`, reads outbound-region and function/VF counts, disables all but function 0, creates the EPC, initializes endpoint memory, allocates a 128 KiB IRQ scratch window, reserves outbound region 0 for IRQs, applies detect-quiet quirk, and notifies EPC init. BAR setup computes the next power-of-two aperture, writes local-management BAR control, resolves PF/VF hardware function numbers, and writes inbound BAR target addresses. Outbound map finds a free region and calls Cadence common translation programming. IRQ delivery reuses region 0 for normal messages, MSI writes, or MSI-X table target writes.

State/persistence: runtime state is `struct cdns_pcie_ep`: outbound region bitmap/address table, IRQ CPU/PCI mapping cache, pending INTx bitmap, spinlock, EPF BAR pointers, function/VF allocation, and quirk flags. Hardware state includes LM function enable bits, BAR config, inbound/outbound AT windows, PCI config capability fields, and interrupt status.

Dependencies/integration: Cadence common helpers, Linux `pci_epc`/`pci_epf`, endpoint memory allocator, PCI capability helpers, platform resources, and optional DT properties `cdns,max-outbound-regions`, `max-functions`, and `max-virtual-functions`.

Risks: outbound region allocation is limited by `BITS_PER_LONG` and reserves region 0, so high region counts need review. VF handling only programs VF BAR config for `vfn == 1`; other VFs rely on computed function mapping. MSI-X assumes the selected BAR pointer and table memory are valid. INTx status updates rely on a narrow spinlock because remote RC and local EP can both touch PCI status. The code does not range-check all capability offsets before using them.

Test signals: EPC function binding, PF and VF header writes, 32/64-bit and prefetch BAR sizing, BAR clear, outbound map exhaustion, INTx assert/deassert, MSI vector counts and writes, MSI-X table/PBA placement, SR-IOV VF #1 device ID, link start, and endpoint teardown freeing EPC memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.c

Purpose: common host-side library shared by classic Cadence and HPA Cadence host drivers. It handles link wait/retrain policy and maps host bridge DMA ranges into Cadence root-port inbound BAR resources.

Important APIs/types/functions: `bar_max_size`, `cdns_pcie_host_training_complete()`, `cdns_pcie_host_wait_for_link()`, `cdns_pcie_retrain()`, `cdns_pcie_host_start_link()`, BAR selectors `cdns_pcie_host_find_min_bar()` and `cdns_pcie_host_find_max_bar()`, `cdns_pcie_host_dma_ranges_cmp()`, `cdns_pcie_host_bar_config()`, and `cdns_pcie_host_map_dma_ranges()`.

Control flow: link start waits for platform-specific link-up, then optionally retrains if a quirk is set and the link came up at Gen1 despite higher capability. DMA mapping either programs an RP_NO_BAR catch-all when no `dma-ranges` exist, or sorts bridge DMA ranges largest-first and splits each range across the smallest fitting available BAR or the largest BAR chunk that can fit part of the range. The actual hardware write is delegated through a callback so classic and HPA layouts can share the algorithm.

State/persistence: BAR availability lives in `rc->avail_ib_bar[]`; this library marks entries used indirectly through the callback. Hardware state persists in inbound address-translation and root BAR registers written by the caller-specific callback. No durable state survives controller reset; resume paths reset `avail_ib_bar` and replay mapping.

Dependencies/integration: PCI host bridge private data, bridge `dma_ranges`, OF helper for `cdns,no-bar-match-nbits`, list sorting, Cadence RC structures, and caller callbacks from `pcie-cadence-host.c` or `pcie-cadence-host-hpa.c`.

Risks: all sizes are assumed power-of-two compatible when passed to callbacks. Splitting consumes a limited three-entry BAR namespace; unusual or many DMA ranges can fail. `bar_max_size[RP_BAR0]` is very large while BAR aperture masks differ by architecture, so callback correctness matters. Link retraining only triggers under a narrow speed condition and may not help other training failures.

Test signals: no-`dma-ranges` fallback, multiple sorted DMA ranges, large range splitting, BAR exhaustion, Gen2 retrain on affected hardware, training timeout, and replay after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.h

Purpose: declaration header for shared Cadence host helper code. It defines the callback types used to abstract classic versus HPA inbound BAR programming and exports the common link and DMA-range mapping helpers.

Important APIs/types/functions: `extern u64 bar_max_size[]`, typedefs `cdns_pcie_host_bar_ib_cfg` and `cdns_pcie_linkup_func`, plus prototypes for link training/wait/retrain, BAR selection, DMA range sorting, classic BAR config, generic BAR config, and DMA-range mapping.

Control flow: no executable flow is present. The header establishes the contract used by `pcie-cadence-host.c`, `pcie-cadence-host-hpa.c`, and SoC glue that wants shared link setup or DMA inbound mapping.

State/persistence: no state is allocated here. The callback signatures shape state transitions in `struct cdns_pcie_rc`, especially `avail_ib_bar[]`, and hardware inbound translation state in the implementation files.

Dependencies/integration: depends on Linux PCI/resource types and on Cadence types from `pcie-cadence.h` being visible to users. It is an internal driver-family interface, not a firmware or user ABI.

Risks: callback type changes must be synchronized across both classic and HPA host implementations. The header declares `cdns_pcie_host_bar_ib_config()` although HPA users use a private equivalent, so mistaken linkage can pick the wrong register layout. Since `bar_max_size` is global, consumers must treat it as read-only policy.

Test signals: compile coverage for both `CONFIG_PCIE_CADENCE_HOST` and HPA users, callback prototype compatibility, and successful DMA-range mapping through both classic and HPA callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-hpa.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-hpa.c

Purpose: host-mode support for Cadence High Performance Architecture PCIe controllers. It provides HPA config-space mapping, root-port setup, PTM response enablement, inbound/outbound address translation, ECAM/non-ECAM config-region handling, and host probing.

Important APIs/types/functions: `cdns_pci_hpa_map_bus()`, `cdns_pcie_hpa_host_bar_ib_config()`, `cdns_pcie_hpa_host_init_root_port()`, `cdns_pcie_hpa_create_region_for_cfg()`, `cdns_pcie_hpa_host_init_address_translation()`, `cdns_pcie_hpa_host_link_setup()`, and public `cdns_pcie_hpa_host_setup()`.

Control flow: setup marks RC mode, maps `reg` and `cfg` unless the glue already did, clears EROM aperture, starts link through platform ops and HPA link polling, resets BAR availability, initializes root-port class/IDs/command bits, programs config region 0 when ECAM is not provided, optionally maps a message region, maps bridge IO/MEM windows to HPA outbound regions, maps DMA ranges unless disabled, installs HPA pci_ops if needed, then calls `pci_host_probe()`.

State/persistence: RC state includes `ecam_supported`, `no_inbound_map`, `cfg_base`, `cfg_res`, `msg_res`, and BAR availability. Hardware state is distributed across HPA register banks: RP config, IP config control, AXI slave outbound regions, AXI master inbound BARs, tag management, and PTM controls.

Dependencies/integration: shared host-common DMA mapping, HPA register definitions, `cdns_pcie_hpa_*` common functions, PCI host bridge resources, optional ECAM setup from glue drivers such as Sky1, and platform link ops.

Risks: register-bank offsets must be correct for every platform. `cdns_pci_hpa_map_bus()` does not explicitly reject config cycles when link is down, unlike the classic path. RP_NO_BAR is remapped to BAR0 control fields in HPA inbound setup, which is subtle. ECAM and non-ECAM paths program different config access machinery, so glue must set `ecam_supported` and `cfg_base` accurately.

Test signals: ECAM and non-ECAM enumeration, config type0/type1 cycles, message outbound region, DMA inbound ranges, `no_inbound_map`, root command bits, PTM enable, link timeout propagation, and register traces in all HPA banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-hpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host.c

Purpose: classic Cadence PCIe host controller implementation. It maps PCI config space through outbound region 0, initializes the root port, programs outbound IO/MEM windows, configures inbound DMA BARs, starts the link, and registers the root bus.

Important APIs/types/functions: `cdns_pci_map_bus()`, `cdns_pcie_host_init_root_port()`, `cdns_pcie_host_bar_ib_config()`, `cdns_pcie_host_init_address_translation()`, `cdns_pcie_host_link_setup()`, `cdns_pcie_host_init()`, `cdns_pcie_host_disable()`, and `cdns_pcie_host_setup()`. It exports `cdns_pci_map_bus`, `cdns_pcie_host_bar_ib_config`, `cdns_pcie_host_init`, `cdns_pcie_host_link_setup`, `cdns_pcie_host_disable`, and `cdns_pcie_host_setup`.

Control flow: host setup maps `reg` and `cfg`, starts the link, marks all inbound BARs available, initializes root port IDs/class/ASPM quirks, reserves outbound region 0 for config cycles, maps bridge windows to outbound regions 1..N, maps DMA ranges through inbound BARs, installs pci_ops when the bridge has none, and calls `pci_host_probe()`. Config access to non-root buses rewrites region 0 bus/devfn/type registers per access.

State/persistence: state is held in `struct cdns_pcie_rc` and host bridge resources. Hardware persistence includes root-port config registers, BAR config, inbound and outbound AT windows, PTM response enable, and link-training bit controlled by platform ops. Disable removes the root bus, deinitializes AT/root-port state, stops link, and disables PTM response.

Dependencies/integration: PCI host bridge framework, Cadence common translation helpers, platform resources named `reg` and `cfg`, optional DT `vendor-id` and `device-id`, and platform-specific `cdns_pcie_ops`.

Risks: `cdns_pcie_host_link_setup()` returns 0 even when `cdns_pcie_host_start_link()` reports the link never came up, so enumeration may continue after link failure. In `cdns_pcie_host_unmap_dma_ranges()`, BAR config reset writes a complemented mask value rather than preserving unrelated bits, which needs hardware validation. Outbound region count is not checked against bridge window count here.

Test signals: root-only config access rejection for nonzero devfn, downstream config cycles, IO and MEM outbound windows, DMA inbound `dma-ranges`, ASPM L0s/L1 quirk masking, link timeout behavior, host disable/remove, and resume replay through users such as J721E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa-regs.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa-regs.h

Purpose: register-definition header for Cadence HPA PCIe controllers. It describes HPA register-bank base offsets, RP config offsets, BAR control encodings, outbound/inbound translation register layouts, PTM, link status, detect-quiet, tag management, and miscellaneous platform fields.

Important APIs/types/functions: macros for HPA banks (`CDNS_PCIE_HPA_IP_REG_BANK`, `CDNS_PCIE_HPA_AXI_SLAVE`, `CDNS_PCIE_HPA_AXI_MASTER`), BAR config (`CDNS_PCIE_HPA_LM_RC_BAR_CFG`, `HPA_LM_RC_BAR_CFG_*`), outbound regions (`CDNS_PCIE_HPA_AT_OB_REGION_*`), inbound RP/EP BAR addresses, link/debug registers (`CDNS_PCIE_HPA_PHY_DBG_STS_REG0`), and control bits like `CDNS_PCIE_HPA_AT_OB_REGION_CTRL0_SUPPLY_BUS`.

Control flow: no runtime flow. These macros are consumed by HPA common and host code to calculate offsets and bitfields for each register write.

State/persistence: no software state is allocated. The definitions encode hardware state layout; changes alter all compiled HPA register programming.

Dependencies/integration: Linux bitfield helpers, PCI BAR numbering, endpoint framework constants, and `pcie-cadence.h` inline HPA accessors. Used by `pcie-cadence-hpa.c`, `pcie-cadence-host-hpa.c`, `pci-sky1.c`, and any HPA platform glue.

Risks: HPA encodings differ from classic Cadence, especially BAR aperture bases, descriptor type fields, and bus/devfn supply controls. Some macros are long single-line expressions and easy to misuse with side effects. Wrong bank offset selection in platform data combined with these relative offsets will silently target the wrong registers.

Test signals: compile coverage, register trace comparison against HPA documentation, outbound MEM/IO/config/message windows, inbound RP and EP BAR maps, PTM response enable, detect-quiet programming, and link-up status read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa.c

Purpose: HPA common helper implementation for Cadence PCIe. It supplies HPA link-up detection, detect-quiet tuning, and outbound region programming for memory/IO and normal-message TLPs.

Important APIs/types/functions: `cdns_pcie_hpa_link_up()`, `cdns_pcie_hpa_detect_quiet_min_delay_set()`, `cdns_pcie_hpa_set_outbound_region()`, and `cdns_pcie_hpa_set_outbound_region_for_normal_msg()`.

Control flow: link-up reads the HPA PHY debug-status register. Detect-quiet updates the HPA PHY-layer config delay field. Outbound region setup rounds requested size up to a power of two, enforces at least 256-byte addressing granularity, writes PCI target address, descriptor type, optional supplied bus/devfn values for RC mode, CPU base, and control bits. Normal-message setup is a specialized outbound region with fixed 128 KiB aperture and message descriptor type.

State/persistence: no private state. Hardware state is the HPA AXI slave outbound region table and IP register detect-quiet field. Values persist until controller reset or later region reprogramming.

Dependencies/integration: HPA register macros and HPA inline read/write accessors. Called by HPA host setup and could be reused by HPA endpoint support.

Risks: `fls64(size - 1)` assumes nonzero size. HPA RC descriptor semantics require bus/devfn supply bits in `CTRL0`; missing them breaks RC-originated TLP IDs. Unlike classic helper, no `cpu_addr_fixup` callback is applied, so platform address aliasing must be handled elsewhere.

Test signals: HPA link-up bit polling, detect-quiet register update, outbound IO and MEM windows of small and large sizes, RC-mode bus/devfn injection, EP-mode captured bus/device use, normal message delivery, and register trace validation for all programmed fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-lga-regs.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-lga-regs.h

Purpose: register-definition header for the classic Cadence PCIe local/global architecture. It defines local-management registers, endpoint/root BAR controls, root-port config base, address-translation registers, inbound/outbound window layouts, PTM, link timing, and normal-message encodings.

Important APIs/types/functions: macros for `CDNS_PCIE_LM_*`, root and endpoint BAR config fields, `CDNS_PCIE_RP_BASE`, `CDNS_PCIE_AT_OB_REGION_*`, `CDNS_PCIE_AT_IB_RP_BAR_*`, `CDNS_PCIE_AT_IB_EP_FUNC_BAR_*`, `CDNS_PCIE_LTSSM_CONTROL_CAP`, `CDNS_PCIE_RP_MAX_IB`, `CDNS_PCIE_MAX_OB`, and normal-message routing/code bits.

Control flow: no executable flow. Host, endpoint, and common code use these macros to compose register writes for config cycles, BAR setup, DMA inbound maps, outbound windows, link tuning, and interrupt messages.

State/persistence: no state is stored here. The macros encode persistent hardware register ABI for classic Cadence controllers.

Dependencies/integration: Linux bitfield helpers and PCI BAR numbering. Included by `pcie-cadence.h`, which exposes typed accessors and structures used throughout the Cadence driver family.

Risks: field encodings differ from HPA, including outbound descriptor bits, BAR aperture base, and function BAR grouping. Many macros shift caller arguments directly, so invalid BAR/function/region numbers can generate plausible but wrong offsets. Constants such as `CDNS_PCIE_MAX_OB` and `CDNS_PCIE_RP_MAX_IB` shape allocation and loop bounds in other files.

Test signals: compile coverage, classic Cadence root/endpoint enumeration, register traces for outbound config/MEM/IO/message windows, inbound RP/EP BAR maps, PTM response, detect-quiet programming, and MSI/INTx normal-message offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-lga-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-plat.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-plat.c

Purpose: generic platform driver for Cadence PCIe controllers in either host or endpoint mode. It allocates the appropriate Cadence RC/EP object, initializes PHYs, enables runtime PM, applies a CPU-to-bus address fixup, and delegates to shared Cadence host or endpoint setup.

Important APIs/types/functions: `struct cdns_plat_pcie`, `cdns_plat_cpu_addr_fixup()`, `cdns_plat_pcie_probe()`, `cdns_plat_pcie_shutdown()`, match data `cdns_plat_pcie_host_of_data` and `cdns_plat_pcie_ep_of_data`, and `cdns_plat_ops`.

Control flow: probe reads match data to determine RC or EP mode, allocates platform state, allocates a host bridge or endpoint structure, initializes generic PHYs through `cdns_pcie_init_phy()`, enables runtime PM, gets an active PM reference, then calls `cdns_pcie_host_setup()` or `cdns_pcie_ep_setup()`. Failure unwinds runtime PM and PHY state. Shutdown drops runtime PM, disables PM, and disables PHY.

State/persistence: `struct cdns_plat_pcie` only points at the active `struct cdns_pcie`. Hardware state is owned by common Cadence setup: PHY power, address translations, link state, and endpoint memory. Runtime PM state is maintained through PM core counters.

Dependencies/integration: OF compatible strings `cdns,cdns-pcie-host` and `cdns,cdns-pcie-ep`, platform resources expected by Cadence common setup, generic PHY framework, runtime PM, and optional build-time host/EP configs.

Risks: probe error paths return 0 after `err_init/err_get_sync`, which can hide setup failures and leave a bound but unusable device. `platform_set_drvdata()` stores `struct cdns_plat_pcie`, while shutdown calls `dev_get_drvdata()` as if it were `struct cdns_pcie *`, which is a type mismatch risk. Device links are deleted manually but PHY devm objects remain.

Test signals: host and endpoint compatible probe, forced PM failure, PHY absent and multi-PHY cases, CPU address fixup behavior, shutdown correctness, and probe failure return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.c

Purpose: shared classic Cadence PCIe core helpers. It implements capability search, link-up polling, detect-quiet tuning, outbound region programming, outbound reset, PHY lifecycle helpers, PHY discovery, and common noirq PM operations.

Important APIs/types/functions: `cdns_pcie_find_capability()`, `cdns_pcie_find_ext_capability()`, `cdns_pcie_linkup()`, `cdns_pcie_detect_quiet_min_delay_set()`, `cdns_pcie_set_outbound_region()`, `cdns_pcie_set_outbound_region_for_normal_msg()`, `cdns_pcie_reset_outbound_region()`, `cdns_pcie_init_phy()`, `cdns_pcie_enable_phy()`, `cdns_pcie_disable_phy()`, and exported `cdns_pcie_pm_ops`.

Control flow: outbound setup rounds size up, builds PCI target and descriptor registers, injects bus/devfn in RC mode or function only in EP mode, applies optional CPU address fixup, and writes CPU base registers. PHY init counts `phy-names`, gets each PHY, adds stateless device links, powers PHYs on, and unwinds on failure. PM suspend powers off/exits PHYs; resume reinitializes/powers them.

State/persistence: no independent global state. `struct cdns_pcie` stores register base, PHY arrays, device links, ops, and mode. Hardware state includes outbound windows, detect-quiet field, and PHY power/init state.

Dependencies/integration: Linux PHY framework, OF properties, device links, PCI capability walking macros, Cadence register definitions, and platform-specific `cdns_pcie_ops` for address fixup or link control.

Risks: `cdns_pcie_set_outbound_region()` assumes nonzero size and available region number. PHY init error unwinding starts from the current index and may not remove links already assigned if failure occurs after allocation but before all fields are stored. `cdns_pcie_init_phy()` treats missing `phy-names` as non-fatal, so boards relying on PHY power must provide correct DT.

Test signals: capability search on RP/EP config spaces, outbound MEM/IO/message TLPs, CPU address fixup platforms, multi-PHY init failure unwinds, no-PHY probe, suspend/resume PHY cycling, and detect-quiet quirk register update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.h

Purpose: central internal interface for the Cadence PCIe driver family. It defines common RC/EP/platform structures, register bank abstractions, read/write helpers, config-space access helpers, link operation wrappers, and prototypes for classic and HPA host/endpoint/common helpers.

Important APIs/types/functions: `enum cdns_pcie_rp_bar`, `struct cdns_pcie_rp_ib_bar`, `enum cdns_pcie_reg_bank`, `struct cdns_pcie_ops`, `struct cdns_plat_pcie_of_data`, `struct cdns_pcie`, `struct cdns_pcie_rc`, `struct cdns_pcie_epf`, `struct cdns_pcie_ep`, inline accessors `cdns_pcie_*`, `cdns_pcie_hpa_*`, RP/EP config access helpers, and public prototypes for host, EP, PHY, translation, and link operations.

Control flow: inline wrappers map generic operations onto platform callbacks when available (`start_link`, `stop_link`, `link_up`) or default classic helpers. Register-bank helpers translate HPA logical banks into offsets before MMIO. Config read/write helpers handle byte/word/dword accesses through aligned dword accesses where needed.

State/persistence: structures declared here own most Cadence runtime state: MMIO bases, resources, PHYs, links, mode, ops, register offsets, RC IDs/quirks/BAR availability, EP outbound region state, IRQ cache, and EPF BAR pointers. The header does not allocate state by itself.

Dependencies/integration: Linux PCI host and endpoint APIs, PHY framework, module/kernel helpers, classic and HPA register headers. It is included by every Cadence source in this work item.

Risks: the header mixes classic and HPA accessors; using the wrong helper on a controller can target different addresses. `cdns_reg_bank_to_off()` depends on non-null `cdns_pcie_reg_offsets` for HPA users. Inline config-size helpers read aligned dwords and mask fields, so callers must pass valid sizes and offsets. Build-time inline stubs return `-ENODEV` when host/EP configs are disabled, which can hide mode support issues until runtime.

Test signals: build matrix for host-only, EP-only, HPA, and platform glue; sparse/compile checks for prototypes; root and endpoint config access sizes; HPA bank offsets; callback fallback behavior; and structure initialization in all glue drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-sg2042.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-sg2042.c

Purpose: Sophgo SG2042 Cadence PCIe host driver. It supplies SG2042-specific config access ops for 4-byte aligned root-port access, disables broken ASPM L0s/L1 advertisement, initializes PHYs, and delegates host setup to classic Cadence code.

Important APIs/types/functions: `sg2042_pcie_root_ops`, `sg2042_pcie_child_ops`, `sg2042_pcie_probe()`, `sg2042_pcie_remove()`, `sg2042_pcie_suspend_noirq()`, `sg2042_pcie_resume_noirq()`, and `sg2042_pcie_pm_ops`.

Control flow: probe allocates a host bridge, installs 32-bit config read/write ops for root bus and generic ops for child buses, sets ASPM quirks, initializes runtime PM without callbacks, initializes PHYs, then calls `cdns_pcie_host_setup()`. Remove disables the Cadence host and PHYs. PM noirq suspend/resume cycles PHY power only.

State/persistence: runtime state is primarily `struct cdns_pcie` embedded in `struct cdns_pcie_rc`, stored as platform drvdata. Hardware state includes PHY power, root-port config and address translations from common Cadence host setup, and ASPM link capability masking.

Dependencies/integration: platform resources consumed by common Cadence host setup, generic PHY framework, runtime PM helper wrappers, and DT compatible `sophgo,sg2042-pcie-host`.

Risks: the root/child config ops split is essential because root-port byte/word config access is not supported. Any future bridge ops override must preserve `child_ops`. Suspend/resume does not reinitialize host translations, so it assumes PHY cycling is sufficient or higher layers preserve controller state.

Test signals: SG2042 root config reads/writes using 32-bit ops, child config byte/word/dword accesses, ASPM disabled in LNKCAP, PHY init and PM resume, host remove cleanup, and enumeration behind bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-sg2042.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Kconfig

Purpose: Kconfig menu for DesignWare-based PCIe controller support. It defines common DWC core symbols, debugfs, host/endpoint capability symbols, and many SoC-specific host/EP options including DRA7xx, Exynos, and i.MX covered in this work item.

Important APIs/types/functions: config symbols `PCIE_DW`, `PCIE_DW_DEBUGFS`, `PCIE_DW_HOST`, `PCIE_DW_EP`, `PCI_IMX6`, `PCI_IMX6_HOST`, `PCI_IMX6_EP`, `PCI_EXYNOS`, `PCI_DRA7XX`, `PCI_DRA7XX_HOST`, and `PCI_DRA7XX_EP`, plus numerous sibling DesignWare platform symbols.

Control flow: Kconfig has declarative dependency flow. SoC options depend on architecture or `COMPILE_TEST`, MSI or endpoint framework needs, OF/HAS_IOMEM/PHY requirements, and select `PCIE_DW_HOST` or `PCIE_DW_EP`, which in turn select the common `PCIE_DW` core. Some aggregate symbols are hidden and selected by host/EP variants.

State/persistence: no runtime state. The file determines which drivers and common objects are compiled into the kernel or modules, and therefore which runtime code paths can exist.

Dependencies/integration: Linux Kconfig, PCI core, endpoint framework, MSI support, debugfs, architecture symbols, and the DWC Makefile object list.

Risks: missing `select` lines can compile a glue driver without required common DWC host/EP code. Overly broad `COMPILE_TEST` can expose missing stubs on unsupported architectures. Some options are bool while others are tristate; common ARM32 constraints, such as Keystone not being loadable due to fault hooks, are documented separately and should not be generalized blindly.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, host-only and EP-only builds, module builds for tristate users, debugfs enabled/disabled builds, and dependency checks for `PCI_MSI` and `PCI_ENDPOINT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Makefile

Purpose: object list for DesignWare PCIe controller drivers. It maps Kconfig symbols to common DWC core objects, debugfs, host/endpoint support, platform glue, SoC-specific drivers, and ACPI quirk objects.

Important APIs/types/functions: `obj-$(CONFIG_PCIE_DW) += pcie-designware.o`, host/EP objects, platform object, and per-driver mappings such as `obj-$(CONFIG_PCI_DRA7XX) += pci-dra7xx.o`, `obj-$(CONFIG_PCI_EXYNOS) += pci-exynos.o`, and `obj-$(CONFIG_PCI_IMX6) += pci-imx6.o`.

Control flow: build flow is declarative. Hidden aggregate symbols such as `PCI_IMX6` and `PCI_DRA7XX` compile a shared source once while host/EP Kconfig symbols control code paths inside the source through `IS_ENABLED()` or selected common support.

State/persistence: no runtime state. It determines which object files are linked into the kernel or modules.

Dependencies/integration: Kbuild, DWC Kconfig, and ACPI/PCI quirk conditions. The ACPI block always builds some quirk objects on ARM64 when ACPI and PCI quirks are enabled, independent of DT driver enablement.

Risks: object symbols must match Kconfig names exactly. A source that supports both host and endpoint must be keyed on the aggregate symbol, not only one mode, or the other mode will not link. Duplicate object inclusion through ACPI and DT paths must remain intentional.

Test signals: `make drivers/pci/controller/dwc/`, `allyesconfig`, `allmodconfig`, host-only and EP-only configs for i.MX/DRA7xx, and ARM64 ACPI quirk builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-dra7xx.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-dra7xx.c

Purpose: TI DRA7xx DesignWare PCIe wrapper supporting root complex and endpoint modes. It handles TI wrapper registers, PHYs, two-lane configuration, interrupt demux, MSI/INTx handling, endpoint interrupt generation, runtime PM, and platform reset/clock sequencing.

Important APIs/types/functions: `struct dra7xx_pcie`, `struct dra7xx_pcie_of_data`, `dra7xx_pcie_probe()`, `dra7xx_add_pcie_port()`, `dra7xx_add_pcie_ep()`, `dra7xx_pcie_irq_handler()`, `dra7xx_pcie_msi_irq_handler()`, `dra7xx_pcie_init_irq_domain()`, `dra7xx_pcie_enable_phy()`, `dra7xx_pcie_unaligned_memaccess()`, and DWC ops `dw_pcie_ops`, `dra7xx_pcie_host_ops`, `pcie_ep_ops`.

Control flow: probe maps `ti_conf`, fetches clocks/PHYs, configures optional two-lane mode, powers PHYs, enables runtime PM, gets optional reset GPIO, disables LTSSM, writes wrapper device type, applies errata i870 unaligned-access workaround, then initializes host or endpoint. Host mode sets up INTx domain, chained MSI/INTx IRQ, DBI base, and `dw_pcie_host_init()`. EP mode maps endpoint DBI regions, initializes EPC and endpoint registers, and notifies EPC init. Main IRQ logs wrapper events and notifies EP link-up.

State/persistence: state includes PHY array/device links, wrapper base, DWC object, IRQ domain, clock, and mode. Hardware state includes TI wrapper interrupt enables/status, device type, LTSSM bit, PHY power, DWC DBI/ATU state, MSI status, and syscon lane/unaligned-access bits.

Dependencies/integration: DWC host/EP core, PHY framework, TI PIPE3, syscon/regmap, GPIO, IRQ domains/chained IRQs, endpoint framework, runtime PM, and DT compatibles for DRA7, DRA746, and DRA726 RC/EP variants.

Risks: MSI IRQ handling loops up to 1000 times to drain status, so interrupt floods can still stress the system. The MSI wrapper switch handles exact status values; simultaneous MSI and INTx bits may not match a single case. Some error paths after PHY/link creation do not delete all device links. Two-lane configuration failure silently falls back to x1.

Test signals: RC enumeration, EP function tests, INTx domain mapping, MSI storm handling, wrapper event logging, two-lane and fallback operation, errata i870 syscon update, suspend/resume PHY cycling and MSE restore, shutdown link stop, and endpoint MSI/INTx raise behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-dra7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-exynos.c

Purpose: Samsung Exynos DesignWare PCIe host driver. It sequences Exynos ELBI sideband DBI access, core resets, clocks, regulators, PHY power, IRQ pulse handling, link startup, host initialization, removal, and noirq suspend/resume.

Important APIs/types/functions: `struct exynos_pcie`, sideband helpers `exynos_pcie_sideband_dbi_w_mode()` and `_r_mode()`, reset helpers, `exynos_pcie_start_link()`, `exynos_pcie_read_dbi()`, `exynos_pcie_write_dbi()`, `exynos_pcie_host_init()`, `exynos_add_pcie_port()`, `exynos_pcie_probe()`, and PM callbacks.

Control flow: probe allocates driver state, gets PHY, enables all clocks, gets/enables `vdd18` and `vdd10`, then initializes the DWC host. Host init installs root-bus own-config ops, asserts core reset, powers PHY, deasserts reset, and enables pulse IRQs. DBI accesses temporarily set ELBI sideband bits before calling generic DWC read/write. Resume re-enables supplies, reruns host init, sets up RC registers, starts link, and waits for link.

State/persistence: runtime state holds embedded `struct dw_pcie`, clock bulk array, PHY, and regulators. Hardware state includes ELBI reset bits, sideband DBI enable bits, pulse interrupt enables/status, PHY power, DWC root-port registers, and regulator state. Suspend powers these down; resume reconstructs them.

Dependencies/integration: DWC host core, Exynos ELBI resource from DWC platform mapping, PHY framework, bulk clocks, regulators, IRQs, and DT compatible `samsung,exynos5433-pcie`.

Risks: `phy_init()` and `phy_power_on()` results in host init are not checked. Root-bus config ops only access the root port and return device-not-found for other slots; downstream config access is handled by DWC host machinery. Probe failure calls `phy_exit()` even if host init failed before PHY init. Regulator/PHY ordering is strict for suspend/resume.

Test signals: regulator and clock enable sequencing, sideband DBI read/write correctness, root-port config access, link-up bit polling, pulse IRQ clear, suspend/resume link restoration, and clean remove with supplies disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-imx6.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-imx6.c

Purpose: NXP/Freescale i.MX DesignWare PCIe driver for many generations in RC and EP modes: i.MX6Q/SX/QP, i.MX7D, i.MX8MQ/MM/MP/Q, and i.MX95. It centralizes variant-specific GPR/syscon programming, clocks, resets, regulators, PHY setup, LTSSM control, endpoint features, suspend/resume workarounds, and i.MX95 stream-ID LUT management.

Important APIs/types/functions: `struct imx_pcie_drvdata`, `struct imx_pcie`, `drvdata[]`, `imx_pcie_probe()`, `imx_pcie_host_init()`, `imx_pcie_host_exit()`, `imx_pcie_start_link()`, `imx_pcie_stop_link()`, `imx_add_pcie_ep()`, `imx_pcie_ep_raise_irq()`, PHY helpers `pcie_phy_read/write()`, reset/refclk helpers, `imx_pcie_add_lut_by_rid()`, `imx_pcie_suspend_noirq()`, `imx_pcie_resume_noirq()`, and `imx_pcie_quirk()`.

Control flow: probe allocates DWC and i.MX state, selects variant data, fetches optional PHY MMIO, reset GPIO, clocks, PHY driver, resets, GPR/regmap or SERDES app regmap, TX tuning properties, max speed, supplies, and power domains. EP mode runs `imx_add_pcie_ep()` and adds a default i.MX95 LUT entry. RC mode sets DWC PM/ATU flags, initializes the host, and enables MSI in the root port when available. Host init enables regulators, installs LUT callbacks when needed, asserts resets/PERST, initializes PHY and mode, enables clocks/refclk, powers PHY, disables LTSSM, deasserts reset/PERST, waits for PLL, and configures MPLL. Link start may force Gen1 first for old variants, then performs directed speed change.

State/persistence: state includes clocks, reset controls, GPIO, GPR regmap, regulators, PHY, power domains, MSI control save, i.MX95 LUT cache, controller ID, TX tuning, and variant flags. Hardware state spans IOMUXC GPRs, PHY registers, DWC DBI/ATU, LTSSM/app reset, PERST, refclk override, regulators, and i.MX95 LUTs. Suspend saves MSI/LUT state and either uses DWC suspend or a broken-suspend workaround; resume restores RC, LUT, and MSI state.

Dependencies/integration: DWC host/EP core, Linux PHY and PCIe PHY APIs, reset, regulator, clock, GPIO, regmap/syscon, power domains, OF ID mapping (`iommu-map`/`msi-map`), PCI endpoint framework, and ARM fault hooks for i.MX6 abort handling.

Risks: variant flags are dense and easy to combine incorrectly. Several helper return values from low-level PHY reads/writes are not always checked. `imx_pcie_start_link()` returns 0 after some speed-change failures after resetting PHY, which can mask link failure. i.MX95 LUT programming must reconcile IOMMU and MSI stream IDs and has only 32 entries with 6-bit SIDs. Broken-suspend paths require MSI and RC reinitialization.

Test signals: boot/enumeration across each compatible, endpoint function tests and BAR feature constraints, Gen1-to-Gen2 speed workaround, PERST timing, refclk/CLKREQ override clear after link, regulator and PHY sequencing, suspend/resume on broken and normal variants, i.MX95 LUT add/remove/save/restore with `iommu-map` and `msi-map`, MSI capability preservation, and i.MX6 config-size quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-imx6.c -->
