# File Research: sources/block-storage/util-linux/libblkid/src/partitions/dos.c

## Purpose
Parses MS-DOS/MBR partition tables, extended/logical partitions, and nested partition tables for selected MBR partition types.

## Main Components
- `dos_nested[]` maps FreeBSD, NetBSD, OpenBSD, UnixWare, Solaris x86, and Minix MBR types to nested probers.
- `is_extended()` identifies DOS, Windows 95, and Linux extended partition types.
- `parse_dos_extended()` follows EBR chains, adds logical data partitions within the extended range, rejects duplicate/non-advancing/out-of-range links, and caps empty-link traversal.
- `is_lvm()` detects `TYPE=LVM2_member` from existing probe values.
- `is_empty_mbr()` detects a valid MBR with no non-empty entries.
- `probe_dos_pt()` reads sector 0, rejects AIX, invalid boot indicators, GPT protective MBR, FAT/exFAT/NTFS boot-sector false positives, and empty MBR-on-LVM cases.
- Records wipe range over the MBR partition table area.
- Extracts disk ID as PTUUID.
- Creates a `dos` table, adds primary partitions, sets part numbers for logical partitions starting at 5, parses extended chains, and subprobes supported nested table types on non-tiny devices.
- `dos_pt_idinfo` detects `55 AA` at bytes 510-511.

## Dependencies and Interactions
Uses MBR definitions from `pt-mbr.h`, superblock false-positive helpers for FAT/exFAT/NTFS, AIX magic, and nested probing from `partitions.c`.

## Research Notes
All starts/sizes are converted to 512-sector units using the device sector-size factor. The parser mirrors kernel conventions such as preserving primary partition numbers for empty entries.
