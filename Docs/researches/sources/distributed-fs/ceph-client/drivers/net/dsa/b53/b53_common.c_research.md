# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_common.c

Purpose: transport-independent Broadcom B53 DSA switch core. It handles chip detection/init, DSA callbacks, VLAN/bridge/FDB/MDB/mirror/EEE/MTU/ageing behavior, phylink, stats/devlink, Broadcom tag setup, and exported allocation/registration helpers.

Important APIs, types, and functions: `b53_switch_alloc()`, `b53_switch_detect()`, and `b53_switch_register()` are transport-facing entry points. `b53_switch_ops` and `b53_phylink_mac_ops` expose DSA/phylink callbacks. VLAN functions maintain `dev->vlans[]` and PVID state; ARL helpers and `b53_arl_ops_*` implement FDB/MDB operations; `b53_switch_chips[]` stores per-chip capabilities.

Control flow: transports allocate with bus ops, register, detect or copy chip ID, initialize chip metadata and caches, then DSA `.setup` resets hardware, configures default VLANs, disables forwarding while applying config, enables CPU ports, disables user ports until opened, and registers devlink resources. Later DSA events replay cached state into VLAN tables, PVLAN masks, ARL entries, phylink override registers, and bridge flags.

State and persistence behavior: `struct b53_device` stores chip metadata, tag protocol, enabled ports, VLAN/filtering flags, VLAN and per-port caches, mutexes, and SerDes lane state. This is runtime-only but used to replay hardware state after reset/reconfiguration. MIB counters are hardware state read under `stats_mutex`.

Dependencies and integration points: DSA, phylink, switchdev bridge/VLAN/FDB/MDB objects, PHYLIB, devlink via DSA helpers, ethtool stats, Broadcom tag protocols, B53 registers, and transport-provided `b53_io_ops`.

Risks: chip-family register differences are dense; VLAN filtering transitions must replay cached state correctly; CPU tag protocol fallback affects VLAN assumptions; ARL full/missing cases need careful handling; RGMII delay quirks are hardware-specific; mirror delete bit handling deserves regression coverage.

Test signals: chip probe matrix, bridge join/leave/STP/flood/learning/isolation tests, VLAN/PVID/filtering toggles, FDB/MDB add/delete/dump across chip families, phylink fixed/PHY/SerDes modes, stats/EEE/MTU/ageing/mirroring/devlink, and reset replay tests.
