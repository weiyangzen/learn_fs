# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.c

## Purpose
`igc_diag.c` implements diagnostic helpers used by the driver's ethtool self-test path. It validates selected MMIO registers with write/read patterns, validates NVM checksum state, and checks physical link availability.

## Important APIs, Types, And Functions
The public functions are `igc_reg_test()`, `igc_eeprom_test()`, and `igc_link_test()`, declared in `igc_diag.h` and called by `igc_ethtool_diag_test()`. The static `reg_test[]` table names registers, array lengths, test type, readable mask, and writable mask. Static helpers `reg_pattern_test()` and `reg_set_and_check()` save the original register value, write a test value, read back, compare with masks, restore the original value, and report failures through `netdev_err()`.

## Control Flow
`igc_reg_test()` first treats `IGC_STATUS` as a special case because it has mixed read-only, toggle, and writable bits. It then walks `reg_test[]` until the zero terminator and dispatches each entry by test type: normal register arrays use `0x40` spacing, receive-address table halves use `8` byte spacing, and MTA tables use `4` byte spacing. On the first failure it stores the failing register or status marker in `*data` and returns false. `igc_eeprom_test()` calls `hw->nvm.ops.validate()`. `igc_link_test()` sleeps five seconds for autonegotiation and calls `igc_has_link()`.

## State And Persistence
Register tests temporarily mutate hardware registers but attempt to restore each original value immediately. NVM validation is read-only through the NVM operation table. Link testing waits but does not intentionally reconfigure link state.

## Dependencies And Integration Points
The file depends on `igc.h` for adapter, ring, register access, and logging infrastructure, and on `igc_diag.h` for the test table type and constants. It is integrated into ethtool offline and online self-tests; offline mode closes or resets the interface around these tests.

## Risks
Pattern tests touch live hardware registers, so they must be run only in the controlled offline path. A bad mask in `reg_test[]` can report false failures or leave state disturbed. `igc_eeprom_test()` assumes `validate` is non-NULL, which is safe only when NVM ops were initialized for the device path that supports validation.

## Test Signals
Signals are `ethtool -t <dev> offline` and `online`, expected self-test data values, kernel log messages for failing registers, preservation of link after test recovery, and no regressions in reset/open paths after offline diagnostics.
