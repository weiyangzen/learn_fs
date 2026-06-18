# Research Report: subset-b-004999

This grouped report covers the requested Synopsys DesignWare PCIe core, host, endpoint, debugfs, generic platform glue, and several SoC-specific DWC controller drivers. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-keystone.c

Purpose: Implements the Texas Instruments Keystone and AM654 DesignWare PCIe glue driver, supporting legacy Keystone root-complex mode and AM654 root-complex/endpoint mode. It owns application-register access, SoC mode selection, PHY/reset sequencing, custom MSI/INTx/error interrupts, Keystone-specific config-space mapping, endpoint interrupt raising, and Keystone/AM654 quirks.

Important APIs and types: `struct keystone_pcie` stores the DWC core pointer, application register mapping/resource, PHY/device-link arrays, interrupt domains, host IRQs, lane count, viewport count, and AM6 flag. `struct ks_pcie_of_data` selects RC/EP mode, host ops, endpoint ops, and DWC version. Key callbacks are `ks_pcie_host_init()`, `ks_pcie_msi_host_init()`, `ks_pcie_start_link()`, `ks_pcie_stop_link()`, `ks_pcie_link_up()`, `ks_pcie_am654_ep_init()`, `ks_pcie_am654_raise_irq()`, `ks_pcie_probe()`, and `ks_pcie_remove()`. IRQ plumbing includes `ks_pcie_msi_irq_chip`, `ks_pcie_intx_irq_chip`, chained MSI/INTx handlers, and an error IRQ handler.

Control flow: Probe matches OF data, maps `app` and `dbics`, installs the shared DWC ops, requests the error IRQ, acquires per-lane PHYs and device links, enables PHY power, enables runtime PM, programs RC/EP mode through syscon, then dispatches to `dw_pcie_host_init()` for RC or `dw_pcie_ep_init()` plus `dw_pcie_ep_init_registers()` for EP. RC init installs Keystone config ops, configures INTx/MSI child interrupt controllers, stops link training, disables RC BARs, optionally programs legacy outbound windows, writes IO range type, and initializes vendor/device IDs from syscon. Link start/stop toggles the LTSSM bit in application `CMD_STATUS`. AM654 EP init programs BAR0 through DBI2 and endpoint IRQ raising delegates MSI/MSI-X to the generic EP core while pulsing application registers for INTx.

State and persistence: Persistent hardware state includes application `CMD_STATUS`, outbound translation windows, BAR masks/values, IRQ enables/status, syscon mode bits, PHY power/reset state, and endpoint BAR/interrupt state. Driver state persists in `keystone_pcie`, the DWC `dw_pcie` object, IRQ domains, chained IRQ handlers, runtime PM, and device links. Remove drops runtime PM, powers off PHYs, and removes links, but most devm allocations are released by driver core.

Dependencies and integration points: Depends on the DWC host/EP core, Linux IRQ domains/MSI framework, PHY/reset/GPIO/runtime-PM APIs, syscon regmap, OF child interrupt-controller nodes, and PCI fixup hooks. It exports no APIs but integrates through `dw_pcie_ops`, `dw_pcie_host_ops`, `dw_pcie_ep_ops`, and `DECLARE_PCI_FIXUP_ENABLE()`. On ARM it registers a fault handler to turn absent-device config aborts into all-ones reads.

Risks: DBI mode switching is a clock-domain-sensitive polling loop without timeout, so a stuck DBI_CS2 bit can hang. Keystone config reads still race link-down even with the defensive link check. IRQ child-node absence is fatal on non-AM6 but tolerated on AM6, so DT compatibility matters. MRRS fixups are broad and must match only Keystone/AM654 root ports. EP BAR feature declarations reserve BAR0/BAR1 in a compatibility-preserving way; changing them can alter userspace EPF behavior. PHY enable error unwinding and device-link cleanup must stay aligned with partially populated lane arrays.

Test signals: Build with `CONFIG_PCI_KEYSTONE_HOST` and `CONFIG_PCI_KEYSTONE_EP`, boot Keystone and AM654 DTs, verify syscon mode programming, link-up logs, PCI enumeration, MRRS limits of 256 bytes or AM654 PG1 128 bytes, MSI and INTx delivery, error IRQ logging, EP `pci_epc` init notifications, MSI/MSI-X/INTx EP raises, suspend/remove PHY cleanup, and absent-device config access on ARM without kernel aborts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-keystone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape-ep.c

Purpose: Provides the NXP/Freescale Layerscape endpoint-mode DWC PCIe glue. It initializes the generic endpoint controller, exposes SoC-specific endpoint capabilities, handles link-up/link-down/hot-reset PME-message interrupts, supports big-endian PF LUT registers, and supplies function-specific DBI offsets for multi-function endpoints.

Important APIs and types: `struct ls_pcie_ep` holds the DWC pointer, mutable `pci_epc_features`, matched `ls_pcie_ep_drvdata`, PME IRQ number, saved link capability register, and endian flag. `struct ls_pcie_ep_drvdata` provides the function DBI stride. Important functions are `ls_pcie_ep_event_handler()`, `ls_pcie_ep_interrupt_init()`, `ls_pcie_ep_init()`, `ls_pcie_ep_raise_irq()`, `ls_pcie_ep_get_dbi_offset()`, and `ls_pcie_ep_probe()`.

