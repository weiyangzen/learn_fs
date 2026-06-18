# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_eeprom.h

## Purpose
`amdgpu_eeprom.h` declares the common AMDGPU I2C EEPROM access API.

## Important APIs, types, and functions
It includes `<linux/i2c.h>` and declares `amdgpu_eeprom_read()` and `amdgpu_eeprom_write()`, each taking an `i2c_adapter`, 32-bit EEPROM address, byte buffer, and transfer length.

## Control flow
The header has no executable control flow. Callers use the declared helpers to route EEPROM access through the common transfer implementation.

## State and persistence behavior
No state is defined here. Persistence behavior is provided by the backing EEPROM device and the implementation in `amdgpu_eeprom.c`.

## Dependencies and integration points
It is the contract between EEPROM consumers, including FRU support, and the low-level I2C transfer helper.

## Risks and edge cases
The API accepts mutable `u8 *` for writes as well as reads, so callers must pass correctly sized buffers and check exact byte counts. Address interpretation is implementation-specific and not self-describing in the prototype.

## Test signals
Build coverage plus successful FRU/RAS EEPROM reads and writes through consumers validate this header contract.
