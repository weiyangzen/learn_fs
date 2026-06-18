# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34v7.c

## Purpose

`rmi_f34v7.c` implements RMI4 Function 34 bootloader v7 and newer firmware flashing. It parses v10 containerized firmware images, reads the device partition table, validates image partition sizes, enters bootloader mode, erases application partitions, rewrites the partition table/config, and writes firmware, UI config, display config, and guest code blocks.

## Important APIs, Types, and Functions

Key functions include `rmi_f34v7_read_flash_status()`, `rmi_f34v7_check_command_status()`, `rmi_f34v7_write_command()`, `rmi_f34v7_write_partition_id()`, `rmi_f34v7_read_partition_table()`, `rmi_f34v7_parse_partition_table()`, `rmi_f34v7_read_queries()`, `rmi_f34v7_read_blocks()`, `rmi_f34v7_write_f34v7_blocks()`, `rmi_f34v7_write_partition_table()`, `rmi_f34v7_parse_image_header_10()`, `rmi_f34v7_parse_image_info()`, `rmi_f34v7_start_reflash()`, `rmi_f34v7_do_reflash()`, and `rmi_f34v7_probe()`.

## Control Flow

Probe reads the bootloader ID, determines the bootloader version, initializes completions, and reads v7 queries plus the current partition table. Starting a reflash parses the image and enters flash programming mode if not already in bootloader mode. The main reflash path enables F34 interrupts, refreshes bootloader version, parses image metadata, validates bootloader config size, erases application partitions, writes flash/bootloader config and partition table data, resets/scans PDT to reload the partition table, then writes firmware, UI config, optional display config, and optional guest code. Block transfers program partition ID, block number, transfer length, command, payload, then wait for idle status.

## State and Persistence Behavior

The v7 substructure of `f34_data` persists flash status, command, bootloader-mode flag, geometry, partition counts, device partition table, image metadata, read/config buffers, and progress accounting. Hardware flash partitions are persistent and are erased/reprogrammed. Completion state is reinitialized for each command, and command completion is normally driven by F34 attention.

## Dependencies and Integration Points

The file depends on RMI block reads/writes, completions, jiffies/timeouts, unaligned little-endian helpers, firmware image memory, and the common F34 sysfs/update orchestration. It also calls `rmi_scan_pdt()` during the v7 sequence after partition-table programming.

## Risks and Edge Cases

Image parsing trusts container offsets and lengths from firmware data; malformed images can point outside the firmware buffer unless higher layers guarantee validity. `rmi_f34v7_read_partition_table()` has a polling loop comparing a timeout value directly to `jiffies` rather than adding it to the current time, which can make the loop ineffective after boot. `rmi_f34v7_write_partition_id()` can leave `partition` unset if `config_area` is invalid. Progress counts blocks in some paths and bytes in v5, so user-visible percentages should be verified. Any interruption after erase can leave the device in bootloader mode.

## Test Signals

Tests should include known-good v10 images, malformed container offsets, missing flash config, unsupported header versions, each optional partition combination, bootloader entry from UI and already-bootloader modes, command timeout/status errors, block transfer chunking by payload length and page size, post-partition-table reset behavior, and full reflash recovery after injected failures.
