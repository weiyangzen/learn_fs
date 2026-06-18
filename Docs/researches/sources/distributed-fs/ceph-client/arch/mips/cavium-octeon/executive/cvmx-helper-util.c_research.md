# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-util.c

## Purpose
Provides shared utilities for mode names, Random Early Drop, common GMX/PKO port geometry, and IPD port/interface mapping.

## Important APIs, Types, And Functions
APIs are `cvmx_helper_interface_mode_to_string()`, `cvmx_helper_setup_red()`, `__cvmx_helper_setup_gmx()`, `cvmx_helper_get_ipd_port()`, `cvmx_helper_get_interface_num()`, and `cvmx_helper_get_interface_index_num()`.

## Control Flow
RED setup disables page-count backpressure, programs all eight RED queues, disables per-port RED-end dropping, and enables RED globally. GMX setup writes TX/RX port counts, PKO GMX port mode, and TX thresholds by model and port count. Mapping functions translate interface/index to IPD ports and back.

## State, Persistence, And Dependencies
State is in IPD, GMX, and PKO CSRs. It depends on helper interface mode detection and Octeon model checks.

## Integration Points
All mode-specific helpers use GMX setup and port mapping. RED setup is exported for packet buffer pressure policy.

## Risks
RED probability divides by `pass_thresh - drop_thresh`; invalid thresholds are dangerous. Mapping covers only known IPD ranges and logs illegal values.

## Test Signals
Check mapping round trips, GMX/PKO register fields for each port count, RED behavior under FPA pressure, and illegal-port diagnostics.