Control flow: Probe allocates the Layerscape and DWC objects plus a feature structure, maps the `regs` resource as DBI, records endianness, initializes a 64-bit DMA mask, saves the initial PCIe link capability register, calls `dw_pcie_ep_init()` and `dw_pcie_ep_init_registers()`, notifies the endpoint core, then enables the named `pme` IRQ. The PME handler acknowledges all pending PME message status bits, restores `PCI_EXP_LNKCAP` after link-up/hot reset loss, sets PF0 config ready, and calls `dw_pcie_ep_linkup()` or `dw_pcie_ep_linkdown()`. IRQ raising delegates INTx/MSI/MSI-X to the DWC EP helpers, using the MSI-X doorbell variant.

State and persistence: Driver state includes the saved `lnkcap`, detected MSI/MSI-X capability bits copied into `ls_epc`, and DBI offset rules. Hardware state includes PME interrupt enable/status, PF0 config-ready, restored non-sticky link capability fields, endpoint BARs/iATU programmed by the generic EP core, and link-notifier state in the PCI EPC framework.

Dependencies and integration points: Integrates with `pcie-designware-ep.c`, Linux platform/OF resources, PCI endpoint controller framework, and DT compatibles for LS1028A/LS1046A/LS1088A/LS2088A/LX2160A endpoint controllers. The `get_dbi_offset` callback is important for multi-function EPF support.

Risks: PME events are shared IRQs and depend on correct status clearing. Losing or failing to restore `PCI_EXP_LNKCAP` after link-down/hot reset can make the host see wrong speed/width. Feature capabilities are inferred only from function 0 during EP init. Incorrect `func_offset` values silently direct per-function DBI writes to the wrong function. Big-endian access must match hardware register wiring.

Test signals: Build endpoint support, probe each compatible, verify `pme` IRQ registration, link-up/link-down EPF notifications, hot-reset behavior, restored max speed/width in config space, multi-function DBI access on LS2/LX2 offsets, MSI/MSI-X/INTx raising, and big-endian DT operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape.c

Purpose: Implements Layerscape root-complex glue for DWC PCIe. It handles PF LUT access, root-port mode validation, bridge header cleanup, message filtering, non-posted error response behavior, SoC-specific PME_Turn_Off and L2-exit sequences, and host suspend/resume integration.

Important APIs and types: `struct ls_pcie` stores the DWC pointer, matched `ls_pcie_drvdata`, PF LUT base, optional SCFG regmap/index, and endian flag. `struct ls_pcie_drvdata` selects PF LUT offset, host ops, L2-exit callback, and SCFG/PM support. Main functions are `ls_pcie_host_init()`, `ls_pcie_send_turnoff_msg()`, `ls_pcie_exit_from_l2()`, `ls1021a_pcie_*()`, `ls1043a_pcie_*()`, `ls_pcie_probe()`, `ls_pcie_suspend_noirq()`, and `ls_pcie_resume_noirq()`.

Control flow: Probe allocates objects, maps `regs` as DBI, sets `pf_lut_base` from drvdata, optionally resolves the SCFG phandle and port index, validates that the controller header is a PCI bridge, then calls `dw_pcie_host_init()`. Host init configures bridge slave error forwarding, temporarily enables DBI read-only writes to clear the multifunction bit, and drops non-vendor message TLPs. Runtime PM hooks call generic DWC suspend/resume only for PM-capable variants; resume first invokes the variant L2-exit sequence through PF MCR, SCFG reset bits, or LS1043A LUT debug soft reset.

State and persistence: Persistent hardware state includes PEX internal configuration, PF LUT command bits, message-filter and error-response registers, bridge header type, SCFG PME/reset bits, and DWC host/iATU/MSI state. Driver state is minimal and static after probe, aside from generic DWC suspend flags.

Dependencies and integration points: Uses the DWC host core, syscon regmap for SCFG-backed SoCs, PCI host bridge resources, OF match data, and noirq system sleep callbacks. `pme_turn_off` callbacks plug into `dw_pcie_suspend_noirq()`.

Risks: PM sequences are SoC-specific and timeout/handshake behavior differs between PF LUT and SCFG paths. The driver returns `-ENODEV` if firmware has not configured bridge mode, so bootloader/RCW setup is part of the contract. Endian selection affects all PF LUT accesses. Clearing multifunction and dropping message TLPs are broad register changes that can affect unusual devices or future capabilities.

Test signals: Probe all supported compatible strings, confirm root-port header detection, enumeration behind the bridge, error-response behavior for failed non-posted requests, PME_Turn_Off on suspend, L2 exit on resume, LS1021A/LS1043A SCFG paths, big-endian DT operation, and clean `dw_pcie_host_deinit()` on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-meson.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-meson.c

Purpose: Implements Amlogic Meson AXG/G12A root-complex glue for DWC PCIe. It manages resets, clocks, PHY power, reset GPIO, local config registers, link training, link status, payload/read-request sizing, and a config-space class-code workaround.

Important APIs and types: `struct meson_pcie` embeds `struct dw_pcie` and stores config-register base, clocks, reset controls, reset GPIO, and PHY. Main functions are `meson_pcie_get_resets()`, `meson_pcie_get_mems()`, `meson_pcie_power_on()`, `meson_pcie_reset()`, `meson_pcie_probe_clocks()`, `meson_pcie_start_link()`, `meson_pcie_rd_own_conf()`, `meson_pcie_link_up()`, `meson_pcie_host_init()`, and `meson_pcie_probe()`.

