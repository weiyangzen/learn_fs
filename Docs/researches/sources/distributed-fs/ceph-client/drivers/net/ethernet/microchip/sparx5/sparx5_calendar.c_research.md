# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_calendar.c

## Purpose
This file configures Sparx5-family traffic calendars. It programs the QSYS auto calendar from port bandwidths and computes, validates, and writes DSM taxi calendars used by the disassembler. The DSM calculation can be family-specific through `sparx5_ops.dsm_calendar_calc`.

## Important APIs, Types, And Functions
Exports include `sparx5_calendar_init()`, `sparx5_cal_speed_to_value()`, `sparx5_get_port_cal_speed()`, and the default `sparx5_dsm_calendar_calc()`. Important internals are `sparx5_config_auto_calendar()`, `sparx5_config_dsm_calendar()`, `sparx5_dsm_calendar_check()`, and `sparx5_dsm_calendar_update()`.

## Control Flow
`sparx5_calendar_init()` first configures QSYS auto calendar. It translates each front/internal port bandwidth into compact calendar codes, checks target SKU bandwidth and core-clock bandwidth, halts the calendar on Sparx5, writes `QSYS_CAL_AUTO`, grants idle use to virtual devices, enables auto mode, and checks hardware error state. DSM configuration allocates a scratch `sparx5_calendar_data`, calls the family calendar calculator for each taxi, validates spacing, programs DSM calendar entries, and switches banks on non-Sparx5 families.

## State And Persistence
State is hardware calendar registers plus temporary calculation buffers. It derives from current port configuration, target chip ID, core clock, and constants in `sparx5->data`. There is no disk persistence.

## Dependencies And Integration Points
The file depends on Sparx5 register accessors, port configuration state, family constants, internal-port mapping, and LAN969x or Sparx5 DSM calculator ops. It is called during driver/port initialization when port bandwidths are known.

## Risks And Edge Cases
Bandwidth guards reject configurations exceeding target or core capacity. The default DSM calculator has several integer scaling and spacing assumptions, including overhead loss compensation and special handling for slow core clocks. The calendar checker iterates modulo slot counts and must avoid zero-slot cases. `sparx5_dsm_calendar_update()` expects readback length to equal `cal_len - 1`.

## Test Signals
Test all core clocks, each supported target SKU, port bandwidth mixes, overcommit rejection, empty taxis, LAN969x calculator dispatch, DSM readback length, QSYS auto error bits, and traffic forwarding after link speed changes.
