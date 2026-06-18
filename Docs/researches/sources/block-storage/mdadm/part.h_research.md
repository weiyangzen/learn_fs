# File Research: sources/block-storage/mdadm/part.h

## Role

`part.h` defines packed MBR and GPT partition table structures used by mdadm partition-detection code.

## Definitions

- MBR constants: `MBR_SIGNATURE_MAGIC`, `MBR_PARTITIONS`, and `MBR_GPT_PARTITION_TYPE`.
- `struct MBR_part_record` for a 16-byte MBR partition entry.
- `struct MBR` for the 446-byte boot area, four partition records, and signature.
- GPT constants: `GPT_SIGNATURE_MAGIC`.
- `struct GPT_part_entry` for GPT partition entry fields.
- `struct GPT` for GPT header fields and padding.

## Invariants

All structures are packed and use explicit Linux integer types/endian conversion macros. They model on-disk layouts, so padding or host-endian assumptions would be incorrect.
