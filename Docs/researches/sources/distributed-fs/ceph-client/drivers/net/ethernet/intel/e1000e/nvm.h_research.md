# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.h

## Purpose
`nvm.h` declares the generic e1000e NVM/EEPROM helper interface used across the driver. It exposes acquisition, polling, read/write, checksum, PBA, MAC address, LED default validation, and release routines implemented in `nvm.c` or related MAC code, and defines `E1000_STM_OPCODE` for NVM command use.

## Important APIs, types, and functions
- Access control: `e1000e_acquire_nvm()` and `e1000e_release_nvm()` bracket exclusive EEPROM access.
- Polling and data movement: `e1000e_poll_eerd_eewr_done()`, `e1000e_read_nvm_eerd()`, and `e1000e_write_nvm_spi()` provide generic read/write mechanisms.
- Identity helpers: `e1000_read_mac_addr_generic()` and `e1000_read_pba_string_generic()` expose persistent MAC/PBA extraction.
- Integrity helpers: `e1000e_validate_nvm_checksum_generic()` and `e1000e_update_nvm_checksum_generic()` expose checksum validation/update.
- LED validation: `e1000e_valid_led_default()` is declared here but implemented in `mac.c`, reflecting a shared NVM-backed LED default contract.
- Constant: `E1000_STM_OPCODE` is defined as `0xDB00`.

## Control flow
This header has no runtime control flow. It is included by driver implementation files that need prototypes for operation tables or direct helper calls. Board-specific initialization can assign these functions into `hw->nvm.ops` and other code can call the exported generic helpers.

## State and persistence behavior
The header itself stores no state. The declared functions operate on `struct e1000_hw`, which carries NVM/MAC/PHY state and hardware register mappings. Some declared functions read or mutate persistent EEPROM content or hardware-shadowed NVM state.

## Dependencies and integration points
The header assumes `struct e1000_hw`, `s32`, `u8`, `u16`, and `u32` are already visible through surrounding e1000e headers. It is part of the e1000e internal API and integrates with `nvm.c`, `mac.c`, board variant files, and callers in probe/ethtool/reset code.

## Risks and edge cases
- Prototype drift between this header and implementations would break operation-table initialization or cross-file calls at build time.
- Because this header declares persistent NVM write/checksum functions, misuse by callers can corrupt EEPROM if acquisition/release and checksum-update contracts are ignored.
- `E1000_STM_OPCODE` has no local context here; changes require checking all command users.

## Test signals
Build coverage is the main direct test signal. Runtime validation comes indirectly from NVM read/write, checksum, MAC/PBA, and LED default paths in the files that include this header.
