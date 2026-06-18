<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-bitbang.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio-bitbang.h

## Purpose
This header defines the bit-banged MDIO bus abstraction for controllers that implement MDIO by toggling GPIO-like MDC/MDIO signals.

## Important APIs, types, and functions
`struct mdiobb_ops` provides `set_mdc`, `set_mdio_dir`, `set_mdio_data`, and `get_mdio_data` callbacks plus module owner. `struct mdiobb_ctrl` carries ops and optional Clause 22 opcode overrides. APIs include Clause 22 and Clause 45 read/write helpers, `alloc_mdio_bitbang`, and `free_mdio_bitbang`.

## Control flow
Controller drivers implement pin callbacks, allocate an unregistered `mii_bus` with `alloc_mdio_bitbang()`, then register it with phylib. MDIO transactions call the bitbang helpers, which sequence MDC edges, MDIO direction changes, opcodes, addresses, turnaround, and data bits.

## State and persistence
State is runtime-only in the controller callbacks, opcode overrides, and allocated `mii_bus`. PHY register state persists in hardware.

## Dependencies and integration points
It depends on phylib `struct mii_bus` and `struct phy_device` support. It integrates GPIO, platform, and legacy MAC drivers with generic MDIO/PHY infrastructure.

## Risks and test signals
Risks include timing violations, wrong turnaround direction, missing module pinning, Clause 45 address phase errors, and nonstandard Clause 22 opcodes. Test PHY ID reads, register writes, bus registration/unregistration, GPIO direction sequencing, and C22/C45 transactions under clock-rate variation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio-bitbang.h -->
