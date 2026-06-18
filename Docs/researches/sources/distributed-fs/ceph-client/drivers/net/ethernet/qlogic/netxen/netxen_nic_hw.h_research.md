# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_hw.h

## Purpose
This header provides NetXen hardware-facing constants, register bit helpers, PHY register numbers, promiscuous-mode constants, and CRB mapping table types used by `netxen_nic_hw.c` and the wider `netxen_nic` driver. It is a local hardware description layer for NIU, PHY, and CRB addressing details.

## Important APIs, Types, and Macros
- `NETXEN_MEMADDR_MAX` and `NETXEN_PCI_MAPSIZE_BYTES` describe hardware memory and PCI mapping size expectations.
- `netxen_nic_set_link_parameters()` is declared for callers that need to refresh adapter link fields.
- `netxen_gb_*` macros set, clear, and query GbE MAC config bits.
- `netxen_gb_mii_mgmt_*` helpers build and inspect MII management commands.
- `NETXEN_NIU_GB_MII_MGMT_ADDR_*` constants name PHY management registers.
- `netxen_get_phy_speed()`, `netxen_get_phy_link()`, and `netxen_get_phy_duplex()` decode PHY status register 17.
- `crb_128M_2M_sub_block_map_t` and `crb_128M_2M_block_map_t` describe CRB offset translations.

## Control Flow
The header has no executable control flow beyond macro expansion. Its macros are used in runtime paths where callers read a 32-bit register value, mutate or decode selected bits, and write the result back. The CRB mapping types are populated in `netxen_nic_hw.c` and consumed by the CRB address translation path.

## State and Persistence
The header itself owns no state. It defines bit layouts that mutate hardware state when used with register writes. Because many helpers modify their argument expression with `|=` or `&=`, callers must pass mutable lvalues, not expressions with side effects.

## Dependencies and Integration Points
The header forward-declares `struct netxen_adapter` and is included by `netxen_nic_hw.c`, `netxen_nic_init.c`, and `netxen_nic_main.c`. Its PHY status helpers are directly used by link-parameter refresh logic, and its CRB map types support P3 direct-versus-indirect register access.

## Risks and Edge Cases
- Mutating macros are not type-safe and can surprise callers if passed complex expressions.
- Bit definitions are hardware-contract sensitive.
- Some comments duplicate headings in a way that can confuse maintenance.
- P2 promiscuous constants differ from P3 firmware vport miss modes; callers must use selected adapter operations.

## Test Signals
Build coverage is the primary direct signal. Runtime signals include correct link speed/duplex reporting, flow-control and reset behavior on P2 hardware, correct all-multicast/promiscuous handling, and absence of sparse/compiler warnings around macro use.
