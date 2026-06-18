# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.h

## Purpose

`igc_phy.h` declares the copper PHY helper interface for the igc driver. It exposes PHY reset, ID, link, power, autoneg/link setup, GPY register access, and firmware-version helpers to the rest of the driver.

## Important APIs, Types, and Functions

The header declares `igc_check_reset_block`, `igc_phy_hw_reset`, `igc_get_phy_id`, `igc_phy_has_link`, `igc_check_downshift`, `igc_setup_copper_link`, `igc_power_up_phy_copper`, `igc_power_down_phy_copper`, `igc_write_phy_reg_gpy`, `igc_read_phy_reg_gpy`, and `igc_read_phy_fw_version`. These functions operate on `struct igc_hw` except for scalar polling/register arguments. The header includes `igc_mac.h` for shared hardware definitions.

## Control Flow

There is no executable control flow. Include guards prevent multiple inclusion, and declarations allow MAC/base/link code to call these helpers or assign them into operation tables.

## State and Persistence Behavior

The header owns no state. The declared functions can mutate PHY registers and `struct igc_hw` PHY fields through the implementation in `igc_phy.c`.

## Dependencies and Integration Points

The header is consumed by `igc_phy.c` and igc modules responsible for hardware initialization, link setup, reset, and power management. Including `igc_mac.h` places it in the shared igc hardware-abstraction header stack.

## Risks and Edge Cases

Prototype changes must stay aligned with PHY operation table assignments and call sites. The `igc_mac.h` include couples PHY declarations to MAC definitions, so header dependency changes can break compilation.

## Test Signals

Compile coverage is the primary signal. Runtime signals come from probe-time PHY discovery, link setup, reset, power management, and GPY register access tests.
