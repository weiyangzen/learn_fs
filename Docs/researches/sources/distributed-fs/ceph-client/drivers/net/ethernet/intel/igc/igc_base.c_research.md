# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.c

## Purpose
`igc_base.c` provides base hardware operations for Intel I225/I226-class controllers. It resets MAC hardware, initializes NVM/MAC/PHY invariants, sets up copper link, initializes hardware filters, powers down PHY when safe, flushes RX FIFOs for manageability errata, classifies device IDs, and publishes the `igc_base_info` operation bundle.

## Important APIs, Types, And Functions
Externally visible functions include `igc_power_down_phy_copper_base()`, `igc_rx_fifo_flush_base()`, `igc_is_device_id_i225()`, `igc_is_device_id_i226()`, and the `igc_base_info` constant. Internal operations include `igc_reset_hw_base()`, `igc_init_nvm_params_base()`, `igc_setup_copper_link_base()`, `igc_init_mac_params_base()`, `igc_init_phy_params_base()`, `igc_get_invariants_base()`, `igc_acquire_phy_base()`, `igc_release_phy_base()`, and `igc_init_hw_base()`.

## Control Flow
Driver setup calls `igc_base_info.get_invariants`, which classifies device IDs as `igc_i225`, sets copper media, initializes MAC ops, NVM parameters, I225-specific NVM parameters, and PHY parameters. Hardware init initializes receive addresses, clears multicast and unicast hash tables, sets up link/flow control, and clears counters. Hardware reset disables PCIe master, masks interrupts, disables RX/TX, waits, asserts `CTRL.RST`, waits for auto-read completion, masks interrupts again, and clears pending causes. RX FIFO flush temporarily disables RX queues, rejects incoming packets while flushing, restores queue and RX control state, and clears generated counters.

## State And Persistence
State is stored in `struct igc_hw`: MAC type and ops, NVM properties, PHY properties, bus function, and device-specific semaphore behavior. Hardware register state is rewritten during reset/init, including interrupt masks, RCTL/TCTL, MTA/UTA tables, RLPML, RFCTL, and queue controls.

## Dependencies And Integration Points
The file depends on `igc_hw.h`, `igc_i225.h`, `igc_mac.h`, `igc_base.h`, and `igc.h`. It uses shared MAC/PHY/NVM helpers such as `igc_disable_pcie_master()`, `igc_get_auto_rd_done()`, `igc_setup_link()`, `igc_clear_hw_cntrs_base()`, and GPY PHY accessors. Main probe code consumes `igc_base_info`.

## Risks
Reset and FIFO flush sequences are timing-sensitive and register-order-sensitive. `igc_reset_hw_base()` deliberately logs but continues after auto-read failure to support blank/no EEPROM cases, so callers must handle partially initialized NVM contexts. Device ID classification controls the entire operation table. RX FIFO workaround must restore prior RX queue state to avoid traffic loss.

## Test Signals
Validate cold probe, reset, link setup, blank-NVM devices, I225/I226 device ID detection, manageability-enabled RX FIFO flush, PHY reset/read, MTA/UTA clearing, and counter clearing. Hardware logs for PCIe master disable and auto-read completion are useful diagnostics.
