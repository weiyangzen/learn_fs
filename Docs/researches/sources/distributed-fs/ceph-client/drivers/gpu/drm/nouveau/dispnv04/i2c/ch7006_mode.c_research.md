<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_mode.c

## Purpose
This file provides CH7006 TV norm tables, supported mode tables, mode lookup, and hardware register calculations for levels, subcarrier frequency, PLL programming, power state, position, contrast, and flicker filtering.

## Important APIs, Types, and Functions
It exports `ch7006_tv_norm_names`, `ch7006_tv_norms`, `ch7006_modes`, `ch7006_lookup_mode`, `ch7006_setup_levels`, `ch7006_setup_subcarrier`, `ch7006_setup_pll`, `ch7006_setup_power_state`, `ch7006_setup_properties`, `ch7006_write`, `ch7006_read`, `ch7006_state_load`, and `ch7006_state_save`.

## Control Flow
Mode tables describe PAL-like and NTSC-like timings with valid norm and scale masks. Lookup matches norm plus exact display geometry, totals, and clock. Setup functions compute DAC gain and black level from norm and brightness, split a calculated subcarrier increment across eight registers, brute-force CH7006 PLL `N/M` values against requested pixel clock, derive power bits from DPMS and subconnector choice, and compute horizontal/vertical positioning from overscan-like margins and aspect ratio. State load/save write/read registers in a defined order, with FFILTER bit reordering after save.

## State and Persistence Behavior
The file manipulates the caller-owned `struct ch7006_state` register array and `struct ch7006_priv` current mode/property state. No persistent kernel object is allocated here; hardware persistence is the CH7006 register set written over I2C.

## Dependencies and Integration Points
It depends on fixed-point helpers/macros in `ch7006_priv.h`, DRM mode definitions, I2C master send/receive, and the driver callbacks in `ch7006_drv.c`.

## Risks
The register calculations use fixed-point constants and table-derived coefficients; small arithmetic mistakes can produce invalid TV colorburst or positioning. PLL search is exhaustive but simple and assumes CH7006 frequency formula. I2C read failures return zero, which can be mistaken for real state. Unsupported norms/modes cannot be synthesized.

## Test Signals
Signals include exact mode lookup for every table entry, PAL/NTSC color output, PLL values close to requested clocks, brightness/contrast/flicker/margin changes on live output, save/restore fidelity, I2C error injection, and visual validation of subcarrier and color levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_mode.c -->
