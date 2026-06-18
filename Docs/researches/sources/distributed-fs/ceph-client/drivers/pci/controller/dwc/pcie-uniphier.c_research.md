## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-uniphier.c

Purpose: Socionext UniPhier DesignWare PCIe root-complex driver. It sets RC mode, handles PHY/pipe readiness, provides link callbacks, and implements a legacy INTx irqdomain behind the UniPhier glue interrupt controller.

Important APIs, types, and functions: `struct uniphier_pcie` embeds `dw_pcie` and stores glue base, clock, reset, optional PHY, and INTx domain. `uniphier_pcie_host_enable()` enables clock/reset, calls `uniphier_pcie_init_rc()`, initializes PHY, and waits for `PCL_PCLK_ALIVE`. `uniphier_pcie_link_up()` checks both RDLH and XMLH status bits. `uniphier_pcie_config_intx_irq()` parses the `legacy-interrupt-controller` child, maps the parent IRQ, creates a 4-line irqdomain, and installs `uniphier_pcie_irq_handler()` as chained handler. Mask/unmask callbacks manipulate INTx mask bits under `pp->lock`.

Control flow: probe maps `"link"`, gets resources, enables host hardware, sets host ops, and calls `dw_pcie_host_init()`. Host init configures the legacy INTx domain and enables non-INTx and INTx event sources. Link start/stop toggles the app LTSSM bit.

State and persistence: volatile state includes glue mode/PERST/aux-power/LTSSM bits, pipe clock readiness, event masks/statuses, INTx irqdomain, clock/reset/PHY state, and DWC host state. No persistent storage exists.

Dependencies and integration points: DesignWare host core, OF IRQ parsing, irqdomain/chained IRQ APIs, optional PHY, clock/reset framework, and platform resource naming.

Risks: Chained interrupt handling clears debug/event statuses before INTx dispatch; changes must preserve ordering. Missing `legacy-interrupt-controller` prevents host init. No remove path removes the irqdomain or chained handler because the driver is built in with platform lifetime assumptions.

Test signals: UniPhier boot should show pipe clock alive, link-up with both status bits, INTx routing for INTA-D, MSI through DWC if enabled by core, host enumeration, and failure handling for missing child interrupt controller or PHY errors.
