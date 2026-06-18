# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp10000.h lines 29880-33197

## Scope

This chunk covers 26,544 bytes of the embedded `emlxs_lp10000_image[]` firmware blob, from image offset `0x3A4F0` through `0x40C9F`. The file belongs to the illumos Emulex Fibre Channel adapter support under subset A. The range is generated/static firmware data, not C implementation code.

The surrounding header defines LP10000 firmware metadata:

- `emlxs_lp10000_label` is `LP10000-S: v1.92a1 (td192a1.all)`.
- `emlxs_lp10000_image[]` is emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- The complete image is declared as `0x5BD00` bytes outside this chunk.

## APIs And Entry Points

This chunk does not define callable C APIs, functions, structs, macros, or control-flow entry points. Its public surface is positional binary content inside `static uint8_t emlxs_lp10000_image[]`.

The driver-facing API is established by adjacent file/header context:

- `fw_lp10000.h` exposes `emlxs_lp10000_size`, `emlxs_lp10000_image`, `emlxs_lp10000_label`, and version words such as `emlxs_lp10000_sli1`/`sli2`.
- `emlxs_fw.h` includes this header and places those fields into `EMLXS_FW_TABLE` entry `LP10000_FW`.
- Consumers treat this data as an adapter firmware image, not as host-executed C code.

## Data Layout And State

- Lines 29880-30223 are mostly zero-filled image space from offsets `0x3A4F0` through `0x3AFAF`, with sparse scalar data.
- Lines 30224-30272 introduce compact byte lookup tables with ascending byte values and `0x80` sentinel-like entries.
- Lines 30273-30300 contain table-like 32-bit quantities and firmware identity metadata, including the embedded ASCII marker `T2D1.92A1`.
- Lines 30301-30354 transition into ARM instruction words and loader/linker-looking data, with markers such as `DEND` and `LINK`.
- Lines 30355-30449 define named firmware sections or internal blocks: `BIUC`, `CRAM`, `FRXQ`, `ARMR`, `FIFO`, `RDMA`, `TDMA`, `LMAU`, and another `DEND`.
- Lines 30450-30522 contain pointer/address tables and diagnostic format strings, including `TIME: %08x  %s` and `Rcverr Frm %x. Idx %x.`.
- Lines 30523-33197 are dense ARM firmware code/data and end mid-routine at offset `0x40C9F`.

## Control Flow

There is no host-side C control flow in this line range. Firmware control flow is present only as opaque ARM instructions stored as bytes.

The firmware region around `0x3B218` starts with common ARM return/prologue patterns after the `T2D1.92A1` metadata. The `DEND`/`LINK` block around `0x3B2C0`-`0x3B3C7` appears to describe linked image records. The dense region after `0x3B908` contains repeated ARM branch/call/load/store encodings and continues beyond the chunk boundary.

## Dependencies

- C/header dependencies are limited to the surrounding `fw_lp10000.h` wrapper: `uint8_t`, include guards, C++ linkage guards, `#pragma align 8`, and the `EMLXS_FW_IMAGE_DEF` gate.
- Driver integration depends on `emlxs_fw.h`, which defines `emlxs_firmware_t` and builds the LP10000 firmware table entry.
- Firmware parsing/loading logic elsewhere depends on common Emulex structures such as `emlxs_fw_image_t`/`emlxs_fw_file_t` in `emlxs_hw.h`.
- The binary content depends on LP10000 adapter firmware conventions and ARM instruction encoding.

## Risks And Edge Cases

- The chunk is opaque vendor firmware; normal C review cannot prove adapter-side safety or bounds behavior.
- Offsets are contractual. Any insertion, deletion, reformatting error, byte-order change, or truncation would corrupt the image.
- Long zero ranges and sparse constants make accidental compression, deduplication, or cleanup especially risky.
- The embedded version marker `T2D1.92A1` aligns with the file label `v1.92a1`; mismatches would cause operational/debugging confusion.
- The chunk ends in the middle of dense firmware code, so routines spanning `0x40C98` require the next chunk.
- The bytes are compiled into kernel/driver memory when `EMLXS_FW_IMAGE_DEF` is enabled.

## Cross-Chunk References

- Previous chunks contain the start of `emlxs_lp10000_image[]`, including the image header and earlier firmware body up to offset `0x3A4EF`.
- This chunk starts in a padded/reserved region and reaches the visible `T2D1.92A1` marker at offsets `0x3B208`-`0x3B217`.
- The next chunk begins at offset `0x40CA0` and continues an ARM code path active at the end of this chunk.
- File-level merge should connect this chunk to the header wrapper at lines 14-24 and 47035-47042, plus `emlxs_fw.h` table construction for `LP10000_FW`.