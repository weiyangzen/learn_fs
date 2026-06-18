# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_x540.c

## Purpose
`ixgbe_x540.c` implements the X540 generation-specific operation tables and helper routines for the ixgbe driver. It supplies X540 invariants, reset/start/link wrappers, EEPROM read/write/checksum/flash-update logic, software/firmware semaphore handling, LED blink control, and the exported `ixgbe_X540_info` descriptor used by probe-time board selection. Some logic is also conditionally shared with E610 paths, notably reset behavior that skips unsupported SAN/WWN handling for `ixgbe_mac_e610`.

## Important APIs, Types, and Functions
- X540 sizing constants define 128 Tx queues, 128 Rx queues, 128 RAR entries, 128 multicast table entries, 128 VFTA entries, and 384 KB Rx packet buffer size.
- Public generation hooks include `ixgbe_get_media_type_X540`, `ixgbe_get_invariants_X540`, `ixgbe_setup_mac_link_X540`, `ixgbe_reset_hw_X540`, `ixgbe_start_hw_X540`, `ixgbe_init_eeprom_params_X540`, `ixgbe_acquire_swfw_sync_X540`, `ixgbe_release_swfw_sync_X540`, `ixgbe_init_swfw_sync_X540`, `ixgbe_blink_led_start_X540`, and `ixgbe_blink_led_stop_X540`.
- EEPROM helpers wrap generic EERD/EEWR operations with X540 semaphore acquisition: `ixgbe_read_eerd_X540`, `ixgbe_read_eerd_buffer_X540`, `ixgbe_write_eewr_X540`, and `ixgbe_write_eewr_buffer_X540`.
- Checksum and persistence helpers include `ixgbe_calc_eeprom_checksum_X540`, `ixgbe_validate_eeprom_checksum_X540`, `ixgbe_update_eeprom_checksum_X540`, `ixgbe_update_flash_X540`, and `ixgbe_poll_flash_update_done_X540`.
- Semaphore internals include `ixgbe_get_swfw_sync_semaphore` and `ixgbe_release_swfw_sync_semaphore`.
- Static operation tables `mac_ops_X540`, `eeprom_ops_X540`, `phy_ops_X540`, `ixgbe_mvals_X540`, and exported `ixgbe_X540_info` connect this implementation to the core ixgbe probe and common code.

## Control Flow
Probe-time setup selects `ixgbe_X540_info`, calls `ixgbe_get_invariants_X540`, and installs the X540 operation tables into `struct ixgbe_hw`. Invariants set copper PHY power control, table sizes, queue counts, Rx packet buffer size, and MSI-X vector count from PCIe capabilities. Link setup is delegated to the PHY `setup_link_speed` operation, while media type is always copper.

`ixgbe_reset_hw_X540` first stops the adapter through the MAC ops table and clears pending Tx transactions. It acquires the PHY/NVM semaphore mask, sets `IXGBE_CTRL_RST`, flushes writes, releases the semaphore, then polls for reset completion and waits for post-reset stabilization. If `IXGBE_FLAGS_DOUBLE_RESET_REQUIRED` is set, it clears the flag and repeats the reset sequence. After reset it programs Rx packet buffer size, reads the permanent MAC address, initializes receive address registers and multicast tables, and, for non-E610 MACs, reads/programs SAN MAC and WWN prefix state.

EEPROM control initializes flash-backed EEPROM parameters once by reading `IXGBE_EEC(hw)` and deriving word size. Read/write operations acquire `IXGBE_GSSR_EEP_SM`, call generic EERD/EEWR helpers, and release the semaphore. Checksum validation first does a quick word-zero read to avoid long repeated failures, then takes the EEPROM semaphore, calculates the checksum by summing base words and valid pointer sections, reads the stored checksum directly with the generic helper, and compares. Updating writes the calculated checksum and triggers a flash update.

Software/firmware synchronization uses two levels of arbitration. `ixgbe_get_swfw_sync_semaphore` obtains the SMBI bit between software drivers and the REGSMP bit between software and firmware. `ixgbe_acquire_swfw_sync_X540` then checks requested software masks, corresponding firmware masks, and flash hardware masks in `SWFW_SYNC`, retrying with sleeps. If firmware or hardware appears stuck, it can assert the software bit anyway; if another software owner appears stuck, it clears known software bits and returns busy. Release clears owned bits and drops the underlying semaphores. `ixgbe_init_swfw_sync_X540` forcibly clears stale locks during initialization.

