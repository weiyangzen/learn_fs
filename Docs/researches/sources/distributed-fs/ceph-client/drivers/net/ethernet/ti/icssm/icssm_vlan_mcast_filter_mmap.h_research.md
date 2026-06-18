# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_vlan_mcast_filter_mmap.h

## Purpose
This header defines firmware memory-map constants for ICSSM VLAN and multicast filtering. The main EMAC driver and switchdev MDB handlers use these offsets and values to program multicast hash bins and filter control bytes.

## Important APIs, types, and functions
- Multicast control values enable/disable filtering and allow/disallow host receive for a hash bin.
- Size macros define the multicast table, hash mask, control byte, override status, and drop counter widths.
- Offset macros define multicast mask, control, override status, drop counter, and table base in PRU DRAM.
- LRE multicast offsets define an alternate control/mask/table region.
- VLAN offsets define a 512-byte 4096-bit VLAN table, control bitmap, drop counter, and LRE switch VLAN filter locations.
- VLAN control bit macros describe enable, untagged, priority-tagged, and service-VLAN flow behavior.
- VLAN ID range and add/remove command constants define firmware command values.

## Control flow
The header has no functions. `icssm_emac_ndo_set_rx_mode()` writes the multicast control byte, resets the table, writes the hash mask, and toggles bins based on netdev and bridge multicast addresses. `icssm_switchdev.c` updates bins for host MDB add/delete events.

## State and persistence behavior
The constants address volatile PRU DRAM/SRAM regions. Filter state is reinitialized during RX mode changes and does not survive driver shutdown or firmware restart.

## Dependencies and integration points
The header is consumed by ICSSM driver code and must match firmware layout. It has no Linux include dependencies beyond what includers provide.

## Risks and edge cases
- The closing comment names a different guard than the actual guard; harmless but confusing.
- A simple 256-bin multicast hash can collide, causing over-allow or careful disallow behavior.
- VLAN constants are defined but not substantially exercised by the researched files, so dead or future ABI drift is possible.

## Test signals
Test multicast receive filtering with no multicast addresses, specific multicast joins, allmulti, promiscuous mode, bridge MDB add/delete, hash collisions, and firmware drop counter changes. VLAN filtering tests should verify table bit layout if implementing VLAN controls against these macros.
