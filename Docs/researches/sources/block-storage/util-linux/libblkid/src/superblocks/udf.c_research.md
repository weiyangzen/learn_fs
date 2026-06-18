# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/udf.c

## Scope

Implements UDF probing, descriptor scanning, label/UUID/version extraction, and metadata identifier export.

## Behavior

- Scans Volume Structure Descriptors at session offset using sector size and candidate UDF block sizes.
- Looks for NSR descriptors, then validates Anchor Volume Descriptor Pointer at block 256 or 512.
- Walks the volume descriptor sequence, capped to 64 descriptors, and confirms real UDF via `*OSTA UDF Compliant` domain ID.
- Extracts volume ID, logical volume ID as primary label, volume set ID, generated UUID from volume set ID, application ID, and publisher ID from relevant descriptors.
- Reads Logical Volume Integrity Descriptor implementation-use data to refine UDF revision.
- Exports version, filesystem block size, and block size.

## Dependencies And Risks

- The idinfo is tolerant because initial magics are generic ECMA-167/ISO-13346 descriptors, not uniquely UDF.
- Descriptor string conversion depends on OSTA compressed Unicode CID mapping to Latin-1 or UTF-16BE.
- Descriptor sequence and LVID traversal are intentionally bounded to avoid crafted-media scanning costs.
