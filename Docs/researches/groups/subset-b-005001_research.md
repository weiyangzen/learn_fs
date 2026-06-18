# Research: subset-b-005001

Grouped research report for the PCI controller sources assigned to subset-b-005001. Each file section is bounded by reconciliation markers so the final documents can be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spacemit-k1.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spacemit-k1.c

Purpose: SpacemiT K1 DesignWare PCIe root-complex glue driver. It owns the platform-specific PMU/syscon controls, link-status registers, PHY selection from the root-port child node, regulator enablement, and the DesignWare host registration path.

Important APIs, types, and functions: `struct k1_pcie` embeds `struct dw_pcie` and stores the external PHY, link MMIO base, PMU regmap, and PMU offset. `k1_pcie_probe()` resolves `spacemit,apmu`, maps the `"link"` resource, enables `vpcie3v3`, configures runtime PM without callbacks, parses the child PHY, and calls `dw_pcie_host_init()`. `k1_pcie_init()` toggles soft reset, enables app clocks/resets from `pci->app_clks` and `pci->app_rsts`, writes vendor/device IDs into DBI with RO override, asserts PERST for `PCIE_T_PVPERL_MS`, sets RC/device power bits, initializes the PHY, deasserts PERST, and disables ASPM L1 as a workaround. `k1_pcie_deinit()` reverses PERST, PHY, reset, and clock state. `k1_pcie_start_link()`, `k1_pcie_stop_link()`, and `k1_pcie_link_up()` implement the `dw_pcie_ops`.

Control flow: probe seeds DesignWare state, holds the PHY in reset, enables supply/PM, then host init invokes the host callbacks. Link start releases `APP_HOLD_PHY_RST`, enables LTSSM, MSI, and the top-level PHY AHB interrupt. Link-up requires both `SMLH_LINK_UP` and `RDLH_LINK_UP`. Removal delegates to `dw_pcie_host_deinit()`, which calls deinit.

State and persistence: state is volatile hardware state only: PMU reset bits, PERST, LTSSM, MSI interrupt enable, DBI IDs, app clocks/resets, runtime PM active state, and PHY init state. There is no persistent storage.

Dependencies and integration points: Linux platform/OF, syscon regmap, regulator framework, clock/reset bulk resources held by DesignWare core, PHY framework, runtime PM, and `pcie-designware.h`. DT must expose `spacemit,k1-pcie`, `spacemit,apmu`, `"link"` resource, a root-port child with PHY, and `vpcie3v3`.

Risks: PMU phandle arguments and offsets are critical; a wrong offset manipulates unrelated PMU bits. The ASPM L1 disable mutates capability advertising and may hide power-saving features. Interrupt enabling is not paired with a local IRQ handler, so correctness relies on DWC MSI plumbing. Error unwinds after PHY init and resource enable are intentionally narrow and should be checked when extending probe.

Test signals: boot with `spacemit,k1-pcie`, observe host bridge enumeration, link-up with both PHY status bits set, MSI delivery, PERST timing, regulator/clock/reset cleanup on remove or probe failure, and NVMe stability with the ASPM workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spacemit-k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spear13xx.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spear13xx.c

Purpose: SPEAr13xx DesignWare PCIe root-complex glue. It initializes the SPEAr application register block, PHY, clock, MSI interrupt path, and root-port DBI quirks for the ST SPEAr1340 compatible.

Important APIs, types, and functions: `struct spear13xx_pcie` stores a pointer to allocated `struct dw_pcie`, application register base derived from DBI plus `0x2000`, PHY, and clock. `struct pcie_app_reg` documents the app register layout. `spear13xx_pcie_probe()` allocates private and DWC objects, gets `"pcie-phy"`, initializes it, enables the clock, applies optional Gen1 restriction from `st,pcie-is-gen1`, and calls `spear13xx_add_pcie_port()`. `spear13xx_pcie_host_init()` limits Max Read Request Size to 128 bytes, programs vendor/device IDs, and enables MSI interrupt masking. `spear13xx_pcie_start_link()` writes RC mode, misc-control enable, LTSSM enable, and region translation enable. `spear13xx_pcie_irq_handler()` services `MSI_CTRL_INT` by calling `dw_handle_msi_irq()`.

Control flow: probe performs PHY/clock setup before DesignWare host init. Host init computes `app_base`, applies DBI changes, and unmasks app MSI. Link training starts when the DWC core calls `start_link()`. The single platform IRQ is requested with `IRQF_SHARED | IRQF_NO_THREAD`; the handler clears all seen app interrupt status bits.

State and persistence: hardware-only state includes app control bits, app interrupt mask/status, clock enable, PHY init, Gen1 limit in DWC state, DBI vendor/device IDs, and Max Read Request Size. No persistent state exists. There is no explicit remove path because the driver is built in and suppresses bind attributes.

Dependencies and integration points: platform DT match `st,spear1340-pcie`, DesignWare host core, `CONFIG_PCI_MSI` for MSI handling, PHY framework, clock framework, OF property parsing, and shared PCI IRQ behavior.

Risks: `phy_init()` return is ignored in probe, so PHY init failure can be hidden. Clock cleanup is only on add-port failure. The IRQ handler uses `BUG_ON(!IS_ENABLED(CONFIG_PCI_MSI))` if MSI status appears without MSI support, which is harsh. `app_base = dbi_base + 0x2000` assumes a fixed mapping.

Test signals: SPEAr1340 boot should show root port registration, a 128-byte read request setting, link-up from `XMLH_LINK_UP`, MSI interrupt delivery through DWC, behavior with `st,pcie-is-gen1`, and failure-path clock cleanup when IRQ or host init fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spear13xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32-ep.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32-ep.c

Purpose: STM32MP25 DesignWare PCIe endpoint controller driver. It configures SYSCFG mode bits for endpoint operation, initializes endpoint controller resources, and responds to host PERST changes by tearing down or reprogramming endpoint registers.

