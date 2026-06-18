# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_vlan.c

## Purpose
`sparx5_vlan.c` implements Sparx5 VLAN membership, PVID/native VLAN handling, egress tagging, PGID mask programming, and bridge forwarding/learning masks. It translates per-port VLAN state in `struct sparx5_port` and switch-wide bitmaps into ANA/REW hardware registers.

## Important APIs, Types, and Functions
- `sparx5_vlan_init()` enables VLAN handling and initializes VLAN-to-FID mapping.
- `sparx5_vlan_port_setup()` programs initial port VLAN control for a port.
- `sparx5_vlan_vid_add()` adds a port to a VID, optionally setting PVID and native untagged VLAN.
- `sparx5_vlan_vid_del()` removes a port from a VID while preserving VID 0 behavior needed for untagged receive.
- `sparx5_vlan_port_apply()` writes ingress VLAN awareness/filtering and egress tag/VID configuration.
- `sparx5_pgid_update_mask()`, `sparx5_pgid_clear()`, and `sparx5_pgid_read_mask()` manipulate 32-bit-sliced PGID port masks.
- `sparx5_update_fwd()` updates source forwarding masks and learning masks for bridged ports.

## Control Flow
Global initialization enables VLAN mode and maps every VLAN ID to the same FID. Per-port setup writes the current PVID with VLAN awareness initially disabled. VLAN add sets native VLAN state if requested, sets the port bit in the switch VLAN mask, writes that mask to hardware, updates PVID if requested, then reapplies port VLAN registers. VLAN delete ignores VID 0, clears membership, resets PVID/native VID if they matched the deleted VID, then reapplies.

Forwarding updates build register-sized masks from bridge bitmaps. For each port in the hardware port range, bridged ports get a source mask containing all other bridged ports, while unbridged ports get zero. Learning is enabled only for ports present in both forwarding and learning masks.

## State and Persistence Behavior
Runtime state is kept in `sparx5->vlan_mask[vid]`, `sparx5->bridge_fwd_mask`, `sparx5->bridge_lrn_mask`, and per-port `pvid`, `vid`, and `vlan_aware` fields. Hardware state persists in ANA VLAN mask/config/filter, PGID, source mask, learning mask, and REW tag/port VLAN registers until changed or reset. There is no disk persistence.

## Dependencies and Integration Points
The file depends on Sparx5 register macros and register access helpers, Linux bitmap helpers, VLAN constants, netdevice error logging, and SoC feature checks via `is_sparx5()`. It integrates with bridge/VLAN netdevice operations elsewhere in the Sparx5 driver, with forwarding database behavior through source masks, and with egress rewriting through REW tag registers.

## Risks and Edge Cases
- Only one native untagged VLAN is allowed per port; attempts to add a second return `-EBUSY`.
- VID 0 deletion is deliberately ignored so untagged traffic keeps working after 8021q module unload.
- Register masks are split across up to three 32-bit words; non-Sparx5 variants only program the first word.
- `sparx5_vlan_vid_add()` updates `port->vid` before hardware mask programming, so an unexpected error would leave partial software state.
- VLAN-aware ports with no PVID drop untagged and priority-tagged frames, which is correct but can surprise tests that expect fallback PVID 0 forwarding.

## Test Signals
- VLAN add/delete tests should cover PVID, untagged native VLAN, duplicate native VLAN rejection, VID 0 delete, and VLAN-aware filtering.
- Bridge tests should verify forwarding masks exclude the ingress port and learning enables only where both masks are set.
- Hardware/register tests should validate 32/64/65-port mask splitting and behavior on non-Sparx5 variants.
- Packet tests should check ingress untagged/tagged handling and egress tag modes for native and tagged VLANs.
