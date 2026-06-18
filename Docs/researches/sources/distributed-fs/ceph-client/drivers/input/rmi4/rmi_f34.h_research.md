# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.h

## Purpose

`rmi_f34.h` is the shared Function 34 firmware-update contract for v5 and v7 bootloader code. It defines command constants, register offsets, timeouts, firmware image structures, v7 partition/container identifiers, metadata structures, and the common `struct f34_data` state passed between `rmi_f34.c` and `rmi_f34v7.c`.

## Important APIs, Types, and Functions

The header defines v5 commands such as `F34_WRITE_FW_BLOCK`, `F34_ERASE_ALL`, and `F34_ENABLE_FLASH_PROG`; v7 data offsets and logical commands; partition IDs; image container IDs; packed register/image structures including `f34v7_query_1_7`, `f34v7_data_1_5`, `partition_table`, `container_descriptor`, `image_header_10`, and `rmi_f34_firmware`; metadata containers such as `image_metadata`, `block_count`, and `physical_address`; and exported functions `rmi_f34v7_start_reflash()`, `rmi_f34v7_do_reflash()`, and `rmi_f34v7_probe()`.

## Control Flow

This file has no runtime control flow. Its structures and constants are consumed by probe, sysfs update, command, image parsing, partition-table reading, erase, read, and write routines in the F34 implementation files. Packed structures describe the bytes read from RMI registers and firmware files.

## State and Persistence Behavior

The header defines all persistent in-memory flashing state. V5 state includes block geometry, control address, command completion, and flash mutex. V7 state includes bootloader mode, command/status, block and payload geometry, partition table data, image metadata, read/config buffers, and command completion. `f34_data` additionally persists user-visible update status and IDs.

## Dependencies and Integration Points

The header depends on kernel fixed-width types, endian types, `BIT()`, RMI function declarations, and firmware structures. It is included by both F34 implementation files and bridges sysfs-triggered update logic with v7 image parsing and flashing internals.

## Risks and Edge Cases

Packed layout and little-endian fields must match Synaptics firmware formats exactly. Several v7 names intentionally preserve historical casing and command naming. Incorrect constants can erase or write the wrong partition. `CONFIG_ID_SIZE` and product ID sizes shape sysfs-visible buffers, so off-by-one errors would leak or truncate identifiers. Structure changes require coordinated updates to both v5 and v7 code.

## Test Signals

Useful checks include compile coverage of both F34 implementation files, static assertions for important image offsets and packed sizes, parsing known v5/v7 firmware images, partition ID mapping tests, and build tests on big- and little-endian architectures.
