# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_phy.c

## Purpose

`igc_phy.c` implements PHY-level support for copper igc devices. It handles PHY reset checks, PHY ID discovery, link polling, copper power up/down, autonegotiation advertisement, copper link setup, MDIC and XMDIO register access, GPY register read/write dispatch, and gPHY firmware version reads.

## Important APIs, Types, and Functions

Public functions are `igc_check_reset_block`, `igc_get_phy_id`, `igc_phy_has_link`, `igc_power_up_phy_copper`, `igc_power_down_phy_copper`, `igc_check_downshift`, `igc_phy_hw_reset`, `igc_setup_copper_link`, `igc_write_phy_reg_gpy`, `igc_read_phy_reg_gpy`, and `igc_read_phy_fw_version`. Private helpers include autoneg setup/wait, MDIC read/write, and XMDIO address/data access. The code operates on `struct igc_hw`, `struct igc_phy_info`, `struct igc_fc_info`, and the callbacks in `hw->phy.ops`.

## Control Flow

`igc_phy_hw_reset` checks whether firmware blocks reset, acquires the PHY semaphore, toggles `IGC_CTRL_PHY_RST`, waits for `IGC_PHY_RST_COMP`, and releases the semaphore. `igc_get_phy_id` reads `PHY_ID1/PHY_ID2` and stores ID/revision. `igc_phy_has_link` double-reads sticky `PHY_STATUS` while polling for link.

Copper link setup masks/defaults autoneg advertisement, programs 10/100/1000/2500 capabilities and pause bits, restarts autoneg, optionally waits for completion, then checks link and configures collision distance and flow control after link up. MDIC paths validate offsets, issue `IGC_MDIC` operations, and poll ready/error bits. GPY register access dispatches normal registers through semaphore-protected MDIC and encoded MMD registers through XMDIO sequencing via `IGC_MMDAC`/`IGC_MMDAAD`.

## State and Persistence Behavior

The file mutates PHY registers and `hw->phy` fields such as ID, revision, speed-downshift status, and autoneg advertisement. Power and reset changes persist until another reset or power transition. MDIC register access is semaphore protected for non-MMD registers. XMDIO access restores `IGC_MMDAC` to zero after address/data operations.

## Dependencies and Integration Points

This file includes `linux/bitfield.h` and `igc_phy.h`, and depends on MII constants, igc register macros, delay helpers, `FIELD_GET`, and register I/O. It integrates with MAC helpers `igc_config_collision_dist` and `igc_config_fc_after_link_up`, and with hardware init/reset/link code through PHY operation tables.

## Risks and Edge Cases

PHY reset-block is treated as nonfatal in `igc_phy_hw_reset`, which can surprise callers expecting a real reset. MDIC timeouts and error bits must propagate. Unsupported 1000/2500 half-duplex advertisement requests are logged but not programmed. Invalid flow-control mode returns `-IGC_ERR_CONFIG`. XMDIO cleanup failure can leave MMD access state selected. Advertisement masks must match hardware capabilities.

## Test Signals

Signals include PHY ID discovery during probe, link-up/link-down across supported speeds, ethtool advertisement and flow-control changes, reset-block scenarios, suspend/resume power transitions, MDIC timeout/error injection, MMD/2.5G advertisement access, watchdog link messages, and repeated reset/open/close cycles with link partner changes.
