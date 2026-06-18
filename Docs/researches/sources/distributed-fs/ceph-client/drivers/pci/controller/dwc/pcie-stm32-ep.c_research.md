## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32-ep.c

Purpose: STM32MP25 DesignWare PCIe endpoint controller driver. It configures SYSCFG mode bits for endpoint operation, initializes endpoint controller resources, and responds to host PERST changes by tearing down or reprogramming endpoint registers.

Important APIs, types, and functions: `struct stm32_pcie` embeds `struct dw_pcie` and stores SYSCFG regmap, reset, PHY, clock, PERST GPIO, and IRQ. `stm32_pcie_probe()` resolves `"st,stm32mp25-syscfg"`, PHY, clock, reset, reset GPIO, runtime PM, and threaded PERST IRQ, then calls `stm32_add_pcie_ep()`. `stm32_add_pcie_ep()` sets `STM32MP25_PCIECR_EP`, toggles controller reset, sets `dw_pcie_ep_ops`, uses 64 KiB page alignment, calls `dw_pcie_ep_init()`, and enables PHY/clock resources. `stm32_pcie_perst_assert()` disables LTSSM, notifies EPC deinit, disables resources, and runtime-suspends. `stm32_pcie_perst_deassert()` resumes runtime PM, enables resources, reinitializes EP registers with `dw_pcie_ep_init_registers()`, notifies EPC init, and enables LTSSM.

Control flow: endpoint initialization occurs at probe, but link start only enables PERST IRQ. The PERST threaded handler reads GPIO value, dispatches assert/deassert logic, and flips IRQ trigger polarity to catch the next edge. Removal stops link, notifies EPC deinit, deinitializes EP, disables resources, and drops runtime PM.

State and persistence: state is volatile: SYSCFG type/LTSSM bits, reset line, PHY init state, clock state, runtime PM usage count, EPC state notifications, DBI endpoint registers reprogrammed after PHY reset, and IRQ trigger type. No persistent storage.

Dependencies and integration points: DesignWare endpoint core, PCI endpoint controller API, syscon regmap, runtime PM, GPIO/IRQ subsystem, PHY/clock/reset frameworks, and shared constants from `pcie-stm32.h`.

Risks: PERST is level-sensitive through GPIO but the driver rewrites IRQ type after each event; missed edges or wrong active level can leave resources enabled or disabled incorrectly. `stm32_add_pcie_ep()` enables resources immediately even though host PERST may later force reinit. Error paths must balance `pm_runtime_get_noresume()` and resource enables.

Test signals: endpoint function binding should succeed, PERST assert should call deinit notify and gate resources, PERST deassert should reinitialize DBI registers and assert link training, MSI/INTx raises should work, and remove should not leak runtime PM or leave IRQ enabled.
