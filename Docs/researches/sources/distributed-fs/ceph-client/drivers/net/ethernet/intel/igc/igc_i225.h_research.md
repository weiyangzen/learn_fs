# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.h

## Purpose
`igc_i225.h` declares the I225/I226-specific helper interface consumed by generic hardware, MAC, main-driver, and ethtool code.

## Important APIs, Types, And Functions
The declarations cover SW/FW synchronization (`igc_acquire_swfw_sync_i225()`, `igc_release_swfw_sync_i225()`), NVM parameter initialization and flash detection (`igc_init_nvm_params_i225()`, `igc_get_flash_presence_i225()`), EEE programming (`igc_set_eee_i225()`), and LTR programming (`igc_set_ltr_i225()`).

## Control Flow
No control flow is implemented here. The prototypes allow generic operation tables and user-facing paths to call I225-specific logic without including implementation details.

## State And Persistence
The declared functions mutate semaphores, NVM/flash operation tables and data, EEE registers, and LTR registers. This header itself stores no state.

## Dependencies And Integration Points
It depends on `struct igc_hw` and `s32` being available through including context, normally via `igc_hw.h`. `igc_hw.h` includes this header, while `igc_i225.c` provides the implementations.

## Risks
Prototype drift would break operation table initialization or cross-file calls. Since these functions include persistent NVM and power-management behavior, callers must handle errors and hardware capability checks correctly.

## Test Signals
Build coverage, successful probe, ethtool EEPROM and EEE operations, link-up LTR programming, and SW/FW semaphore acquisition paths are the relevant signals.
