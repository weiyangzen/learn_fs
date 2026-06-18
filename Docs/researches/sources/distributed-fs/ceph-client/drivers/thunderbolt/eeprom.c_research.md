# sources/distributed-fs/ceph-client/drivers/thunderbolt/eeprom.c

## Purpose

`eeprom.c` reads and parses Thunderbolt/USB4 DROM data for switches. It supports legacy bit-banged EEPROM access, host DROM copies from EFI properties, DROM copies from active NVM through the DMA port, and USB4 router DROM reads. Parsed DROM entries populate switch identity, vendor/device names, port disable/link metadata, dual-link relationships, and USB4 product IDs.

## Important APIs, Types, and Functions

Low-level EEPROM helpers are `tb_eeprom_ctl_read/write()`, `tb_eeprom_active()`, `tb_eeprom_transfer()`, `tb_eeprom_out()`, `tb_eeprom_in()`, `tb_eeprom_get_drom_offset()`, and `tb_eeprom_read_n()`. Integrity helpers are `tb_crc8()` and `tb_crc32()`.

DROM ABI structures include `struct tb_drom_header`, `struct tb_drom_entry_header`, `struct tb_drom_entry_generic`, `struct tb_drom_entry_port`, and `struct tb_drom_entry_desc`. Public APIs are `tb_drom_read_uid_only()` and `tb_drom_read()`.

Copy/parse helpers include `tb_drom_copy_efi()`, `tb_drom_copy_nvm()`, `usb4_copy_drom()`, `tb_drom_bit_bang()`, `tb_drom_parse_v1()`, `usb4_drom_parse()`, `tb_drom_parse()`, `tb_drom_parse_entries()`, `tb_drom_parse_entry_generic()`, and `tb_drom_parse_entry_port()`.

## Control Flow

For non-root switches, `tb_drom_read()` reads the DROM through USB4 DROM access or legacy EEPROM bit banging, then parses it. For root switches, USB4 hosts read UID and DROM via USB4 helpers; non-USB4 hosts first try EFI property `ThunderboltDROM`, then DMA-port NVM copy, and finally minimal UID-only read.

Bit-banged reads enable EEPROM access through plug-events capability control bits, send SPI-like read opcode and offset bytes, read each byte by toggling clock/data bits, then disable access. DROM copy functions allocate `sw->drom`, wire it to the debugfs blob when enabled, and free it on copy or parse failure.

Parsing validates total size, dispatches by `device_rom_revision`, checks UID CRC8 for v1 DROM, warns but continues on data CRC32 mismatch, then walks variable-length entries. Generic entries set vendor/device names or USB4 product IDs. Port entries mark ports disabled and, for lane ports, set link number and dual-link partner.

## State and Persistence Behavior

The parsed DROM persists in `sw->drom` for the switch lifetime and may be exposed as a debugfs blob. Parsed fields persist in `struct tb_switch`, including UID, vendor/device IDs, names, disabled port flags, link numbers, and dual-link pointers.

The file does not write persistent storage, but it reads persistent EEPROM/NVM/firmware data. The warning in `tb_eeprom_active()` is operationally important: leaving bit-banging enabled can prevent controller reprobe, so successful paths must disable access after use.

## Dependencies and Integration Points

The file depends on switch/port config-space helpers, plug-events capability definitions, DMA-port flash reads, USB4 DROM/UID helpers, EFI/device properties, CRC32C, debugfs blob fields, and switch structures from `tb.h`.

It feeds switch discovery and debugfs. `tb_drom_read_uid_only()` is used during resume to verify switch identity without trusting cached `sw->drom`.

## Risks and Edge Cases

`tb_eeprom_read_n()` does not use a single cleanup exit after enabling EEPROM access. If `tb_eeprom_out()` or `tb_eeprom_in()` fails, it returns immediately without disabling bit-banging, matching the file's own warning as a risk.

`tb_drom_read_uid_only()` casts `data + 1` to `u64 *`, which may be unaligned on architectures that fault on unaligned access. The kernel often tolerates this on x86, but portable code would use `get_unaligned_le64()` or similar.

CRC32 mismatch only warns and continues. That improves compatibility with bad DROMs but can propagate corrupted names or port metadata. Port entries referring to port numbers within `max_port_number` but invalid dual-link partners are trusted.

Host DROM fallback behavior can leave root switches with only UID populated when full DROM copy is unavailable. Callers must tolerate absent vendor/device names and absent port metadata.

## Test Signals

Tests should cover EFI DROM copy, DMA-port NVM DROM copy, USB4 DROM read, legacy bit-banged read, UID-only read, CRC8 failure, CRC32 warning path, size mismatch, variable-entry overrun detection, unknown DROM revision fallback, extra port entries beyond max port, disabled port entries, dual-link port metadata, and failure cleanup that disables EEPROM access.
