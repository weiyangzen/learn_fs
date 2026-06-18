# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 69696-70310

## Scope

This chunk is the tail of the generated LP11000 firmware header. It remains inside `static uint8_t emlxs_lp11000_image[]` until line 70295, then defines the public size macro and the no-image fallback macros under `EMLXS_FW_IMAGE_DEF`.

## APIs and Exports

- `emlxs_lp11000_image[]`: embedded LP11000 firmware byte array.
- `emlxs_lp11000_size`: defined as `sizeof (emlxs_lp11000_image)`; final image length comment records `0x893DC` bytes.
- Fallback macros: when `EMLXS_FW_IMAGE_DEF` is unset, both `emlxs_lp11000_image` and `emlxs_lp11000_size` become `0`.
- The chunk closes the array, `EMLXS_FW_IMAGE_DEF` conditional, C++ guard, and `_FW_LP11000_H`.

## Firmware Structure

Visible directory/table tags include `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `RDM2`, `TDMA`, `LMAU`, `PCIR`, and `DEND`. The `LINK` record begins before this chunk and continues here. These look like firmware-owned register or memory-region descriptors, with sequential big-endian-looking 32-bit entries such as `0x0a000400...` and `0x0b000000...`.

After `DEND`, the chunk contains embedded ARM instruction words, pointer/vector tables, lookup tables using `0x80` as a sentinel, configuration/address-length pairs, large zero-filled reserved regions, sparse constants, and a final trailer/signature-like byte pattern.

## Control Flow and State

There is no host-side C control flow beyond preprocessor selection. Runtime behavior is opaque adapter firmware:

- ARM code begins around offset `0x886d0`.
- It includes supervisor calls, mode/status register operations, branch-and-link instructions, loops, and returns via `mov pc, lr` encodings.
- It appears to touch memory-mapped state around offsets such as `0x0c`, `0x44`, `0x4f0`, and `0x35c`.
- Host-visible state is only immutable firmware bytes plus the exported size macro.

## Dependencies

- Depends on `EMLXS_FW_IMAGE_DEF` to emit storage versus zero placeholders.
- Depends on `uint8_t` from including driver headers.
- Consumed via `emlxs_fw.h`, which binds `emlxs_lp11000_size` and `emlxs_lp11000_image` into the Emulex firmware catalog.
- Semantics depend on LP11000 adapter firmware format and hardware, not normal illumos C logic.

## Risks

- Any byte edit can corrupt firmware code, descriptor tables, branch targets, reserved fields, or trailer/checksum material while still compiling.
- Byte order must remain exact.
- Fallback macros mean callers must not dereference `emlxs_lp11000_image` unless the image-bearing build path is active.
- Because this chunk closes the array and header guards, syntax damage here breaks all consumers of `fw_lp11000.h`.

## Cross-Chunk References

- Earlier chunks contain the image header and most firmware code/data.
- This chunk continues a `LINK` record that starts before line 69696.
- `DEND` marks the end of a directory/table block that began in earlier chunks.
- This is the final chunk for the file and supplies the closing size/fallback definitions.