
# sources/distributed-fs/ceph-client/include/linux/platform_data/emif_plat.h

## Purpose
This header defines TI EMIF platform data for DDR memory controller setup. It captures low-power policy, hardware capabilities, IP/PHY revisions, DDR device geometry, timing tables, and board-specific custom configuration.

## Important APIs And Types
Constants define EMIF low-power modes, hardware capability bits, EMIF IP revisions (`EMIF_4D`, `EMIF_4D5`), PHY types, and custom config masks. `struct ddr_device_info` describes memory type, density, bus width, CS1 use, calibration resistor topology, and manufacturer. `struct emif_custom_configs` describes requested low-power mode, performance/power timeout choices, frequency threshold, and temperature polling interval. `struct emif_platform_data` ties together capabilities, DDR info, LPDDR2 timings/min cycles, custom configs, IP revision, and PHY type.

## Control Flow, State, And Persistence
The EMIF driver consumes this at probe and during frequency/power management to program timing and low-power registers. Custom config masks determine which policies override driver defaults. State persists in hardware registers across runtime until context loss or reprogramming; this header stores only the platform description.

## Dependencies And Integration Points
It references LPDDR2 timing/min-tck structures, OMAP/TI platform code, memory-controller drivers, PM/OPP frequency management, and temperature alert polling.

## Risks And Test Signals
Incorrect DDR geometry or timing data can cause memory instability. Low-power thresholds can trade performance for power or trigger resume failures. Test signals include memory stress across supported frequencies, suspend/resume and context-loss restore, temperature polling behavior, low-power-mode register programming, and validation with both default and custom timing data.
