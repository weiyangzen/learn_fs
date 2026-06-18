# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_93cx6.c

## Purpose

`aic7xxx_93cx6.c` implements bit-banged access to 93C46/56/66-style serial EEPROM chips used by AIC7xxx adapters for BIOS and controller settings. It supports read, write, write-enable/disable sequencing, chip reset, and checksum verification for `struct seeprom_config`.

## Important APIs, Types, and Functions

- `struct seeprom_cmd` stores opcode length and bit sequence.
- Static command definitions cover short C46 and long C56/C66 write-enable/write-disable opcodes plus common read/write opcodes.
- `CLOCK_PULSE(sd, rdy)` waits for SEEPROM ready and clears the clock by reading the control port.
- `send_seeprom_cmd()` asserts chip select and clocks command bits through descriptor-provided `CS`, `CK`, and `DO` masks.
- `reset_seeprom()` drops chip select and clocks the device back to idle/reset state.
- `ahc_read_seeprom()` sends read opcode/address cycles and reads 16-bit words, including the leading zero bit specified by the chip protocol.
- `ahc_write_seeprom()` selects the correct EWEN/EWDS opcode width, writes each addressed 16-bit word, waits for write completion by polling data-in, and returns the chip to write-protect mode.
- `ahc_verify_cksum()` sums all config words except the checksum and compares the low 16 bits to `sc->checksum`, rejecting zero checksums.

## Control Flow and State

Reads iterate from `start_addr` through `start_addr + count - 1`. For each word the code sends the read opcode, clocks the 6- or 8-bit address MSB first based on `sd_chip`, reads 17 cycles to discard the initial zero and collect 16 bits, stores the word, and resets chip select. Writes first enable programming, then for each word send write opcode, address, data bits MSB first, poll until the chip reports completion, reset chip select, and finally disable programming.

All hardware state is external to the file and accessed through the `seeprom_descriptor` macros in the header. The functions assume the caller has already acquired exclusive SEEPROM access and configured the descriptor offsets/masks.

## State and Persistence Behavior

Reads are non-mutating except for control-line toggling. Writes persist new 16-bit words into serial EEPROM hardware. Checksum verification is pure over a `struct seeprom_config` memory image.

## Dependencies and Integration Points

The file includes `aic7xxx_osm.h`, `aic7xxx_inline.h`, and `aic7xxx_93cx6.h`. It depends on `ahc_inb()`, `ahc_outb()`, and `ahc_flush_device_writes()` via macros. Bus attach/config code uses these functions to load or update adapter NVRAM before applying target and termination settings.

## Risks

- The polling loops have no timeout. Broken hardware or an incorrect ready/data mask can hang the caller.
- Write support persists hardware settings; callers must validate length, checksum, and exclusive access before invoking it.
- Descriptor bit masks must match the specific adapter wiring; swapped DO/DI/CK/CS masks would corrupt reads or writes.
- Checksum logic treats checksum zero as invalid even if the arithmetic comparison would otherwise pass.

## Test Signals

- Read known-good EEPROM contents and verify expected signature/checksum.
- Write a test image only on disposable hardware or emulator, then reread and verify exact word match.
- Test both C46 6-bit and C56/C66 8-bit address modes.
- Fault-inject invalid ready/data masks to ensure higher layers avoid unbounded hangs where possible.
