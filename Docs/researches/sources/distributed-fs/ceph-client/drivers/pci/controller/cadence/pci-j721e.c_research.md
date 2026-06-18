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
