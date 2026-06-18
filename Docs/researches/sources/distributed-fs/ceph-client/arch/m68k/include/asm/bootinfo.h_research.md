<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootinfo.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootinfo.h

## Purpose
This header wraps the m68k boot information UAPI and declares optional helpers for preserving boot records and processing U-Boot command lines.

## Important APIs, Types, And Functions
- Includes `<uapi/asm/bootinfo.h>` for `struct bi_record` and bootinfo constants.
- `save_bootinfo()` is real when `CONFIG_BOOTINFO_PROC` is enabled and a no-op inline otherwise.
- `process_uboot_commandline()` is real when `CONFIG_UBOOT` is enabled and a no-op inline otherwise.

## Control Flow
Early boot code parses boot records and calls `save_bootinfo()` if proc exposure is enabled. U-Boot boot paths call `process_uboot_commandline()` to merge or translate command-line data.

## State And Persistence Behavior
When enabled, bootinfo is persisted by implementation code for later `/proc` visibility. Otherwise calls are compiled away. Command-line processing mutates the provided command buffer only in U-Boot-enabled builds.

## Dependencies And Integration Points
It integrates with m68k boot parsers, platform config code, `/proc` bootinfo support, and U-Boot entry paths.

## Risks And Edge Cases
No-op stubs can hide missing config dependencies in code that expects side effects. Command buffer size must be honored by the U-Boot implementation.

## Test Signals
Boot with and without `CONFIG_BOOTINFO_PROC` and `CONFIG_UBOOT`; validate boot record parsing, `/proc` bootinfo output, and command-line preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootinfo.h -->
