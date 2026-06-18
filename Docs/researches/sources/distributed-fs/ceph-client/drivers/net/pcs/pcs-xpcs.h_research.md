# sources/distributed-fs/ceph-client/drivers/net/pcs/pcs-xpcs.h

Purpose: Provides private DesignWare XPCS register definitions, data structures, and helper prototypes shared by the XPCS core, platform frontend, and vendor PMA files.

Important APIs, types, and functions: The header defines vendor-register access marker `DW_VENDOR`, VR PCS/MII register offsets and bit fields, USXGMII speed encodings, Clause 73 advertisement bits, Clause 37 mode bits, EEE controls, and polarity bits. `DW_XPCS_INFO_DECLARE()` creates static `dw_xpcs_info` match data. `enum dw_xpcs_clock` names core/pad clocks. `struct dw_xpcs` stores IDs, descriptor, MDIO device, clocks, phylink PCS, current interface, reset flag, and EEE multiplier. It declares XPCS MDIO accessors and vendor PMA callbacks.

Control flow: Core code uses these constants to program autoneg, link-up, reset, EEE, and vendor registers. Platform code uses `DW_XPCS_INFO_DECLARE()` for OF match data. Vendor files call `xpcs_read/write/modify()` against PMA/PCS registers.

State and persistence behavior: The only mutable software state defined is `struct dw_xpcs`, which persists for the XPCS object lifetime. Register macros describe hardware state persisted in the PCS/PMA.

Dependencies and integration points: It includes kernel bit helpers and the public `linux/pcs/pcs-xpcs.h` UAPI/internal interface. It is private to `drivers/net/pcs` implementation files.

Risks and edge cases: Register offsets combine standard and vendor MMD spaces; using the wrong MMD or forgetting `DW_VENDOR` writes the wrong hardware location. Bit-field encodings for SGMII/USXGMII speeds are reused across mode paths. Private struct layout is shared across module objects, so all XPCS object files must be built together.

Test signals: Compile all XPCS objects together, verify register writes against hardware documentation, test each speed encoding, and run sparse/build checks for prototype drift between core and vendor helpers.
