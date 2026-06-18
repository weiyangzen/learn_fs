# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_diag.h

## Purpose
`igc_diag.h` declares the diagnostic self-test entry points and the register-test table format shared by `igc_diag.c` and the ethtool self-test implementation.

## Important APIs, Types, And Functions
It declares `igc_reg_test(struct igc_adapter *, u64 *)`, `igc_eeprom_test(struct igc_adapter *, u64 *)`, and `igc_link_test(struct igc_adapter *, u64 *)`. It also defines `struct igc_reg_test` with fields `reg`, `array_len`, `test_type`, `mask`, and `write`. Test type constants are `PATTERN_TEST`, `SET_READ_TEST`, `TABLE32_TEST`, `TABLE64_TEST_LO`, and `TABLE64_TEST_HI`.

## Control Flow
The header itself has no runtime flow. Its table contract drives `igc_reg_test()` dispatch: regular arrays are spaced differently from 32-bit tables and 64-bit low/high table halves.

## State And Persistence
No state is stored in this header. Its declarations describe functions that may temporarily alter hardware registers during offline diagnostics and read NVM/link state.

## Dependencies And Integration Points
The prototypes rely on `struct igc_adapter` being visible through prior includes from callers such as `igc_ethtool.c`. The register table structure is tightly coupled to register spacing assumptions documented in the comment block.

## Risks
Because the header has no include guard in the displayed file, it relies on normal inclusion discipline and may be vulnerable to duplicate declarations if included through unusual paths. Any change to `struct igc_reg_test` or test constants must be synchronized with `igc_diag.c`.

## Test Signals
Build coverage is the main signal for prototype and structure consistency. Runtime signals come through ethtool self-tests that exercise all declared functions.
