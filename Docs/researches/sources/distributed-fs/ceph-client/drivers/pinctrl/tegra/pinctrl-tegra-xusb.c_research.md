<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra-xusb.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra-xusb.c

## Purpose
Implements the legacy Tegra124 XUSB pad controller as both a pinctrl/pinmux/pinconf provider for XUSB lanes and a generic PHY provider for PCIe and SATA lanes. It controls lane muxing, IDDQ state, ELPG clamp sequencing, and PLL power-on/off sequences.

## Important APIs, Types, And Functions
Core types are `struct tegra_xusb_padctl`, `struct tegra_xusb_padctl_soc`, `struct tegra_xusb_padctl_function`, and `struct tegra_xusb_padctl_lane`. Pinctrl callbacks parse `nvidia,function`, `nvidia,lanes`, and `nvidia,iddq`; pinmux uses `tegra_xusb_padctl_pinmux_set`; pinconf uses `tegra_xusb_padctl_pinconf_group_get/set`. PHY operations are `pcie_phy_ops` and `sata_phy_ops`, backed by `tegra_xusb_padctl_enable/disable`, `pcie_phy_power_on/off`, and `sata_phy_power_on/off`. Exported legacy entry points are `tegra_xusb_padctl_legacy_probe` and `tegra_xusb_padctl_legacy_remove`.

## Control Flow
Probe allocates state, deasserts reset, maps registers, registers a pinctrl device, creates PCIe and SATA PHYs, and registers an OF PHY provider. DT pinctrl subnodes become mux and config maps per lane. Pinmux writes function indices into lane bitfields. PHY init increments a shared enable count and unclamps ELPG registers; exit decrements and reclamps. PHY power-on sequences program PLL/control bits and poll lock-detect with a 50 ms timeout.

## State And Persistence Behavior
Runtime state includes MMIO base, reset control, mutex, selected SoC lane tables, pinctrl descriptor/device, PHY provider, two PHY handles, and a reference-count-like `enable` counter. Hardware state persists in padctl lane mux/IDDQ fields, ELPG clamp bits, and PCIe/SATA PLL registers until reset or power-management code changes them.

## Dependencies And Integration Points
Depends on pinctrl core utilities, generic PHY, reset controller, device tree, Tegra XUSB binding constants, MMIO accessors, and legacy Tegra124 padctl matching. Consumers obtain PHYs by phandle index and pin states through the pinctrl framework.

## Risks And Edge Cases
Lane `iddq == 0` means unsupported, so lane metadata must not use bit zero for a real IDDQ field in this encoding. The SATA power-off path writes `value |= ~BIT` masks, which is unusually broad and should be treated carefully in behavior changes. PLL polling has fixed timeout/sleep intervals. The shared `enable` counter is mutex-protected but must remain balanced across PHY users.

## Test Signals
Tegra124 XUSB padctl probe/remove, reset assert/deassert, pinctrl DT lane muxing, IDDQ set/get, PCIe and SATA PHY init/exit/power-on/power-off, PLL lock timeout handling, multiple concurrent PHY users, and OF PHY xlate bounds checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra-xusb.c -->
