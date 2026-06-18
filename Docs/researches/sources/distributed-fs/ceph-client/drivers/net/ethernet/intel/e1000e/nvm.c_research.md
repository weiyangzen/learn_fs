# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/nvm.c

## Purpose
`nvm.c` implements generic EEPROM/NVM primitives for the e1000e driver. It provides bit-banged SPI EEPROM clock/data helpers, register-based EERD reads, SPI writes, NVM arbitration, PBA string decoding, MAC address extraction, checksum validation/update, and NVM reload. Board-specific code installs these routines through `hw->nvm.ops`, while callers use wrappers such as `e1000_read_nvm()`, `e1000_write_nvm()`, and `e1000_validate_nvm_checksum()`.

## Important APIs, types, and functions
- Low-level EEPROM signaling: `e1000_raise_eec_clk()`, `e1000_lower_eec_clk()`, `e1000_shift_out_eec_bits()`, and `e1000_shift_in_eec_bits()` manipulate EECD clock, data-in, data-out, and chip-select bits with `udelay(hw->nvm.delay_usec)`.
- NVM arbitration and command framing: `e1000e_acquire_nvm()` requests EECD ownership and waits for grant, `e1000e_release_nvm()` clears the request after `e1000_stop_nvm()`, `e1000_standby_nvm()` toggles SPI chip select, and `e1000_ready_nvm_eeprom()` waits for the SPI status register ready bit.
- Register polling/read: `e1000e_poll_eerd_eewr_done()` waits for EERD/EEWR done, and `e1000e_read_nvm_eerd()` validates bounds then reads words through the EERD register.
- Write path: `e1000e_write_nvm_spi()` validates bounds, acquires NVM, waits for readiness, sends write-enable and write opcodes, streams words byte-swapped into page-sized SPI writes, sleeps for completion, and releases ownership.
- Device data helpers: `e1000_read_pba_string_generic()` reads legacy or pointer-guarded PBA numbers, `e1000_read_mac_addr_generic()` copies RAL/RAH register contents into `hw->mac.perm_addr` and `hw->mac.addr`.
- Integrity and reload: `e1000e_validate_nvm_checksum_generic()` sums words through `NVM_CHECKSUM_REG` and compares with `NVM_SUM`, with a TGP uninitialized-checksum exception; `e1000e_update_nvm_checksum_generic()` recomputes and writes the checksum; `e1000e_reload_nvm_generic()` toggles `CTRL_EXT.EE_RST`.

## Control flow
For register reads, callers pass an offset, word count, and buffer into `e1000e_read_nvm_eerd()`. The function rejects zero-length or out-of-bounds requests, writes the target word index and start bit to EERD, polls `E1000_NVM_RW_REG_DONE`, and extracts the returned 16-bit word from EERD.

For SPI writes, `e1000e_write_nvm_spi()` loops until all requested words are written. Each page transaction acquires NVM ownership, waits until the EEPROM ready bit clears, toggles standby, sends `NVM_WREN_OPCODE_SPI`, sends the write opcode plus address, shifts each word MSB-first after byte swapping, stops at a page boundary, waits 10-11 ms for programming, then releases ownership. Callers are expected to update the NVM checksum afterward.

PBA string reading first reads `NVM_PBA_OFFSET_0` and `NVM_PBA_OFFSET_1`. If the guard word is absent, it decodes a legacy packed hex PBA into a fixed string. If the guard is present, it treats the second word as a pointer, validates the section length, checks caller buffer space, then reads each word as two ASCII bytes.

Checksum validation reads and accumulates NVM words from zero through the checksum word. The result must equal `NVM_SUM`, except Tiger Lake/PCH TGP can ignore an explicitly uninitialized checksum word. Updating sums all words before the checksum, writes `NVM_SUM - checksum` back to `NVM_CHECKSUM_REG`, and returns the write status.

## State and persistence behavior
This file directly mutates EEPROM/NVM contents only in `e1000e_write_nvm_spi()` and `e1000e_update_nvm_checksum_generic()`. It also changes hardware access state through EECD request/grant/chip-select bits and reloads NVM shadow state through `CTRL_EXT.EE_RST`. MAC and PBA helpers read persistent device identity data and place it into `hw->mac` or caller buffers.

NVM access is serialized by hardware grant bits, not by a local mutex in this file. The caller-provided operation table determines whether these generic helpers are combined with board-specific locking. Timing behavior is persistent only insofar as EEPROM commands require precise delays and page-boundary handling.

## Dependencies and integration points
The file includes `e1000.h` and depends on register access macros (`er32`, `ew32`, `e1e_flush`), `struct e1000_hw`, `struct e1000_nvm_info`, `struct e1000_mac_info`, NVM constants and opcodes, Linux delay helpers, error codes, and debug logging. It is used by probe, ethtool/NVM paths, board variant setup, and reset flows that need MAC address, checksum, PBA, or EEPROM reload services.

## Risks and edge cases
- Incorrect bounds checks or word counts could read/write outside the EEPROM word size; this file rejects offset overflow and zero-word requests.
- SPI bit-banging depends on exact EECD transitions and delays. Changes can break EEPROMs with strict timing or address-bit handling.
- `e1000e_write_nvm_spi()` writes persistent NVM and warns that checksum update is required. Interrupted or misordered writes can leave invalid configuration.
- Page-boundary handling is critical; crossing a page without standby/program delay can wrap or corrupt EEPROM data.
- PBA string parsing must validate length and caller buffer size to avoid malformed NVM data overruns.
- TGP checksum exception deliberately accepts an uninitialized value; tests must distinguish intended platform behavior from silent checksum acceptance elsewhere.

## Test signals
Validation signals include successful probe MAC read, NVM checksum validation, PBA string display in device info, ethtool EEPROM read/write behavior where enabled, checksum update after writes, SPI write page-boundary tests, invalid offset/count rejection, NVM grant timeout handling, hardware reset/NVM reload behavior, malformed PBA sections, and uninitialized TGP checksum coverage.
