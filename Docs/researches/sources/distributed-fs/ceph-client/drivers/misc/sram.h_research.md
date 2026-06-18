# sources/distributed-fs/ceph-client/drivers/misc/sram.h

## Purpose
`sram.h` is the private header shared by the generic SRAM driver and its executable-SRAM helper. It defines the driver-private configuration, device, partition, and reservation structures plus conditional prototypes for protected executable SRAM support.

## Important APIs, Types, and Functions
`struct sram_config` provides optional platform initialization and the `map_only_reserved` policy. `struct sram_partition` contains a mapped partition base, optional `gen_pool`, sysfs binary attribute, mutex, and list node. `struct sram_dev` stores per-device configuration, base mapping, root pool, partition array, and count. `struct sram_reserve` describes a parsed reserved child block with start/size/resource and export/pool/protect-exec flags. `sram_check_protect_exec()` and `sram_add_protect_exec()` are declared when `CONFIG_SRAM_EXEC` is enabled and otherwise return `-ENODEV`.

## Control Flow
The header has no runtime flow. Its structures are filled by `sram.c` during platform probe and consumed by `sram-exec.c` when protected executable partitions are enabled.

## State and Persistence
The header defines in-memory state containers only. Persistence behavior is determined by SRAM hardware and the implementation files.

## Dependencies and Integration Points
It assumes Linux kernel definitions for `struct device`, `struct gen_pool`, `struct bin_attribute`, `struct mutex`, `struct list_head`, and `struct resource` are included by users. It is internal to `drivers/misc` SRAM code and not a UAPI contract.

## Risks and Edge Cases
The `CONFIG_SRAM_EXEC` stubs make `protect-exec` reservations fail with `-ENODEV` when executable SRAM support is disabled. The single `list_head` in `struct sram_partition` is used for executable pool tracking, so additional list uses would need a new member.

## Test Signals
Build both with and without `CONFIG_SRAM_EXEC`, verify `protect-exec` DT behavior in each configuration, and check structure users initialize mutexes/list hooks before use.
