# Chunk Research: fw_lpe11000.h lines 36515-39832

Source: `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h`

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.

## Chunk Identity

This chunk is a contiguous section of the static firmware image `emlxs_lpe11000_image[]` for Emulex LPe11000 adapters. The file header identifies the firmware as `LPe11000-S: v2.82a4 (zd282a4.all)`.

The selected line range covers image offsets `0x47448` through `0x4DBF0`, inclusive by row start. There are 3,318 initializer rows, each carrying 8 bytes, for 26,544 bytes of firmware payload in this chunk. Offset continuity is intact.

## APIs And Public Surface

No callable C API, type definition, macro definition, or preprocessor control is introduced inside this chunk. It is data inside the `static uint8_t emlxs_lpe11000_image[]` initializer guarded by `#ifdef EMLXS_FW_IMAGE_DEF`.

The external API relationship is established outside this chunk:

- `emlxs_fw.h` includes `fw_lpe11000.h` when building the firmware table.
- `EMLXS_FW_TABLE` maps `LPe11000_FW` to `emlxs_lpe11000_size`, `emlxs_lpe11000_image`, `emlxs_lpe11000_label`, and firmware component words.
- `emlxs_firmware_t` exposes the image pointer and size to the driver firmware path.
- `emlxs_extern.h` declares `emlxs_fw_load`, `emlxs_fw_download`, and `emlxs_fw_table`.

Adapter selection ties this image to Zephyr-family LPe11000 hardware in `emlxs_adapters.h`; single-port `LPe11000` and Oracle-branded `LPe11000_O` use `LPe11000_FW`.

## Control Flow Visible In The Chunk

At the C level, there is no local control flow. The compiler sees this range as byte constants only.

At the firmware-binary level, the data is ARM instruction stream material. Frequent instruction encodings include load/store forms (`E590...`, `E580...`, `E5C...`, `E5D...`), immediate/data-processing forms (`E3A...`, `E3C...`, `E38...`, `E33...`), prologue/epilogue-looking forms (`E1A0C00D`, `E92D...`, `E24CB004`, `E91B...`), and branch/call encodings.

Parsed as 32-bit words, this chunk contains 270 unconditional `EA...` branches, 125 `EB...` branch-with-link words, 494 condition-prefixed branch-like words, and 82 literal-load `E59F...` words.

The chunk begins mid-routine at `0x47448` and ends mid-routine at `0x4DBF0`; adjacent rows before and after continue instruction flow.

## State And Data Dependencies

The firmware code appears to operate on register-passed structures and memory-mapped or firmware-private state. Repeated accesses target small offsets such as `0x00`, `0x04`, `0x08`, `0x0c`, `0x10`, `0x14`, `0x18`, `0x1c`, `0x20`, `0x24`, `0x30`, `0x3c`, `0x40`, and `0x44`.

Those offsets are not named in the C header. The host driver treats the full array as opaque adapter firmware and supplies it through firmware loading/downloading routines.

No ASCII strings of length 4 or greater were present in the extracted chunk payload.

## Dependencies

Direct compile-time dependencies:

- `uint8_t` must already be defined by includers.
- `EMLXS_FW_IMAGE_DEF` controls whether the image bytes are emitted.
- `#pragma align 8(emlxs_lpe11000_image)` outside the chunk establishes alignment.

Runtime/driver dependencies visible from surrounding headers:

- Firmware table construction in `emlxs_fw.h`.
- Adapter identification in `emlxs_adapters.h`.
- Firmware loading/downloading declarations in `emlxs_extern.h`.
- Firmware layout structures in `emlxs_hw.h`.

## Risks And Review Notes

- Opaque binary risk: normal C review cannot validate memory safety or protocol correctness inside adapter-executed firmware.
- Integrity sensitivity: any byte edit changes firmware behavior.
- Chunk boundary risk: both start and end are inside firmware instruction flow.
- Build-size risk: this chunk contributes 26,544 bytes to the full `0x8A5CC` byte image when embedded.
- Portability/endian risk: the byte array must remain byte-exact and must not be word-swapped.

## Cross-Chunk References

- Previous chunk: required for the routine leading into `0x47448`.
- Next chunk: required for the routine continuing after `0x4DBF0`.
- File-level report should summarize this as one segment of `emlxs_lpe11000_image[]` and avoid inventing host-side APIs for this chunk.