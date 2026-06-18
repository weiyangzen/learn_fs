# File Research: sources/block-storage/lvm2/lib/label/label.h

## Purpose
Declares the LVM on-disk label header format, in-memory label/labeller interfaces, label scan entry points, and bcache-backed device byte I/O wrappers implemented in `label.c`.

## Main Contents
- Defines `LABEL_ID`, `LABEL_SIZE`, `LABEL_SCAN_SECTORS`, and `LABEL_SCAN_SIZE`.
- Defines packed `struct label_header`, whose 32-byte on-disk layout stores the label id, label sector, CRC, payload offset, and type.
- Defines in-core `struct label` with type, sector, labeller, device, and format-specific info pointer.
- Defines `struct label_ops`, the vtable for format-specific label detection, read, write, initialization, label destruction, and labeller destruction.
- Declares scan APIs for whole-system scans, selected device scans, cached/rw/exclusive scans, online VG scans, PVID lookup, invalidation, bcache setup/open/reopen, and bcache destroy/drop.
- Declares byte I/O wrappers used by other modules instead of calling bcache directly.

## Dependencies
Includes LVM IDs, `struct device`, and bcache definitions. Forward-declares command context, filters, labellers, and logical volumes to keep the header usable across label, metadata, device, and activation code.

## Risk Notes
`LABEL_SIZE` is deliberately one sector and the header warns to think carefully before changing it. The scan constants and packed on-disk layout are format compatibility boundaries. The byte I/O wrapper declarations make this header a broad dependency beyond label scanning.
