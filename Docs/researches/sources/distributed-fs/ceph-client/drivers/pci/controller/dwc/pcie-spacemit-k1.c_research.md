## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spacemit-k1.c

Purpose: SpacemiT K1 DesignWare PCIe root-complex glue driver. It owns the platform-specific PMU/syscon controls, link-status registers, PHY selection from the root-port child node, regulator enablement, and the DesignWare host registration path.

Important APIs, types, and functions: `struct k1_pcie` embeds `struct dw_pcie` and stores the external PHY, link MMIO base, PMU regmap, and PMU offset. `k1_pcie_probe()` resolves `spacemit,apmu`, maps the `"link"` resource, enables `vpcie3v3`, configures runtime PM without callbacks, parses the child PHY, and calls `dw_pcie_host_init()`. `k1_pcie_init()` toggles soft reset, enables app clocks/resets from `pci->app_clks` and `pci->app_rsts`, writes vendor/device IDs into DBI with RO override, asserts PERST for `PCIE_T_PVPERL_MS`, sets RC/device power bits, initializes the PHY, deasserts PERST, and disables ASPM L1 as a workaround. `k1_pcie_deinit()` reverses PERST, PHY, reset, and clock state. `k1_pcie_start_link()`, `k1_pcie_stop_link()`, and `k1_pcie_link_up()` implement the `dw_pcie_ops`.

Control flow: probe seeds DesignWare state, holds the PHY in reset, enables supply/PM, then host init invokes the host callbacks. Link start releases `APP_HOLD_PHY_RST`, enables LTSSM, MSI, and the top-level PHY AHB interrupt. Link-up requires both `SMLH_LINK_UP` and `RDLH_LINK_UP`. Removal delegates to `dw_pcie_host_deinit()`, which calls deinit.

State and persistence: state is volatile hardware state only: PMU reset bits, PERST, LTSSM, MSI interrupt enable, DBI IDs, app clocks/resets, runtime PM active state, and PHY init state. There is no persistent storage.

Dependencies and integration points: Linux platform/OF, syscon regmap, regulator framework, clock/reset bulk resources held by DesignWare core, PHY framework, runtime PM, and `pcie-designware.h`. DT must expose `spacemit,k1-pcie`, `spacemit,apmu`, `"link"` resource, a root-port child with PHY, and `vpcie3v3`.

Risks: PMU phandle arguments and offsets are critical; a wrong offset manipulates unrelated PMU bits. The ASPM L1 disable mutates capability advertising and may hide power-saving features. Interrupt enabling is not paired with a local IRQ handler, so correctness relies on DWC MSI plumbing. Error unwinds after PHY init and resource enable are intentionally narrow and should be checked when extending probe.

Test signals: boot with `spacemit,k1-pcie`, observe host bridge enumeration, link-up with both PHY status bits set, MSI delivery, PERST timing, regulator/clock/reset cleanup on remove or probe failure, and NVMe stability with the ASPM workaround.
