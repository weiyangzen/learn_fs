# File Research: sources/block-storage/util-linux/libblkid/src/partitions/partitions.h

## Purpose
Internal partition-probing header shared by `partitions.c` and individual partition table parsers.

## Main Components
- Includes internal `blkidP.h` and MBR definitions.
- Declares table/list creation helpers.
- Declares partition table ID/UUID setters.
- Declares partition add/part-number/parent lookup helpers.
- Declares nested subprobe entry point and type-only detection.
- Declares PTUUID setters for UUID and string IDs.
- Declares nested dimension validation.
- Declares partition setters for name, UTF-8 name, UUID, generated UUID, numeric type, type string, type UUID, and flags.
- Declares all partition prober `blkid_idinfo` objects.

## Dependencies and Interactions
Included by every partition prober in this group. It exposes only internal helpers, not public API; public declarations live in `blkid.h.in`.

## Research Notes
The header makes format probers small: each parser only needs to detect/parse its format and fill generic partition objects through these helpers.