Important APIs, types, and functions: `struct stm32_pcie` embeds `struct dw_pcie` and stores SYSCFG regmap, reset, PHY, clock, PERST GPIO, and IRQ. `stm32_pcie_probe()` resolves `"st,stm32mp25-syscfg"`, PHY, clock, reset, reset GPIO, runtime PM, and threaded PERST IRQ, then calls `stm32_add_pcie_ep()`. `stm32_add_pcie_ep()` sets `STM32MP25_PCIECR_EP`, toggles controller reset, sets `dw_pcie_ep_ops`, uses 64 KiB page alignment, calls `dw_pcie_ep_init()`, and enables PHY/clock resources. `stm32_pcie_perst_assert()` disables LTSSM, notifies EPC deinit, disables resources, and runtime-suspends. `stm32_pcie_perst_deassert()` resumes runtime PM, enables resources, reinitializes EP registers with `dw_pcie_ep_init_registers()`, notifies EPC init, and enables LTSSM.

Control flow: endpoint initialization occurs at probe, but link start only enables PERST IRQ. The PERST threaded handler reads GPIO value, dispatches assert/deassert logic, and flips IRQ trigger polarity to catch the next edge. Removal stops link, notifies EPC deinit, deinitializes EP, disables resources, and drops runtime PM.

State and persistence: state is volatile: SYSCFG type/LTSSM bits, reset line, PHY init state, clock state, runtime PM usage count, EPC state notifications, DBI endpoint registers reprogrammed after PHY reset, and IRQ trigger type. No persistent storage.

Dependencies and integration points: DesignWare endpoint core, PCI endpoint controller API, syscon regmap, runtime PM, GPIO/IRQ subsystem, PHY/clock/reset frameworks, and shared constants from `pcie-stm32.h`.

Risks: PERST is level-sensitive through GPIO but the driver rewrites IRQ type after each event; missed edges or wrong active level can leave resources enabled or disabled incorrectly. `stm32_add_pcie_ep()` enables resources immediately even though host PERST may later force reinit. Error paths must balance `pm_runtime_get_noresume()` and resource enables.

Test signals: endpoint function binding should succeed, PERST assert should call deinit notify and gate resources, PERST deassert should reinitialize DBI registers and assert link training, MSI/INTx raises should work, and remove should not leak runtime PM or leave IRQ enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.c

Purpose: STM32MP25 DesignWare PCIe root-complex driver. It sets RC mode in SYSCFG, controls PERST and optional WAKE GPIOs under a root-port child node, integrates suspend/resume, and registers the DWC host.

Important APIs, types, and functions: `struct stm32_pcie` stores DWC state, SYSCFG regmap, reset, PHY, clock, PERST GPIO, and optional WAKE GPIO. `stm32_pcie_probe()` gets syscfg, clock, reset, parses root-port PHY/GPIOs, enables port resources, toggles controller reset, enables the core clock and runtime PM, then calls `dw_pcie_host_init()`. `stm32_add_pcie_port()` sets PHY mode/init, programs `STM32MP25_PCIECR_RC`, deasserts PERST with required delays, and registers a dedicated wake IRQ for WAKE GPIO. `stm32_pcie_start_link()` and `stm32_pcie_stop_link()` toggle `STM32MP25_PCIECR_LTSSM_EN`. `stm32_pcie_suspend_noirq()` and `stm32_pcie_resume_noirq()` handle DWC noirq state, PERST, clock, PHY, and pinctrl state.

Control flow: probe parses the first available child as root port, initializes PHY before reset/clock/host registration, then DWC host setup starts link training through callbacks. Suspend disables DWC, asserts PERST, disables clock, optionally exits PHY if not a wakeup path, and selects sleep pinctrl. Resume selects init pinctrl first, reinitializes PHY when needed, enables clock, deasserts PERST, resumes DWC, and restores default pinctrl.

State and persistence: state is hardware-only: syscfg RC/LTSSM bits, reset, PERST line, wake IRQ registration, clock/PHY state, runtime PM active state, DWC host resources, and pinctrl state. No disk persistence.

Dependencies and integration points: DesignWare host core, STM32 syscfg regmap, GPIO descriptors via root-port fwnode, wake IRQ framework, PM/pinctrl, PHY, clock/reset, and constants in `pcie-stm32.h`.

Risks: `of_get_next_available_child()` is not checked before using its fwnode for GPIOs, so malformed DT without a child could be fragile. Suspend/resume sequencing is sensitive because DBI access depends on REFCLK/CLKREQ pin state. Optional PERST means some systems rely entirely on LTSSM and PHY behavior.

Test signals: RC boot enumeration, link training after PERST delays, wake GPIO falling-edge wake, suspend/resume with and without wake path, noirq DWC errors, pinctrl state transitions, and clean removal with host deinit and wake IRQ cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.h -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.h

Purpose: Shared STM32MP25 PCIe definitions for the RC and EP drivers. It centralizes the private-data lookup macro and SYSCFG register fields used to select controller mode and LTSSM state.

Important APIs, types, and functions: `to_stm32_pcie(x)` maps a `dw_pcie` instance back to driver private data through `dev_get_drvdata((x)->dev)`. `STM32MP25_PCIECR_TYPE_MASK`, `STM32MP25_PCIECR_EP`, `STM32MP25_PCIECR_RC`, and `STM32MP25_PCIECR_LTSSM_EN` define the mode and link-training bits in `SYSCFG_PCIECR`. `SYSCFG_PCIECR` is the syscfg offset used by both drivers.

Control flow: this header has no runtime flow. It is included by `pcie-stm32.c` and `pcie-stm32-ep.c`, which use the constants during probe, link start/stop, and PERST handling.

State and persistence: the header defines volatile register bits only. It stores no state and has no persistence behavior.

Dependencies and integration points: depends on Linux bit macros and device APIs. It forms the interface between STM32 DesignWare glue code and the system configuration regmap named by the platform drivers.

Risks: mode values are asymmetric: EP is encoded as zero while RC is `BIT(10)` within a wider `GENMASK(11, 8)` type field. Callers must use `regmap_update_bits()` with the full type mask or stale mode bits can survive. The lookup macro assumes `platform_set_drvdata()` points to the enclosing `struct stm32_pcie`.

Test signals: compile coverage for both STM32 RC and EP drivers, and runtime verification that syscfg writes put the controller into the expected RC or EP mode and that LTSSM toggling affects link training.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194-acpi.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194-acpi.c

Purpose: ACPI ECAM quirk implementation for Tegra194 PCIe host controllers. It adapts an ACPI `pci_config_window` into separate config, iATU, and DBI regions and programs outbound iATU windows before non-root config accesses.

