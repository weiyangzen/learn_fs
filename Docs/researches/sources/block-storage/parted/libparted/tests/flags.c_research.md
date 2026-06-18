# File Research: sources/block-storage/parted/libparted/tests/flags.c

## Purpose

`flags.c` tests that setting filesystem/system type does not overwrite selected partition type flags.

## Main Responsibilities

- Creates an 80 MiB temporary disk image per test case.
- Tests GPT:
  - creates a GPT partition,
  - sets `PED_PARTITION_BIOS_GRUB`,
  - calls `ped_partition_set_system(ext4)`,
  - verifies the BIOS_GRUB flag remains set.
- Tests msdos:
  - creates an msdos partition,
  - sets `PED_PARTITION_BLS_BOOT`,
  - calls `ped_partition_set_system(ext4)`,
  - verifies the BLS_BOOT flag remains set.

## Dependencies and Interactions

Uses libparted GPT and msdos label implementations and the shared exception-aborting test handler.

## Notable Details

The comments in the msdos test say “BIOS_GRUB” even though the actual flag under test is `BLS_BOOT`.
