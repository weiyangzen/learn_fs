# sources/distributed-fs/ceph-client/drivers/thermal/ti-soc-thermal/ti-bandgap.h

## Purpose
`ti-bandgap.h` defines the shared data model, feature bits, and public APIs for the TI bandgap thermal driver and per-SoC data files.

## Important APIs, Types, and Functions
Core types are `temp_sensor_registers`, `temp_sensor_data`, `temp_sensor_regval`, `ti_bandgap`, `ti_temp_sensor`, and `ti_bandgap_data`. Feature macros include TSHUT, TSHUT_CONFIG, TALERT, MODE_CONFIG, COUNTER, POWER_SWITCH, CLK_CTRL, FREEZE_BIT, COUNTER_DELAY, HISTORY_BUFFER, ERRATA_814, UNRELIABLE, and CONT_MODE_ONLY. Public prototypes expose update intervals, temperature, private sensor data, and trend.

## Control Flow
The header has no executable flow. `ti-bandgap.c` interprets feature bits and descriptors to decide which registers to touch and which runtime paths to enable.

## State and Persistence Behavior
It defines runtime state shape: `ti_bandgap` owns MMIO, clocks, lock, IRQs, saved register values, and suspend state; `temp_sensor_regval` persists per-sensor context across PM transitions.

## Dependencies and Integration Points
It depends on spinlocks, CPU PM, device/PM runtime types, and conditional Kconfig externs for per-family data symbols. Per-SoC data files and `ti-thermal-common.c` include it.

## Risks and Edge Cases
Feature-bit accuracy is critical because it gates register access. Flexible-array `sensors[]` requires static initializers to keep `sensor_count` consistent. Conditional externs become `NULL` when configs are disabled.

## Test Signals
Build all family configurations, static checks for descriptor initialization, probe tests validating feature-driven paths, and PM save/restore tests for `temp_sensor_regval`.