Control flow: Probe creates the embedded DWC object, acquires `pcie` PHY and reset GPIO, deasserts port/APB resets, maps legacy `elbi`/DBI and `cfg` resources, powers the PHY, performs PHY and controller reset sequencing, enables required clocks, installs host and DWC ops, and calls `dw_pcie_host_init()`. Host init replaces root-bus PCI ops to fabricate bridge class code and writes max payload/read request sizes. Link start enables LTSSM in the Meson config block and toggles endpoint PERST through the reset GPIO.

State and persistence: Hardware state includes reset controls, PHY power, clock enables and rates, Meson config `APP_LTSSM_ENABLE`, device-control payload/read-request fields, and the GPIO reset line. Driver state is devm-managed and no explicit remove path powers down after successful probe.

Dependencies and integration points: Integrates with DWC host core, Linux clock/reset/PHY/GPIO APIs, and DT resources named `elbi` and `cfg`. The root config accessor uses `dw_pcie_own_conf_map_bus()` but overrides reads for `PCI_CLASS_REVISION`.

Risks: The class-code workaround is essential because software cannot program `PCI_CLASS_DEVICE`; removing it can break PCI core recognition. The historical `elbi`-as-DBI DT compatibility path is fragile but needed. Clock/reset/PHY order is timing-sensitive. Lack of explicit remove/suspend support means cleanup relies on devm and boot-time usage assumptions.

Test signals: Boot AXG/G12A DTs, verify PHY/reset/clock acquisition, bridge class code seen by PCI core, Gen/link status through Meson status bits, payload/read request values of 256 bytes, enumeration behind the root port, failed-probe PHY power-off, and no regressions with old `elbi` DT naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-meson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-al.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-al.c

Purpose: Provides Amazon Annapurna Labs PCIe support in two forms: an ACPI ECAM quirk path for root-complex DBI access and a DT platform driver for Alpine/Graviton-style DWC host controllers with controller-specific config-window target-bus programming.

Important APIs and types: Under ACPI quirks, `struct al_pcie_acpi`, `al_pcie_init()`, and `al_pcie_map_bus()` implement `const struct pci_ecam_ops al_pcie_ops`. Under `CONFIG_PCIE_AL`, `struct al_pcie` stores DWC/root-port state, controller register base, ECAM size, revision, register offsets, and target-bus cache. Key functions are `al_pcie_rev_id_get()`, `al_pcie_reg_offsets_set()`, `al_pcie_target_bus_set()`, `al_pcie_conf_addr_map_bus()`, `al_pcie_config_prepare()`, `al_pcie_host_init()`, and `al_pcie_probe()`.

Control flow: The ACPI path obtains the root-complex DBI resource via `acpi_get_rc_resources()` and maps root-bus slot 0 accesses to DBI while all other buses use normal ECAM. The DT path maps the `config` and `controller` resources, marks native ECAM, runs DWC host init, detects controller revision from device ID bits, chooses register offsets, computes how many bus bits are represented in the ECAM address versus the controller target-bus register, programs the target-bus mask/value and secondary/subordinate bus numbers, and installs child config ops that update the target-bus register when crossing bus ranges.

State and persistence: Hardware state includes the controller outbound-control target bus and secondary/subordinate bus fields. Driver state caches revision-derived offsets, ECAM size, and current target-bus register value. ACPI state is kept in `cfg->priv`.

Dependencies and integration points: Depends on Linux PCI ECAM, ACPI root resources, optional `CONFIG_PCI_QUIRKS`, DWC host core, and DT resources. The platform driver delegates standard resource/iATU/link setup to `dw_pcie_host_init()` but overrides child config mapping.

Risks: Bus-number split logic depends on ECAM window size and 256-bus maximum assumptions; bad firmware resources can misroute config cycles. Revision detection only recognizes x4/x8/x16 encoded device IDs. The ACPI root bus filter intentionally rejects functions/devices other than slot 0, matching DWC root-port behavior. Incorrect target-bus cache updates would create intermittent config access failures.

Test signals: ACPI boot with `AMZN0001` root resources, DT boot on Alpine v2/v3, root-bus slot filtering, enumeration beyond one bus, target-bus register changes during config scans, revision-specific outbound-control offsets, large ECAM warning behavior, and config reads across secondary/subordinate ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-al.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-amd-mdb.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-amd-mdb.c

Purpose: Implements the AMD MDB PCIe bridge host driver for `amd,versal2-mdb-host`. It wraps the DWC host core with MDB SLCR interrupt handling, event and INTx IRQ domains, reset GPIO parsing, PERST sequencing, and simple warning reports for completion/error/PM events.

Important APIs and types: `struct amd_mdb_pcie` embeds `struct dw_pcie`, maps SLCR registers, stores event and INTx IRQ domains, PERST GPIO, and INTx IRQ. Main functions are `amd_mdb_pcie_init_irq_domains()`, `amd_mdb_setup_irq()`, `amd_mdb_pcie_event()`, `amd_mdb_pcie_intr_handler()`, `dw_pcie_rp_intx()`, `amd_mdb_pcie_init_port()`, `amd_mdb_parse_pcie_port()`, `amd_mdb_add_pcie_port()`, and `amd_mdb_pcie_probe()`.

