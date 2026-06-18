# sources/distributed-fs/ceph-client/include/linux/phy/tegra/xusb.h

## Purpose
NVIDIA Tegra XUSB pad controller and PHY coordination API for USB3/HSIC/UTMI power, context, wake, and port mapping.

## Important APIs, Types, and Functions
Declares `tegra_xusb_padctl_get()`, `tegra_xusb_padctl_put()`, USB3 context save, HSIC idle, LFPS detect control, VBUS override, UTMI pad power and reset helpers, USB3 companion and port-number lookup, sleepwalk enable/disable, wake enable/disable, and remote wake detection.

## Control Flow
USB/XUSB controller code obtains a pad controller, configures port-specific PHY behavior, saves context before low-power transitions, enables sleepwalk/wake for suspend, checks remote wake, and releases the pad controller.

## State and Persistence
Persistent state is owned by the Tegra pad controller implementation and PHY hardware: port context, idle flags, LFPS detection, VBUS override, sleepwalk/wake configuration, and saved USB3 state.

## Dependencies and Integration Points
Integrates Tegra XUSB host/device controller code, generic `struct phy`, device model, and USB speed enumeration.

## Risks
Suspend/resume ordering and port-number mismatches can break wake or restore wrong lane context. Missing reference release can leak padctl references.

## Test Signals
Tegra USB2/USB3 enumeration, suspend/resume remote wake, HSIC idle tests, LFPS detection tests, and XUSB controller probe/remove tests.
