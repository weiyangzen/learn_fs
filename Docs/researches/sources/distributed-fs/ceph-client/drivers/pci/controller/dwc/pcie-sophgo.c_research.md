# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-sophgo.c

Purpose: This is the Sophgo SG2044 DesignWare PCIe host-controller driver. It maps Sophgo app registers, enables clocks, creates a legacy INTx IRQ domain with chained IRQ dispatch, enables MSI signaling, disables ASPM L0s/L1 capability advertisement, and initializes the DWC root complex.

Important APIs, types, and functions: `struct sophgo_pcie` embeds `struct dw_pcie` and stores app register base, clocks, and INTx IRQ domain. App accessors are `sophgo_pcie_readl_app()` and `sophgo_pcie_writel_app()`. IRQ flow is implemented by `sophgo_pcie_intx_handler()`, `sophgo_intx_irq_mask()`, `sophgo_intx_irq_unmask()`, `sophgo_pcie_intx_map()`, and `sophgo_pcie_init_irq_domain()`. Host setup helpers are `sophgo_pcie_msi_enable()`, `sophgo_pcie_disable_l0s_l1()`, `sophgo_pcie_host_init()`, `sophgo_pcie_clk_init()`, and `sophgo_pcie_configure_rc()`.

Control flow: Probe allocates state, stores drvdata, maps the `app` region, enables all clocks using `devm_clk_bulk_get_all_enabled()`, then configures RC mode by setting DWC host ops and calling `dw_pcie_host_init()`. Host init obtains the child `interrupt-controller` fwnode, gets its IRQ, creates a four-entry INTx domain, installs a chained handler, clears L0s/L1 ASPM bits from the PCIe Link Capabilities register under DBI read-only write enable, and sets the MSI enable bit in the Sophgo interrupt-enable register. INTx mask/unmask update per-line bits under the DWC root-port raw spinlock.

State and persistence behavior: Runtime state is app-register interrupt enable/mask state, IRQ domain mappings, clock enablement, and DWC host state. There is no durable state and no explicit remove callback; devm resources and built-in driver lifetime are relied upon.

Dependencies and integration points: Uses DWC host core, Linux clock bulk APIs, IRQ domains/chained IRQs, fwnode child lookup, platform resources, and PCI DBI capability editing. It relies on DWC MSI handling while Sophgo app registers gate the MSI interrupt signal.

Risks: INTx status bits are read from a field shifted into bits 8:5; wrong field handling would dispatch wrong hwirqs. Mask/unmask share one app register with MSI enable and must preserve unrelated bits under lock. ASPM L0s/L1 are forcibly hidden, likely due to hardware issues; re-enabling can destabilize links. Missing child interrupt controller or IRQ causes host init failure.

Test signals: Test SG2044 probe, clock enablement, INTx child fwnode parsing, chained INTx delivery and mask/unmask, MSI interrupt delivery, ASPM capability clearing visible in config space, absent interrupt-controller failure, and concurrent INTx/MSI enable register updates.