Control flow: Probe allocates the embedded DWC object, parses a child `pcie*` reset GPIO or falls back to the host node reset GPIO, maps `slcr`, creates a 32-entry MDB event domain and a four-entry wired INTx domain from the DT child interrupt-controller, disables/clears/enables all supported TLP interrupts, maps/request IRQs for named event causes, maps INTx through the event domain, requests the top-level platform IRQ as the event demux, deasserts PERST after PCIe timing delays, and enters `dw_pcie_host_init()`.

State and persistence: SLCR interrupt enable/disable/status registers retain event/INTx masks and pending bits. IRQ-domain state maps hardware causes to Linux IRQs. `pp->lock` serializes mask updates. PERST GPIO state controls endpoint reset. Generic host state lives in the embedded DWC root port.

Dependencies and integration points: Depends on OF child interrupt-controller nodes, Linux irqdomain APIs, GPIO descriptor APIs, DWC host core, and PCI timing constants. The current host ops table is empty; all platform-specific behavior is interrupt/reset setup before generic host init.

Risks: `amd_mdb_pcie_event()` demuxes every unmasked status bit, but only configured causes have installed leaf handlers; unknown bits can still hit the domain. Error events currently log warnings rather than integrating with AER. INTx status extraction relies on packed bit layout and `AMD_MDB_PCIE_INTR_INTX_ASSERT()`. Only one root port is supported despite child-node iteration. IRQ domain cleanup is manual on setup failure.

Test signals: Boot the Versal2 MDB DT, verify child or fallback reset GPIO handling, top-level interrupt demux, completion-timeout/PME/correctable/nonfatal/fatal warning logs, wired INTx delivery to PCI devices, masking/unmasking writes, host enumeration after PERST delays, and cleanup on IRQ setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-amd-mdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-andes-qilai.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-andes-qilai.c

Purpose: Implements the Andes QiLai DWC PCIe root-complex glue. It enables LTSSM through APB registers, reports link state from APB status bits, enables MSI at the APB interrupt-control level, and programs IO coherence-port cache attributes after host initialization.

Important APIs and types: `struct qilai_pcie` embeds `struct dw_pcie` and stores `apb_base`. Key functions are `qilai_pcie_link_up()`, `qilai_pcie_start_link()`, `qilai_pcie_enable_msi()`, `qilai_pcie_iocp_cache_setup()`, `qilai_pcie_host_init()`, `qilai_pcie_host_post_init()`, and `qilai_pcie_probe()`.

Control flow: Probe allocates the embedded DWC object, enables use of parent DT ranges and required generic resources with `dw_pcie_cap_set(..., REQ_RES)`, maps the `apb` resource, enables runtime PM without callbacks, and calls `dw_pcie_host_init()`. Host init sets the APB MSI enable bit. After the PCI host is probed, post-init enables write-back/read-write-allocate ARCACHE/AWCACHE modes in `PCIE_LOGIC_COHERENCY_CONTROL3`.

State and persistence: Hardware state includes APB LTSSM enable, MSI interrupt enable, APB link status, and DWC coherency-control cache attributes. Driver state is the mapped APB base and embedded DWC core; runtime PM is marked active but has no callbacks.

Dependencies and integration points: Integrates with the generic DWC host core, runtime PM helpers, OF resource mapping, and DWC clock/reset resource management through `REQ_RES`. Cache attribute programming depends on DBI read-only write enable/disable.

Risks: Coherency mode affects DMA visibility and system-cache snooping; wrong ARCACHE/AWCACHE values can cause data coherency or performance problems. MSI requires both APB and generic DWC MSI setup. The link-up helper uses `FIELD_GET()` on single-bit masks, which is correct but easy to misread. Parent DT ranges must describe address translation correctly.

Test signals: Probe `andestech,qilai-pcie`, verify required clocks/resets are obtained, link-up via SMLH/RDLH bits, MSI interrupt delivery, coherency-control register values after post-init, PCI DMA correctness under cache pressure, and runtime PM active state during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-andes-qilai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-armada8k.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-armada8k.c

Purpose: Implements Marvell Armada-8K DWC PCIe root-complex glue. It enables clocks/PHYs, selects root-complex mode, configures AXI cache/domain attributes, enables/discards latched legacy INTx causes, controls LTSSM, and delegates host bring-up to the DWC core.

Important APIs and types: `struct armada8k_pcie` stores the DWC pointer, main and register clocks, up to four PHYs, and PHY count. Main functions are `armada8k_pcie_setup_phys()`, `armada8k_pcie_enable_phys()`, `armada8k_pcie_disable_phys()`, `armada8k_pcie_link_up()`, `armada8k_pcie_start_link()`, `armada8k_pcie_host_init()`, `armada8k_pcie_irq_handler()`, `armada8k_add_pcie_port()`, and `armada8k_pcie_probe()`.

