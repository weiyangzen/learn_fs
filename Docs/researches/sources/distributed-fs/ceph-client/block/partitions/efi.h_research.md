<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.h -->
# sources/distributed-fs/ceph-client/block/partitions/efi.h

## Purpose
`efi.h` defines GPT/PMBR constants, well-known partition type GUIDs, and packed on-disk structure layouts used by `efi.c`.

## Important APIs, Types, and Functions
There are no functions. Constants cover MBR signature, EFI protective MBR OS types, GPT primary LBA, GPT signature/revision, and common GUIDs for EFI system, legacy MBR, Microsoft reserved/basic data, Linux RAID, swap, and LVM. Types include `gpt_header`, `gpt_entry_attributes`, `gpt_entry`, `gpt_mbr_record`, and `legacy_mbr`.

## Control Flow
The header has no executable flow. `efi.c` uses these definitions to validate disk bytes and to populate partition metadata.

## State and Persistence Behavior
The structs model persistent GPT and PMBR on-disk state. Packed layout and little-endian fields are part of the disk-format contract.

## Dependencies and Integration Points
It depends on Linux EFI GUID types, endian integer typedefs, filesystem/kernel headers, and compiler packing. It is tightly coupled to the parser and any code comparing well-known partition type GUIDs.

## Risks and Edge Cases
Changing field order, packing, bitfield widths, or GUID constants would break GPT parsing. `gpt_entry_attributes` uses bitfields inside a packed type, so compiler expectations matter. The header intentionally omits variable reserved tail bytes from `gpt_header`; parser size checks handle full logical-block headers.

## Test Signals
Compile-time structure size/offset checks, GPT parser tests on known images, GUID comparison tests for RAID/swap/LVM/basic data, and cross-architecture endian/packing builds are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/efi.h -->
