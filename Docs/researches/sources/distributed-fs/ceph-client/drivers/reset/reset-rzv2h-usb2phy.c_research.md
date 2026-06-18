# sources/distributed-fs/ceph-client/drivers/reset/reset-rzv2h-usb2phy.c

Purpose: Renesas RZ/V2H(P) USB2 PHY reset controller for a single reset line, using register sequences and also registering an auxiliary mux device.

Important APIs/types/functions: `rzv2h_usb2phy_reset_of_data` packages init/assert/deassert sequences and status bits. Reset ops call `regmap_multi_reg_write()` for assert/deassert and read the configured status register. `rzv2h_usb2phy_reset_mux_register()` allocates an IDA ID and creates a devm auxiliary device named `vbenctl`.

Control flow: probe maps MMIO to a sleeping regmap, obtains a shared deasserted parent reset, enables runtime PM, installs a PM put action, writes the init sequence, registers one reset provider with zero cells, and creates the auxiliary mux.

State and persistence: hardware registers store reset state; software keeps match-data pointers, regmap, runtime PM reference, and IDA auxiliary IDs. Device-managed actions free IDs and drop PM references.

Dependencies and integration: depends on platform probing, reset controls, runtime PM, regmap sequences, auxiliary bus, and `renesas,r9a09g057-usb2phy-reset`.

Risks and test signals: `status()` ignores `regmap_read()` errors. Sequence ordering and delay values are hardware-sensitive. Test init-sequence programming, assert/deassert status, auxiliary-device creation failure cleanup, PM reference cleanup, and parent reset acquisition.