Control flow: Probe enables the unnamed clock and optional `reg` clock, maps `ctrl` as DBI/vendor registers, discovers up to four PHYs from DT, initializes/powers them with `PHY_MODE_PCIE` and lane count, installs DWC ops, requests the controller IRQ, then calls `dw_pcie_host_init()`. Host init disables LTSSM if the link is down, writes device type as RC, sets AR/AW cache and domain attributes, and unmasks INT A-D latch bits. The IRQ handler only clears latched controller causes because endpoint/device handlers service the real interrupts.

State and persistence: Hardware state includes clock enables, PHY mode/power, global control/status, root-complex device type, AXI cache/user-domain registers, global interrupt masks, and DWC iATU/MSI/host state. Driver state tracks optional PHYs and clocks; error paths explicitly unwind PHY and clock enables.

Dependencies and integration points: Depends on DWC host core, clock and PHY frameworks, platform IRQs, OF PHY lookup, and Armada8K vendor registers at offset `0x8000`.

Risks: `armada8k_pcie_disable_phys()` iterates all four PHY slots even when some are NULL; this relies on PHY helpers tolerating NULL or can be fragile depending on API behavior. Optional old DTs without PHY handles are accepted with a warning. The controller IRQ is a latch-clear path, not a hierarchical INTx domain; changing it could duplicate device interrupt handling. AXI cache/domain defaults are platform integration sensitive.

Test signals: Boot Armada8K DTs with one/four lanes and old no-PHY bindings, verify clock and optional reg-clock handling, PHY mode lane count, RC mode register, Gen/link-up logs, legacy INTx devices still interrupt correctly while latch causes are cleared, failed host-init unwind, and DMA coherency under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-armada8k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-artpec6.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-artpec6.c

Purpose: Implements Axis ARTPEC-6/ARTPEC-7 DWC PCIe glue for both root-complex and endpoint modes. It performs variant-specific PHY and NoC power sequencing, core reset control, LTSSM start/stop, address fixups for translated CPU/controller addresses, endpoint feature/IRQ support, and RC/EP OF-mode selection.

Important APIs and types: `struct artpec6_pcie` stores the DWC pointer, syscon regmap, PHY register mapping, variant, and mode. `struct artpec_pcie_of_data` selects ARTPEC6/ARTPEC7 and RC/EP mode. Key functions are `artpec6_pcie_cpu_addr_fixup()`, `artpec6_pcie_establish_link()`, `artpec6_pcie_stop_link()`, `artpec6_pcie_init_phy_a6()`, `artpec6_pcie_init_phy_a7()`, `artpec6_pcie_wait_for_phy_*()`, `artpec6_pcie_host_init()`, `artpec6_pcie_ep_init()`, `artpec6_pcie_raise_irq()`, and `artpec6_pcie_probe()`.

Control flow: Probe maps the `phy` resource, gets `axis,syscon-pcie`, installs DWC ops, then dispatches to RC or EP mode based on match data and Kconfig. RC host init optionally sets ARTPEC7 N_FTS values, asserts reset, initializes PHY/NoC/reference clock fields, deasserts reset, waits for PHY readiness, and enters generic DWC host initialization. EP mode clears device-type bits, initializes the DWC endpoint controller, initializes endpoint registers, and notifies EPC clients. Link start/stop toggles the syscon LTSSM bit.

State and persistence: Hardware state includes syscon `PCIECFG`, `PCIESTAT`, `NOCCFG`, PHY status/ASIC handshake registers, reset bits, reference-clock selection, LTSSM enable, and DWC RC/EP/iATU state. `cpu_addr_fixup()` changes DWC parent-bus offset behavior by subtracting RC config or EP address-space bases.

Dependencies and integration points: Integrates with the DWC host and endpoint cores, syscon regmap, platform resources, OF match data, and PCI endpoint framework. Endpoint features expose common DWC BAR defaults and MSI capability; INTx is explicitly unsupported.

Risks: Variant-specific sequencing is timing-sensitive and uses retry loops that log errors but continue. Address fixup is critical for correct iATU parent-bus offsets; broken DT ranges will be warned and corrected by the common core. EP mode supports MSI but not INTx/MSI-X, so EPF expectations must match. ARTPEC7 reference-clock selection depends on hardware strap/status.

Test signals: Boot ARTPEC6/7 RC and EP compatibles, verify PHY wait logs, link training, DWC parent-bus offset warnings/absence, ARTPEC7 N_FTS programming, endpoint EPC init notification, MSI raise success and INTx rejection, suspend/reset recovery where applicable, and enumeration behind RC mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-artpec6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-debugfs.c

Purpose: Adds optional debugfs support for DWC PCIe controllers: RAS-DES lane/debug state, RAS-DES error injection, RAS-DES event counters, LTSSM status, and PTM debug controls/clock reads. It is shared by RC and EP mode via `dwc_pcie_debugfs_init()` and `dwc_pcie_debugfs_deinit()`.

Important APIs and types: `struct dwc_pcie_rasdes_info` stores the RAS-DES VSEC offset and event-register mutex. `struct dwc_pcie_rasdes_priv` stores per-file PCI pointer and table index. Static tables `err_inj_list[]` and `event_list[]` enumerate supported injections and counters. Main functions are `dwc_pcie_rasdes_debugfs_init()`, `err_inj_write()`, `counter_*_{read,write}()`, `ltssm_status_show()`, PTM callbacks in `dw_pcie_ptm_ops`, `dwc_pcie_debugfs_init()`, and `dwc_pcie_debugfs_deinit()`.

