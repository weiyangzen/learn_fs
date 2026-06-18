# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_hw.c

## Purpose
`ngbe_hw.c` contains GbE PF hardware-specific reset, EEPROM checksum, and SFP power-control routines layered on top of shared `wx` hardware helpers.

## Important APIs, Types, and Functions
Exports are `ngbe_eeprom_chksum_hostif()`, `ngbe_sfp_modules_txrx_powerctl()`, and `ngbe_reset_hw()`. Internal `ngbe_reset_misc()` runs common misc reset and powers down GPIO-controlled SFP modules.

## Control Flow
Probe calls `ngbe_reset_hw()` after management/flash readiness checks. Reset stops the adapter, optionally triggers a LAN reset for non-MDI MAC types and polls completion, resets misc hardware, clears hardware counters, reads the permanent MAC, initializes receive addresses, and re-enables PCI bus mastering. EEPROM checksum sends a host-interface command and checks firmware mailbox status for pass/fail.

## State and Persistence Behavior
The file updates hardware reset state, GPIO output state, counters, MAC receive address registers, and `wx->mac.perm_addr`/`num_rar_entries`. SFP power state persists in GPIO until changed or reset. No disk persistence exists.

## Dependencies and Integration Points
It depends on `wx_stop_adapter()`, `wx_reset_misc()`, `wx_clear_hw_cntrs()`, `wx_get_mac_addr()`, `wx_init_rx_addrs()`, host-interface command helpers, PCI APIs, and `ngbe_type.h` register constants. It is used by `ngbe_probe()`, resume, and reset paths.

## Risks and Edge Cases
LAN reset polling uses a fixed timeout and a hard-coded status register in the poll call. GPIO power control semantics are inverted (`0` is on), so wrong boolean use can power down optics. EEPROM checksum validation depends on firmware status magic values.

## Test Signals
Test probe/reset on MDI and RGMII/SFP variants, GPIO-controlled modules, failed host-interface checksum, LAN reset timeout, permanent MAC read, and post-reset traffic. Verify SFP power toggles during down/up.