Important APIs, types, and functions: `struct tegra194_pcie_ecam` stores `config_base`, `iatu_base`, and `dbi_base`. `tegra194_acpi_init()` allocates that structure, assigns `cfg->win`, `cfg->win + SZ_256K`, and `cfg->win + SZ_512K`, and stores it in `cfg->priv`. `program_outbound_atu()` writes unrolled DWC outbound ATU registers for base, target, limit, type, and enable. `tegra194_map_bus()` routes root bus device 0 accesses to DBI, rejects other root slots and nonzero direct-child slots, programs CFG0 for the direct downstream device or CFG1 for deeper buses, and returns `config_base + where`. `tegra194_pcie_ops` exposes init/map/read/write via `pci_ecam_ops`.

Control flow: PCI core calls ECAM init during host creation. For each config access, `map_bus()` validates bus range and topology, programs ATU index 0 for the requested bus/device/function, then returns a window address used by generic config read/write.

State and persistence: state is in `cfg->priv` and transient iATU register programming. The same outbound region is reprogrammed per access. No persistent storage exists.

Dependencies and integration points: ACPI PCI host infrastructure, generic PCI ECAM ops, DesignWare iATU register definitions from `pcie-designware.h`, and PCI topology assumptions matching Tegra194 host layout.

Risks: ATU region 0 is shared across accesses and relies on PCI config serialization. Incorrect ACPI window layout breaks all offsets. The mapper deliberately filters unsupported slots, so firmware topology descriptions must match the one-device downstream assumption.

Test signals: ACPI boot should enumerate root port via DBI, discover the direct endpoint using CFG0, enumerate subordinate bridges using CFG1, reject invalid slots cleanly, and show stable config access under concurrent enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194.c

Purpose: NVIDIA Tegra194/Tegra234 DesignWare PCIe controller driver for both root-complex and endpoint modes. It coordinates APPL glue registers, BPMP firmware, UPHY/PHY lanes, regulators, clocks/resets, interconnect bandwidth, DWC host/EP core, debugfs ASPM counters, endpoint PERST handling, and system sleep.

Important APIs, types, and functions: `struct tegra_pcie_dw_of_data` captures SoC/mode quirks, DWC IP version, CDM interrupt bit, Gen4 presets, N_FTS values, and workaround flags. `struct tegra_pcie_dw` is the central runtime state. RC path: `tegra_pcie_config_rp()`, `tegra_pcie_init_controller()`, `tegra_pcie_dw_host_init()`, `tegra_pcie_dw_start_link()`, `tegra_pcie_rp_irq_handler()`, `tegra_pcie_deinit_controller()`. EP path: `tegra_pcie_config_ep()`, `tegra_pcie_ep_pex_rst_irq()`, `pex_ep_event_pex_rst_assert()`, `pex_ep_event_pex_rst_deassert()`, EP IRQ handlers, and `pcie_ep_ops` for INTx/MSI/MSI-X. Shared helpers include `tegra_pcie_dw_parse_dt()`, BPMP controller/PLL commands, slot regulator helpers, PHY enable/disable, Gen3/Gen4 equalization preset programming, ASPM/debugfs setup, PME turnoff, and PM callbacks.

Control flow: probe loads OF match data, parses resources and DT properties, acquires regulators, clocks, APPL/ATU mappings, resets, P2U PHYs, IRQ, BPMP, and interconnect path, then branches on mode. RC mode requests the APPL IRQ, enables runtime PM, configures pins, BPMP, regulators, clocks, PHYs, APPL RC mode, iATU base, DWC host, link training, bandwidth/clock rate, interrupts, and debugfs if the link is up. EP mode requests APPL and PERST IRQs, initializes DWC EPC, and waits with `ep_state = DISABLED`; PERST deassert performs full controller enable, APPL EP programming, interrupt enables, DBI cleanup/reinitialization, ASPM/equalization setup, MSI-X match setup, EPC init notify, and LTSSM enable. PERST assert or remove tears it down. Suspend blocks active EP mode, while RC suspend turns off PME/L2, unconfigures hardware, and resume reconstructs controller state.

State and persistence: volatile state includes APPL mode/control/interrupt bits, DBI capabilities, DWC host or EP state, BPMP-controlled controller/PLL state, regulator/clock/reset/PHY state, interconnect bandwidth, debugfs counters, `link_state`, `ep_state`, PERST IRQ enabled state, and endpoint link status bit. No persistent storage is used.

Dependencies and integration points: DesignWare host/endpoint core, Tegra BPMP MRQ_UPHY ABI, regulator, clock, reset, PHY, GPIO, pinctrl, runtime/system PM, interconnect, debugfs, PCI endpoint APIs, PCIe ASPM/AER/MSI options, and DT properties such as `num-lanes`, `nvidia,bpmp`, ASPM timing values, PHY names, `supports-clkreq`, `nvidia,enable-srns`, `nvidia,enable-ext-refclk`, reset GPIOs, and supplies.

Risks: This file is highly sequence-sensitive: DBI access depends on clocks/refclk/PHY, endpoint DBI is reset during PERST cycles, and BPMP errors must be unwound cleanly. Workarounds for DLF, SBR/surprise link down, L1SS exit, LTR, MSI-X doorbell access, and Tegra234 L1.2 advertisement are SoC-specific; applying the wrong OF data can hang config access or lose link. `tegra_pcie_config_rp()` returns success on `-ENOMEDIUM` probe path while leaving `link_state` false, so callers must honor that guard. IRQ paths clear many status registers and must avoid masking DMA/AER side effects.

Test signals: RC enumeration on Tegra194 and Tegra234, Gen4 link training and fallback with DLF disabled, MSI/INTx/AER interrupts, bandwidth-management events, debugfs ASPM counter reads, suspend/resume with link present and absent, PME turnoff/L2 entry, endpoint PERST assert/deassert cycles, EPC init/deinit notifications, INTx/MSI/MSI-X raises, LTR behavior, and BPMP/regulator/PHY failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier-ep.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier-ep.c

Purpose: Socionext UniPhier DesignWare PCIe endpoint glue. It supports Pro5 and NX1 SoC variants, initializes link glue registers, clocks/resets/PHY, and provides endpoint IRQ raise and feature reporting.

