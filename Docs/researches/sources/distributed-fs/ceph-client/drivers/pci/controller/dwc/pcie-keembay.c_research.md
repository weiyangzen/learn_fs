# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-keembay.c

Purpose: This is the Intel Keem Bay DesignWare PCIe driver supporting both root-complex and endpoint modes. It configures APB registers, master/aux clocks, internal PLL, endpoint reset GPIO in host mode, custom MSI interrupt acknowledgement in host mode, endpoint interrupt capabilities, and DWC link callbacks.

Important APIs, types, and functions: `struct keembay_pcie` embeds `struct dw_pcie` and stores APB base, mode, clocks, and reset GPIO. Link callbacks are `keembay_pcie_link_up()`, `keembay_pcie_start_link()`, and `keembay_pcie_stop_link()`. Host helpers include `keembay_pcie_probe_clocks()`, `keembay_pcie_pll_init()`, `keembay_pcie_msi_irq_handler()`, `keembay_pcie_setup_msi_irq()`, and `keembay_pcie_add_pcie_port()`. Endpoint callbacks are `keembay_pcie_ep_init()`, `keembay_pcie_ep_raise_irq()`, and `keembay_pcie_get_features()`.

Control flow: Probe maps APB registers and branches by OF-selected mode. RC mode sets host ops, marks `msi_irq[0]` invalid so the custom chained IRQ path is used, installs the `pcie` IRQ handler, obtains reset GPIO, enables master and 24 MHz aux clocks, bypasses PHY SRAM, sets RC device type, initializes and polls the low-jitter PLL, deasserts controller reset, releases endpoint reset, calls `dw_pcie_host_init()`, then enables MSI controller interrupts if MSI is configured. EP mode installs endpoint ops, calls `dw_pcie_ep_init()` and `dw_pcie_ep_init_registers()`, and notifies EPC. Link start for RC disables LTSSM, waits for PHY MPLLA lock, then enables LTSSM; EP start is a no-op.

State and persistence behavior: State is in driver memory, APB registers, and DWC endpoint/host structures. Clocks use devm action cleanup. Host reset GPIO controls downstream PERST. Endpoint initialization enables eDMA interrupts in APB. There is no persistent storage or explicit remove path.

Dependencies and integration points: Uses DWC host/endpoint core, Linux clocks, GPIO, chained IRQ handling, platform resources, and Keem Bay APB/PLL registers. MSI dispatch integrates by calling `dw_handle_msi_irq()` after filtering APB interrupt status and clearing Keem Bay-specific status bits.

Risks: The host MSI path relies on an extra APB status clear after `dw_handle_msi_irq()`. PLL and PHY lock polling are mandatory before LTSSM. Endpoint mode does not initialize clocks/PLL in this file, so platform/firmware assumptions matter. INTx is explicitly unsupported in endpoint mode and must return `-EINVAL`. BAR feature restrictions expose only 64-bit BAR0/2/4 with 16 KiB alignment.

Test signals: Test RC and EP compatibles, master/aux clock enable and aux rate setting, PLL lock timeout, host link-up bits, MSI delivery/clear, endpoint MSI/MSI-X raising and INTx rejection, endpoint BAR alignment/features, EP register initialization, and absent endpoint/no-link handling.
