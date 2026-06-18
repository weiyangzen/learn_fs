# sources/distributed-fs/ceph-client/drivers/net/phy/Makefile

## Purpose
Maps PHY-layer Kconfig symbols to built objects. It builds the phylib core, phylink, MDIO helpers, SFP support, timestamping support, vendor PHY drivers, and subdirectories.

## Important APIs, Types, and Functions
The main aggregates are `libphy-y`, which contains core phylib objects such as `phy.o`, `phy-c45.o`, `phy-core.o`, `phy_device.o`, `linkmode.o`, `phy_link_topology.o`, `phy_caps.o`, `mdio_bus_provider.o`, `phy_port.o`, and `mdio_device.o`, and symbol-gated `obj-$(CONFIG_...)` lines for each driver. For this subset, relevant mappings include `adin.o`, `adin1100.o`, `air_en8811h.o`, `amd.o`, `aquantia/`, `as21xxx.o`, `ax88796b.o` or `ax88796b_rust.o`, `bcm-cygnus.o`, `bcm-phy-lib.o`, and `bcm-phy-ptp.o`.

## Control Flow and State
There is no runtime control flow. Build-time flow is conditional: `stubs.o` is forced into `obj-y` whenever `CONFIG_PHYLIB` is set so built-in consumers can link; SFP bus support is collected through `sfp-obj-*`; `CONFIG_AX88796B_RUST_PHY` switches the AX88796B implementation from C to Rust while keeping the same `CONFIG_AX88796B_PHY` driver selection.

## Dependencies and Integration Points
This file is consumed by Kbuild and depends on the Kconfig symbols defined in this directory and vendor subdirectories. It ties the top-level PHY subsystem to subdirectories such as `aquantia/`, `mediatek/`, `mscc/`, `qcom/`, and `realtek/`, and to optional modules for PTP, HWMON-backed drivers, Rust drivers, and MACSEC-enabled objects.

## Risks and Test Signals
Risks are stale Kconfig/object names, duplicate or missing objects, unexpected built-in/module linkage, and the Rust/C AX88796B switch diverging from user expectation. Test signals include building each relevant symbol as `y` and `m`, checking module names with `modinfo`, and ensuring that `CONFIG_AX88796B_RUST_PHY=y` produces `ax88796b_rust.o` instead of the C object.
