# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx.h

## Purpose
This header defines the private data model used by the MxL862xx DSA driver. It centralizes hardware size constants, firmware portmap helpers, per-port VLAN Filter and Extended VLAN bookkeeping, software statistics accumulators, and the top-level `mxl862xx_priv` structure.

## Important APIs, Types, and Functions
- `MXL862XX_MAX_PORTS`, `MXL862XX_MAX_BRIDGES`, `MXL862XX_MAX_BRIDGE_PORTS`, `MXL862XX_TOTAL_EVLAN_ENTRIES`, and `MXL862XX_TOTAL_VF_ENTRIES` define driver sizing assumptions.
- `mxl862xx_fw_portmap_set_bit()`, `mxl862xx_fw_portmap_clear_bit()`, and `mxl862xx_fw_portmap_is_empty()` operate on firmware-format 128-bit portmaps represented as little-endian 16-bit words.
- `struct mxl862xx_vf_vid` tracks a software VID entry in a per-port VLAN Filter block, including hardware index and egress untagged state.
- `struct mxl862xx_vf_block` tracks a hardware VLAN Filter allocation, active scan count, block size, and VID list.
- `struct mxl862xx_evlan_block` tracks Extended VLAN block allocation, enable state, block ID, total size, and active rule count.
- `struct mxl862xx_port_stats` stores 64-bit accumulated link stats plus previous raw hardware snapshots.
- `struct mxl862xx_port` is the per-port runtime object.
- `struct mxl862xx_priv` is the driver-wide object associated with `dsa_switch::priv`.

## Control Flow
The header itself has no control flow beyond inline portmap helpers. Its structures are populated by `mxl862xx_probe()`, `mxl862xx_setup()`, `mxl862xx_port_setup()`, VLAN callbacks, bridge callbacks, stats work, and remove/shutdown paths in `mxl862xx.c`.

## State and Persistence Behavior
All state is runtime-only and rebuilt on probe. `struct mxl862xx_port` records bridge/FID, learning, flood-block, PVID, VLAN filtering, VF/EVLAN allocations, deferred work, and stats per port. `struct mxl862xx_priv` records the MDIO device, DSA switch, CRC/work flags, shared drop meter ID, per-port array, DSA-bridge-to-firmware-bridge mapping, table block sizing, and delayed stats work. No state is persisted outside memory; firmware state is expected to be reset and reallocated during setup.

## Dependencies and Integration Points
The header includes Linux MDIO and workqueue types plus `net/dsa.h`. Its types are tightly coupled to firmware command structures in other MxL862xx headers, particularly because firmware portmaps use little-endian words and VLAN/EVLAN block IDs come from firmware allocation commands.

## Risks and Edge Cases
- Portmap helpers do not bounds-check `port`; callers must keep indexes below `MXL862XX_MAX_BRIDGE_PORTS`.
- Little-endian bit operations require careful use of `cpu_to_le16()` and cannot be safely replaced with native bitmaps.
- `mxl862xx_fw_portmap_is_empty()` checks raw `__le16` words for zero, which is valid for zero but would not be suitable for arbitrary numeric interpretation.
- `setup_done` is used as a concurrency guard for deferred work; any new worker touching per-port state must respect it.
- Stats locking only protects accumulators, not the MDIO reads that produce snapshots.

## Test Signals
Header-level validation is mostly compile-time and behavior driven from `mxl862xx.c`. KUnit-style tests could exercise firmware portmap bit set/clear/empty behavior on little-endian arrays, while integration tests should verify VF/EVLAN allocation state transitions, work cancellation, and stat accumulator locking under polling plus `get_stats64()`.
