# sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93cx6.c

Purpose: provides exported bit-banged access routines for 93cx6 Microwire EEPROMs, especially 93c46 and 93c66, using callbacks supplied in `struct eeprom_93cx6`.

Important APIs, types, and functions: exported functions are `eeprom_93cx6_read()`, `eeprom_93cx6_multiread()`, `eeprom_93cx6_readb()`, `eeprom_93cx6_multireadb()`, `eeprom_93cx6_wren()`, and `eeprom_93cx6_write()`. Internal helpers pulse clock high/low, assert/deassert chip select, write bits, and read bits. The implementation uses callback fields `register_read()` and `register_write()` plus bit fields such as `reg_data_in`, `reg_data_out`, `reg_data_clock`, `reg_chip_select`, and `drive_data`.

Control flow: read operations start the EEPROM transaction, send a READ opcode plus word/byte address based on EEPROM width, optionally perform an extra read cycle quirk, read 16 or 8 bits, and clean up chip select. Multi-read functions loop single reads and convert word reads to little-endian for callers. `eeprom_93cx6_wren()` sends EWEN or EWDS. Write sends WRITE opcode/address, sends 16 data bits, releases data drive, waits for data-out to go high as ready/busy with up to 100 sleep-loop iterations, then cleans up.

State and persistence: persistent state is EEPROM contents and write-enable state. Runtime state is entirely in the caller-provided `struct eeprom_93cx6`, whose register image is repeatedly read/modified/written by callbacks. The helper does not allocate per-device state or provide locking.

Dependencies and integration points: depends on `linux/eeprom_93cx6.h` opcode/width/quirk definitions and hardware-specific drivers that provide register callbacks. Exported symbols are used as a small library by network/wireless or other device drivers with embedded Microwire EEPROMs.

Risks: callers must serialize access and correctly implement register callbacks; the helper itself has no locking. Timing is delay-based and assumes 450 ns pulses plus millisecond write polling are suitable. Address width and byte/word addressing must be configured correctly or reads/writes target the wrong cells. Write-enable is a separate operation; accidental enable plus writes can alter calibration data.

Test signals: callback-level tests on simulated registers, hardware reads for 93c46/93c66 widths, byte and word multi-read ordering, extra-read-cycle quirk behavior, write-enable/disable and write polling, timeout logging when ready never asserts, and endian checks for `multiread()`.