Important APIs, types, and functions: `struct uniphier_pcie_ep_priv` stores glue MMIO base, embedded DWC state, clocks/resets, optional GIO clock/reset, PHY, and SoC data. `struct uniphier_pcie_ep_soc_data` supplies variant flags, init/wait hooks, and EPC features. `uniphier_pcie_pro5_init_ep()` and `uniphier_pcie_nx1_init_ep()` program EP mode, clock request/aux power/PERST behavior, and LTSSM off state. `uniphier_pcie_ep_enable()` enables clocks, deasserts resets, runs variant init, resets/initializes PHY, and waits for NX1 pipe clock if needed. `uniphier_pcie_ep_raise_irq()` dispatches INTx and MSI, with INTx pulsed in glue registers and MSI programmed through vendor MSI registers.

Control flow: probe obtains match data, maps `"link"`, acquires variant-dependent resources, enables the endpoint block, assigns DWC EP ops, calls `dw_pcie_ep_init()` and `dw_pcie_ep_init_registers()`, then notifies EPC init. DWC start/stop link simply toggles glue LTSSM enable.

State and persistence: volatile glue register state includes mode, PERST emulation, app clock request, LTSSM enable, MSI/INTx pulse registers, reset lines, clocks, PHY init state, and DWC endpoint registers. There is no persistent state and no explicit remove path.

Dependencies and integration points: DesignWare endpoint core, PCI endpoint controller features, OF match data, clock/reset/PHY frameworks, bitfield helpers, and UniPhier glue register layout. Compatible strings distinguish Pro5 and NX1.

Risks: Error unwind in `uniphier_pcie_ep_enable()` deasserts/asserts resources in a compact path; variant resources must be present only when `has_gio` is true. `uniphier_pcie_ep_raise_irq()` returns 0 after logging an unknown type instead of `-EINVAL`, which can hide caller bugs. MSI vector encoding subtracts one, so interrupt numbers must be 1-based.

Test signals: EP controller registration for both compatibles, BAR feature layout and alignment, pipe-clock wait on NX1, LTSSM start/stop, INTx pulse width, MSI vector delivery, and correct cleanup when clock/reset/PHY acquisition or initialization fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier.c

Purpose: Socionext UniPhier DesignWare PCIe root-complex driver. It sets RC mode, handles PHY/pipe readiness, provides link callbacks, and implements a legacy INTx irqdomain behind the UniPhier glue interrupt controller.

Important APIs, types, and functions: `struct uniphier_pcie` embeds `dw_pcie` and stores glue base, clock, reset, optional PHY, and INTx domain. `uniphier_pcie_host_enable()` enables clock/reset, calls `uniphier_pcie_init_rc()`, initializes PHY, and waits for `PCL_PCLK_ALIVE`. `uniphier_pcie_link_up()` checks both RDLH and XMLH status bits. `uniphier_pcie_config_intx_irq()` parses the `legacy-interrupt-controller` child, maps the parent IRQ, creates a 4-line irqdomain, and installs `uniphier_pcie_irq_handler()` as chained handler. Mask/unmask callbacks manipulate INTx mask bits under `pp->lock`.

Control flow: probe maps `"link"`, gets resources, enables host hardware, sets host ops, and calls `dw_pcie_host_init()`. Host init configures the legacy INTx domain and enables non-INTx and INTx event sources. Link start/stop toggles the app LTSSM bit.

State and persistence: volatile state includes glue mode/PERST/aux-power/LTSSM bits, pipe clock readiness, event masks/statuses, INTx irqdomain, clock/reset/PHY state, and DWC host state. No persistent storage exists.

Dependencies and integration points: DesignWare host core, OF IRQ parsing, irqdomain/chained IRQ APIs, optional PHY, clock/reset framework, and platform resource naming.

Risks: Chained interrupt handling clears debug/event statuses before INTx dispatch; changes must preserve ordering. Missing `legacy-interrupt-controller` prevents host init. No remove path removes the irqdomain or chained handler because the driver is built in with platform lifetime assumptions.

Test signals: UniPhier boot should show pipe clock alive, link-up with both status bits, INTx routing for INTA-D, MSI through DWC if enabled by core, host enumeration, and failure handling for missing child interrupt controller or PHY errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-visconti.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-visconti.c

Purpose: Toshiba Visconti DesignWare PCIe root-complex glue driver. It controls ULREG, SMU, and MPU register blocks, clocks, reset sequencing, link training, and a CPU-address translation quirk for Visconti SoCs.

Important APIs, types, and functions: `struct visconti_pcie` embeds DWC state and holds ULREG/SMU/MPU bases plus ref/core/aux clocks. Register helpers wrap relaxed MMIO. `visconti_pcie_host_init()` enables SMU clocks, releases ULREG reset, selects RC mode, drives PERST, releases power-up reset, waits for PHY SRAM init, marks external load done, and waits for core reset monitor. `visconti_pcie_start_link()` enables LTSSM, polls L0, unmasks event interrupts, and enables MPU memory protection if DWC sees link-up. `visconti_pcie_stop_link()` disables LTSSM and MPU. `visconti_pcie_cpu_addr_fixup()` strips `pp->io_base` from CPU addresses for this SoC bus mapping.

Control flow: probe allocates state, maps three named resources, acquires clocks, sets DWC ops, gets the `"intr"` IRQ, attaches host ops, and calls `dw_pcie_host_init()`. DWC host setup calls the platform init and link callbacks.

State and persistence: volatile register state includes SMU clock/reset bits, ULREG mode/PERST/PHY status/LTSSM/event masks, MPU enable bit, DWC host state, and clock handles. There is no persistent state and no remove path.

Dependencies and integration points: DesignWare host core, platform MMIO resources `"ulreg"`, `"smu"`, `"mpu"`, named clocks `ref`, `core`, `aux`, platform IRQ `"intr"`, and DT compatible `toshiba,visconti-pcie`.

Risks: Link-up checks `val & PCIE_UL_S_L0`, which treats any set bit overlap with `0x11` as true rather than equality; this may over-report link in other LTSSM states. Clock handles are acquired but not explicitly enabled in this file, implying reset/clock control is partially through SMU or external setup. CPU address fixup depends on DT `io_base`.

