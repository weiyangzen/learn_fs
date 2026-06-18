# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1s.c

## Purpose
Implements Microchip 10BASE-T1S support for LAN867x B1/C1/C2/D0 and LAN865x Rev.B internal PHYs. It applies revision-specific application-note fixups, configures PLCA/collision behavior, handles fixed 10M half-duplex status for older parts, and provides direct C45 MMD access for OA TC6 MAC-PHYs.

## Important APIs, Types, And Functions
Fixup tables encode AN1699 and AN1760 register programming. `lan865x_revb_indirect_read()` and `lan865x_generate_cfg_offsets()` derive per-chip calibration offsets. `lan865x_setup_cfgparam()` and `lan865x_setup_sqi_cfgparam()` compute offset-adjusted values. `lan867x_check_reset_complete()` gates initialization. `lan86xx_plca_set_cfg()` wraps generic PLCA and collision detector policy.

## Control Flow
Each revision has its own `config_init`. LAN865x Rev.B reads offsets, writes base fixups, injects calculated parameters, configures SQI parameter registers, then writes SQI fixups. LAN867x Rev.C reuses the first LAN865x fixups plus SQI setup. Rev.B1 applies masked RMW fixups. Rev.D0 writes its own values and sets link-status selection for default CSMA/CD mode. PLCA set config updates Rev.D0 link-status selection, delegates to generic PLCA, then disables collision detection in PLCA mode and enables it in CSMA/CD.

## State And Persistence
No private state is allocated. All state is in PHY registers: fixups, offset-derived parameters, PLCA configuration, collision detector enable, and Rev.D0 link-status selection.

## Dependencies And Integration Points
Depends on phylib C45 PLCA helpers, OA TC6 direct C45 bus operations, ethtool OATC14 cable/SQI helpers for Rev.D0, and MDIO driver registration.

## Risks
Fixup tables are revision-sensitive. Offset-derived functions should be checked against datasheet field preservation rules. Always reporting link up for older parts can mask wiring faults. Rev.D0 relies on generic status plus link-status selection rather than the fixed `read_status` path.

## Test Signals
Probe every supported PHY ID, verify reset-complete handling, compare MDIO traces to AN1699/AN1760, toggle PLCA and collision detection, test OA TC6 direct C45 access, and run Rev.D0 cable/SQI ethtool paths.