Control flow: Debugfs init creates `dwc_pcie_<devname>`, tries to locate the RAS-DES VSEC, skips RAS-DES gracefully if absent, creates lane debug files, one write-only file per error injection, one directory per event counter with enable/value and optional lane-select files, then adds LTSSM status and PTM debugfs through the generic PTM helper. RAS-DES counter operations serialize on `reg_event_lock` because group/event/lane/value share shadow registers. Error injection parses counter/value-difference/VC arguments based on injection group, writes the group-specific register, then enables that injection group.

State and persistence: Debugfs state is devm-allocated and referenced from `pci->debugfs`. Hardware-visible state includes RAS-DES lane select, error injection registers, event counter enable/lane selection, PTM context update/valid bits, and PTM timestamps/clocks. `pci->mode` gates PTM file visibility for RC versus EP.

Dependencies and integration points: Depends on Linux debugfs, seq_file, DWC DBI accessors, VSEC discovery helpers from `pcie-designware.c`, generic PCIe PTM debugfs helpers, and DWC LTSSM helpers. Host and EP init call it after controller setup; cleanup is called from host deinit and EP cleanup.

Risks: `dwc_pcie_debugfs_deinit()` unconditionally calls RAS-DES deinit when `pci->debugfs` exists; if RAS-DES capability was absent, `rasdes_info` may be NULL unless callers avoid that path or the implementation is hardened. Error injection is powerful and can intentionally corrupt PCIe traffic; file permissions are debugfs-only but still dangerous. Input validation checks ranges for some groups but does not validate every hardware-supported lane/event combination. Timestamp reads loop until MSB is stable, which assumes registers make progress.

Test signals: Mount debugfs and verify directory creation with and without RAS-DES VSEC, read LTSSM status, exercise lane detect/RX valid lane selection, enable/read counters for representative groups, inject controlled errors on a test link, verify mutex-protected counter selection under concurrent reads, create/destroy PTM files in RC and EP modes, and unload/deinit without NULL dereferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-ep.c

Purpose: Implements the shared DWC PCIe endpoint controller backend used by platform EP glue drivers. It creates the Linux EPC device, manages endpoint function metadata, configures BARs and inbound/outbound iATU windows, writes endpoint headers, handles MSI/MSI-X/INTx operations, initializes non-sticky endpoint registers, tracks link notifications, and cleans up eDMA/debugfs/resources.

Important APIs and types: Public APIs include `dw_pcie_ep_init()`, `dw_pcie_ep_init_registers()`, `dw_pcie_ep_deinit()`, `dw_pcie_ep_cleanup()`, `dw_pcie_ep_linkup()`, `dw_pcie_ep_linkdown()`, `dw_pcie_ep_reset_bar()`, `dw_pcie_ep_get_func_from_ep()`, `dw_pcie_ep_raise_intx_irq()`, `dw_pcie_ep_raise_msi_irq()`, `dw_pcie_ep_raise_msix_irq()`, and `dw_pcie_ep_raise_msix_irq_doorbell()`. Internal state uses `struct dw_pcie_ep`, `struct dw_pcie_ep_func`, BAR/iATU bitmaps, per-BAR ATU indexes, MSI mapping cache fields, and `epc_ops`.

Control flow: `dw_pcie_ep_init()` creates the EPC object, gathers DWC and `addr_space` resources, computes parent-bus offset, reads `max-functions`, optionally calls glue `pre_init`, initializes EPC memory, and reserves a page for MSI/MSI-X writes. `dw_pcie_ep_init_registers()` verifies EP header type, detects version/iATU/eDMA, allocates iATU maps, creates per-function records and capability offsets, calls glue `init`, disables BARs, hides PTM responder/root bits as needed, runs non-sticky setup, and starts debugfs. EPC ops then program headers, BAR masks/resizable BAR capabilities, BAR-match or address-match inbound ATUs, outbound mappings, MSI/MSI-X configuration, and start/stop link through glue DWC ops.

State and persistence: Persistent driver state includes per-function capability offsets, active BAR descriptors, inbound/outbound iATU bitmaps, address-match submap indexes, cached outbound MSI iATU mapping, MSI target address/size, and endpoint memory allocations. Hardware state includes DBI/DBI2 BAR masks, resizable BAR caps, command/header fields, iATU windows, MSI/MSI-X capability/table registers, PTM capability bits, DWC link parameters, eDMA registration, and debugfs state. Link-down reinitializes non-sticky DWC registers before notifying EPF drivers.

Dependencies and integration points: This file is the bridge between DWC glue drivers and Linux `pci_epc`/`pci_epf`. It depends on DWC core iATU/eDMA/version/debugfs helpers, endpoint framework memory windows, capability walkers, DBI per-function accessors, and glue-provided `dw_pcie_ep_ops` for features, DBI offsets, initialization, IRQ raising, and link control.

Risks: BAR programming has many subtle contracts: 64-bit BARs must be even-numbered, submap mode is update-only after host assignment, resizable BAR selected-size semantics are controller-specific, and reserved BAR behavior comes from glue features. MSI keeps an outbound iATU mapped to avoid unsafe reprogramming while traffic is in flight; host MSI address changes force unmap/remap with no universal quiescence check. MSI-X non-doorbell path maps and unmaps for each interrupt. Inbound/outbound window exhaustion and alignment errors must be surfaced cleanly. EP cleanup must match init order to avoid leaked eDMA/debugfs/iATU state.

