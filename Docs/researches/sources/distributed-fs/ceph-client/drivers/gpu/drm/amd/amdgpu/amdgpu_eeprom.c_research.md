# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.c

## Purpose
`amdgpu_eeprom.c` provides common I2C EEPROM read/write helpers for AMDGPU components such as FRU and RAS EEPROM users. It handles 19-bit EEPROM addressing, two-byte memory offsets, page-limited writes, adapter quirk limits, and read/write transfer chunking.

## Important APIs, types, and functions
Public entry points are `amdgpu_eeprom_read()` and `amdgpu_eeprom_write()`. Internal helpers are `amdgpu_eeprom_xfer()` and `__amdgpu_eeprom_xfer()`. Constants define 256-byte EEPROM write pages, two-byte offsets, and `MAKE_I2C_ADDR()` for mapping high address bits into the I2C EEPROM device address.

## Control flow
Callers pass an I2C adapter, EEPROM memory address, buffer, and byte count. `amdgpu_eeprom_xfer()` checks `i2c_adapter_quirks`; without quirks it delegates directly, otherwise it subtracts offset bytes from the adapter transfer limit and splits the operation into partial chunks. `__amdgpu_eeprom_xfer()` loops until all data is moved, fills an address-message plus data-message pair, caps writes so they do not cross a 256-byte page boundary, caps reads to `U16_MAX`, calls `i2c_transfer()`, and sleeps 10 ms after writes to allow the EEPROM self-timed write cycle.

## State and persistence behavior
The helper has no long-lived kernel state. Writes persist in the external EEPROM device. The only temporary state is stack I2C message setup and caller-provided buffers.

## Dependencies and integration points
It depends on Linux I2C adapter APIs, adapter quirk metadata, `msleep()`, AMDGPU device logging indirectly through callers, and `str_read_write()` from included AMDGPU headers. `amdgpu_fru_eeprom.c` and other EEPROM consumers rely on this file for consistent address and page handling.

## Risks and edge cases
The function returns a byte count for partial progress when `i2c_transfer()` returns a non-negative short result, so callers must check exact lengths. Adapter limits less than or equal to the two-byte offset are rejected. Write behavior depends on the fixed 10 ms delay rather than acknowledge polling. Address encoding must match 2-Mbit EEPROM wiring; wrong high address bits target the wrong chip or region. Page-boundary handling is critical because EEPROM page writes can wrap within the page.

## Test signals
Test signals include full and partial reads, page-boundary writes, adapter quirk-limited transfers, exact-length checks by FRU/RAS callers, invalid quirk limits returning `-EINVAL`, I2C transfer error propagation, and persistence verification across rereads.
