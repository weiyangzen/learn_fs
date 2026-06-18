# sources/distributed-fs/ceph-client/drivers/phy/amlogic/phy-meson-g12a-usb3-pcie.c

Purpose: Drives the G12A combo PHY that can operate as either USB3 or PCIe. It programs top-level combo registers and exposes a secondary CR bus as a regmap for detailed USB3 analog workaround writes.

Important APIs and types: `struct phy_g12a_usb3_pcie_priv` holds top-level and CR regmaps, reference clock, reset array, PHY, and selected mode. `phy_g12a_usb3_pcie_xlate()` selects `PHY_TYPE_USB3` or `PHY_TYPE_PCIE` from the phandle argument. CR bus read/write helpers implement the PHY's acknowledge-based address/data handshake.

Control flow: probe maps the top registers, creates both MMIO and custom CR regmaps, gets `ref_clk` enabled and reset array, creates a PHY, and registers a custom xlate provider. USB3 init resets the PHY, switches the combo to USB3, applies CR-bus workarounds for TX alt bus, RX equalization, TX amplitude/preemphasis, MPLL loop control, and top-level VBOOST/LOS fields. PCIe power-on/off changes the PCIe power-state field, and PCIe reset toggles the reset array with 500 us delays. USB3 exit resets the block.

State and persistence: The selected `mode` is stored globally in the provider instance at xlate time, so one hardware block is treated as a single-mode resource. Hardware state is not saved across PM.

Dependencies and integration: It depends on generic PHY, reset, enabled reference clock, regmap custom bus callbacks, and `dt-bindings/phy/phy.h`. Device-tree consumers must pass the desired PHY type.

Risks and test signals: Because `mode` is overwritten by each xlate call, simultaneous USB3 and PCIe consumers would race logically. CR-bus polling timeouts are critical failure signals. Test both phandle modes, invalid xlate args, USB3 SuperSpeed enumeration after workaround programming, PCIe reset/power states, and bootloader-preconfigured PCIe noted by the TODO.