Test signals: EPF tests for header writes, BAR clear/set for fixed/programmable/resizable BARs, 32/64-bit BAR rejection on odd numbers, address-match submaps, host-assigned BAR update without clearing PCI address, outbound map/unmap exhaustion, MSI and MSI-X delivery including host MSI address changes, linkup/linkdown notifications, multi-function link capability mirroring, PTM capability hiding, eDMA detection paths, and repeated stop/start/deinit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-ep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-host.c

Purpose: Implements the shared DWC PCIe root-complex backend. It allocates PCI host bridges, maps config resources, decides ECAM versus iATU config access, creates MSI domains, configures outbound/inbound iATU windows, sets up RC config registers, handles link training and PCI enumeration, integrates eDMA/debugfs, and provides noirq suspend/resume.

Important APIs and types: Public APIs include `dw_pcie_host_init()`, `dw_pcie_host_deinit()`, `dw_pcie_setup_rc()`, `dw_pcie_msi_host_init()`, `dw_pcie_msi_init()`, `dw_handle_msi_irq()`, `dw_pcie_allocate_domains()`, `dw_pcie_free_msi()`, `dw_pcie_own_conf_map_bus()`, `dw_pcie_suspend_noirq()`, and `dw_pcie_resume_noirq()`. Important internals are `dw_pcie_host_get_resources()`, `dw_pcie_iatu_setup()`, `dw_pcie_config_ecam_iatu()`, MSI bottom irq-chip/domain ops, config-space map/read/write ops, and equalization preset programming.

Control flow: Host init allocates a `pci_host_bridge`, maps `config`/DBI/ATU/resources, runs glue `init`, sets up MSI either through glue/firmware MSI parent or the DWC iMSI-RX path, detects DWC version and iATU capabilities, derives lane count and equalization presets, reserves optional MSG TLP space, detects eDMA, sets up RC registers/iATU, starts link if needed, waits for link, probes the PCI host bridge, runs glue `post_init`, and initializes debugfs. Deinit reverses debugfs, root bus, link, eDMA, MSI, glue deinit, and ECAM allocation. Suspend sends PME_Turn_Off by glue callback or generic MSG iATU, waits for L2/L3 where possible, stops link, calls deinit, and marks suspended; resume re-runs init, RC setup, link start/wait, and post-init.

State and persistence: `struct dw_pcie_rp` owns the host bridge, config windows, ECAM object, MSI domain and bitmaps, IRQ masks, MSI target address, equalization presets, optional message resource/index, and suspend flag. Hardware state includes RC BARs, class/command/bus numbers, iATU windows for CFG/MEM/IO/MSG/DMA ranges, MSI target/masks/enables, link speed/width/equalization fields, L1SS visibility, eDMA, and debugfs state.

Dependencies and integration points: Integrates with Linux PCI host bridge probing/removal, MSI irqdomain library, OF PCI ranges and equalization presets, ECAM helpers, DWC core iATU/link/eDMA/debugfs helpers, and glue-provided `dw_pcie_host_ops`. Vendor drivers can override root/child config ops, MSI init, PME turnoff, post-init, and deinit.

Risks: Resource translation and iATU window accounting are high risk: config windows reserve index 0 or 0/1 under ECAM, memory resources may need splitting by `region_limit`, IO may share CFG0 if windows are scarce, and MSG TLP needs its own reserved region. MSI setup has multiple paths and must avoid 64-bit-only targets for devices lacking 64-bit MSI. `dw_pcie_wait_for_link()` treats no-device and not-active as non-timeout statuses that host init allows, while true timeout fails. Suspend PM depends on endpoint PME acknowledgments but intentionally proceeds after timeout.

Test signals: Enumeration with ECAM and non-ECAM config access, multiple MEM windows and DMA ranges, IO-space sharing fallback, MSI/MSI-X allocation/free/mask/ack across split `msiX` IRQs, systems with `msi-parent`/`msi-map`, link timeout/no-device/not-active cases, equalization preset programming for Gen3+, PME suspend/resume, root bus removal, eDMA registration, and debugfs init/deinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-plat.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-plat.c

Purpose: Provides a minimal generic Synopsys DesignWare PCIe platform driver for DT compatibles `snps,dw-pcie` and `snps,dw-pcie-ep`. It wires generic DWC host or endpoint initialization when no SoC-specific glue is needed.

Important APIs and types: `struct dw_plat_pcie` stores the DWC pointer and selected mode. `struct dw_plat_pcie_of_data` stores match mode. Main functions are `dw_plat_add_pcie_port()`, `dw_plat_pcie_ep_raise_irq()`, `dw_plat_pcie_get_features()`, and `dw_plat_pcie_probe()`. Endpoint features use `DWC_EPC_COMMON_FEATURES` with MSI and MSI-X capable.

Control flow: Probe matches RC or EP mode, allocates `dw_plat_pcie` and `dw_pcie`, stores platform driver data, then dispatches. RC mode requires `CONFIG_PCIE_DW_PLAT_HOST`, gets platform IRQ index 1, sets `MAX_MSI_IRQS`, installs empty host ops, and calls `dw_pcie_host_init()`. EP mode requires `CONFIG_PCIE_DW_PLAT_EP`, installs endpoint ops, calls `dw_pcie_ep_init()`, initializes EP registers, and notifies EPC clients.

