# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-meson.c

Purpose: Implements Amlogic Meson AXG/G12A root-complex glue for DWC PCIe. It manages resets, clocks, PHY power, reset GPIO, local config registers, link training, link status, payload/read-request sizing, and a config-space class-code workaround.

Important APIs and types: `struct meson_pcie` embeds `struct dw_pcie` and stores config-register base, clocks, reset controls, reset GPIO, and PHY. Main functions are `meson_pcie_get_resets()`, `meson_pcie_get_mems()`, `meson_pcie_power_on()`, `meson_pcie_reset()`, `meson_pcie_probe_clocks()`, `meson_pcie_start_link()`, `meson_pcie_rd_own_conf()`, `meson_pcie_link_up()`, `meson_pcie_host_init()`, and `meson_pcie_probe()`.

Control flow: Probe creates the embedded DWC object, acquires `pcie` PHY and reset GPIO, deasserts port/APB resets, maps legacy `elbi`/DBI and `cfg` resources, powers the PHY, performs PHY and controller reset sequencing, enables required clocks, installs host and DWC ops, and calls `dw_pcie_host_init()`. Host init replaces root-bus PCI ops to fabricate bridge class code and writes max payload/read request sizes. Link start enables LTSSM in the Meson config block and toggles endpoint PERST through the reset GPIO.

State and persistence: Hardware state includes reset controls, PHY power, clock enables and rates, Meson config `APP_LTSSM_ENABLE`, device-control payload/read-request fields, and the GPIO reset line. Driver state is devm-managed and no explicit remove path powers down after successful probe.

Dependencies and integration points: Integrates with DWC host core, Linux clock/reset/PHY/GPIO APIs, and DT resources named `elbi` and `cfg`. The root config accessor uses `dw_pcie_own_conf_map_bus()` but overrides reads for `PCI_CLASS_REVISION`.

Risks: The class-code workaround is essential because software cannot program `PCI_CLASS_DEVICE`; removing it can break PCI core recognition. The historical `elbi`-as-DBI DT compatibility path is fragile but needed. Clock/reset/PHY order is timing-sensitive. Lack of explicit remove/suspend support means cleanup relies on devm and boot-time usage assumptions.

Test signals: Boot AXG/G12A DTs, verify PHY/reset/clock acquisition, bridge class code seen by PCI core, Gen/link status through Meson status bits, payload/read request values of 256 bytes, enumeration behind the root port, failed-probe PHY power-off, and no regressions with old `elbi` DT naming.