LED blink control checks index bounds, forces MAC link/speed if the link is down so LED blinking can work, updates the `IXGBE_LEDCTL` blink mode, and later restores default link-active LED mode and clears forced MAC link bits.

## State and Persistence Behavior
Most state changes are hardware register writes through MMIO. Reset mutates adapter hardware state, reinitializes Rx address/filter state, updates `hw->mac.perm_addr`, may reserve the last RAR for SAN MAC, and may decrement `hw->mac.num_rar_entries`. EEPROM initialization updates the runtime `hw->eeprom` cache. EEPROM write/checksum paths mutate shadow RAM and then request hardware to copy shadow RAM to persistent flash using `IXGBE_EEC_FLUP`; revision 0 hardware may require an additional sector update when `IXGBE_EEC_SEC1VAL` is set.

Semaphore functions mutate `SWFW_SYNC` and `SWSM` hardware bits and are critical for persistent NVM/flash and PHY accesses. LED blink functions temporarily alter MAC forced-link bits and LED control bits, restoring them on stop. There is no disk persistence.

## Dependencies and Integration Points
The file depends on Linux PCI/delay/scheduler APIs and ixgbe internal headers `ixgbe.h`, `ixgbe_mbx.h`, `ixgbe_phy.h`, and `ixgbe_x540.h`. It delegates much work to generic ixgbe helpers: adapter stop/start, Tx pending clear, PCIe MSI-X count, generic link and PHY operations, generic EEPROM EERD/EEWR, generic checksum/PBA helpers, RAR/MTA/VLAN/RSS/filter setup, flow control, firmware driver version, anti-spoofing, mailbox ops, and copper PHY power/overtemperature handling.

Its exported `ixgbe_X540_info` is consumed by the PCI board table in main driver code. X550 code includes `ixgbe_x540.h` and can reuse selected X540 operations. E610 code includes the X540 header as well, and `ixgbe_reset_hw_X540` has an explicit E610 branch that returns before unsupported SAN MAC and WWN work.

## Risks and Edge Cases
- Reset sequencing depends on semaphore acquisition and polling `IXGBE_CTRL_RST_MASK`. Timeout or semaphore failure leaves the adapter stopped or partially reset.
- Double-reset handling uses a MAC flag and `goto`; callers must ensure the flag is only set for conditions that really require one extra reset.
- The reset function sets `hw->mac.num_rar_entries = IXGBE_X540_MAX_TX_QUEUES`, which has the same value as RAR entries but is semantically odd; changing constants independently could introduce a bug.
- EEPROM checksum calculation intentionally bypasses synchronized EEPROM ops while already holding the semaphore. Calling it without proper outer synchronization would race with firmware or other software.
- Flash update polling uses fixed microsecond delays and returns `-EIO` on timeout; slow or busy flash hardware can cause checksum update failure after shadow RAM was already written.
- SW/FW semaphore recovery can force ownership when firmware/hardware appears stuck. This avoids permanent deadlock but risks conflicting with firmware if the apparent hang is only a long operation.
- LED blink start forces link bits when link is down; stop must run to restore MAC state. Error or removal paths should not leave forced-link settings active.
- E610 reuse of X540 reset behavior is guarded only for later SAN/WWN work; earlier register writes must remain valid for E610 users.

## Test Signals
- Probe tests should verify invariants: queue limits, table sizes, Rx packet buffer size, copper media type, MSI-X count, and operation table assignment.
- Reset tests should cover normal reset, semaphore failure, reset-bit timeout, double-reset flag, E610 skip path, SAN MAC programming, and RAR count adjustment.
- EEPROM tests should exercise read/write single and buffer paths, checksum validation success/failure, invalid pointer sections, word-zero read failure, flash update timeout, and revision-0 second-sector update.
- Concurrency tests should stress `ixgbe_acquire_swfw_sync_X540` and release with NVM, PHY, I2C, SW management, firmware-owned, hardware flash-owned, and stuck software-owner masks.
- LED tests should cover invalid indices, link-up blink, link-down forced blink, and restoration of `IXGBE_MACC` and `IXGBE_LEDCTL`.
- Build tests should ensure all operation table callbacks remain compatible with `struct ixgbe_mac_operations`, `struct ixgbe_eeprom_operations`, and `struct ixgbe_phy_operations`.
