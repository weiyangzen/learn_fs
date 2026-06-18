# sources/distributed-fs/ceph-client/drivers/soundwire/generic_bandwidth_allocation.c

## Purpose
Implements the generic SoundWire bandwidth allocation algorithm used by master drivers. It chooses bus clock/frame parameters, optionally assigns nonzero lanes, groups streams by sample rate and lane, and computes master/slave transport and port parameters for audio and BPT streams.

## Important APIs, Types, and Functions
Exported functions are `sdw_compute_params()` and `sdw_compute_slave_ports()`. Local types are `struct sdw_group_params` for per-rate/lane bandwidth and hwidth, and `struct sdw_group` for dynamically collected rate/lane groups. Important helpers include `sdw_compute_dp0_port_params()`, `sdw_compute_master_ports()`, `sdw_compute_group_params()`, `sdw_get_group_count()`, `sdw_compute_port_params()`, `sdw_select_row_col()`, `is_clock_scaling_supported()`, `is_lane_connected_to_all_peripherals()`, `get_manager_lane()`, and `sdw_compute_bus_params()`.

## Control Flow
`sdw_compute_params()` first calls `sdw_compute_bus_params()` to find current data rate and frame shape. The bus computation selects clock gear/frequency lists from master properties, limits dynamic scaling if any attached slave lacks support, checks whether lane0 has enough bandwidth at a given rate, and otherwise tries to move the latest runtime to a nonzero manager lane connected to all participating peripherals. It then derives default column from data rate, frame rate, and row, and validates row/column through `sdw_select_row_col()`. For BPT streams, DP0 master/slave port parameters use most of the frame except column 0. For audio streams, `sdw_get_group_count()` builds unique sample-rate/lane groups, `sdw_compute_group_params()` computes payload bandwidth and horizontal width per group, and `_sdw_compute_port_params()` lays groups from the end of the frame toward column 1 while calling `sdw_compute_master_ports()` and `sdw_compute_slave_ports()`.

## State and Persistence Behavior
The function mutates `bus->params.curr_dr_freq`, `row`, `col`, and per-lane used bandwidth during bus computation. It also mutates each `sdw_port_runtime` transport and port parameter structure and may set master and peripheral lane fields. Temporary grouping arrays are allocated and freed per computation. No external persistence is performed, but computed state remains in stream runtimes until recomputed or streams are removed.

## Dependencies and Integration Points
Depends on SoundWire stream runtime lists, master/slave properties, frame row/column tables, bit operations, and the inline fillers in `bus.h`. AMD, Intel, and other master drivers can install this function as `bus->compute_params`, or call `sdw_compute_slave_ports()` from custom algorithms. Later stream code consumes the computed parameters through master port ops and slave register programming.

## Risks
The algorithm assumes valid stream rates, bit depths, channel masks, default rows/columns, and frame-rate properties; divide-by-zero or invalid frame shapes are guarded only in some paths. Lane accounting uses `bus->lane_used_bandwidth` and may be stale if not reset by callers before recomputation. Multilane selection only checks the first slave runtime to find a candidate manager lane, then verifies connectivity for all peripherals. Group allocation grows arrays one element at a time and must keep rates/lanes arrays consistent on allocation failure. Column 0 reservation applies only lane0; nonzero-lane capacity checks differ.

## Test Signals
Tests should cover single-rate and mixed-rate streams, playback/capture mirror mode, BPT DP0 streams, insufficient bandwidth failures, default row/column validation, clock gear and explicit clock frequency selection, slaves with and without dynamic scaling support, multilane routing with connected and disconnected lane maps, lane bandwidth reset across repeated computations, paused/disabled streams included in bandwidth, and computed hstart/hstop/offset/sample interval values applied by master and slave port ops.
