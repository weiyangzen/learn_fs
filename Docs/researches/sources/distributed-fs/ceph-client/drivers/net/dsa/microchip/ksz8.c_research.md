# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.c

Purpose: KSZ8-family switch implementation for the Microchip KSZ common DSA core, covering KSZ8463, KSZ8863/8873, KSZ8895/8864, and KSZ8794/8795/8765 style devices.

Important APIs/types/functions: exports setup, switch init/exit, reset, port address helpers, PHY read/write, MIB reads, FDB/MDB add/delete/dump, VLAN filtering/add/delete, mirroring, CPU-port setup, phylink link-up, MTU change, PME access, and queue split. Internal helpers handle indirect reads/writes, table access, dynamic/static MAC tables, VLAN encode/decode/cache, PHY BMCR/control emulation, MIB packet counters, and chip-family MTU logic.

Control flow: setup configures DSA MTU/tagging flags, link auto-aging, half-duplex backoff, VLAN/mirror/tag defaults, VLAN cache, PME disablement, and EEE errata. Port setup enables storm limit, queue split, priority behavior, membership maps, and default WoL disablement. CPU-port setup enables tail tagging, configures CPU interface/RMII clock, disables user ports by STP, detects fiber mode, and disables unsupported KSZ8463 PTP handling.

State and persistence: state spans `struct ksz_device`, per-port state, VLAN cache, MIB counters, mirror bitmaps, ALU mutex, and hardware tables. Static MAC and VLAN entries persist in hardware; dynamic entries are read by indexed iteration. Some dropped counters use software delta tracking for wrapping hardware counters.

Dependencies and integration: KSZ common helpers/chip data, DSA, switchdev, phylink, bridge/VLAN flags, Micrel PHY constants, regmap accessors, and chip-specific masks/shifts/register arrays. Linked into `ksz_switch.o`.

Risks and test signals: per-chip register differences, PHY emulation inversions, unsupported VLAN filtering on KSZ88x3/KSZ8463, single remove-tag behavior, static table capacity, FID equals VID simplification, MIB overflow handling, and asymmetric pause limitations. Test PHY emulation, VLAN/PVIDs, FDB/MDB capacity and deletion, dynamic dump, MIB overflow, mirror configuration, tail tagging, STP transitions, MTU changes, and KSZ87xx EEE erratum writes.
