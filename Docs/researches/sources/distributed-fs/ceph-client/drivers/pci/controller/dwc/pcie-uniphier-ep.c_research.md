## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier-ep.c

Purpose: Socionext UniPhier DesignWare PCIe endpoint glue. It supports Pro5 and NX1 SoC variants, initializes link glue registers, clocks/resets/PHY, and provides endpoint IRQ raise and feature reporting.

Important APIs, types, and functions: `struct uniphier_pcie_ep_priv` stores glue MMIO base, embedded DWC state, clocks/resets, optional GIO clock/reset, PHY, and SoC data. `struct uniphier_pcie_ep_soc_data` supplies variant flags, init/wait hooks, and EPC features. `uniphier_pcie_pro5_init_ep()` and `uniphier_pcie_nx1_init_ep()` program EP mode, clock request/aux power/PERST behavior, and LTSSM off state. `uniphier_pcie_ep_enable()` enables clocks, deasserts resets, runs variant init, resets/initializes PHY, and waits for NX1 pipe clock if needed. `uniphier_pcie_ep_raise_irq()` dispatches INTx and MSI, with INTx pulsed in glue registers and MSI programmed through vendor MSI registers.

Control flow: probe obtains match data, maps `"link"`, acquires variant-dependent resources, enables the endpoint block, assigns DWC EP ops, calls `dw_pcie_ep_init()` and `dw_pcie_ep_init_registers()`, then notifies EPC init. DWC start/stop link simply toggles glue LTSSM enable.

State and persistence: volatile glue register state includes mode, PERST emulation, app clock request, LTSSM enable, MSI/INTx pulse registers, reset lines, clocks, PHY init state, and DWC endpoint registers. There is no persistent state and no explicit remove path.

Dependencies and integration points: DesignWare endpoint core, PCI endpoint controller features, OF match data, clock/reset/PHY frameworks, bitfield helpers, and UniPhier glue register layout. Compatible strings distinguish Pro5 and NX1.

Risks: Error unwind in `uniphier_pcie_ep_enable()` deasserts/asserts resources in a compact path; variant resources must be present only when `has_gio` is true. `uniphier_pcie_ep_raise_irq()` returns 0 after logging an unknown type instead of `-EINVAL`, which can hide caller bugs. MSI vector encoding subtracts one, so interrupt numbers must be 1-based.

Test signals: EP controller registration for both compatibles, BAR feature layout and alignment, pipe-clock wait on NX1, LTSSM start/stop, INTx pulse width, MSI vector delivery, and correct cleanup when clock/reset/PHY acquisition or initialization fails.
