## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.c

Purpose: STM32MP25 DesignWare PCIe root-complex driver. It sets RC mode in SYSCFG, controls PERST and optional WAKE GPIOs under a root-port child node, integrates suspend/resume, and registers the DWC host.

Important APIs, types, and functions: `struct stm32_pcie` stores DWC state, SYSCFG regmap, reset, PHY, clock, PERST GPIO, and optional WAKE GPIO. `stm32_pcie_probe()` gets syscfg, clock, reset, parses root-port PHY/GPIOs, enables port resources, toggles controller reset, enables the core clock and runtime PM, then calls `dw_pcie_host_init()`. `stm32_add_pcie_port()` sets PHY mode/init, programs `STM32MP25_PCIECR_RC`, deasserts PERST with required delays, and registers a dedicated wake IRQ for WAKE GPIO. `stm32_pcie_start_link()` and `stm32_pcie_stop_link()` toggle `STM32MP25_PCIECR_LTSSM_EN`. `stm32_pcie_suspend_noirq()` and `stm32_pcie_resume_noirq()` handle DWC noirq state, PERST, clock, PHY, and pinctrl state.

Control flow: probe parses the first available child as root port, initializes PHY before reset/clock/host registration, then DWC host setup starts link training through callbacks. Suspend disables DWC, asserts PERST, disables clock, optionally exits PHY if not a wakeup path, and selects sleep pinctrl. Resume selects init pinctrl first, reinitializes PHY when needed, enables clock, deasserts PERST, resumes DWC, and restores default pinctrl.

State and persistence: state is hardware-only: syscfg RC/LTSSM bits, reset, PERST line, wake IRQ registration, clock/PHY state, runtime PM active state, DWC host resources, and pinctrl state. No disk persistence.

Dependencies and integration points: DesignWare host core, STM32 syscfg regmap, GPIO descriptors via root-port fwnode, wake IRQ framework, PM/pinctrl, PHY, clock/reset, and constants in `pcie-stm32.h`.

Risks: `of_get_next_available_child()` is not checked before using its fwnode for GPIOs, so malformed DT without a child could be fragile. Suspend/resume sequencing is sensitive because DBI access depends on REFCLK/CLKREQ pin state. Optional PERST means some systems rely entirely on LTSSM and PHY behavior.

Test signals: RC boot enumeration, link training after PERST delays, wake GPIO falling-edge wake, suspend/resume with and without wake path, noirq DWC errors, pinctrl state transitions, and clean removal with host deinit and wake IRQ cleanup.
