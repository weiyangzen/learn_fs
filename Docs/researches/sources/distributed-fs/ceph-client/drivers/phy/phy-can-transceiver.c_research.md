# sources/distributed-fs/ceph-client/drivers/phy/phy-can-transceiver.c

Purpose: This generic PHY driver controls external CAN transceivers through optional GPIOs and an optional mux state. It lets CAN controller drivers power transceivers on and off uniformly while carrying a `max-bitrate` PHY attribute from device tree.

Important APIs/types/functions: `struct can_transceiver_data` describes per-compatible flags for standby, enable, dual-channel, and silent GPIO support. `struct can_transceiver_phy` stores one generic PHY plus optional GPIO descriptors and a backpointer. `struct can_transceiver_priv` stores the optional mux state, channel count, and a flexible array of per-channel PHYs. PHY ops are `can_transceiver_phy_power_on()` and `can_transceiver_phy_power_off()`. `can_transceiver_phy_xlate()` selects channel 0 for single-channel parts or an indexed PHY for dual-channel parts.

Control flow: Probe matches the OF compatible to driver data, chooses one or two channels, allocates a flexible private structure, optionally gets a mux state, reads `max-bitrate`, then loops over channels creating one PHY per channel. Depending on flags, it obtains indexed `standby`, `enable`, and `silent` GPIOs with safe default output values. Power-on selects the mux, deasserts silent and standby, and asserts enable. Power-off asserts silent and standby, deasserts enable, and deselects the mux.

State and persistence: Runtime state is held in GPIO output levels, mux selection, `phy->attrs.max_link_rate`, and the private per-channel descriptors. No software power boolean is cached. Device-tree configuration persists compatible-specific capabilities and optional `max-bitrate`.

Dependencies and integration points: The driver depends on OF matching, platform devices, generic PHY, GPIO descriptors, optional mux consumer API, and CAN controller consumers that request the PHY. Supported compatibles include TI TCAN1042/1043, NXP TJA1048/TJA1051/TJA1057/TJR1443.

Risks: `of_match_node()` is assumed to return a match; a platform device without OF match data would dereference null. Optional GPIO descriptors can be absent even when flags say the line is supported, so boards must ensure that omission is electrically safe. Shared mux state is stored at device level, so dual-channel use needs careful consumer sequencing if channels can be powered independently.

Test signals: Validate single- and dual-channel phandle translation, GPIO default states at probe, power-on/off line levels, mux select/deselect calls, `max_link_rate` propagation, and CAN bus operation at and above declared bitrate limits. Error tests should cover invalid channel index, invalid zero `max-bitrate`, missing optional GPIOs, and mux selection failure.
