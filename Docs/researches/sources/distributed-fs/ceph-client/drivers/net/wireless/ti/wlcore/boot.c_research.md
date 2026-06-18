# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/boot.c

## Purpose
Implements the common wlcore firmware boot pipeline: firmware image upload, NVS upload, firmware start/handshake, firmware-version parsing/validation, static-data handling, mailbox discovery, event unmasking, and partition transition to running mode.

## Important APIs, types, and functions
- `wlcore_boot_upload_firmware()` parses a big-endian chunked firmware image and writes chunks to target memory.
- `wl1271_boot_upload_firmware_chunk()` sets download partitions and streams fixed-size chunks with partition-window updates.
- `wlcore_boot_upload_nvs()` validates legacy or wl128x NVS layout, patches the active MAC address into NVS bytes, bursts register writes, aligns and uploads NVS tables.
- `wlcore_boot_run_firmware()` halts/runs firmware, verifies chip id, polls init-complete interrupt, reads command/event mailbox pointers, reads static data, unmasks events, and switches to work partition.
- `wlcore_boot_parse_fw_ver()` and `wlcore_validate_fw_ver()` parse firmware version strings and enforce chip-family minimums.
- `wlcore_boot_static_data()` reads static data and delegates lower-driver private handling.

## Control flow
Firmware upload reads the first word as chunk count, then loops over address/length/data records, rejecting oversized chunks and requiring 4-byte-aligned lengths. NVS upload chooses legacy or non-legacy layout based on quirks and size, updates the primary MAC address, interprets burst-write records until a zero-length marker, aligns to the NVS table area, switches to work partition, and writes the table to the command mailbox data address. Run-firmware selects boot partition, verifies the chip id after starting firmware, polls `REG_INTERRUPT_NO_CLEAR` for `WL1271_ACX_INTR_INIT_COMPLETE`, acknowledges it, reads mailbox pointers, validates firmware static data, calls lower-driver static-data handler, unmasks events, and sets the work partition.

## State and persistence behavior
Mutates runtime device state: `wl->enable_11a` from NVS, patched in-memory `wl->nvs`, `wl->cmd_box_addr`, `wl->mbox_ptr[]`, `wl->chip.fw_ver_str`, `wl->chip.fw_ver[]`, and lower-driver static-data state. It may free and NULL malformed NVS buffers. Hardware memory/register state is heavily changed; no filesystem persistence.

## Dependencies and integration points
Depends on wlcore I/O, partitioning, event unmasking, RX/event headers, lower-driver callbacks `wlcore_identify_fw()` and `wlcore_handle_static_data()`, platform family NVS names, and firmware/NVS formats. Exported functions are used by chip-family boot implementations such as wl18xx.

## Risks and test signals
Risks include malformed firmware/NVS bounds, incorrect partition-window updates, MAC byte-order patching errors, legacy NVS compatibility, timeout polling init-complete, firmware version parsing assumptions, and mailbox pointer errors. Test with valid/invalid firmware chunks, valid/invalid legacy and wl128x NVS sizes, 5 GHz enablement from NVS, chip-id mismatch, firmware version below minimum, init timeout, mailbox read failures, and recovery boot loops.