Test signals: boot enumeration, host init poll completion, LTSSM L0 polling, event-mask setup, MPU enable/disable, outbound address correctness for IO windows, and behavior when PHY/core poll timeouts occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-visconti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Kconfig

Purpose: Kconfig menu for Mobiveil-based PCIe controllers. It defines common library symbols, host support, and two platform drivers: NXP Layerscape Gen4 and generic Mobiveil AXI soft IP.

Important APIs, types, and functions: `PCIE_MOBIVEIL` is the common bool selected by host support. `PCIE_MOBIVEIL_HOST` depends on `PCI_MSI`, selects `IRQ_MSI_LIB`, and selects the common core. `PCIE_LAYERSCAPE_GEN4` depends on `ARCH_LAYERSCAPE || COMPILE_TEST` and `PCI_MSI`, selects host support, and describes Layerscape SoC Gen4 support. `PCIE_MOBIVEIL_PLAT` depends on `ARCH_ZYNQMP || COMPILE_TEST`, `OF`, and `PCI_MSI`, selects host support, and describes the Mobiveil AXI soft IP with up to eight windows.

Control flow: no runtime flow. Build selection controls which objects are compiled by the adjacent Makefile.

State and persistence: no runtime state. The persistent effect is kernel configuration symbols that determine object inclusion and dependency availability.

Dependencies and integration points: Linux PCI subsystem, PCI MSI, IRQ MSI library, OF for platform soft-IP, and architecture symbols for Layerscape and ZynqMP.

Risks: Both concrete drivers require `PCI_MSI`, so platforms without MSI cannot enable them even if legacy INTx exists. `PCIE_MOBIVEIL` is hidden and must be selected indirectly. Build coverage through `COMPILE_TEST` is allowed but runtime dependencies still need proper DT resources.

Test signals: Kconfig should select `pcie-mobiveil.o` and `pcie-mobiveil-host.o` with either platform option, expose menu entries under PCI, and fail neither allyesconfig nor architecture-specific builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Makefile -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Makefile

Purpose: Object list for Mobiveil PCIe controller support.

Important APIs, types, and functions: `obj-$(CONFIG_PCIE_MOBIVEIL)` builds `pcie-mobiveil.o`; `obj-$(CONFIG_PCIE_MOBIVEIL_HOST)` builds `pcie-mobiveil-host.o`; `obj-$(CONFIG_PCIE_MOBIVEIL_PLAT)` builds `pcie-mobiveil-plat.o`; `obj-$(CONFIG_PCIE_LAYERSCAPE_GEN4)` builds `pcie-layerscape-gen4.o`.

Control flow: no runtime flow. Kbuild includes objects according to Kconfig symbols.

State and persistence: no runtime state. The file persists the mapping between config symbols and compilation units.

Dependencies and integration points: Kbuild and the Kconfig symbols in the same directory. The layering mirrors the code architecture: common CSR/window helpers, host-mode shared code, and platform-specific front ends.

Risks: If a platform driver selects `PCIE_MOBIVEIL_HOST` but not the common symbol, build would fail; Kconfig currently selects correctly. Adding endpoint support would need new object mappings and symbols.

Test signals: build logs should include the common and host objects when either platform option is enabled; disabling both platform options should not build platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-layerscape-gen4.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-layerscape-gen4.c

Purpose: NXP Layerscape Gen4 PCIe host driver layered on the Mobiveil host library. It provides Layerscape-specific PF register access, link-up detection, interrupt enablement, and PAB reset recovery.

Important APIs, types, and functions: `struct ls_g4_pcie` embeds `struct mobiveil_pcie`, delayed reset work, and IRQ. `ls_g4_pcie_link_up()` checks PF LTSSM L0. `ls_g4_pcie_enable_interrupt()` clears and enables PAB reset, INTx, MSI, uncorrectable, PM redirect, and event collector interrupts. `ls_g4_pcie_isr()` reads Mobiveil misc status, disables interrupts and schedules delayed work on PAB reset, clears status, and returns handled. `ls_g4_pcie_reinit_hw()` waits for `PF_INT_STAT_PABRST` and no PAB activity, toggles PF debug write-enable/reset bits, calls `mobiveil_host_init(..., true)`, and waits for link. `ls_g4_pcie_probe()` allocates host bridge private data, validates `msi-parent`, initializes ops, and calls `mobiveil_pcie_host_probe()`.

Control flow: platform probe delegates most host setup to the Mobiveil library, then enables interrupts. PAB reset interrupts are handled asynchronously by `ls_g4_pcie_reset()` which clears bridge bus reset and attempts hardware reinit.

State and persistence: volatile state includes PF debug/reset bits, Mobiveil PAB misc interrupt masks/status, delayed work, host bridge private state, and window/MSI state reprogrammed by `mobiveil_host_init()`. No persistent state.

Dependencies and integration points: Mobiveil common/host code, platform IRQ named `"intr"`, OF `msi-parent`, host bridge allocation, and compatible `fsl,lx2160a-pcie`.

Risks: Reset recovery returns early on success before re-enabling interrupts; interrupt state relies on earlier or hardware behavior and deserves scrutiny. `mobiveil_host_init(reinit=true)` skips bus-number setup but reprograms windows. The delayed work is not explicitly canceled in a remove path because the driver is built in.

Test signals: Layerscape Gen4 enumeration, MSI parent validation, PAB reset interrupt generation and recovery, link re-training after reset, INTx/MSI delivery through Mobiveil core, and timeout logs for PAB activity or link training failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-layerscape-gen4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-host.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-host.c

Purpose: Shared Mobiveil host-mode implementation. It provides PCI config access, DT resource parsing, root-port initialization, outbound/inbound window programming orchestration, INTx and MSI interrupt domains, integrated interrupt handling, and final `pci_host_probe()`.

