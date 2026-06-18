<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ethtool.c

## Purpose
`spectrum_ethtool.c` implements Spectrum netdev ethtool operations and link-mode conversion. It reports driver/firmware identity, link extended state, pause settings, statistics, module EEPROM and power controls, timestamp capabilities, standards-based MAC/PHY/RMON stats, module reset, and generation-specific PTYS speed/link-mode mapping for Spectrum-1 and Spectrum-2-or-newer devices.

## Important APIs, Types, and Functions
The exported objects are `mlxsw_sp_port_ethtool_ops`, `mlxsw_sp1_port_type_speed_ops`, and `mlxsw_sp2_port_type_speed_ops`. Key functions include pause get/set, link ksettings get/set, stats string/count/data callbacks, module EEPROM/page accessors, `mlxsw_sp_get_ts_info()`, MAC/PHY/control/RMON stats helpers, `mlxsw_sp_reset()`, and module power-mode get/set. Link-mode tables are `mlxsw_sp1_port_link_mode[]` and `mlxsw_sp2_port_link_mode[]`.

## Control Flow
EtHTool callbacks are dispatched from the netdev operation table. Pause set rejects autonegotiated pause and PFC coexistence, recomputes port headroom for link-level PAUSE, writes PFCC, updates software pause bits, and rolls headroom back on failure. Stats collection builds string arrays from several PPCNT counter groups, per-priority counters, per-TC counters, PTP ops, and transceiver overheat counters, then queries PPCNT groups to fill values. Link ksettings query reads PTYS, converts supported/admin/oper protocol masks through generation-specific ops, and sets port connector type. Link ksettings set converts requested autoneg advertisement or forced speed/lanes back to PTYS masks, intersects with capabilities, writes PTYS, records autoneg state, and toggles admin status if the netdev is running.

## State and Persistence Behavior
Software state updated here includes `mlxsw_sp_port->link.rx_pause`, `tx_pause`, `autoneg`, and module overheat baseline-derived statistics. Hardware state is accessed through PTYS, PFCC, PDDR, PPCNT, MLCR, module EEPROM/power environment helpers, and module reset commands. Link-mode operation tables are static and selected by device generation.

## Dependencies and Integration Points
The file depends on Linux ethtool APIs, Spectrum register helpers, `core_env` module-management helpers, PTP ops, buffer headroom functions, DCB PFC state, netdev carrier/admin status, and generation-specific Spectrum core setup that chooses the correct `port_type_speed_ops`.

## Risks and Edge Cases
Pause and PFC are mutually exclusive across this file and `spectrum_dcb.c`. Link-mode conversion must respect port lane width; Spectrum-2 forced speed selection differs when userspace specifies lane count versus speed only. `mlxsw_sp2_from_ptys_link_mode()` uses a representative ethtool bit from each mask list, so table ordering matters. Many stats silently remain zero on register query errors. Extended link state returns `-ENODATA` when link is up, status opcode is zero, or the firmware opcode is unmapped.

## Test Signals
Signals include `ethtool -i`, `ethtool -a/-A`, `ethtool -S`, `ethtool --show-eee` absence expectations, `ethtool -k` unaffected operation, `ethtool <dev>` link mode reports for Spectrum-1 and Spectrum-2+, forced speed/lane changes, module EEPROM and power-mode commands, RMON/MAC/PHY stats, LED identify, link-down extended-state mapping, and PTP stats count consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ethtool.c -->
