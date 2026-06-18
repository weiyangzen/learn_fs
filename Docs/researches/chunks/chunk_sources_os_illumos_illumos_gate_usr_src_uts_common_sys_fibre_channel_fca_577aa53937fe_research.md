# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 13289-16606

## Scope

This chunk is line range 13289-16606 of `fw_lpe11000.h`, an oversized generated firmware header in the illumos `emlxs` Fibre Channel adapter driver. The exact range is inside `static uint8_t emlxs_lpe11000_image[]` and covers firmware image byte offsets approximately `0x19E78` through `0x206B8`.

The surrounding file declares metadata for the LPe11000/LPe11000-S firmware image:

- `emlxs_lpe11000_label`: `LPe11000-S: v2.82a4 (zd282a4.all)`
- `emlxs_lpe11000_kern`: `0xFFE01250`
- `emlxs_lpe11000_stub`: `0x02E82894`
- `emlxs_lpe11000_sli1`: `0x06E32893`
- `emlxs_lpe11000_sli2`: `0x07E32894`
- `emlxs_lpe11000_sli3`: `0x0BE32894`
- `emlxs_lpe11000_sli4`: `0x00000000`
- full image size, outside this chunk: `0x8A5CC` bytes

## APIs And Exports

This chunk does not define C functions, macros, structs, or callable driver APIs. It contributes contiguous initializer bytes to `emlxs_lpe11000_image[]` when `EMLXS_FW_IMAGE_DEF` is enabled.

The public C-facing surface for the whole file is outside the chunk:

- `emlxs_lpe11000_image[]`, an 8-byte-aligned static byte array when embedded firmware images are compiled in.
- `emlxs_lpe11000_size`, `sizeof (emlxs_lpe11000_image)` when embedded; `0` otherwise.
- LPe11000 firmware label and version words used by `emlxs_fw.h`.

`emlxs_fw.h` registers this file in `EMLXS_FW_TABLE` as an `emlxs_firmware_t` entry with id `LPe11000_FW`. `emlxs_adapters.h` maps LPe11000 and Oracle-branded LPe11000-S adapter descriptors to `LPe11000_FW`.

## Control Flow

There is no host-side C control flow in the chunk. The apparent branches, calls, loads, stores, and returns are ARM instruction encodings stored as data for adapter firmware.

For the illumos driver, these bytes are opaque. The host-side flow is: build includes the byte array, firmware table references it, the driver selects `LPe11000_FW` for matching hardware, and firmware download logic transfers the blob to the adapter.

## State And Data

The chunk is source data only: a static `uint8_t` initializer, with no C variables or runtime state inside the range. Runtime state affected by this chunk exists in adapter firmware memory after download.

Visible data characteristics:

- Starts mid-routine around offset `0x19E78`; adjacent earlier bytes are active instruction data.
- Contains dense executable firmware bytes.
- Includes embedded literal/address tables and sentinel-like constants, including `0x12345678`, `0x11223344`, `0xAAAAAAAA`, ASCII-like `NEME`, and repeated address constants.
- Ends mid-routine; later bytes continue the same opaque firmware stream.

## Dependencies

- `EMLXS_FW_IMAGE_DEF` controls whether this byte data is compiled in.
- `EMLXS_FW_TABLE_DEF` in `emlxs_fw.h` includes this header and builds the firmware table.
- `MODFW_SUPPORT` can switch the image and size macros to zero placeholders.
- `emlxs_firmware_t` carries the image pointer, size, label, and version words.
- `emlxs_adapters.h` maps LPe11000-class devices to `LPe11000_FW`.

## Risks

- Opaque vendor firmware cannot be meaningfully validated as C source.
- Chunk boundaries split firmware routines; partial edits can break branch targets, literal pools, checksums, or layout.
- Offset comments are important for audit and correlation.
- Consumers must handle builds where embedded firmware is disabled and image/size are zero.
- Any byte change should be treated as firmware replacement, not a normal driver patch.

## Cross-Chunk References

- Earlier chunks define the array start, metadata, bootstrap/vector data, and bytes leading into this range.
- This chunk starts mid-routine around `0x19E78`; incoming branches and literal-pool references may originate earlier.
- Internal firmware branches may target outside this range.
- Later chunks continue the active routine and eventually contain the array terminator and `emlxs_lpe11000_size`.
- The final per-file report should merge this as an opaque middle segment of the LPe11000 firmware image.