Important APIs, types, and functions: `mobiveil_pcie_map_bus()` maps root-port DBI or endpoint config space, programming the config outbound window BDF fields for non-root accesses. `mobiveil_pcie_parse_dt()` maps `"config_axi_slave"` and `"csr_axi_slave"` and reads `apio-wins`/`ppio-wins`. `mobiveil_host_init()` sets bus numbers, command bits, PAB PIO enablement, config/inbound windows, DT memory/IO windows, and class code. Interrupt support includes `mobiveil_pcie_isr()`, `mobiveil_pcie_intx_map()`, mask/unmask callbacks, MSI parent domain ops, `mobiveil_compose_msi_msg()`, allocation/free, and `mobiveil_pcie_integrated_interrupt_init()`. `mobiveil_pcie_host_probe()` validates bridge header type, initializes host/windows/interrupts, assigns `bridge->sysdata` and ops, brings the link up, and calls `pci_host_probe()`.

Control flow: platform drivers allocate `struct pci_host_bridge` and embedded `mobiveil_pcie`, set `pdev`, optional PAB/root-port ops, and call this probe. The library parses resources, initializes hardware, initializes either platform-provided or integrated interrupts, waits for link, then hands off to generic PCI enumeration.

State and persistence: volatile state includes mapped CSR/config/APB bases, physical controller base for MSI messages, APIO/PPIO window counts, configured window counters, INTx/MSI irqdomains, MSI allocation bitmap, interrupt masks, and PAB register state. No persistent storage.

Dependencies and integration points: platform resources, Mobiveil CSR helpers from `pcie-mobiveil.c`, Linux MSI parent-domain library, irqdomain/chained IRQ, PCI host bridge, OF ranges/windows, and optional platform `interrupt_init`/`link_up` ops.

Risks: `mobiveil_pcie_map_bus()` relies on global PCI config serialization when reprogramming the shared config window. INTx hwirq values are one-based in handling but domain size is four, so mapping semantics must remain consistent. MSI has only 16 vectors. Host init increments window counters without failing when windows overflow; it logs but may leave resources unmapped.

Test signals: config reads across root and child buses, rejection of invalid root/direct-child slots, memory/IO window programming from DT, inbound 256 GiB window behavior, INTx routing, MSI allocation/exhaustion/free, link timeout handling, and platform override interrupt path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-plat.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-plat.c

Purpose: Generic platform front end for Mobiveil AXI PCIe soft IP. It allocates a host bridge with Mobiveil private storage and delegates all real setup to the shared Mobiveil host probe.

Important APIs, types, and functions: `mobiveil_pcie_probe()` calls `devm_pci_alloc_host_bridge(dev, sizeof(*pcie))`, gets the private `struct mobiveil_pcie`, assigns `pcie->rp.bridge` and `pcie->pdev`, then returns `mobiveil_pcie_host_probe(pcie)`. The OF table matches `mbvl,gpex40-pcie`.

Control flow: platform probe is a thin adapter. Kbuild registers it as a built-in platform driver. Shared code handles DT resource mapping, interrupts, windows, link, and enumeration.

State and persistence: no local state beyond the embedded Mobiveil structure allocated as host-bridge private data. No persistent state.

Dependencies and integration points: Mobiveil host library, PCI host bridge allocation, OF platform matching, and the resources/properties expected by `pcie-mobiveil-host.c`.

Risks: There is no platform-specific `link_up` or `interrupt_init` override, so the generic IP must match the integrated interrupt and LTSSM behavior in the shared library. Remove/unwind is entirely devm/platform lifetime based.

Test signals: DT-compatible probe, host bridge allocation, successful shared probe using `"config_axi_slave"`, `"csr_axi_slave"`, and `"apb_csr"` resources, MSI/INTx interrupts through integrated path, and link-up via common LTSSM register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.c

Purpose: Common Mobiveil CSR, address translation window, and link polling helpers used by Mobiveil host-mode drivers.

Important APIs, types, and functions: `mobiveil_pcie_sel_page()` and `mobiveil_pcie_comp_addr()` implement the controller's paged CSR address scheme for offsets at or above `PAGED_ADDR_BNDRY`. `mobiveil_csr_read()` and `mobiveil_csr_write()` wrap size-checked MMIO access and report bad alignment/size. `mobiveil_pcie_link_up()` calls platform `ops->link_up` when present or checks common `LTSSM_STATUS`. `program_ob_windows()` and `program_ib_windows()` program APIO/PPIO address translation windows, extended high registers, type, size mask, AXI/PEX bases, and counters. `mobiveil_bringup_link()` polls link-up using retry constants.

Control flow: shared host init and platform reset recovery call these helpers to program windows and poll link. CSR access selects the register page on every access before touching the composed address.

State and persistence: state is volatile CSR page-select bits, translation window registers, `ob_wins_configured`/`ib_wins_configured` counters in `struct mobiveil_pcie`, and LTSSM status. No persistent state.

Dependencies and integration points: `struct mobiveil_pcie` and register definitions from `pcie-mobiveil.h`, platform device for logging, Linux MMIO and delay APIs, and optional platform-specific PAB ops.

Risks: Page selection is mutable shared hardware state; callers rely on PCI or higher-level serialization. Window overflow only logs and returns void, so host setup can continue with incomplete mappings. Size programming assumes power-of-two sizes because it writes `~(size - 1)`. Misaligned CSR accesses return a PCI BIOS error internally but the read wrapper still returns zero.

Test signals: direct and paged CSR offsets, byte/word/dword access alignment, outbound/inbound window register values for 32/64-bit addresses, max-window overflow logs, platform override link-up, common LTSSM polling timeout, and enumeration with IO/MEM ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.h -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.h

Purpose: Shared Mobiveil PCIe register definitions, private data structures, operation hooks, and helper prototypes for the common and host implementations.

Important APIs, types, and functions: The header defines PAB register offsets, page-selection macros, LTSSM constants, PIO control/status, interrupt bits, APIO/PPIO address-map register constructors, MSI register offsets, window type constants, limits, and retry constants. `struct mobiveil_msi` tracks MSI domain and bitmap. `struct mobiveil_root_port` stores config aperture, outbound config resource, root-port ops, IRQ/domain state, MSI state, and host bridge. `struct mobiveil_pcie` stores platform device, CSR/APB bases, physical base, window counts/counters, PAB ops, and root-port data. Inline wrappers expose typed CSR reads/writes.

Control flow: no executable flow beyond inline wrappers delegating to `mobiveil_csr_read()`/`mobiveil_csr_write()`. Other Mobiveil files use the definitions to program windows, interrupts, MSI, and link state.

