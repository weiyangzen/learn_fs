# sources/distributed-fs/ceph-client/include/linux/ieee80211-mesh.h

## Purpose
Defines IEEE 802.11s mesh header layouts, mesh configuration and channel-switch elements, HWMP/RANN fields, mesh action codes, and mesh path/sync/root mode identifiers.

## Important APIs, Types, And Functions
Key packed structures are `ieee80211s_hdr`, `ieee80211_mesh_chansw_params_ie`, `ieee80211_meshconf_ie`, and `ieee80211_rann_ie`. Constants cover mesh ID length, address-extension flags, power-save flag, PREQ flags, channel-switch flags, mesh capability flags, RANN gate flag, action codes, sync methods, path protocols, path metrics, and root modes.

## Control Flow
Mesh data paths parse `ieee80211s_hdr` to determine TTL, sequence, address extension, and optional extended addresses. Management paths parse mesh configuration, channel switch, PREQ/RANN, and action-code fields to drive peering, HWMP path selection, root announcements, and channel changes.

## State And Persistence
No state is stored here. Mesh peering, path tables, sequence numbers, root mode, and beacon/configuration state live in mac80211 mesh code and driver state.

## Dependencies And Integration Points
Depends on Linux types and Ethernet constants. Integrates with mac80211 mesh networking, HWMP routing, mesh power save, channel switch announcements, beacon/probe parsing, and mesh action-frame handling.

## Risks
Packed/aligned mesh headers require careful length checks before accessing optional addresses. TTL/sequence and path metric interpretation affects loop prevention and routing. Capability mismatches can break peering or forwarding.

## Test Signals
Mesh peering and forwarding tests, HWMP PREQ/PREP/RANN behavior, address-extension frame parsing, mesh channel-switch handling, root mode transitions, power-save flags, and malformed mesh element fuzzing.
