# sources/distributed-fs/ceph-client/include/linux/eeprom_93cx6.h

## Purpose
This header defines a bit-banged access abstraction for 93cx6 EEPROM chips used by PCI/network drivers. It supplies opcodes, address widths, controller callbacks, line-state fields, quirks, and read/write helper declarations.

## Important APIs, types, and functions
Constants define widths for 93C46/56/66/86, opcode width, read/write/erase and write-enable/disable opcodes, and `PCI_EEPROM_QUIRK_EXTRA_READ_CYCLE`. `struct eeprom_93cx6` contains private data, `register_read` and `register_write` callbacks, width, quirks, drive-data flag, and register line fields for data in/out, clock, and chip select. APIs include word and byte read/multiread functions, `eeprom_93cx6_wren()`, `eeprom_93cx6_write()`, and `has_quirk_extra_read_cycle()`.

## Control flow, state, and persistence
The implementation toggles the line-state fields and calls driver-provided register read/write callbacks to clock commands and data into the EEPROM. EEPROM contents persist in hardware; the struct stores transient bus line state and controller-specific context.

## Dependencies and integration points
It depends on `linux/bits.h` and integrates with drivers that provide register access to EEPROM pins, such as wireless or Ethernet adapters.

## Risks and test signals
Risks include wrong address width, missing extra read cycle for quirky chips, write-enable misuse, endian mistakes in multiread, and callbacks that do not update line fields correctly. Tests should cover read/write opcode sequencing, byte and word reads, write enable/disable, quirk handling, and driver callback ordering.