State and persistence: the defined structures hold volatile runtime state allocated by platform drivers. No persistent state exists.

Dependencies and integration points: Linux PCI, IRQ, MSI APIs, the local `../../pci.h`, and all Mobiveil implementation files. It is the ABI between platform-specific drivers and common host/core code.

Risks: Register macros encode hardware layout and window stride; mistakes propagate broadly. MSI vector count is fixed at 16. `ops` and `rp.ops` are optional in some paths but dereferenced in selected helpers, so platform initialization must match expectations. Inline accessors use literal sizes `0x4`, `0x2`, and `0x1`.

Test signals: compile all Mobiveil drivers, static checks for macro expansion, runtime window programming across all indices, MSI allocation up to `PCI_NUM_MSI`, and platform override ops behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-aardvark.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-aardvark.c

Purpose: Marvell Armada 3700 Aardvark PCIe root-complex driver. It configures the controller, emulates a standards-compliant root bridge config space, performs endpoint config cycles through PIO, manages outbound windows, INTx/MSI/PME/AER IRQ domains, optional PHY/reset GPIO, and PCI host enumeration.

Important APIs, types, and functions: `struct advk_pcie` stores MMIO base, outbound window descriptors, IRQ domains/chips, MSI bitmap/locks, link generation, bridge emulation state, optional reset GPIO, and PHY. Hardware setup is in `advk_pcie_setup_hw()` and `advk_pcie_train_link()`. PIO config access is implemented by `advk_pcie_rd_conf()`, `advk_pcie_wr_conf()`, `advk_pcie_wait_pio()`, and `advk_pcie_check_pio_status()`. Root bridge emulation is handled by `advk_pci_bridge_emul_*` callbacks and `advk_sw_pci_bridge_init()`. IRQ support includes MSI parent-domain ops, INTx domain ops, root-port IRQ domain, PME/MSI/INT handlers, and the top-level `advk_pcie_irq_handler()`. `advk_pcie_probe()` prepares windows from host bridge resources, maps MMIO, requests IRQ, gets reset GPIO/max-link-speed/PHY, sets hardware, initializes bridge emulation and domains, then calls `pci_host_probe()`.

Control flow: probe builds non-transparent IO/MEM outbound windows, initializes the controller as RC, fixes vendor/class/device-control values, enables MSI and summary interrupts, programs default transparent memory access, disables PIO address-window usage, programs additional outbound windows, trains the link, initializes the emulated root bridge, then registers PCI ops. Root-bus config reads/writes are served by the emulator; downstream config cycles program PIO type/address/strobe, start transfer, poll completion, handle RRS retry or software-visible RRS, and extract byte/word fields. Interrupt handling demultiplexes core summary status into PME, AER/root-port IRQ, MSI bits, and legacy INTx lines.

State and persistence: volatile state includes hardware control/status registers, LTSSM, PIO command/status, outbound window register values, MSI masks/status and bitmap, bridge emulated config buffer, IRQ domain mappings, reset GPIO state, PHY power, and link generation. No persistent storage.

Dependencies and integration points: PCI host bridge core, `pci-bridge-emul`, ECAM offset helpers, OF PCI ranges, MSI parent-domain library, irqdomain, PHY framework, GPIO descriptors, platform IRQ/MMIO, and compatible `marvell,armada-3700-pcie`.

Risks: PIO while link-down can wedge the controller; the driver explicitly filters non-root accesses when link is down and checks stale PIO start state. Window sizing requires power-of-two, aligned, >=64 KiB regions; invalid ranges abort probe. The emulated bridge must stay synchronized with hardware for command, reset, SERR, link, Root Control/Status, and AER fields. `advk_pcie_disable_phy()` calls PHY operations even if `pcie->phy` is NULL in remove, which relies on remove only after successful setup or should be treated carefully. MSI address uses `virt_to_phys(pcie)` as target.

Test signals: Armada 3700 enumeration, root bridge config-space compliance, downstream Type0/Type1 reads/writes including RRS handling, link-down config filtering, PERST reset timing, outbound IO/MEM windows, INTx/MSI delivery, PME and AER root-port interrupts, max-link-speed values 1-3, remove cleanup with bus removal/domains/MSI/PHY/windows, and invalid range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-aardvark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ftpci100.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ftpci100.c

Purpose: Faraday FTPCI100 conventional PCI host controller driver, used for Gemini and dual variants. It implements config cycles through controller registers, optional cascaded INTx, DMA range programming, bus clock setup, and root-bus scanning.

Important APIs, types, and functions: `struct faraday_pci_variant` flags whether the controller has an embedded cascaded IRQ controller. `struct faraday_pci` stores device, MMIO base, irqdomain, scanned bus, and bus clock. `faraday_res_to_memcfg()` converts IO/DMA resource base and power-of-two size to Faraday memory base/size encoding. `faraday_raw_pci_read_config()` and `faraday_raw_pci_write_config()` issue CONFIG/DATA register accesses; `faraday_pci_ops` wraps them for PCI core. IRQ support includes ack/mask/unmask callbacks, `faraday_pci_irq_handler()`, irqdomain map, and `faraday_pci_setup_cascaded_irq()`. `faraday_pci_parse_map_dma_ranges()` writes up to three DMA memory windows. `faraday_pci_probe()` allocates a host bridge, enables clocks, maps registers, configures IO size, command bits, IRQs, bus speed, DMA windows, scans, assigns resources, and adds devices.

Control flow: probe uses firmware-parsed host bridge windows and DMA ranges. It programs the controller before scanning. If `cascaded_irq` is true, it creates mappings for four INTx lines below the child interrupt-controller node. Bus speed is optionally increased to 66 MHz when both clock rate and capability allow it.

State and persistence: volatile state includes controller IO size/protection/control/config registers, PCI config registers on bus 0 device 0, DMA window registers, clock rate, irqdomain, root bus pointer, and scanned PCI devices. No persistent storage.

Dependencies and integration points: PCI host bridge APIs, OF PCI windows and DMA ranges, platform MMIO, clock framework (`PCLK`, `PCICLK`), irqdomain/chained IRQ, and compatible variants `faraday,ftpci100` and `faraday,ftpci100-dual`.

