<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/msdos.c -->
# sources/distributed-fs/ceph-client/block/partitions/msdos.c

## Purpose

`msdos.c` implements the Linux parser for DOS/MBR partition tables and several MBR-contained subpartition formats. It recognizes primary and extended partitions, protects GPT disks by ignoring protective MBRs, detects AIX labels, and optionally parses Solaris x86 VTOC, BSD disklabels, UnixWare slices, and Minix subpartitions.

## Important APIs, Types, And Functions

The public entry point is `msdos_partition(struct parsed_partitions *state)`. Core helpers are `nr_sects()`, `start_sect()`, `is_extended_partition()`, `msdos_magic_present()`, `aix_magic_present()`, `set_info()`, and `parse_extended()`.

Subpartition support is split across `parse_solaris_x86()`, `parse_bsd()`, `parse_freebsd()`, `parse_netbsd()`, `parse_openbsd()`, `parse_unixware()`, and `parse_minix()`, gated by Kconfig symbols. The `subtypes[]` table maps MBR type ids to subparsers. Local disk-format structs model Solaris VTOC, BSD disklabels, UnixWare slices, and Minix secondary MBRs.

## Control Flow

`msdos_partition()` reads sector 0. Before checking the DOS `55 aa` magic, it calls `aix_magic_present()` because some AIX disks lack DOS magic. AIX detection returns to `aix_partition()` when configured, otherwise prints `[AIX]` and declines the disk.

When DOS magic is present, the parser validates all four boot indicators as either `0` or `0x80`; if the first invalid indicator still looks like a FAT boot sector, it treats the disk as a whole-disk FAT volume and returns success without partitions. It then ignores GPT protective MBRs when EFI partition support is configured.

The first pass emits primary partitions and follows extended partitions. Extended partition parsing treats logical partitions as a linked list of partition tables, emits data entries, follows the first extended link, guards against loops with `loopct > 100`, and validates suspicious third/fourth entries against parent extended bounds. The second pass invokes subtype parsers for recognized primary partition ids.

## State And Persistence Behavior

The parser mutates `state->next` for logical and subpartition allocation, fills per-slot metadata UUIDs from the MBR disk signature in `set_info()`, and sets RAID flags for Linux RAID ids. It does not persist data. On-disk persistent inputs include the MBR, EBR chain, disk signature, type ids, and optional nested labels.

## Dependencies And Integration Points

Dependencies include `linux/msdos_fs.h`, `linux/msdos_partition.h`, `linux/unaligned.h`, `check.h`, and `efi.h`. It integrates with AIX and EFI parsers through conditional calls and with the generic partition scanner through `parsed_partitions`. FAT boot-sector checks use `struct fat_boot_sector` and `fat_valid_media()`.

## Risks And Edge Cases

Extended partition chains are attacker-controlled linked lists; the loop counter, `state->limit`, DOS magic checks, and bounds checks on unusual entries prevent infinite loops and bogus partitions. Logical block sizes larger than 512 bytes are handled with `sector_size`, but the protective one-sector extended partition placeholder is intentionally approximate. AIX and Solaris share confusing signatures/type ids with Linux swap/data cases, so detection includes compatibility heuristics. Subparsers must avoid duplicating parent whole-disk entries and reject out-of-parent BSD subpartitions.

## Test Signals

Tests should cover plain MBRs, invalid boot indicators, whole-disk FAT, GPT protective MBR, AIX magic with and without Linux partitions, extended chains including loops and OS/2-style extra entries, Linux RAID flags, DM/EZD annotations, and each configured subparser. Expected signals include stable primary slots 1-4, logical slots starting at 5, disk-signature UUIDs like `<disk>-<slot>`, and graceful stop at `state->limit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/msdos.c -->
