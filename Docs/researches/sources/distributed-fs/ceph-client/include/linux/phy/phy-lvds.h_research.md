# sources/distributed-fs/ceph-client/include/linux/phy/phy-lvds.h

## Purpose
LVDS configuration payload for generic PHY providers.

## Important APIs, Types, and Functions
Defines `struct phy_configure_opts_lvds` with bits per lane per differential clock cycle, differential clock rate, lane count, and `is_slave` for dual-link master/slave operation.

## Control Flow
No functions. Consumers pass the structure through `phy_configure()` and providers validate/program LVDS hardware.

## State and Persistence
Configuration is transient input. Applied lane/clock/master-slave state persists in the PHY until changed.

## Dependencies and Integration Points
Included by `linux/phy/phy.h`; integrates display pipelines and LVDS PHY providers.

## Risks
Incorrect clock or lane count causes panel timing failures. Dual-link slave state must match the paired master PHY and display bridge configuration.

## Test Signals
Panel bring-up tests, single/dual-link LVDS mode validation, and display timing regression tests.