Risks: `faraday_res_to_memcfg()` supports only enumerated power-of-two sizes and warns but truncates low address bits. Only three DMA ranges are programmed; extras are ignored. Config read debug logs print `*value` before it is read. The driver manually scans/adds devices instead of `pci_host_probe()`, so removal support is absent.

Test signals: Gemini boot enumeration, IO size programming, three DMA range mappings, cascaded INTx delivery and masking, 33/66 MHz clock selection, config byte/word/dword access correctness, and rejection of unsupported resource sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ftpci100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.c

Purpose: Common library for simple ECAM/CAM PCI host controller drivers. It maps config space, initializes a generic host bridge, and provides a shared remove path.

Important APIs, types, and functions: `pci_host_common_ecam_create()` parses the first `reg` resource from OF, locates the bus range in `bridge->windows`, creates a `pci_config_window` with supplied `pci_ecam_ops`, and registers `pci_ecam_free()` via devm action. `pci_host_common_init()` calls `of_pci_check_probe_only()`, stores bridge drvdata, creates ECAM, assigns `bridge->sysdata`, ops, optional enable/disable callbacks, marks MSI domain support, and calls `pci_host_probe()`. `pci_host_common_probe()` gets match data as `pci_ecam_ops`, allocates a host bridge, and delegates init. `pci_host_common_remove()` stops and removes the root bus under rescan/remove locking.

Control flow: generic platform drivers provide only OF match data containing ECAM ops. Probe allocates bridge and calls common init; remove tears down the scanned bus.

State and persistence: volatile state includes devm-managed ECAM config window, host bridge drvdata, root bus, and bridge ops. No persistent state.

Dependencies and integration points: OF address and PCI parsing, PCI ECAM library, platform driver infrastructure, and host bridge core.

Risks: Requires a valid bus resource in `bridge->windows`; missing bus range returns `-ENODEV`. The cast from `ops->pci_ops` to `struct pci_ops *` assumes lifetime and constness are safe. MSI domain is unconditionally true for common hosts.

Test signals: generic ECAM/CAM host probes, malformed `reg` rejection, missing bus range rejection, ECAM free on probe failure/remove, and clean root bus removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.h -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.h

Purpose: Public declarations for the common PCI host controller helper library.

Important APIs, types, and functions: forward declares `struct pci_ecam_ops` and declares `pci_host_common_probe()`, `pci_host_common_init()`, `pci_host_common_remove()`, and `pci_host_common_ecam_create()`.

Control flow: no runtime flow; it is included by generic host drivers and the implementation file.

State and persistence: no state. It exposes functions that manage host bridge and ECAM runtime state elsewhere.

Dependencies and integration points: platform PCI host drivers use this header to share the ECAM creation/probe/remove path. The header relies on standard kernel struct declarations being visible from including translation units.

Risks: Function prototypes mention `struct platform_device`, `struct pci_host_bridge`, `struct device`, and `struct pci_config_window` without local forward declarations for all of them; current includes in users satisfy this. ABI changes in the common implementation require updating this header.

Test signals: compile users such as `pci-host-generic.c`, module symbol availability for exported helpers, and type-checking under different include orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-generic.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-generic.c

Purpose: Generic firmware-initialized PCI host controller driver for CAM/ECAM systems and selected DesignWare ECAM-compatible hosts. It supplies OF match data and filtering wrappers, then delegates probe/remove to `pci-host-common`.

Important APIs, types, and functions: `gen_pci_cfg_cam_bus_ops` defines CAM config mapping with `bus_shift = 16`. `pci_dw_valid_device()` filters DesignWare ECAM direct-downstream slots greater than zero to prevent duplicated devices. `pci_dw_ecam_map_bus()` applies that filter before `pci_ecam_map_bus()`. `pci_dw_ecam_bus_ops` wraps generic read/write with the filtered mapper. `gen_pci_of_match` maps compatible strings to CAM, generic ECAM, or filtered DWC ECAM ops. The platform driver uses `pci_host_common_probe` and `pci_host_common_remove`.

Control flow: OF match selects ops; common probe maps ECAM and registers the host bridge. Config access is generic except for DWC-compatible filtering.

State and persistence: no private runtime state in this file; state is ECAM window and host bridge state managed by the common helper.

Dependencies and integration points: PCI ECAM library, `pci-host-common`, OF platform matching, generic PCI config read/write, and compatible strings such as `pci-host-ecam-generic`, `pci-host-cam-generic`, `snps,dw-pcie-ecam`, Armada8k, and SynQuacer.

Risks: DWC filtering assumes only slot 0 below the root bus is valid. Selecting the wrong compatible can expose duplicate devices or hide valid devices. The CAM bus shift is fixed at 16.

Test signals: generic ECAM and CAM enumeration, DWC ECAM duplicate-slot filtering, root bus removal, and OF match data coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv-intf.c -->
## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv-intf.c

Purpose: Small exported interface layer between generic PCI users and the Hyper-V PCI frontend. It provides callback indirection for block configuration reads, writes, and invalidation registration.

Important APIs, types, and functions: global `struct hyperv_pci_block_ops hvpci_block_ops` is exported GPL so the Hyper-V PCI frontend can populate operations. `hyperv_read_cfg_blk()` calls `hvpci_block_ops.read_block` if present. `hyperv_write_cfg_blk()` calls `write_block`. `hyperv_reg_block_invalidate()` calls `reg_blk_invalidate`. All wrappers return `-EOPNOTSUPP` when the relevant callback is absent. All wrapper functions are exported GPL.

Control flow: clients call the exported helpers; helpers dispatch through the global ops table. There is no probe path.

State and persistence: state is the global function-pointer table only, populated by another module/driver at runtime. No persistent storage exists.

Dependencies and integration points: Hyper-V headers, PCI device pointers, module export infrastructure, and whichever Hyper-V PCI frontend owns `hvpci_block_ops` initialization.

Risks: The global ops table has no explicit locking here, so writers and callers must rely on module load/unload ordering or external synchronization. A missing callback produces feature-not-supported behavior. The helper layer does not validate buffer lengths beyond forwarding them.

Test signals: symbol export resolution, calls before frontend registration returning `-EOPNOTSUPP`, successful read/write/invalidate callback dispatch after registration, and module unload ordering safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/pci-hyperv-intf.c -->