State and persistence: The file itself has minimal state. Persistent hardware state is entirely established by the generic DWC host/EP core: resources, iATU windows, MSI, BARs, link, endpoint memory, eDMA, and debugfs.

Dependencies and integration points: Directly depends on DWC host/endpoint core, Linux platform/OF APIs, endpoint controller framework, and the IRQ numbering convention for generic host mode. It is a baseline integration point for simple DWC hardware.

Risks: The generic driver has no clocks/resets/PHY sequencing unless the common core `REQ_RES` capability is set by another path, so it is only safe for platforms that need no extra glue. Host IRQ index 1 is a binding contract. EP error handling deinitializes on register-init failure but still calls `pci_epc_init_notify()` after that block in current control flow, which should be validated against the exact return path behavior.

Test signals: Probe both compatibles under matching Kconfig, host enumeration and MSI delivery with IRQ index 1, EP BAR/MSI/MSI-X operations, failed EP register initialization behavior, endpoint start/stop, and absence of platform-specific resource needs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware.c

Purpose: Implements the shared non-mode-specific DWC PCIe support layer: resource discovery, DBI/DBI2/ATU/eDMA register access, version/type detection, capability discovery/removal, outbound/inbound iATU programming, link setup/status, eDMA discovery/removal, L1SS hiding, common link speed/width setup, LTSSM stringification, and parent-bus offset handling.

Important APIs and types: Public APIs include `dw_pcie_get_resources()`, `dw_pcie_version_detect()`, `dw_pcie_find_capability()`, `dw_pcie_find_ext_capability()`, `dw_pcie_find_rasdes_capability()`, `dw_pcie_find_ptm_capability()`, `dw_pcie_remove_capability()`, `dw_pcie_remove_ext_capability()`, `dw_pcie_read()`, `dw_pcie_write()`, `dw_pcie_read_dbi()`, `dw_pcie_write_dbi()`, `dw_pcie_write_dbi2()`, `dw_pcie_prog_outbound_atu()`, `dw_pcie_prog_inbound_atu()`, `dw_pcie_prog_ep_inbound_atu()`, `dw_pcie_disable_atu()`, `dw_pcie_wait_for_link()`, `dw_pcie_link_up()`, `dw_pcie_iatu_detect()`, `dw_pcie_edma_detect()`, `dw_pcie_edma_remove()`, `dw_pcie_hide_unsupported_l1ss()`, `dw_pcie_setup()`, and `dw_pcie_parent_bus_offset()`.

Control flow: Resource discovery maps DBI/DBI2/ATU/eDMA/ELBI resources or computes legacy offsets, optionally obtains common clocks/resets/GPIO reset for `REQ_RES`, reads max speed and lanes from DT, and enables CDM check if requested. Setup detects version/type and iATU topology, configures link speed/width/N_FTS/CDM/DLL, and programs ATU windows. iATU programming validates index, size, alignment, and region-limit boundaries, writes base/limit/target/control registers, and polls enable. eDMA detection infers legacy/unrolled mapping, channel counts, IRQ layout, allocates LLP memory, and probes the DW eDMA device. Link wait polls vendor/default link-up and categorizes no-device, connected-not-active, and timeout LTSSM states.

State and persistence: `struct dw_pcie` accumulates mapped bases, physical addresses, resource-derived parent-bus offset, clock/reset descriptors, version/type, capability flags, lane/speed settings, iATU window counts/alignment/limit, eDMA metadata, L1SS support flag, and suspend/debugfs-related state used by host/EP layers. Hardware state includes DWC DBI registers, capability linked lists, iATU windows, link-control registers, eDMA registration/LLP memory, and optional CDM checking.

Dependencies and integration points: This is the foundation for `pcie-designware-host.c`, `pcie-designware-ep.c`, debugfs, and all glue drivers. It depends on platform resources, OF properties, clock/reset/GPIO frameworks, PCI capability walkers, DW eDMA, and optional glue `dw_pcie_ops` for custom DBI access, link-up, and CPU-address fixups.

Risks: Resource fallback offsets (`dbi + 4K`, `dbi + DEFAULT_DBI_ATU_OFFSET`, `atu + DEFAULT_DBI_DMA_OFFSET`) depend on controller layout. iATU region alignment/limit detection writes probe values to ATU registers and must happen before real mappings. Parent-bus offset logic warns and compensates for broken DT ranges, but wrong fixups can misprogram all ATUs. DWC 4.90A/5.00A ECRC workaround forces TD on outbound ATU traffic. eDMA detection intentionally treats missing/invalid eDMA as non-fatal, so eDMA absence can be silent except logs.

Test signals: Unit-level build coverage for host and EP glue, boot with viewport and unrolled iATU controllers, resource layouts with explicit and fallback DBI2/ATU/eDMA, ATU alignment and boundary error paths, Gen speed/width limiting, L1SS hiding unless glue opts in, eDMA legacy/unroll/no-device cases, PTM/RAS-DES VSEC discovery, parent-bus offset warnings on translated DTs, and link wait statuses for no device, inactive device, and successful Gen x width reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware.c -->
