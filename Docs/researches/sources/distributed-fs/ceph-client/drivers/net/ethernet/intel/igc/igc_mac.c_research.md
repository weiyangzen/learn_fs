# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.c

## Purpose
`igc_mac.c` provides generic MAC-level operations for PCIe master disable, receive address programming, link and flow-control setup, counter clearing, speed/duplex reporting, hardware semaphore release, management pass-through detection, and multicast table programming.

## Important APIs, Types, And Functions
Public functions include `igc_disable_pcie_master()`, `igc_init_rx_addrs()`, `igc_setup_link()`, `igc_force_mac_fc()`, `igc_clear_hw_cntrs_base()`, `igc_rar_set()`, `igc_check_for_copper_link()`, `igc_config_collision_dist()`, `igc_config_fc_after_link_up()`, `igc_get_auto_rd_done()`, `igc_get_speed_and_duplex_copper()`, `igc_put_hw_semaphore()`, `igc_enable_mng_pass_thru()`, and `igc_update_mc_addr_list()`. Static helpers are `igc_set_fc_watermarks()` and `igc_hash_mc_addr()`.

## Control Flow
Link setup checks for reset blocking, normalizes default flow control, calls the hardware physical-interface setup op, initializes pause frame registers, and writes flow-control watermarks. Copper link checks run only when `mac->get_link_status` is set, call PHY link detection, clear the flag on link, check downshift, configure collision distance, resolve negotiated pause mode, and update I225 LTR. Flow-control resolution reads local and partner advertisement registers and applies IEEE pause/asymmetric-pause rules before forcing MAC bits. Multicast updates rebuild the software MTA shadow and write the full hardware MTA table.

## State And Persistence
The file mutates `hw->fc.current_mode`, `hw->fc.requested_mode`, `hw->mac.get_link_status`, `hw->mac.mta_shadow`, RAR registers, MTA registers, flow-control registers, TCTL collision distance, CTRL flow-control bits, SWSM semaphore bits, and LTR registers through the I225 helper. Counter clearing reads hardware counters that clear on read.

## Dependencies And Integration Points
It depends on `igc_mac.h`, `igc_hw.h`, PHY helpers such as `igc_phy_has_link()` and `igc_check_downshift()`, and I225 LTR support. `igc_base.c` wires several functions into MAC operation tables. `igc_main.c` calls link setup, multicast programming, and reset flows; ethtool pause/link settings call flow-control and setup helpers.

## Risks
Flow-control negotiation has many branch combinations and must preserve requested versus current mode. Counter clearing by read has destructive semantics for hardware counters. RAR writes require flushes to avoid bridge write combining. Multicast hash behavior depends on `mta_reg_count` and `mc_filter_type`; invalid values can misprogram filters. Link checks overwrite `ret_val` with LTR result at exit, which can mask earlier success/failure semantics if changed carelessly.

## Test Signals
Signals include link-up/down at all speeds, pause negotiation combinations, half-duplex disabling flow control, multicast reception with many addresses, RAR programming for MAC address changes, management pass-through behavior, reset with PCIe master disable, counter reset/update behavior, and ethtool pause/link setting changes.
