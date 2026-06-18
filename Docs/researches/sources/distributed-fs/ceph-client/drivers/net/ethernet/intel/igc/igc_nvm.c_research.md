# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_nvm.c

## Purpose

`igc_nvm.c` implements the small NVM/EEPROM support layer used by the igc hardware abstraction. It provides register-driven EEPROM reads through EERD, reads the permanent MAC address from receive address registers, validates the NVM checksum, and updates the checksum through the configured NVM write operation.

## Important APIs, Types, and Functions

The public functions are `igc_read_nvm_eerd`, `igc_read_mac_addr`, `igc_validate_nvm_checksum`, and `igc_update_nvm_checksum`. The file-private helper `igc_poll_eerd_eewr_done` waits for EERD/EEWR completion. It operates on `struct igc_hw`, especially `hw->nvm`, `hw->nvm.ops`, and `hw->mac.addr/perm_addr`. Key registers/macros include `IGC_EERD`, `IGC_EEWR`, `IGC_NVM_RW_REG_START`, `IGC_NVM_RW_REG_DONE`, `IGC_RAL(0)`, `IGC_RAH(0)`, `NVM_CHECKSUM_REG`, and `NVM_SUM`.

## Control Flow

`igc_read_nvm_eerd` validates `offset` and `words` against `hw->nvm.word_size`, rejects zero-length and out-of-bounds requests, then writes an EERD command for each word, polls for completion, and extracts the 16-bit data field. `igc_poll_eerd_eewr_done` loops up to 100000 attempts with 5 microsecond delays, returning `0` on done or `-IGC_ERR_NVM` on timeout. `igc_read_mac_addr` decodes RAL0/RAH0 into `perm_addr` and active `addr`. `igc_validate_nvm_checksum` sums NVM words through the checksum register and requires `NVM_SUM`; `igc_update_nvm_checksum` writes the computed complement through `hw->nvm.ops.write`.

## State and Persistence Behavior

The file reads persistent NVM contents, but only `igc_update_nvm_checksum` writes persistent state, delegated to the configured NVM write op. `igc_read_mac_addr` updates in-memory MAC fields from hardware registers. Polling is synchronous and stateless.

## Dependencies and Integration Points

This file includes `igc_mac.h` and `igc_nvm.h` and depends on igc register access, delays, and error constants. Probe-time logic in `igc_main.c` validates flash-backed NVM and reads the MAC through these operations when no platform MAC address is supplied. Hardware invariant setup wires these helpers into operation tables.

## Risks and Edge Cases

The polling loop can take roughly 500 ms per failed operation. Incorrect `word_size` setup affects bounds checking. Multiword reads can leave partial output when a later word fails, so callers must honor the return code. Checksum update safety depends on platform write support. MAC register reads assume hardware has already loaded RAL/RAH correctly.

## Test Signals

Signals include successful probe-time checksum validation, expected failure on corrupted checksum images, correct MAC reporting without a platform MAC address, timeout behavior when EERD/EEWR completion is blocked, bounds tests for zero/overflowing reads, and safe checksum update tests where NVM writes are supported.
