# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_i225.c

## Purpose
`igc_i225.c` implements I225/I226-specific hardware services for SW/FW semaphore coordination, NVM shadow RAM and flash access, checksum validation/update, EEE programming, and Latency Tolerance Reporting threshold calculation.

## Important APIs, Types, And Functions
Public functions are `igc_acquire_swfw_sync_i225()`, `igc_release_swfw_sync_i225()`, `igc_init_nvm_params_i225()`, `igc_get_flash_presence_i225()`, `igc_set_eee_i225()`, and `igc_set_ltr_i225()`. Static helpers include NVM acquire/release wrappers, `igc_get_hw_semaphore_i225()`, shadow RAM read/write helpers, checksum validate/update helpers, and flash update polling.

## Control Flow
NVM access first acquires driver/FW semaphores, then performs burst reads or writes capped by `IGC_EERD_EEWR_MAX_COUNT`, releasing between bursts to avoid holding synchronization too long. Checksum validation temporarily swaps `hw->nvm.ops.read` to a no-semaphore read while a semaphore is already held. Checksum update reads words up to `NVM_CHECKSUM_REG`, writes the complement to reach `NVM_SUM`, then commits shadow RAM to flash. EEE programming toggles advertisement bits and LPI enable bits. LTR calculation reads link speed, EEE timing, and Rx packet buffer size, computes min/max latency thresholds and scales, then writes LTR registers only when changed.

## State And Persistence
This file mutates hardware semaphore registers, `SW_FW_SYNC`, NVM shadow RAM, flash contents, EEE registers, LTR registers, and `hw->dev_spec._base.clear_semaphore_once`. Flash update and checksum paths are persistent device changes. EEE and LTR are runtime hardware state derived from driver settings and link state.

## Dependencies And Integration Points
It depends on `igc_hw.h` for register constants, operation structures, `rd32`/`wr32`, and shared helper declarations. `igc_base.c` calls `igc_init_nvm_params_i225()`. `igc_main.c`, `igc_mac.c`, and ethtool EEE paths call EEE/LTR helpers during reset, link, suspend/resume, and user configuration.

## Risks
Semaphore timeout handling is critical: failure can block PHY/NVM access or race firmware. NVM writes can partially complete, leaving shadow RAM inconsistent if a later word fails. The wrapper write path passes the original `offset` for each burst, which is worth reviewing if multi-burst writes are used. LTR arithmetic must avoid invalid thresholds and preserve expected power behavior.

## Test Signals
Signals include NVM read/write/checksum validation, flash commit completion, probe on flash and no-flash devices, forced semaphore contention tests, EEE enable/disable and advertised mode checks, link-up LTR programming at all supported speeds, suspend/resume power tests, and ethtool EEPROM/EEE workflows.
