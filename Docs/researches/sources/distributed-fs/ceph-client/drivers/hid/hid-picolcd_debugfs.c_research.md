<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_debugfs.c

## Purpose
This module provides PicoLCD debugfs controls and HID report tracing. It exposes `reset`, `eeprom`, and `flash` debugfs files when corresponding reports exist, implements EEPROM/flash read/write protocols using synchronous HID commands, and decodes outgoing/incoming reports into the HID debug stream.

## Important APIs, types, and functions
Debugfs file operations include `picolcd_debug_reset_fops`, `picolcd_debug_eeprom_fops`, and `picolcd_debug_flash_fops`. EEPROM handlers use `REPORT_EE_READ`, `REPORT_EE_WRITE`, and expect `REPORT_EE_DATA`. Flash helpers `_picolcd_flash_read`, `_picolcd_flash_erase64`, and `_picolcd_flash_write` support both LCD mode (`REPORT_READ_MEMORY`, `REPORT_ERASE_MEMORY`, `REPORT_WRITE_MEMORY`) and bootloader mode (`REPORT_BL_*`). `picolcd_debug_out_report` and `picolcd_debug_raw_event` decode many report IDs for `hid_debug_event`. `picolcd_init_devfs` creates debugfs files and determines flash address width; `picolcd_exit_devfs` removes them and destroys `mutex_flash`.

## Control flow
Reset debugfs writes accept `all` or `fb`, calling `picolcd_reset` and/or `picolcd_fb_reset`. EEPROM reads/writes operate in chunks of up to 20 bytes, send address/length/data payloads, and verify the echoed response before copying to/from userspace. Flash reads loop in up to 32-byte chunks within the 0x0000-0x5fff range. Flash writes require 64-byte alignment and size multiples, lock `mutex_flash`, erase each 64-byte block, write it in chunks, and stop on the first error.

Report debug functions are invoked by the header macro wrapping `hid_hw_request` and by core raw-event dispatch. They allocate temporary buffers, dump raw bytes as hex, decode known report fields, emit messages to `hdev->debug_list`, and wake `debug_wait`.

## State and persistence behavior
Debugfs state lives in `picolcd_data.debug_reset`, `debug_eeprom`, `debug_flash`, `mutex_flash`, and `addr_sz`. Flash/EEPROM writes affect persistent device memory, unlike most other PicoLCD state. Partial flash write failures are explicitly documented as leaving the target block undefined.

## Dependencies and integration points
The module depends on debugfs, seq_file, HID debug infrastructure, userspace copy helpers, hex formatting, and the core synchronous `picolcd_send_and_wait` path. It integrates with normal and bootloader report IDs.

## Risks and test signals
This is the highest-risk PicoLCD surface because it writes device EEPROM/flash from debugfs. Risks include partial writes after erase, address-size misdetection, userspace copy failures mid-operation, unchecked raw report sizes in debug decode paths, and concurrent access outside flash writes. Tests should cover read boundaries, zero-length handling, unaligned flash write rejection, 64-byte write/erase verification, bootloader reports, debug tracing enabled/disabled, and disconnect during synchronous debugfs I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-picolcd_debugfs.c -->
