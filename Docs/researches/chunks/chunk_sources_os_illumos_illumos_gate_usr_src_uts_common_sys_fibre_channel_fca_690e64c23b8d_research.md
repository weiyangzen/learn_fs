# Chunk Research: `fw_lp11002.h` lines 69696-72641

## Scope

This chunk is the final ordered slice of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11002.h`. It covers byte offsets `0x88130` through `0x8DCB8` of the generated `static uint8_t emlxs_lp11002_image[]` firmware array, then closes the `EMLXS_FW_IMAGE_DEF`, C++, and header include guards. The whole source file is an Emulex LP11002-S firmware image header for the illumos `emlxs` Fibre Channel adapter driver; this chunk does not define normal C functions.

## APIs And Compile-Time Interface

- `emlxs_lp11002_image[]`: the primary artifact whose tail appears here. When `EMLXS_FW_IMAGE_DEF` is set, this header contributes the actual embedded firmware bytes.
- `emlxs_lp11002_size`: defined at the end of this chunk as `sizeof (emlxs_lp11002_image)`, with the closing array comment documenting `0x8DCB8` bytes.
- Fallback macros: when `EMLXS_FW_IMAGE_DEF` is not set, this chunk defines `emlxs_lp11002_image` and `emlxs_lp11002_size` as `0`, allowing descriptor-only inclusion without allocating the blob.
- Include/ABI guards: the chunk closes `#ifdef __cplusplus` and `_FW_LP11002_H`, so it participates in the C/C++ compatible header surface.
- External consumer visible in adjacent file context: `emlxs_fw.h` includes `fw_lp11002.h` while building `EMLXS_FW_TABLE`, using `LP11002_FW`, `emlxs_lp11002_size`, `emlxs_lp11002_image`, label, kernel/stub, and SLI revision constants as an `emlxs_firmware_t` descriptor.

## Data And State

- The state in this chunk is immutable compiled-in firmware data. There are no C variables updated by host code and no host-side synchronization or lifetime management here.
- Lines 69696-72006 continue ARM-looking firmware instruction words. The bytes show common ARM encodings for loads/stores, branches, subroutine calls, status-byte updates, and return sequences. From the host driver perspective these are opaque bytes.
- Around lines 72007-72387 the blob transitions into mixed code/data: short numeric tables, embedded ASCII/debug or section labels, and address-like big-endian values following `DEND`.
- Lines 72388-72622 are mostly zero-filled/padding and sparse configuration words, likely reserved fixed-size image-table or trailer space.
- Lines 72623-72624 contain final nonzero trailer words immediately before the array closes, likely integrity, fill, or sentinel bytes within the firmware format.

## Control Flow

- There is no host C control flow in this chunk except preprocessor selection: embedded image plus computed size when `EMLXS_FW_IMAGE_DEF` is active, otherwise zero-valued image/size macros.
- The byte stream itself contains firmware-side control flow, with ARM branch/call patterns crossing within this chunk and likely to/from earlier chunks.
- The array starts before this chunk and ends here, so any byte offset, checksum, or jump-table entry in the tail depends on exact bytes from prior chunks.

## Dependencies

- Depends on `uint8_t` being available before including this header when `EMLXS_FW_IMAGE_DEF` is enabled.
- Depends on `EMLXS_FW_IMAGE_DEF` policy from `emlxs_fw.h`.
- The driver firmware table depends on the end-of-array `emlxs_lp11002_size`; corruption in this tail changes the payload size or contents observed by firmware download code.
- The blob is tied to metadata declared at the top of the file: label, kernel/stub addresses, and SLI revision constants.

## Risks And Cross-Chunk References

- Editing any byte can silently corrupt adapter firmware; changes should be treated as binary-image replacement.
- The final trailer/checksum/sentinel-looking bytes may be validated by loader or device firmware.
- Missing, extra, or reordered initializer bytes would change the image length and break embedded offsets.
- Prior chunks define the prologue, metadata, and earlier image bytes; this chunk cannot stand alone because it starts mid-initializer and closes the full image.
- `emlxs_fw.h` cross-references this file as the LP11002 entry in `EMLXS_FW_TABLE`; the final per-file report should connect this chunk’s trailer and size macro to that descriptor table.