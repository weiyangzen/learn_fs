# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_calendar.c

## Purpose
This file calculates DSM taxi calendars for LAN969x. It maps each taxi to LAN969x port positions, groups active devices by required speed, verifies taxi bandwidth, chooses a calendar length and slot spacing, and fills `sparx5_calendar_data->schedule`.

## Important APIs, Types, And Functions
The exported function is `lan969x_dsm_calendar_calc()`. Internal helpers are `lan969x_dsm_cal_idx_get()`, `lan969x_dsm_cal_get_dev()`, and `lan969x_dsm_cal_get_speed()`. `struct lan969x_dsm_cal_dev_speed` accumulates devices, required slot count, and slot gap per speed class.

## Control Flow
The function computes taxi bandwidth from core clock period, copies the static LAN969x taxi-port map, translates active port bandwidths through common Sparx5 calendar helpers, and sums required bandwidth. Empty taxis get an empty schedule. Non-empty taxis search for the smallest calendar length that can fit all slots at the computed bandwidth per slot. It clears the 64-slot schedule, then places each speed class by repeatedly finding the next empty slot and advancing by the class gap.

## State And Persistence
Only caller-provided `sparx5_calendar_data` is mutated. Hardware is not programmed here; common `sparx5_calendar.c` validates and writes the schedule later. No persistent state exists.

## Dependencies And Integration Points
The file depends on `sparx5_clk_period()`, `sparx5_get_port_cal_speed()`, `sparx5_cal_speed_to_value()`, `SPX5_DSM_CAL_LEN`, and the common calendar update path through `sparx5_ops.dsm_calendar_calc`.

## Risks And Edge Cases
Taxi port entries use sentinel value `99`; callers must keep `n_ports_all` below that sentinel meaning. The slot-placement algorithm can return `-ENOENT` if the gap pattern cannot find an empty slot. It checks required bandwidth against taxi bandwidth but relies on the later common checker for spacing quality. Calendar length greater than `SPX5_DSM_CAL_LEN` is rejected.

## Test Signals
Test empty taxis, single-speed taxis, mixed 10G/5G/2.5G/1G taxis, overcommitted bandwidth, all supported core clocks, and final hardware update through common DSM calendar init.
