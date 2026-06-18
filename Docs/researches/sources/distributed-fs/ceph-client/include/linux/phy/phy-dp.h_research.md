# sources/distributed-fs/ceph-client/include/linux/phy/phy-dp.h

## Purpose
DisplayPort/eDP configuration payload for the generic PHY framework.

## Important APIs, Types, and Functions
Defines `PHY_SUBMODE_DP`, `PHY_SUBMODE_EDP`, and `struct phy_configure_opts_dp` containing main-link rate, lane count, per-lane voltage swing, per-lane pre-emphasis, spread-spectrum clocking, and bit flags indicating which parts of the configuration should be applied.

## Control Flow
No functions. Consumers fill the structure and call generic `phy_configure()` or provider-specific validation/configuration ops. Providers inspect the `set_rate`, `set_lanes`, and `set_voltages` flags to limit reconfiguration.

## State and Persistence
The structure is transient input, but applied settings persist in DP PHY hardware until reconfigured or powered down.

## Dependencies and Integration Points
Included by `linux/phy/phy.h` and used by display bridge, controller, and PHY drivers for DisplayPort and embedded DisplayPort link training.

## Risks
Invalid lane counts, unsupported link rates, or out-of-range voltage/pre-emphasis values can break link training. Per-lane arrays assume up to four lanes.

## Test Signals
DP/eDP link-training tests across lane counts and rates, PHY validate failures for invalid inputs, and display mode-set regression tests.
